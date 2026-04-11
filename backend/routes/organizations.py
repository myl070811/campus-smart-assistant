from flask import Blueprint, jsonify, request

from data.organization_store import (
    create_organization as create_organization_row,
    delete_organization as delete_organization_row,
    get_organization as fetch_organization,
    list_organizations as fetch_organizations,
    update_organization as update_organization_row,
)
from .auth_guard import require_login, require_roles

bp = Blueprint("organizations", __name__, url_prefix="/api/organizations")


@bp.get("")
@require_login
def get_organizations():
    return jsonify({"data": fetch_organizations()})


@bp.get("/<org_id>")
@require_login
def get_organization(org_id: str):
    row = fetch_organization(org_id)
    if not row:
        return jsonify({"error": "not_found", "message": "organization not found"}), 404
    return jsonify({"data": row})


@bp.post("")
@require_roles("org_admin", "tw_admin")
def create_organization():
    payload = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})
    logo_file = request.files.get("logo")
    ok, err, data = create_organization_row(payload, logo_file)
    if not ok:
        return jsonify({"error": "bad_request", "message": err}), 400
    return jsonify({"data": data}), 201


@bp.patch("/<org_id>")
@require_roles("org_admin", "tw_admin")
def update_organization(org_id: str):
    payload = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})
    logo_file = request.files.get("logo")
    ok, err, data = update_organization_row(org_id, payload, logo_file)
    if not ok:
        code = 404 if err == "organization not found" else 400
        error = "not_found" if code == 404 else "bad_request"
        return jsonify({"error": error, "message": err}), code
    return jsonify({"data": data})


@bp.delete("/<org_id>")
@require_roles("org_admin", "tw_admin")
def delete_organization(org_id: str):
    ok, err = delete_organization_row(org_id)
    if not ok:
        code = 404 if err == "organization not found" else 400
        error = "not_found" if code == 404 else "bad_request"
        return jsonify({"error": error, "message": err}), code
    return jsonify({"success": True})
