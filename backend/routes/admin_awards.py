from flask import Blueprint, jsonify, request

from data import profile_store
from .auth_guard import require_roles

bp = Blueprint("admin_awards", __name__, url_prefix="/api/admin/awards")


@bp.get("")
@require_roles("tw_admin")
def list_awards():
    status = (request.args.get("status") or "").strip() or None
    return jsonify({"data": profile_store.list_awards_for_admin(status=status)})


@bp.patch("/<award_id>/review")
@require_roles("tw_admin")
def review_award(award_id: str):
    body = request.get_json(silent=True) or {}
    status = str(body.get("status") or "").strip()
    review_comment = str(body.get("review_comment") or "").strip()
    reviewer = str(body.get("reviewed_by") or "admin").strip()
    ok, err, data = profile_store.review_award(award_id, status, review_comment, reviewer)
    if not ok:
        code = 404 if err == "award not found" else 400
        error = "not_found" if code == 404 else "bad_request"
        return jsonify({"error": error, "message": err}), code
    return jsonify({"data": data})
