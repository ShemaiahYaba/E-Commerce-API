"""Review service: create (purchaser only), list by product, update, delete."""

from database import db
from models import Review, Order, OrderItem
from schemas import ReviewCreate
from exceptions import ProductNotFoundError, ValidationError
from services.base_service import BaseService
from services.product_service import get_by_id as get_product


def user_has_ordered_product(user_id: int, product_id: int) -> bool:
    """Return True if user has at least one order containing this product."""
    return (
        db.session.query(Order.id)
        .join(OrderItem, OrderItem.order_id == Order.id)
        .filter(Order.user_id == user_id, OrderItem.product_id == product_id)
        .first()
        is not None
    )


def create(user_id: int, product_id: int, data: ReviewCreate) -> Review:
    """Create review; only if user has purchased the product (PM-09)."""
    get_product(product_id)
    if not user_has_ordered_product(user_id, product_id):
        raise ValidationError("You can only review products you have purchased", field="product_id")
    existing = Review.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing:
        raise ValidationError("You have already reviewed this product", field="product_id")
    review = Review(
        user_id=user_id,
        product_id=product_id,
        rating=data.rating,
        comment=data.comment,
    )
    db.session.add(review)
    db.session.commit()
    db.session.refresh(review)
    return review


def get_by_product(product_id: int, page: int = 1, per_page: int = 20) -> dict:
    """List reviews for product; paginated."""
    get_product(product_id)
    per_page = min(per_page, 100)
    q = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc())
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    pagination = BaseService.pagination_dict(total, page, per_page)
    return {"reviews": items, **pagination}


def get_by_id(review_id: int) -> Review:
    from exceptions import AppException
    r = db.session.get(Review, review_id)
    if not r:
        raise AppException("Review not found", 404)
    return r


def delete(review_id: int, user_id: int, admin: bool = False) -> None:
    """Delete own review or admin delete any."""
    r = get_by_id(review_id)
    if not admin and r.user_id != user_id:
        raise ValidationError("Not authorized to delete this review", field="review_id")
    db.session.delete(r)
    db.session.commit()
