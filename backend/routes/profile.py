from flask import Blueprint, jsonify, request

from data import profile_store
from .auth_guard import require_login

bp = Blueprint("profile", __name__, url_prefix="/api/profile")


@bp.get("")
@require_login
def get_profile():
    return jsonify({"data": profile_store.get_profile()})


@bp.put("")
@require_login
def update_profile():
    body = request.get_json(silent=True) or {}
    data = profile_store.update_student_profile(body)
    return jsonify({"data": data})


@bp.post("/awards")
@require_login
def create_award_submission():
    student_id = (request.form.get("student_id") or "").strip()
    award_name = (request.form.get("award_name") or "").strip()
    award_time = (request.form.get("award_time") or "").strip()
    proof_file = request.files.get("proof_file")
    ok, err, award = profile_store.submit_award(student_id, award_name, award_time, proof_file)
    if not ok:
        return jsonify({"error": "bad_request", "message": err}), 400
    return jsonify({"data": award}), 201
