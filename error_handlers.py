"""Root shim: re-exports from errors.handlers for backwards compatibility."""
from errors.handlers import register_error_handlers  # noqa: F401

__all__ = ["register_error_handlers"]
