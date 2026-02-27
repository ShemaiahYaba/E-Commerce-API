"""Auth decorators for routes: jwt_required, admin_required."""

from functools import wraps
from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from utils.responses import error_response
from http import HTTPStatus


def admin_required(fn):
    """Require valid JWT and admin role."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        from models import User
        from database import db
        user_id = get_jwt_identity()
        user = db.session.get(User, int(user_id))
        if not user or user.role != "admin":
            return error_response("Admin access required", HTTPStatus.FORBIDDEN)
        return fn(*args, **kwargs)
    return wrapper
