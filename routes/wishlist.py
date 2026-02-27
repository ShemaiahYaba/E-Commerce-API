"""Wishlist routes: add, list, remove."""

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from http import HTTPStatus
from pydantic import ValidationError

from schemas import WishlistAdd, WishlistItemResponse, ProductResponse
from services import wishlist_service
from utils.responses import success_response, error_response

wishlist_bp = Blueprint("wishlist", __name__, url_prefix="/api/v1/wishlist")


@wishlist_bp.route("", methods=["GET"])
@jwt_required()
def get_wishlist():
    """Get current user wishlist (with product details)."""
    user_id = int(get_jwt_identity())
    items = wishlist_service.get_wishlist(user_id)
    data = [
        {
            "id": item.id,
            "user_id": item.user_id,
            "product_id": item.product_id,
            "product": ProductResponse.model_validate(item.product).model_dump(),
        }
        for item in items
    ]
    return success_response(data=data)


@wishlist_bp.route("", methods=["POST"])
@jwt_required()
def add_to_wishlist():
    """Add product to wishlist (product_id in body)."""
    try:
        body = WishlistAdd.model_validate(request.get_json())
    except ValidationError as e:
        return error_response("Validation failed", HTTPStatus.BAD_REQUEST, e.errors())
    user_id = int(get_jwt_identity())
    try:
        item = wishlist_service.add(user_id, body.product_id)
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_response(e.message, e.status_code)
        raise
    return success_response(
        data=WishlistItemResponse.model_validate(item).model_dump(),
        status=HTTPStatus.CREATED,
    )


@wishlist_bp.route("/<int:product_id>", methods=["DELETE"])
@jwt_required()
def remove_from_wishlist(product_id: int):
    """Remove product from wishlist."""
    user_id = int(get_jwt_identity())
    found = wishlist_service.remove(user_id, product_id)
    if not found:
        return error_response("Product not in wishlist", HTTPStatus.NOT_FOUND)
    return "", HTTPStatus.NO_CONTENT
