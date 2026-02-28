"""Cart routes: get, add, update item, remove item, clear."""

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from http import HTTPStatus
from pydantic import ValidationError

from schemas import CartItemAdd, CartItemUpdate
from services import cart_service
from utils.responses import success_response, error_response

cart_bp = Blueprint("cart", __name__, url_prefix="/api/v1/cart")


def _serialize_cart(data: dict) -> dict:
    """Build cart response with items and total."""
    items = []
    for item in data["items"]:
        d = {
            "id": item.id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "product": {
                "id": item.product.id,
                "name": item.product.name,
                "price": str(item.product.price),
                "sku": item.product.sku,
            },
        }
        items.append(d)
    return {"items": items, "total": str(data["total"])}


@cart_bp.route("", methods=["GET"])
@jwt_required()
def get_cart():
    """Get current user cart.
    ---
    tags: [cart]
    security: [Bearer: []]
    responses:
      200:
        description: Cart items and total
    """
    user_id = int(get_jwt_identity())
    data = cart_service.get_cart(user_id)
    return success_response(data=_serialize_cart(data))


@cart_bp.route("/items", methods=["POST"])
@jwt_required()
def add_item():
    """Add item to cart (product_id, quantity).
    ---
    tags: [cart]
    security: [Bearer: []]
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required: [product_id]
          properties:
            product_id: { type: integer }
            quantity: { type: integer }
    responses:
      201:
        description: Item added to cart
    """
    try:
        body = CartItemAdd.model_validate(request.get_json())
    except ValidationError as e:
        return error_response("Validation failed", HTTPStatus.BAD_REQUEST, e.errors())
    user_id = int(get_jwt_identity())
    try:
        item = cart_service.add_item(user_id, body.product_id, body.quantity)
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_response(e.message, e.status_code)
        raise
    return success_response(
        data={
            "id": item.id,
            "product_id": item.product_id,
            "quantity": item.quantity,
        },
        status=HTTPStatus.CREATED,
    )


@cart_bp.route("/items/<int:cart_item_id>", methods=["PUT"])
@jwt_required()
def update_item(cart_item_id: int):
    """Update cart item quantity (0 = remove).
    ---
    tags: [cart]
    security: [Bearer: []]
    parameters:
      - name: cart_item_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            quantity: { type: integer }
    responses:
      200:
        description: Item updated or removed
    """
    try:
        body = CartItemUpdate.model_validate(request.get_json())
    except ValidationError as e:
        return error_response("Validation failed", HTTPStatus.BAD_REQUEST, e.errors())
    user_id = int(get_jwt_identity())
    try:
        item = cart_service.update_quantity(user_id, cart_item_id, body.quantity)
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_response(e.message, e.status_code)
        raise
    if item is None:
        return success_response(data={"message": "Item removed"})
    return success_response(data={"id": item.id, "product_id": item.product_id, "quantity": item.quantity})


@cart_bp.route("/items/<int:cart_item_id>", methods=["DELETE"])
@jwt_required()
def remove_item(cart_item_id: int):
    """Remove cart item.
    ---
    tags: [cart]
    security: [Bearer: []]
    parameters:
      - name: cart_item_id
        in: path
        type: integer
        required: true
    responses:
      204:
        description: Item removed
    """
    user_id = int(get_jwt_identity())
    found = cart_service.remove_item(user_id, cart_item_id)
    if not found:
        return error_response("Cart item not found", HTTPStatus.NOT_FOUND)
    return "", HTTPStatus.NO_CONTENT


@cart_bp.route("", methods=["DELETE"])
@jwt_required()
def clear_cart():
    """Clear all cart items.
    ---
    tags: [cart]
    security: [Bearer: []]
    responses:
      200:
        description: Cart cleared
    """
    user_id = int(get_jwt_identity())
    cart_service.clear_cart(user_id)
    return success_response(data={"message": "Cart cleared"})
