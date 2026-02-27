"""Cart request/response schemas."""

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class CartItemAdd(BaseModel):
    """Add or update cart line."""

    product_id: int
    quantity: int = Field(1, ge=1)


class CartItemUpdate(BaseModel):
    """Update quantity."""

    quantity: int = Field(..., ge=0)


class CartItemProductRef(BaseModel):
    id: int
    name: str
    price: Decimal
    sku: str


class CartItemResponse(BaseModel):
    """Cart line in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product: CartItemProductRef | None = None
    quantity: int
    created_at: datetime


class CartResponse(BaseModel):
    """Full cart with items and total."""

    items: list[CartItemResponse]
    total: Decimal
