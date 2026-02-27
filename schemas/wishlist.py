"""Wishlist request/response schemas."""

from pydantic import BaseModel, ConfigDict


class WishlistAdd(BaseModel):
    """Add product to wishlist."""

    product_id: int


class WishlistItemResponse(BaseModel):
    """Wishlist item in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    product_id: int
