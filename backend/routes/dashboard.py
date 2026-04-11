from flask import Blueprint, jsonify

from data.dashboard_store import get_dashboard_data as fetch_dashboard_data
from .auth_guard import require_login

bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@bp.get("")
@require_login
def get_dashboard_data():
    return jsonify({"data": fetch_dashboard_data()})
