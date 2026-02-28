"""Cart business rules: quantity and stock validation."""

from validators.base_validator import BaseValidator


class CartValidator(BaseValidator):
    """Validate cart quantities and stock."""

    @staticmethod
    def validate_quantity(quantity: int, available_stock: int, field: str = "quantity") -> None:
        """Raise ValidationError if quantity < 1 or > available_stock."""
        if quantity < 1:
            BaseValidator._raise("Quantity must be at least 1", field=field)
        if quantity > available_stock:
            BaseValidator._raise(
                f"Insufficient stock: available {available_stock}, requested {quantity}",
                field=field,
            )
