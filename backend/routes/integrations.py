from flask import Blueprint, jsonify, request

from data.integration_store import import_data, list_logs
from .auth_guard import require_login, require_roles

bp = Blueprint("integrations", __name__, url_prefix="/api/integrations")


@bp.post("/import")
@require_roles("org_admin", "tw_admin")
def import_integration_data():
    import_type = (request.form.get("import_type") or "").strip()
    file = request.files.get("file")
    ok, err, payload = import_data(import_type, file)
    if not ok:
        return jsonify({"error": "bad_request", "message": err}), 400
    return jsonify({"data": payload})


@bp.get("/logs")
@require_login
def get_integration_logs():
    limit_raw = request.args.get("limit")
    try:
        limit = int(limit_raw) if limit_raw else 50
    except ValueError:
        limit = 50
    return jsonify({"data": list_logs(limit=limit)})

