"""Order and OrderItem schemas."""

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class OrderItemResponse(BaseModel):
    """Order line in responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    product_id: int
    quantity: int
    price: Decimal


class OrderResponse(BaseModel):
    """Order in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: str
    total: Decimal
    payment_intent_id: str | None
    created_at: datetime
    order_items: list[OrderItemResponse] = []


class OrderStatusUpdate(BaseModel):
    """Admin: update order status."""

    status: str
