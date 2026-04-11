from flask import Blueprint, jsonify, request

from data import schedule_provider
from .auth_guard import require_login

bp = Blueprint("schedule", __name__, url_prefix="/api/schedule")


@bp.get("/events")
@require_login
def get_events():
    raw_types = request.args.get("event_types", "").strip()
    event_types = [x.strip() for x in raw_types.split(",") if x.strip()] if raw_types else None
    data = schedule_provider.list_events(event_types=event_types)
    return jsonify({"data": data})


@bp.post("/plans")
@require_login
def create_schedule_plan():
    body = request.get_json(silent=True) or {}
    try:
        created = schedule_provider.create_personal_plan(body)
    except ValueError as exc:
        return jsonify({"error": "bad_request", "message": str(exc)}), 400
    return jsonify({"data": created}), 201


@bp.put("/plans/<plan_id>")
@require_login
def update_schedule_plan(plan_id: str):
    body = request.get_json(silent=True) or {}
    try:
        updated = schedule_provider.update_personal_plan(plan_id, body)
    except ValueError as exc:
        return jsonify({"error": "bad_request", "message": str(exc)}), 400
    if not updated:
        return jsonify({"error": "not_found", "message": "plan not found"}), 404
    return jsonify({"data": updated})


@bp.delete("/plans/<plan_id>")
@require_login
def delete_schedule_plan(plan_id: str):
    ok = schedule_provider.delete_personal_plan(plan_id)
    if not ok:
        return jsonify({"error": "not_found", "message": "plan not found"}), 404
    return jsonify({"success": True})
