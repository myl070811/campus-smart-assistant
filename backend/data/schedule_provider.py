"""
Unified schedule event provider (mock).

Event schema (snake_case):
- id
- title
- event_type: class | personal_plan | org_task | volunteer | work_study | innovation_project
- source
- start_at (ISO datetime, local)
- end_at (ISO datetime, local)
- location
- description
- is_editable
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import func, or_

from .db import db
from .models import ScheduleEvent


EVENT_TYPE_CLASS = "class"
EVENT_TYPE_PERSONAL_PLAN = "personal_plan"
EVENT_TYPE_ORG_TASK = "org_task"
EVENT_TYPE_VOLUNTEER = "volunteer"
EVENT_TYPE_WORK_STUDY = "work_study"
EVENT_TYPE_INNOVATION_PROJECT = "innovation_project"

EVENT_TYPES = (
    EVENT_TYPE_CLASS,
    EVENT_TYPE_PERSONAL_PLAN,
    EVENT_TYPE_ORG_TASK,
    EVENT_TYPE_VOLUNTEER,
    EVENT_TYPE_WORK_STUDY,
    EVENT_TYPE_INNOVATION_PROJECT,
)


def _is_schedule_admin(user: Optional[Dict[str, Any]]) -> bool:
    role = str((user or {}).get("role") or "").strip()
    return role in {"org_admin", "tw_admin"}


def _schedule_student_sid(user: Optional[Dict[str, Any]]) -> str:
    return str((user or {}).get("student_id") or "").strip()


def _assert_personal_plan_write(user: Optional[Dict[str, Any]], row: ScheduleEvent) -> None:
    if _is_schedule_admin(user):
        return
    sid = _schedule_student_sid(user or {})
    owner = str(row.owner_student_id or "").strip()
    if sid and owner == sid:
        return
    raise PermissionError("forbidden")


def _to_iso(dt: Optional[datetime]) -> str:
    if not dt:
        return ""
    # keep frontend-compatible ISO-like string without timezone suffix
    if dt.tzinfo is None:
        return dt.isoformat(timespec="seconds")
    return dt.astimezone(timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds")


def _parse_iso(v: str) -> datetime:
    try:
        raw = (v or "").strip()
        if len(raw) == 10:
            return datetime.strptime(raw, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid datetime format, expected ISO datetime") from exc


def _event_public(e: ScheduleEvent) -> Dict[str, Any]:
    return {
        "id": e.id,
        "title": e.title,
        "event_type": e.event_type,
        "source": e.source,
        "start_at": _to_iso(e.start_at),
        "end_at": _to_iso(e.end_at),
        "location": e.location or "",
        "description": e.description or "",
        "is_editable": bool(e.is_editable),
    }


def _next_plan_id() -> str:
    max_num = (
        db.session.query(func.max(func.substr(ScheduleEvent.id, 6).cast(db.Integer)))
        .filter(ScheduleEvent.id.like("plan_%"))
        .scalar()
    )
    n = int(max_num or 1000) + 1
    return f"plan_{n}"


def list_events(
    event_types: Optional[List[str]] = None,
    user: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    q = ScheduleEvent.query
    if event_types:
        allow = set(event_types)
        q = q.filter(ScheduleEvent.event_type.in_(allow))
    if user is not None and not _is_schedule_admin(user):
        sid = _schedule_student_sid(user)
        if sid:
            q = q.filter(
                or_(
                    ScheduleEvent.is_personal_plan.is_(False),
                    ScheduleEvent.owner_student_id == sid,
                )
            )
        else:
            q = q.filter(ScheduleEvent.is_personal_plan.is_(False))
    events = q.order_by(ScheduleEvent.start_at.asc()).all()
    return [_event_public(x) for x in events]


def create_personal_plan(
    payload: Dict[str, Any], user: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    role = str((user or {}).get("role") or "").strip()
    sid = _schedule_student_sid(user or {})
    if _is_schedule_admin(user or {}):
        owner = str(payload.get("owner_student_id") or "").strip() or sid
    else:
        if role != "student" or not sid:
            raise ValueError("profile not linked to student account")
        owner = sid
    plan = {
        "id": _next_plan_id(),
        "title": str(payload.get("title", "")).strip(),
        "event_type": EVENT_TYPE_PERSONAL_PLAN,
        "source": "manual_input",
        "start_at": str(payload.get("start_at", "")).strip(),
        "end_at": str(payload.get("end_at", "")).strip(),
        "location": str(payload.get("location", "")).strip(),
        "description": str(payload.get("description", "")).strip(),
        "is_editable": True,
    }
    _validate_plan(plan)
    row = ScheduleEvent(
        id=plan["id"],
        title=plan["title"],
        event_type=plan["event_type"],
        source=plan["source"],
        start_at=_parse_iso(plan["start_at"]),
        end_at=_parse_iso(plan["end_at"]),
        location=plan["location"],
        description=plan["description"],
        is_editable=True,
        is_personal_plan=True,
        owner_student_id=owner,
    )
    db.session.add(row)
    db.session.commit()
    return _event_public(row)


def update_personal_plan(
    plan_id: str, payload: Dict[str, Any], user: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    old = ScheduleEvent.query.filter_by(id=plan_id, is_personal_plan=True).first()
    if not old:
        return None
    _assert_personal_plan_write(user, old)
    plan = {
        "id": old.id,
        "title": str(payload.get("title", old.title)).strip(),
        "event_type": old.event_type,
        "source": old.source,
        "start_at": str(payload.get("start_at", old.start_at)).strip(),
        "end_at": str(payload.get("end_at", old.end_at)).strip(),
        "location": str(payload.get("location", old.location or "")).strip(),
        "description": str(payload.get("description", old.description or "")).strip(),
        "is_editable": bool(old.is_editable),
    }
    _validate_plan(plan)
    old.title = plan["title"]
    old.start_at = _parse_iso(plan["start_at"])
    old.end_at = _parse_iso(plan["end_at"])
    old.location = plan["location"]
    old.description = plan["description"]
    db.session.commit()
    return _event_public(old)


def delete_personal_plan(plan_id: str, user: Optional[Dict[str, Any]] = None) -> bool:
    row = ScheduleEvent.query.filter_by(id=plan_id, is_personal_plan=True).first()
    if not row:
        return False
    _assert_personal_plan_write(user, row)
    db.session.delete(row)
    db.session.commit()
    return True


def _validate_plan(plan: Dict[str, Any]) -> None:
    if not plan["title"]:
        raise ValueError("title is required")
    if not plan["start_at"] or not plan["end_at"]:
        raise ValueError("start_at and end_at are required")
    start = _parse_iso(plan["start_at"])
    end = _parse_iso(plan["end_at"])
    if end <= start:
        raise ValueError("end_at must be later than start_at")
