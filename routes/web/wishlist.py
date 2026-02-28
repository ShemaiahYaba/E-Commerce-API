"""Web UI wishlist routes: view, add, remove."""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from services import wishlist_service
from errors.exceptions import ProductNotFoundError
from routes.web.utils import require_login

wishlist_web_bp = Blueprint(
    "web_wishlist", __name__, url_prefix="/web", template_folder="../../templates"
)


@wishlist_web_bp.route("/wishlist")
def wishlist_view():
    guard = require_login()
    if guard:
        return guard

    try:
        items = wishlist_service.get_wishlist(session["user_id"])
    except Exception:
        flash("Error loading wishlist.", "error")
        items = []

    return render_template("wishlist/view.html", items=items)


@wishlist_web_bp.route("/wishlist/add/<int:product_id>", methods=["POST"])
def wishlist_add(product_id: int):
    guard = require_login()
    if guard:
        return guard

    try:
        wishlist_service.add(session["user_id"], product_id)
        flash("Added to wishlist! ❤️", "success")
    except ProductNotFoundError:
        flash("Product not found.", "error")
    except Exception as e:
        flash(getattr(e, "message", "Could not add to wishlist."), "error")

    return redirect(request.referrer or url_for("web_products.products_list"))


@wishlist_web_bp.route("/wishlist/remove/<int:product_id>", methods=["POST"])
def wishlist_remove(product_id: int):
    guard = require_login()
    if guard:
        return guard

    try:
        wishlist_service.remove(session["user_id"], product_id)
        flash("Removed from wishlist.", "success")
    except Exception as e:
        flash(getattr(e, "message", "Could not remove from wishlist."), "error")

    return redirect(request.referrer or url_for("web_wishlist.wishlist_view"))
