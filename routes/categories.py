"""Category routes: list, get, create, update, delete (admin for write)."""

from flask import Blueprint, request
from http import HTTPStatus
from pydantic import ValidationError

from schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from services import category_service
from middleware.auth import admin_required
from flask_jwt_extended import jwt_required
from utils.responses import success_response, error_response

categories_bp = Blueprint("categories", __name__, url_prefix="/api/v1/categories")


@categories_bp.route("", methods=["GET"])
def list_categories():
    """List all categories (public).
    ---
    tags: [categories]
    responses:
      200:
        description: List of categories
    """
    items = category_service.get_all()
    return success_response(
        data=[CategoryResponse.model_validate(c).model_dump() for c in items]
    )


@categories_bp.route("/<int:category_id>", methods=["GET"])
def get_category(category_id: int):
    """Get category by id (public).
    ---
    tags: [categories]
    parameters:
      - name: category_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Category
      404:
        description: Not found
    """
    try:
        cat = category_service.get_by_id(category_id)
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_response(e.message, e.status_code)
        raise
    return success_response(data=CategoryResponse.model_validate(cat).model_dump())


@categories_bp.route("", methods=["POST"])
@jwt_required()
@admin_required
def create_category():
    """Create category (admin).
    ---
    tags: [categories]
    security: [Bearer: []]
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required: [name]
          properties:
            name: { type: string }
            parent_id: { type: integer }
    responses:
      201:
        description: Category created
    """
    try:
        data = CategoryCreate.model_validate(request.get_json())
    except ValidationError as e:
        return error_response("Validation failed", HTTPStatus.BAD_REQUEST, e.errors())
    try:
        cat = category_service.create(data)
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_response(e.message, e.status_code)
        raise
    return success_response(
        data=CategoryResponse.model_validate(cat).model_dump(),
        status=HTTPStatus.CREATED,
    )


@categories_bp.route("/<int:category_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_category(category_id: int):
    """Update category (admin).
    ---
    tags: [categories]
    security: [Bearer: []]
    parameters:
      - name: category_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            name: { type: string }
            parent_id: { type: integer }
    responses:
      200:
        description: Category updated
    """
    try:
        data = CategoryUpdate.model_validate(request.get_json() or {})
    except ValidationError as e:
        return error_response("Validation failed", HTTPStatus.BAD_REQUEST, e.errors())
    try:
        cat = category_service.update(category_id, data)
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_response(e.message, e.status_code)
        raise
    return success_response(data=CategoryResponse.model_validate(cat).model_dump())


@categories_bp.route("/<int:category_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_category(category_id: int):
    """Delete category (admin).
    ---
    tags: [categories]
    security: [Bearer: []]
    parameters:
      - name: category_id
        in: path
        type: integer
        required: true
    responses:
      204:
        description: Category deleted
    """
    try:
        category_service.delete(category_id)
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_response(e.message, e.status_code)
        raise
    return "", HTTPStatus.NO_CONTENT
