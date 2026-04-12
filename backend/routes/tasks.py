from flask import Blueprint, jsonify, request

from data import task_service
from .auth_guard import get_current_user, require_login

bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")


def _actor() -> str:
    return (request.headers.get("X-Actor") or "user").strip() or "user"


def _normalize_status(raw: str) -> str:
    s = (raw or "").strip()
    mapping = {
        "待查看": "pending",
        "待处理": "pending",
        "pending": "pending",
        "已查看": "viewed",
        "已读": "viewed",
        "viewed": "viewed",
        "进行中": "in_progress",
        "in_progress": "in_progress",
        "已完成": "done",
        "完成": "done",
        "done": "done",
    }
    return mapping.get(s, s)


def _normalize_priority(raw: str) -> str:
    s = (raw or "").strip().lower()
    mapping = {
        "高": "high",
        "紧急": "high",
        "high": "high",
        "中": "medium",
        "medium": "medium",
        "低": "low",
        "low": "low",
    }
    return mapping.get(s, s)


@bp.get("")
@require_login
def get_tasks():
    user = get_current_user() or {}
    current_org_id = (request.args.get("current_org_id") or "").strip() or None
    status_raw = (request.args.get("status") or "").strip() or None
    status = _normalize_status(status_raw) if status_raw else None
    return jsonify({"data": task_service.list_tasks_for_user(user, current_org_id=current_org_id, status=status)})


@bp.post("")
@require_login
def create_task():
    user = get_current_user() or {}
    body = request.get_json(silent=True) or {}
    if "status" in body:
        body["status"] = _normalize_status(str(body.get("status") or ""))
    ok, err_code, message, payload = task_service.create_task(body, _actor(), user=user)
    if not ok:
        status = 403 if err_code == "forbidden" else 400
        return jsonify({"message": message or err_code, "error": err_code}), status
    return jsonify({"data": payload}), 201


@bp.get("/<task_id>")
@require_login
def get_task_detail(task_id: str):
    user = get_current_user() or {}
    row = task_service.get_task_detail(task_id, _actor(), user=user)
    if not row:
        return jsonify({"error": "not_found", "message": "任务不存在"}), 404
    task, logs = row
    return jsonify({"data": {"task": task, "logs": logs}})


@bp.patch("/<task_id>/status")
@require_login
def update_task_status(task_id: str):
    user = get_current_user() or {}
    body = request.get_json(silent=True) or {}
    new_status = body.get("status")
    if not new_status or not isinstance(new_status, str):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "bad_request",
                    "message": "请求体需包含 status",
                }
            ),
            400,
        )

    ok, err_code, message, payload = task_service.update_status(
        task_id, _normalize_status(new_status.strip()), _actor(), user=user
    )
    if not ok and err_code == "not_found":
        return jsonify({"error": "not_found", "message": message or "任务不存在"}), 404
    if not ok and err_code == "forbidden":
        return jsonify({"error": "forbidden", "message": message or "无权限执行该操作"}), 403
    if not ok:
        return jsonify(
            {"success": False, "error": err_code, "message": message or err_code}
        )

    return jsonify({"success": True, "data": payload})


@bp.patch("/<task_id>/priority")
@require_login
def update_task_priority(task_id: str):
    user = get_current_user() or {}
    body = request.get_json(silent=True) or {}
    raw = body.get("priority")
    if raw is None or not isinstance(raw, str) or not str(raw).strip():
        return (
            jsonify(
                {
                    "success": False,
                    "error": "bad_request",
                    "message": "请求体需包含 priority",
                }
            ),
            400,
        )
    new_priority = _normalize_priority(str(raw).strip())
    ok, err_code, message, payload = task_service.update_priority(
        task_id, new_priority, _actor(), user=user
    )
    if not ok and err_code == "not_found":
        return jsonify({"error": "not_found", "message": message or "任务不存在"}), 404
    if not ok and err_code == "forbidden":
        return jsonify({"error": "forbidden", "message": message or "无权限执行该操作"}), 403
    if not ok:
        return jsonify({"success": False, "error": err_code, "message": message or err_code}), 400
    return jsonify({"success": True, "data": payload})


@bp.post("/<task_id>/transfer")
@require_login
def create_task_transfer(task_id: str):
    user = get_current_user() or {}
    body = request.get_json(silent=True) or {}
    to_owner = body.get("to_owner")
    note = body.get("note") if body.get("note") is not None else ""
    to_org_id = body.get("to_org_id") if body.get("to_org_id") is not None else ""

    ok, err_code, message, payload = task_service.transfer_task(
        task_id,
        to_owner if isinstance(to_owner, str) else "",
        note if isinstance(note, str) else "",
        _actor(),
        to_org_id if isinstance(to_org_id, str) else "",
        user=user,
    )
    if not ok:
        status = 404 if err_code == "not_found" else 403 if err_code == "forbidden" else 400
        return (
            jsonify({"message": message or err_code, "error": err_code}),
            status,
        )

    return jsonify({"data": payload})
