from . import enums as E
from .models import ScheduleEvent, Task, VolunteerRecord


def get_dashboard_data() -> dict:
    anchor_date = "2026-04-02"
    schedule_events_rows = (
        ScheduleEvent.query
        .order_by(ScheduleEvent.start_at.asc())
        .limit(20)
        .all()
    )
    schedule_events = [
        {
            "id": x.id,
            "title": x.title,
            "event_type": x.event_type,
            "source": x.source,
            "start_at": x.start_at,
            "end_at": x.end_at,
            "location": x.location or "",
            "description": x.description or "",
            "is_editable": bool(x.is_editable),
        }
        for x in schedule_events_rows
    ]
    task_rows = Task.query.order_by(Task.id.asc()).limit(5).all()
    task_previews = [{"title": x.title, "status": x.status} for x in task_rows]

    today_course_count = sum(1 for x in schedule_events if x["event_type"] == E.SCHEDULE_EVENT_TYPE_CLASS and x["start_at"].startswith(anchor_date))
    pending_task_count = Task.query.filter(Task.status.in_([E.TASK_STATUS_PENDING, E.TASK_STATUS_VIEWED])).count()
    ongoing_task_count = Task.query.filter_by(status=E.TASK_STATUS_IN_PROGRESS).count()
    volunteer_hours_total = round(sum(float(x.hours or 0) for x in VolunteerRecord.query.all()), 1)

    return {
        "stats": {
            "today_course_count": today_course_count,
            "pending_task_count": pending_task_count,
            "ongoing_task_count": ongoing_task_count,
            "volunteer_hours_total": volunteer_hours_total,
        },
        "date_label": "2026-04-02 周四",
        "schedule_events": schedule_events,
        "task_previews": task_previews,
    }
