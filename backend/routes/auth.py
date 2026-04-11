from flask import Blueprint, jsonify, request, session

from .auth_guard import get_current_user

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# student_id 与 data/seed.py 中 Student 主键一致，用于档案/奖项与登录账号绑定
DEMO_USERS = {
    "student01": {
        "username": "student01",
        "password": "123456",
        "display_name": "演示学生",
        "role": "student",
        "student_id": "2023XXXX0218",
    },
    "student02": {
        "username": "student02",
        "password": "123456",
        "display_name": "李华",
        "role": "student",
        "student_id": "2023XXXX0219",
    },
    "orgadmin01": {
        "username": "orgadmin01",
        "password": "123456",
        "display_name": "组织负责人",
        "role": "org_admin",
        "student_id": "2023XXXX0218",
    },
    "twadmin01": {
        "username": "twadmin01",
        "password": "123456",
        "display_name": "团委管理员",
        "role": "tw_admin",
        "student_id": "2023XXXX0218",
    },
}


def _public_user(u: dict) -> dict:
    return {
        "username": u.get("username", ""),
        "display_name": u.get("display_name", ""),
        "role": u.get("role", "student"),
        "student_id": str(u.get("student_id") or "").strip(),
    }


@bp.post("/login")
def login():
    body = request.get_json(silent=True) or {}
    username = str(body.get("username") or "").strip()
    password = str(body.get("password") or "").strip()
    user = DEMO_USERS.get(username)
    if not user or user.get("password") != password:
        return jsonify({"error": "invalid_credentials", "message": "账号或密码错误"}), 400
    public = _public_user(user)
    session["auth_user"] = public
    session.permanent = True
    return jsonify({"data": {"user": public}})


@bp.get("/me")
def me():
    user = get_current_user()
    if not user:
        return jsonify({"error": "unauthorized", "message": "未登录"}), 401
    return jsonify({"data": {"user": user}})


@bp.post("/logout")
def logout():
    session.pop("auth_user", None)
    return jsonify({"data": {"success": True}})

