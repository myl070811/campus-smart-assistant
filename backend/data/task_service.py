from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, func, or_

from . import enums as E
from .db import db
from .models import Organization, Task, TaskLog

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


def _parse_due_date(raw: str) -> Optional[datetime]:
    s = (raw or "").strip()
    if not s:
        return None
    try:
        if len(s) == 10:
            return datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def _due_date_display(dt: Optional[datetime]) -> str:
    if not dt:
        return ""
    if dt.tzinfo is None:
        return dt.strftime("%Y-%m-%d")
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d")


def _normalize_task_flow(raw: str) -> str:
    s = (raw or "").strip()
    if s in E.TASK_FLOW_TYPES:
        return s
    return E.LEGACY_ASSIGNMENT_TO_FLOW.get(s, E.TASK_FLOW_SINGLE_DEPARTMENT)


def _parse_collaborating_org_ids(task: Task) -> List[str]:
    try:
        data = json.loads(task.collaborating_org_ids_json or "[]")
        if isinstance(data, list):
            return [str(x).strip() for x in data if str(x).strip()]
    except json.JSONDecodeError:
        pass
    return []


def _collaborating_org_ids_from_payload(normalized: Dict[str, Any]) -> List[str]:
    raw = normalized.get("collaborating_org_ids")
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            raw = []
    if not isinstance(raw, list):
        return []
    return [str(x).strip() for x in raw if str(x).strip()]


def _student_sid(user: Optional[Dict[str, Any]]) -> str:
    return str((user or {}).get("student_id") or "").strip()


def _student_owns_personal_task(user: Dict[str, Any], task: Task) -> bool:
    if not task.owner_is_self:
        return False
    sid = _student_sid(user)
    if not sid:
        return False
    cid = str(getattr(task, "creator_student_id", None) or "").strip()
    if cid:
        return cid == sid
    return str(task.current_owner_id or "").strip() == sid


def _assigned_org_task_to_student(user: Dict[str, Any], task: Task) -> bool:
    if task.owner_is_self:
        return False
    username = str((user or {}).get("username") or "").strip()
    display_name = str((user or {}).get("display_name") or "").strip()
    names = {x for x in {username, display_name} if x}
    return bool(task.current_owner_name and task.current_owner_name in names)


def user_can_view_task(user: Dict[str, Any], task: Task) -> bool:
    role = str((user or {}).get("role") or "").strip()
    if role in {"org_admin", "tw_admin"}:
        return True
    return _student_owns_personal_task(user, task) or _assigned_org_task_to_student(user, task)


def _task_public(task: Task) -> Dict[str, Any]:
    flow = _normalize_task_flow(task.assignment_type or "")
    collab = _parse_collaborating_org_ids(task)
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description or "",
        "task_type": task.task_type,
        "source_type": task.source_type,
        "assignment_type": flow,
        "collaborating_org_ids": collab,
        "parent_task_id": task.parent_task_id or "",
        "source_org_id": task.source_org_id or "",
        "current_org_id": task.current_org_id or "",
        "current_owner_id": task.current_owner_id or "",
        "current_owner_name": task.current_owner_name or "",
        "owner_name": task.current_owner_name or "",
        "owner_is_self": bool(task.owner_is_self),
        "due_date": _due_date_display(task.due_date),
        "deadline": _due_date_display(task.due_date),
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
    rows = TaskLog.query.filter_by(task_id=task_id).order_by(TaskLog.id.asc()).all()
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


