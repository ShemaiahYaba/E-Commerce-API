"""Base validator: shared pattern for business-rule validation."""

from exceptions import ValidationError


class BaseValidator:
    """Base for domain validators; raise ValidationError with optional field."""

    @staticmethod
    def _raise(message: str, field: str | None = None) -> None:
        raise ValidationError(message, field=field)
