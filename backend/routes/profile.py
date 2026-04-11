from flask import Blueprint, jsonify, request

from data import profile_store
from .auth_guard import get_current_user, require_login

bp = Blueprint("profile", __name__, url_prefix="/api/profile")


def _session_student_id() -> str:
    user = get_current_user() or {}
    return str(user.get("student_id") or "").strip()


@bp.get("")
@require_login
def get_profile():
    return jsonify({"data": profile_store.get_profile(_session_student_id())})


@bp.put("")
@require_login
def update_profile():
    body = request.get_json(silent=True) or {}
    ok, err, data = profile_store.update_student_profile(_session_student_id(), body)
    if not ok:
        return jsonify({"error": "bad_request", "message": err}), 400
    return jsonify({"data": data})


@bp.post("/awards")
@require_login
def create_award_submission():
    sid = _session_student_id()
    if not sid:
        return jsonify({"error": "bad_request", "message": "profile not linked to student account"}), 400
    form_sid = (request.form.get("student_id") or "").strip()
    if form_sid and form_sid != sid:
        return jsonify({"error": "forbidden", "message": "student_id mismatch"}), 403
    award_name = (request.form.get("award_name") or "").strip()
    award_time = (request.form.get("award_time") or "").strip()
    proof_file = request.files.get("proof_file")
    ok, err, award = profile_store.submit_award(sid, award_name, award_time, proof_file)
    if not ok:
        code = 404 if err == "student not found" else 400
        return jsonify({"error": "bad_request" if code == 400 else "not_found", "message": err}), code
    return jsonify({"data": award}), 201
