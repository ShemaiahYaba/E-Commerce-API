"""Order routes: create, list, get; admin list and status update."""

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from http import HTTPStatus

from schemas import OrderResponse, OrderItemResponse, OrderStatusUpdate
from services import order_service
from middleware.auth import admin_required
from utils.responses import success_response, error_response

orders_bp = Blueprint("orders", __name__, url_prefix="/api/v1/orders")


def _order_to_dict(order) -> dict:
    """Serialize order with items."""
    return {
        "id": order.id,
        "user_id": order.user_id,
        "status": order.status,
        "total": str(order.total),
        "payment_intent_id": order.payment_intent_id,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "order_items": [
            {
                "id": oi.id,
                "order_id": oi.order_id,
                "product_id": oi.product_id,
                "quantity": oi.quantity,
                "price": str(oi.price),
            }
            for oi in order.order_items
        ],
    }


@orders_bp.route("", methods=["POST"])
@jwt_required()
def create_order():
    """Create order from current user cart.
    ---
    tags: [orders]
    security: [Bearer: []]
    responses:
      201:
        description: Order created from cart
      400:
        description: Cart empty or insufficient stock
    """
    user_id = int(get_jwt_identity())
    try:
        order = order_service.create_order(user_id)
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_response(e.message, e.status_code)
        raise
    return success_response(data=_order_to_dict(order), status=HTTPStatus.CREATED)


@orders_bp.route("", methods=["GET"])
@jwt_required()
def list_orders():
    """List current user orders.
    ---
    tags: [orders]
    security: [Bearer: []]
    parameters:
      - name: page
        in: query
        type: integer
      - name: per_page
        in: query
        type: integer
    responses:
      200:
        description: Paginated orders
    """
    user_id = int(get_jwt_identity())
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    result = order_service.get_user_orders(user_id, page=page, per_page=per_page)
    orders = result.pop("orders")
    return success_response(
        data={
            "orders": [_order_to_dict(o) for o in orders],
            **result,
        }
    )


@orders_bp.route("/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id: int):
    """Get order by id (owner only).
    ---
    tags: [orders]
    security: [Bearer: []]
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Order details
    """
    user_id = int(get_jwt_identity())
    try:
        order = order_service.get_by_id(order_id, user_id=user_id)
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_response(e.message, e.status_code)
        raise
    return success_response(data=_order_to_dict(order))


@orders_bp.route("/<int:order_id>/status", methods=["PUT"])
@jwt_required()
@admin_required
def update_order_status(order_id: int):
    """Admin: update order status.
    ---
    tags: [orders]
    security: [Bearer: []]
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          required: [status]
          properties:
            status: { type: string }
    responses:
      200:
        description: Order status updated
    """
    try:
        body = OrderStatusUpdate.model_validate(request.get_json())
    except Exception as e:
        return error_response("Validation failed", HTTPStatus.BAD_REQUEST)
    try:
        order = order_service.update_status(order_id, body.status)
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_response(e.message, e.status_code)
        raise
    return success_response(data=_order_to_dict(order))
