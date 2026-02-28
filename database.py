"""Root shim: re-exports from config.database for backwards compatibility."""
from config.database import db, migrate  # noqa: F401

__all__ = ["db", "migrate"]
