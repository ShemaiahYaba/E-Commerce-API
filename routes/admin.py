"""Admin routes: stats, inventory, list orders, cancel/delete orders, user management."""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from http import HTTPStatus
from sqlalchemy import func
from database import db
from models import User, Order, OrderItem, Product, CartItem

from middleware.auth import admin_required
from services import order_service, user_service
from utils.responses import success_response, error_response

admin_bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")


@admin_bp.route("/stats", methods=["GET"])
@jwt_required()
@admin_required
def dashboard_stats():
    """Dashboard: total users, orders, revenue, popular products.
    ---
    tags: [admin]
    security: [Bearer: []]
    responses:
      200:
        description: Dashboard statistics
    """
    total_users = User.query.count()
    total_orders = Order.query.count()
    revenue = db.session.query(func.coalesce(func.sum(Order.total), 0)).scalar() or 0
    # Popular products: by order item quantity
    popular = (
        db.session.query(Product.id, Product.name, func.sum(OrderItem.quantity).label("qty"))
        .join(OrderItem, OrderItem.product_id == Product.id)
        .group_by(Product.id, Product.name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(10)
        .all()
    )
    return success_response(
        data={
            "total_users": total_users,
            "total_orders": total_orders,
            "revenue": float(revenue),
            "popular_products": [{"id": p.id, "name": p.name, "quantity_sold": p.qty} for p in popular],
        }
    )


@admin_bp.route("/inventory", methods=["GET"])
@jwt_required()
@admin_required
def inventory():
    """Inventory: stock levels; low_stock threshold query param (default 5).
    ---
    tags: [admin]
    security: [Bearer: []]
    parameters:
      - name: low_stock_threshold
        in: query
        type: integer
    responses:
      200:
        description: Products and low-stock list
    """
    threshold = request.args.get("low_stock_threshold", 5, type=int)
    products = Product.query.order_by(Product.stock.asc()).all()
    low_stock = [p for p in products if p.stock < threshold]
    return success_response(
        data={
            "products": [
                {"id": p.id, "name": p.name, "sku": p.sku, "stock": p.stock}
                for p in products
            ],
            "low_stock": [
                {"id": p.id, "name": p.name, "sku": p.sku, "stock": p.stock}
                for p in low_stock
            ],
        }
    )


@admin_bp.route("/orders", methods=["GET"])
@jwt_required()
@admin_required
def list_all_orders():
    """Admin: list all orders (paginated).
    ---
    tags: [admin]
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
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    result = order_service.get_all_orders_admin(page=page, per_page=per_page)
    orders = result.pop("orders")

    def _order_dict(o):
        return {
            "id": o.id,
            "user_id": o.user_id,
            "status": o.status,
            "total": str(o.total),
            "payment_intent_id": o.payment_intent_id,
            "created_at": o.created_at.isoformat() if o.created_at else None,
            "order_items": [
                {"id": oi.id, "order_id": oi.order_id, "product_id": oi.product_id, "quantity": oi.quantity, "price": str(oi.price)}
                for oi in o.order_items
            ],
        }
    return success_response(
        data={"orders": [_order_dict(o) for o in orders], **result}
    )


@admin_bp.route("/orders/<int:order_id>/cancel", methods=["POST"])
@jwt_required()
@admin_required
def cancel_order(order_id: int):
    """Admin: cancel an order and restore product stock.
    ---
    tags: [admin]
    security: [Bearer: []]
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Order cancelled and stock restored
      404:
        description: Order not found
      400:
        description: Order already cancelled or delivered
    """
    order = db.session.get(Order, order_id)
    if not order:
        return error_response(f"Order {order_id} not found", HTTPStatus.NOT_FOUND)
    if order.status in ("cancelled", "delivered"):
        return error_response(
            f"Cannot cancel an order with status '{order.status}'",
            HTTPStatus.BAD_REQUEST,
        )
    # Restore stock for each line item
    for oi in order.order_items:
        product = db.session.get(Product, oi.product_id)
        if product:
            product.stock += oi.quantity
    order.status = "cancelled"
    db.session.commit()
    db.session.refresh(order)
    return success_response(data=_order_dict(order))


@admin_bp.route("/orders/<int:order_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_order(order_id: int):
    """Admin: hard-delete an order record (use cancel instead where possible).
    ---
    tags: [admin]
    security: [Bearer: []]
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
    responses:
      204:
        description: Order deleted
      404:
        description: Order not found
    """
    order = db.session.get(Order, order_id)
    if not order:
        return error_response(f"Order {order_id} not found", HTTPStatus.NOT_FOUND)
    db.session.delete(order)
    db.session.commit()
    return "", HTTPStatus.NO_CONTENT


@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@admin_required
def list_users():
    """Admin: list all users (paginated).
    ---
    tags: [admin]
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
        description: Paginated user list
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    result = user_service.get_all_paginated(page=page, per_page=per_page)
    return success_response(data=result)


@admin_bp.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
@admin_required
def get_user(user_id: int):
    """Admin: get a user by ID.
    ---
    tags: [admin]
    security: [Bearer: []]
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: User detail
      404:
        description: User not found
    """
    try:
        from schemas import UserResponse
        user = user_service.get_by_id(user_id)
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_response(e.message, e.status_code)
        raise
    return success_response(data=UserResponse.model_validate(user).model_dump())
