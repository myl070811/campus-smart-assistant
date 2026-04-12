from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from sqlalchemy import func, or_

from . import enums as E
from .db import db
from .models import Organization, ScheduleEvent, Task, VolunteerRecord


def _to_iso(dt: datetime | None) -> str:
    if not dt:
        return ""
    if dt.tzinfo is None:
        return dt.isoformat(timespec="seconds")
    return dt.astimezone(timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds")


def get_dashboard_data(user: Optional[Dict[str, Any]] = None) -> dict:
    """
    Dashboard statistics from database (no mock).
    Keep response shape compatible with current frontend mapper.
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start = today_start + timedelta(days=1)
    date_label = today_start.astimezone(timezone.utc).strftime("%Y-%m-%d")

    pending_count = Task.query.filter_by(status="pending").count()
    in_progress_count = Task.query.filter_by(status="in_progress").count()
    done_count = Task.query.filter_by(status="done").count()
    organization_count = Organization.query.count()
    today_course_count = (
        ScheduleEvent.query
        .filter(ScheduleEvent.event_type == "class")
        .filter(ScheduleEvent.start_at >= today_start, ScheduleEvent.start_at < tomorrow_start)
        .count()
    )
    today_ev_q = (
        ScheduleEvent.query.filter(
            ScheduleEvent.start_at >= today_start, ScheduleEvent.start_at < tomorrow_start
        )
    )
    if user is not None:
        role = str(user.get("role") or "").strip()
        if role not in {"org_admin", "tw_admin"}:
            sid = str(user.get("student_id") or "").strip()
            if sid:
                today_ev_q = today_ev_q.filter(
                    or_(
                        ScheduleEvent.is_personal_plan.is_(False),
                        ScheduleEvent.owner_student_id == sid,
                    )
                )
            else:
                today_ev_q = today_ev_q.filter(ScheduleEvent.is_personal_plan.is_(False))
    today_events = today_ev_q.order_by(
        ScheduleEvent.start_at.asc(), ScheduleEvent.id.asc()
    ).all()

    db_val = (
        db.session.query(func.sum(VolunteerRecord.hours))
        .filter(VolunteerRecord.status == E.VOLUNTEER_STATUS_RECOGNIZED)
        .scalar()
    )
    volunteer_hours_total = float(db_val) if db_val else 0.0
    recent_tasks = (
        Task.query
        .order_by(Task.created_at.desc(), Task.id.desc())
        .limit(5)
        .all()
    )

    # Keep frontend-compatible fields used by mapDashboardFromApi / Dashboard.vue
    # while exposing required real metrics from DB.
    return {
        "stats": {
            "today_course_count": today_course_count,
            "pending_task_count": pending_count,
            "ongoing_task_count": in_progress_count,
            "volunteer_hours_total": round(volunteer_hours_total, 1),
            "done_task_count": done_count,
            "organization_count": organization_count,
        },
        "date_label": date_label,
        "schedule_events": [
            {
                "id": row.id,
                "title": row.title,
                "event_type": row.event_type,
                "source": row.source,
                "start_at": _to_iso(row.start_at),
                "end_at": _to_iso(row.end_at),
                "location": row.location or "",
                "description": row.description or "",
                "is_editable": bool(row.is_editable),
            }
            for row in today_events
        ],
        "task_previews": [{"title": row.title, "status": row.status} for row in recent_tasks],
        "recent_tasks": [{"title": row.title, "status": row.status} for row in recent_tasks],
    }

