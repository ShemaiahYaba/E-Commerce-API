"""Web UI product routes: list, detail, reviews."""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from services import product_service, category_service, review_service
from errors.exceptions import ProductNotFoundError, ValidationError
from routes.web.utils import require_login
from schemas import ReviewCreate

products_web_bp = Blueprint(
    "web_products", __name__, url_prefix="/web", template_folder="../../templates"
)


@products_web_bp.route("/products")
def products_list():
    guard = require_login()
    if guard:
        return guard

    search = request.args.get("q", "").strip()
    category_id = request.args.get("category_id", type=int)
    page = request.args.get("page", 1, type=int)
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    in_stock = request.args.get("in_stock") == "1"
    min_rating = request.args.get("min_rating", type=int)

    try:
        result = product_service.get_all_paginated(
            page=page,
            per_page=12,
            search=search or None,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            in_stock_only=in_stock,
            min_rating=min_rating,
        )
        categories = category_service.get_all()
    except Exception:
        flash("Error loading products.", "error")
        result = {"products": [], "total": 0, "page": 1, "pages": 1}
        categories = []

    return render_template(
        "products/list.html",
        products=result["products"],
        total=result["total"],
        page=result["page"],
        pages=result["pages"],
        categories=categories,
        current_category=category_id,
        search_query=search,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        min_rating=min_rating,
    )


@products_web_bp.route("/products/<int:product_id>")
def product_detail(product_id: int):
    guard = require_login()
    if guard:
        return guard

    try:
        product = product_service.get_by_id(product_id)
        # Load reviews
        rev_result = review_service.get_by_product(product_id, page=1, per_page=50)
        reviews = rev_result.get("reviews", [])
        
        # Calculate rating
        review_count = len(reviews)
        avg_rating = sum(r.rating for r in reviews) / review_count if review_count > 0 else 0
        
    except ProductNotFoundError:
        flash("Product not found.", "error")
        return redirect(url_for("web_products.products_list"))
    except Exception:
        flash("Error loading product details.", "error")
        return redirect(url_for("web_products.products_list"))

    return render_template(
        "products/detail.html", 
        product=product,
        reviews=reviews,
        review_count=review_count,
        avg_rating=avg_rating
    )


@products_web_bp.route("/products/<int:product_id>/review", methods=["POST"])
def submit_review(product_id: int):
    guard = require_login()
    if guard:
        return guard

    rating = request.form.get("rating", type=int)
    comment = request.form.get("comment", "").strip()

    if not rating or rating < 1 or rating > 5:
        flash("Please provide a valid 1-5 star rating.", "error")
        return redirect(url_for("web_products.product_detail", product_id=product_id))

    try:
        data = ReviewCreate(rating=rating, comment=comment or None)
        review_service.create(session["user_id"], product_id, data)
        flash("Thanks for your review!", "success")
    except ValidationError as e:
        # e.g. "You can only review products you have purchased"
        flash(getattr(e, "message", str(e)), "error")
    except Exception as e:
        flash(getattr(e, "message", "Could not submit review."), "error")

    return redirect(url_for("web_products.product_detail", product_id=product_id))


@products_web_bp.route("/products/<int:product_id>/review/<int:review_id>/delete", methods=["POST"])
def delete_review(product_id: int, review_id: int):
    guard = require_login()
    if guard:
        return guard

    is_admin = session.get("user_role") == "admin"
    try:
        review_service.delete(review_id, session["user_id"], admin=is_admin)
        flash("Review deleted.", "success")
    except ValidationError:
        flash("Not authorized to delete this review.", "error")
    except Exception as e:
        flash(getattr(e, "message", "Could not delete review."), "error")

    return redirect(url_for("web_products.product_detail", product_id=product_id))
