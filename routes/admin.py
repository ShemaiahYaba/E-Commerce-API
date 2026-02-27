"""Admin routes: stats, inventory, list orders (admin only)."""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from http import HTTPStatus
from sqlalchemy import func
from database import db
from models import User, Order, OrderItem, Product

from middleware.auth import admin_required
from services import order_service
from utils.responses import success_response, error_response

admin_bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")


@admin_bp.route("/stats", methods=["GET"])
@jwt_required()
@admin_required
def dashboard_stats():
    """Dashboard: total users, orders, revenue, popular products."""
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
    """Inventory: stock levels; low_stock threshold query param (default 5)."""
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
    """Admin: list all orders (paginated)."""
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
