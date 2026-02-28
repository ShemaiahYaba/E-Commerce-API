"""Review routes: create (purchaser only), list by product, delete."""

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from http import HTTPStatus
from pydantic import ValidationError

from schemas import ReviewCreate, ReviewResponse
from services import review_service
from middleware.auth import admin_required
from utils.responses import success_response, error_response

reviews_bp = Blueprint("reviews", __name__, url_prefix="/api/v1/products")


@reviews_bp.route("/<int:product_id>/reviews", methods=["GET"])
def list_reviews(product_id: int):
    """List reviews for product (public); paginated.
    ---
    tags: [reviews]
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
      - name: page
        in: query
        type: integer
      - name: per_page
        in: query
        type: integer
    responses:
      200:
        description: Paginated reviews
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    result = review_service.get_by_product(product_id, page=page, per_page=per_page)
    reviews = result.pop("reviews")
    return success_response(
        data={
            "reviews": [ReviewResponse.model_validate(r).model_dump() for r in reviews],
            **result,
        }
    )


@reviews_bp.route("/<int:product_id>/reviews", methods=["POST"])
@jwt_required()
def create_review(product_id: int):
    """Create review (customer; must have purchased product).
    ---
    tags: [reviews]
    security: [Bearer: []]
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          required: [rating]
          properties:
            rating: { type: integer }
            comment: { type: string }
    responses:
      201:
        description: Review created
    """
    try:
        data = ReviewCreate.model_validate(request.get_json())
    except ValidationError as e:
        return error_response("Validation failed", HTTPStatus.BAD_REQUEST, e.errors())
    user_id = int(get_jwt_identity())
    try:
        review = review_service.create(user_id, product_id, data)
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_response(e.message, e.status_code)
        raise
    return success_response(
        data=ReviewResponse.model_validate(review).model_dump(),
        status=HTTPStatus.CREATED,
    )


@reviews_bp.route("/<int:product_id>/reviews/<int:review_id>", methods=["DELETE"])
@jwt_required()
def delete_review(product_id: int, review_id: int):
    """Delete own review (or admin).
    ---
    tags: [reviews]
    security: [Bearer: []]
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
      - name: review_id
        in: path
        type: integer
        required: true
    responses:
      204:
        description: Review deleted
    """
    from models import User
    from database import db
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    is_admin = user and user.role == "admin"
    try:
        review_service.delete(review_id, user_id, admin=is_admin)
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_response(e.message, e.status_code)
        raise
    return "", HTTPStatus.NO_CONTENT
