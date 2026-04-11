from __future__ import annotations

from functools import wraps
from typing import Callable

from flask import jsonify, session


def get_current_user():
    user = session.get("auth_user")
    if isinstance(user, dict):
        return user
    return None


def _auth_error(status: int, error: str, message: str):
    return jsonify({"success": False, "error": error, "message": message}), status


def require_login(fn: Callable):
    @wraps(fn)
    def _wrapped(*args, **kwargs):
        user = get_current_user()
        if not user:
            return _auth_error(401, "unauthorized", "请先登录")
        return fn(*args, **kwargs)

    return _wrapped


def require_roles(*roles: str):
    allow = {str(x).strip() for x in roles if str(x).strip()}

    def _decorator(fn: Callable):
        @wraps(fn)
        def _wrapped(*args, **kwargs):
            user = get_current_user()
            if not user:
                return _auth_error(401, "unauthorized", "请先登录")
            role = str(user.get("role") or "").strip()
            if allow and role not in allow:
                return _auth_error(403, "forbidden", "无权限执行该操作")
            return fn(*args, **kwargs)

        return _wrapped

    return _decorator

