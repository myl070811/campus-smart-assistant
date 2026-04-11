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

from sqlalchemy import func

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


def list_events(event_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    q = ScheduleEvent.query
    if event_types:
        allow = set(event_types)
        q = q.filter(ScheduleEvent.event_type.in_(allow))
    events = q.order_by(ScheduleEvent.start_at.asc()).all()
    return [_event_public(x) for x in events]


def create_personal_plan(payload: Dict[str, Any]) -> Dict[str, Any]:
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
    )
    db.session.add(row)
    db.session.commit()
    return _event_public(row)


def update_personal_plan(plan_id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    old = ScheduleEvent.query.filter_by(id=plan_id, is_personal_plan=True).first()
    if not old:
        return None
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


def delete_personal_plan(plan_id: str) -> bool:
    row = ScheduleEvent.query.filter_by(id=plan_id, is_personal_plan=True).first()
    if not row:
        return False
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


