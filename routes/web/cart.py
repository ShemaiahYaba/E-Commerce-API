"""Web UI cart routes: view, add, update, remove, checkout."""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from services import cart_service, order_service
from errors.exceptions import ProductNotFoundError, OrderNotFoundError
from routes.web.utils import require_login

cart_web_bp = Blueprint(
    "web_cart", __name__, url_prefix="/web", template_folder="../../templates"
)


@cart_web_bp.route("/cart")
def cart_view():
    guard = require_login()
    if guard:
        return guard

    try:
        cart = cart_service.get_cart(session["user_id"])
    except Exception:
        flash("Error loading cart.", "error")
        cart = {"items": [], "total": 0}

    return render_template("cart/view.html", items=cart["items"], total=cart["total"])


@cart_web_bp.route("/cart/add/<int:product_id>", methods=["POST"])
def cart_add(product_id: int):
    guard = require_login()
    if guard:
        return guard

    quantity = request.form.get("quantity", 1, type=int)
    try:
        cart_service.add_item(session["user_id"], product_id, quantity)
        flash("Item added to cart!", "success")
    except ProductNotFoundError:
        flash("Product not found.", "error")
    except Exception as e:
        flash(getattr(e, "message", "Could not add to cart."), "error")

    return redirect(request.referrer or url_for("web_products.products_list"))


@cart_web_bp.route("/cart/update/<int:item_id>", methods=["POST"])
def cart_update(item_id: int):
    guard = require_login()
    if guard:
        return guard

    quantity = request.form.get("quantity", 1, type=int)
    try:
        cart_service.update_quantity(session["user_id"], item_id, quantity)
    except Exception as e:
        flash(getattr(e, "message", "Could not update cart."), "error")

    return redirect(url_for("web_cart.cart_view"))


@cart_web_bp.route("/cart/remove/<int:item_id>", methods=["POST"])
def cart_remove(item_id: int):
    guard = require_login()
    if guard:
        return guard

    cart_service.remove_item(session["user_id"], item_id)
    flash("Item removed from cart.", "success")
    return redirect(url_for("web_cart.cart_view"))


@cart_web_bp.route("/cart/checkout", methods=["POST"])
def cart_checkout():
    guard = require_login()
    if guard:
        return guard

    try:
        order = order_service.create_order(session["user_id"])
        flash(f"Order #{order.id} placed successfully! 🎉", "success")
        return redirect(url_for("web_orders.order_detail", order_id=order.id))
    except Exception as e:
        flash(getattr(e, "message", "Could not place order."), "error")
        return redirect(url_for("web_cart.cart_view"))
