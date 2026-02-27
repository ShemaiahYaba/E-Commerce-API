"""User routes: profile (GET/PUT /users/me), admin list/deactivate."""

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from http import HTTPStatus
from pydantic import ValidationError

from schemas import UserUpdate, UserResponse
from services import user_service
from middleware.auth import admin_required
from utils.responses import success_response, error_response

users_bp = Blueprint("users", __name__, url_prefix="/api/v1/users")


@users_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    """Get current user profile."""
    user_id = int(get_jwt_identity())
    user = user_service.get_by_id(user_id)
    return success_response(data=UserResponse.model_validate(user).model_dump())


@users_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_me():
    """Update current user profile."""
    user_id = int(get_jwt_identity())
    try:
        data = UserUpdate.model_validate(request.get_json() or {})
    except ValidationError as e:
        return error_response("Validation failed", HTTPStatus.BAD_REQUEST, e.errors())
    try:
        user_dict = user_service.update_profile(user_id, data)
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_response(e.message, e.status_code)
        raise
    return success_response(data=user_dict)


@users_bp.route("", methods=["GET"])
@jwt_required()
@admin_required
def list_users():
    """List users (admin only); paginated."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    result = user_service.get_all_paginated(page=page, per_page=per_page)
    return success_response(data=result)


@users_bp.route("/<int:user_id>/deactivate", methods=["PATCH"])
@jwt_required()
@admin_required
def deactivate_user(user_id):
    """Deactivate user (admin only)."""
    user_service.set_active(user_id, False)
    return success_response(data={"message": "User deactivated"})
