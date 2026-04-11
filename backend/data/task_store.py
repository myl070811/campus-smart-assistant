from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func

from . import enums as E
from .db import db
from .models import Task, TaskLog

NEXT_STATUS: Dict[str, Optional[str]] = {
    E.TASK_STATUS_PENDING: E.TASK_STATUS_VIEWED,
    E.TASK_STATUS_VIEWED: E.TASK_STATUS_IN_PROGRESS,
    E.TASK_STATUS_IN_PROGRESS: E.TASK_STATUS_DONE,
    E.TASK_STATUS_DONE: None,
}


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _to_iso(dt: Optional[datetime]) -> str:
    if not dt:
        return ""
    return dt.isoformat().replace("+00:00", "Z")


def _task_public(task: Task) -> Dict[str, Any]:
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description or "",
        "task_type": task.task_type,
        "source_type": task.source_type,
        "source_org_id": task.source_org_id or "",
        "current_org_id": task.current_org_id or "",
        "current_owner_name": task.current_owner_name or "",
        "owner_name": task.current_owner_name or "",
        "owner_is_self": bool(task.owner_is_self),
        "due_date": task.due_date or "",
        "deadline": task.due_date or "",
        "priority": task.priority,
        "status": task.status,
    }


def _log_public(log: TaskLog) -> Dict[str, Any]:
    return {
        "id": f"log_{log.id}",
        "action": log.action,
        "actor": log.actor,
        "created_at": _to_iso(log.created_at),
        "note": log.note or "",
        "from_status": log.from_status,
        "to_status": log.to_status,
        "from_owner": log.from_owner or "",
        "to_owner": log.to_owner or "",
        "from_org_id": log.from_org_id or "",
        "to_org_id": log.to_org_id or "",
    }


def _task_logs(task_id: str) -> List[Dict[str, Any]]:
    rows = (
        TaskLog.query.filter_by(task_id=task_id)
        .order_by(TaskLog.id.asc())
        .all()
    )
    return [_log_public(x) for x in rows]


def _append_log(task_id: str, actor: str, action: str, **fields: Any) -> TaskLog:
    log = TaskLog(
        task_id=task_id,
        action=action,
        actor=(actor or "user").strip() or "user",
        created_at=_now(),
        note=fields.get("note"),
        from_status=fields.get("from_status"),
        to_status=fields.get("to_status"),
        from_owner=fields.get("from_owner"),
        to_owner=fields.get("to_owner"),
        from_org_id=fields.get("from_org_id"),
        to_org_id=fields.get("to_org_id"),
    )
    db.session.add(log)
    return log


def _next_task_id() -> str:
    max_num = (
        db.session.query(func.max(func.substr(Task.id, 2).cast(db.Integer)))
        .filter(Task.id.like("t%"))
        .scalar()
    )
    n = int(max_num or 0) + 1
    return f"t{n}"


def list_tasks(current_org_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    q = Task.query
    if current_org_id:
        q = q.filter(Task.current_org_id == current_org_id)
    if status:
        q = q.filter(Task.status == status)
    rows = q.order_by(Task.id.asc()).all()
    return [_task_public(t) for t in rows]


def create_task(payload: Dict[str, Any], actor: str) -> Tuple[bool, Optional[str], Optional[str], Optional[Dict[str, Any]]]:
    title = str(payload.get("title", "")).strip()
    task_type = str(payload.get("task_type", "")).strip()
    source_org_id = str(payload.get("source_org_id", "")).strip()
    current_org_id = str(payload.get("current_org_id", "")).strip()
    current_owner_name = str(payload.get("current_owner_name", "")).strip()
    due_date = str(payload.get("deadline", "") or payload.get("due_date", "")).strip()
    description = str(payload.get("description", "")).strip()
    status = str(payload.get("status", E.TASK_STATUS_PENDING)).strip() or E.TASK_STATUS_PENDING

    if not title:
        return False, "bad_request", "title is required", None
    if not task_type:
        return False, "bad_request", "task_type is required", None
    if not current_org_id:
        return False, "bad_request", "current_org_id is required", None
    if not current_owner_name:
        return False, "bad_request", "current_owner_name is required", None
    if not due_date:
        return False, "bad_request", "deadline is required", None
    if status not in E.TASK_STATUSES:
        return False, "bad_request", "invalid status", None

    task = Task(
        id=_next_task_id(),
        title=title,
        description=description,
        task_type=task_type,
        source_type=E.TASK_SOURCE_ORGANIZATION if source_org_id else E.TASK_SOURCE_PERSONAL,
        source_org_id=source_org_id,
        current_org_id=current_org_id,
        current_owner_name=current_owner_name,
        owner_is_self=False,
        due_date=due_date,
        priority=str(payload.get("priority", E.TASK_PRIORITY_MEDIUM)),
        status=status,
    )
    db.session.add(task)
    db.session.flush()
    _append_log(task.id, actor, E.TASK_LOG_CREATE, note=description or None)
    _append_log(task.id, actor, "assign", to_owner=current_owner_name, to_org_id=current_org_id, note="initial assignment")
    db.session.commit()
    return True, None, None, {"task": _task_public(task), "logs": _task_logs(task.id)}


def get_task_detail(task_id: str, actor: str) -> Optional[Tuple[Dict[str, Any], List[Dict[str, Any]]]]:
    task = Task.query.filter_by(id=task_id).first()
    if not task:
        return None
    _append_log(task.id, actor, E.TASK_LOG_VIEW)
    db.session.commit()
    return _task_public(task), _task_logs(task.id)


def update_status(task_id: str, new_status: str, actor: str) -> Tuple[bool, Optional[str], Optional[str], Optional[Dict[str, Any]]]:
    task = Task.query.filter_by(id=task_id).first()
    if not task:
        return False, "not_found", "任务不存在", None
    cur = task.status
    expected = NEXT_STATUS.get(cur)
    if expected != new_status:
        return False, "invalid_transition", "请按顺序推进状态", None
    _append_log(task.id, actor, E.TASK_LOG_STATUS_CHANGE, from_status=cur, to_status=new_status)
    task.status = new_status
    db.session.commit()
    return True, None, None, {"task": _task_public(task), "logs": _task_logs(task.id)}


def transfer_task(task_id: str, to_owner: str, note: str, actor: str, to_org_id: str = "") -> Tuple[bool, Optional[str], Optional[str], Optional[Dict[str, Any]]]:
    task = Task.query.filter_by(id=task_id).first()
    if not task:
        return False, "not_found", "任务不存在", None
    to_owner = (to_owner or "").strip()
    if not to_owner:
        return False, "bad_request", "负责人不能为空", None

    from_owner = task.current_owner_name or ("本人" if task.owner_is_self else "")
    from_org_id = task.current_org_id or ""
    to_org = (to_org_id or "").strip() or from_org_id
    _append_log(
        task.id,
        actor,
        E.TASK_LOG_TRANSFER,
        from_owner=from_owner,
        to_owner=to_owner,
        from_org_id=from_org_id,
        to_org_id=to_org,
        note=(note or "").strip() or None,
    )
    task.current_owner_name = to_owner
    task.current_org_id = to_org
    task.owner_is_self = False
    db.session.commit()
    return True, None, None, {"task": _task_public(task), "logs": _task_logs(task.id)}