def list_tasks_for_user(
    user: Dict[str, Any],
    current_org_id: Optional[str] = None,
    status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    role = str((user or {}).get("role") or "").strip()
    if role in {"org_admin", "tw_admin"}:
        return list_tasks(current_org_id=current_org_id, status=status)

    q = Task.query
    if current_org_id:
        q = q.filter(Task.current_org_id == current_org_id)
    if status:
        q = q.filter(Task.status == status)

    username = str((user or {}).get("username") or "").strip()
    display_name = str((user or {}).get("display_name") or "").strip()
    names = {x for x in {username, display_name} if x}
    sid = _student_sid(user)

    visibility = []
    if names:
        visibility.append(
            and_(Task.owner_is_self.is_(False), Task.current_owner_name.in_(list(names)))
        )
    if sid:
        creator_blank = or_(Task.creator_student_id.is_(None), Task.creator_student_id == "")
        personal_mine = and_(
            Task.owner_is_self.is_(True),
            or_(Task.creator_student_id == sid, and_(creator_blank, Task.current_owner_id == sid)),
        )
        visibility.append(personal_mine)

    if not visibility:
        return []

    q = q.filter(or_(*visibility))
    rows = q.order_by(Task.id.asc()).all()
    return [_task_public(t) for t in rows]


def _can_operate_task(user: Dict[str, Any], task: Task) -> bool:
    role = str((user or {}).get("role") or "").strip()
    if role in {"org_admin", "tw_admin"}:
        return True
    if task.owner_is_self:
        return _student_owns_personal_task(user, task)
    username = str((user or {}).get("username") or "").strip()
    display_name = str((user or {}).get("display_name") or "").strip()
    names = {x for x in {username, display_name} if x}
    return bool(task.current_owner_name and task.current_owner_name in names)


def create_task(
    payload: Dict[str, Any], actor: str, user: Optional[Dict[str, Any]] = None
) -> Tuple[bool, Optional[str], Optional[str], Optional[Dict[str, Any]]]:
    role = str((user or {}).get("role") or "").strip()
    username = str((user or {}).get("username") or "").strip()
    display_name = str((user or {}).get("display_name") or "").strip()

    normalized = dict(payload or {})
    if role == "student":
        if str(normalized.get("source_org_id") or "").strip():
            return False, "forbidden", "无权限执行该操作", None
        stu_id = str((user or {}).get("student_id") or "").strip()
        if not stu_id:
            return False, "bad_request", "profile not linked to student account", None
        normalized["source_org_id"] = ""
        normalized["current_org_id"] = str(normalized.get("current_org_id") or "personal").strip() or "personal"
        normalized["current_owner_name"] = display_name or username or "本人"
        normalized["current_owner_id"] = stu_id
        normalized["creator_student_id"] = stu_id
        normalized["owner_is_self"] = True

    title = str(normalized.get("title", "")).strip()
    task_type = str(normalized.get("task_type", "")).strip()
    source_org_id = str(normalized.get("source_org_id", "")).strip()
    current_org_id = str(normalized.get("current_org_id", "")).strip()
    current_owner_id = str(normalized.get("current_owner_id", "")).strip()
    current_owner_name = str(normalized.get("current_owner_name", "")).strip()
    due_date_raw = str(normalized.get("deadline", "") or normalized.get("due_date", "")).strip()
    description = str(normalized.get("description", "")).strip()
    status = str(normalized.get("status", E.TASK_STATUS_PENDING)).strip() or E.TASK_STATUS_PENDING
    parent_task_id = str(normalized.get("parent_task_id", "")).strip()
    owner_is_self = bool(normalized.get("owner_is_self"))

    if not title:
        return False, "bad_request", "title is required", None
    if not task_type:
        return False, "bad_request", "task_type is required", None
    if not current_org_id:
        return False, "bad_request", "current_org_id is required", None
    if not current_owner_name:
        return False, "bad_request", "current_owner_name is required", None
    if not due_date_raw:
        return False, "bad_request", "deadline is required", None
    due_date = _parse_due_date(due_date_raw)
    if not due_date:
        return False, "bad_request", "invalid deadline format", None
    if status not in E.TASK_STATUSES:
        return False, "bad_request", "invalid status", None

    if role == "student":
        flow = E.TASK_FLOW_SINGLE_DEPARTMENT
        collab_json = "[]"
    else:
        flow = _normalize_task_flow(
            str(normalized.get("assignment_type") or normalized.get("task_flow") or "").strip()
            or E.TASK_FLOW_SINGLE_DEPARTMENT
        )
        collab_ids = _collaborating_org_ids_from_payload(normalized)
        if flow not in E.TASK_FLOW_TYPES:
            return False, "bad_request", "invalid task flow", None
        if flow == E.TASK_FLOW_CROSS_DEPARTMENT:
            uniq = list(dict.fromkeys(collab_ids))
            if len(uniq) < 2:
                return False, "bad_request", "cross_department_requires_two_orgs", None
            if current_org_id not in uniq:
                return False, "bad_request", "cross_department_current_org_must_be_in_list", None
            for oid in uniq:
                if not Organization.query.filter_by(id=oid).first():
                    return False, "bad_request", "organization not found", None
            collab_json = json.dumps(uniq, ensure_ascii=False)
        elif flow == E.TASK_FLOW_TOP_DOWN:
            if not source_org_id:
                return False, "bad_request", "top_down_requires_source_org", None
            pair = list(dict.fromkeys([source_org_id, current_org_id]))
            collab_json = json.dumps(pair, ensure_ascii=False)
        else:
            if current_org_id and current_org_id != "personal":
                collab_json = json.dumps([current_org_id], ensure_ascii=False)
            else:
                collab_json = "[]"

    creator_student_id = ""
    if role == "student":
        creator_student_id = str((user or {}).get("student_id") or "").strip()
    task = Task(
        id=_next_task_id(),
        title=title,
        description=description,
        task_type=task_type,
        source_type=E.TASK_SOURCE_ORGANIZATION if source_org_id else E.TASK_SOURCE_PERSONAL,
        assignment_type=flow,
        collaborating_org_ids_json=collab_json,
        parent_task_id=parent_task_id,
        source_org_id=source_org_id,
        current_org_id=current_org_id,
        current_owner_id=current_owner_id,
        current_owner_name=current_owner_name,
        owner_is_self=owner_is_self,
        creator_student_id=creator_student_id,
        due_date=due_date,
        priority=str(normalized.get("priority", E.TASK_PRIORITY_MEDIUM)),
        status=status,
    )
    db.session.add(task)
    db.session.flush()
    _append_log(task.id, actor, E.TASK_LOG_CREATE, note=description or None)
    _append_log(task.id, actor, "assign", to_owner=current_owner_name, to_org_id=current_org_id, note="initial assignment")
    db.session.commit()
    return True, None, None, {"task": _task_public(task), "logs": _task_logs(task.id)}


def get_task_detail(
    task_id: str, actor: str, user: Optional[Dict[str, Any]] = None
) -> Optional[Tuple[Dict[str, Any], List[Dict[str, Any]]]]:
    task = Task.query.filter_by(id=task_id).first()
    if not task:
        return None
    if user is not None and not user_can_view_task(user, task):
        return None
    _append_log(task.id, actor, E.TASK_LOG_VIEW)
    db.session.commit()
    return _task_public(task), _task_logs(task.id)


def update_status(
    task_id: str, new_status: str, actor: str, user: Optional[Dict[str, Any]] = None
) -> Tuple[bool, Optional[str], Optional[str], Optional[Dict[str, Any]]]:
    task = Task.query.filter_by(id=task_id).first()
    if not task:
        return False, "not_found", "任务不存在", None
    if not _can_operate_task(user or {}, task):
        return False, "forbidden", "无权限执行该操作", None
    cur = task.status
    expected = NEXT_STATUS.get(cur)
    if expected != new_status:
        return False, "invalid_transition", "请按顺序推进状态", None
    _append_log(task.id, actor, E.TASK_LOG_STATUS_CHANGE, from_status=cur, to_status=new_status)
    task.status = new_status
    db.session.commit()
    return True, None, None, {"task": _task_public(task), "logs": _task_logs(task.id)}


def update_priority(
    task_id: str, new_priority: str, actor: str, user: Optional[Dict[str, Any]] = None
) -> Tuple[bool, Optional[str], Optional[str], Optional[Dict[str, Any]]]:
    task = Task.query.filter_by(id=task_id).first()
    if not task:
        return False, "not_found", "任务不存在", None
    if not _can_operate_task(user or {}, task):
        return False, "forbidden", "无权限执行该操作", None
    if new_priority not in E.TASK_PRIORITIES:
        return False, "bad_request", "invalid priority", None
    old = str(task.priority or E.TASK_PRIORITY_MEDIUM).strip() or E.TASK_PRIORITY_MEDIUM
    if old == new_priority:
        return True, None, None, {"task": _task_public(task), "logs": _task_logs(task.id)}
    _append_log(
        task.id,
        actor,
        E.TASK_LOG_PRIORITY_CHANGE,
        note=f"{old} -> {new_priority}",
    )
    task.priority = new_priority
    db.session.commit()
    return True, None, None, {"task": _task_public(task), "logs": _task_logs(task.id)}


def transfer_task(
    task_id: str,
    to_owner: str,
    note: str,
    actor: str,
    to_org_id: str = "",
    user: Optional[Dict[str, Any]] = None,
) -> Tuple[bool, Optional[str], Optional[str], Optional[Dict[str, Any]]]:
    task = Task.query.filter_by(id=task_id).first()
    if not task:
        return False, "not_found", "任务不存在", None
    if not _can_operate_task(user or {}, task):
        return False, "forbidden", "无权限执行该操作", None
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

