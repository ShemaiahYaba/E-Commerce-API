"""Environment-based configuration."""

import os
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_database_url() -> str:
    base = Path(__file__).resolve().parent.parent
    instance = base / "instance"
    instance.mkdir(exist_ok=True)
    return f"sqlite:///{instance / 'ecommerce.db'}"


class BaseConfig(BaseSettings):
    """Base config; env and .env loaded."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    FLASK_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-change-in-production"
    JWT_SECRET_KEY: str = "dev-jwt-secret-change-in-production"
    DATABASE_URL: str = ""
    CORS_ORIGINS: List[str] = []

    def __init__(self, **kwargs):  # type: ignore[no-untyped-def]
        if "DATABASE_URL" not in kwargs or not kwargs.get("DATABASE_URL"):
            kwargs.setdefault("DATABASE_URL", _default_database_url())
        super().__init__(**kwargs)


class DevelopmentConfig(BaseConfig):
    """Development settings."""

    DEBUG: bool = True
    CORS_ORIGINS: List[str] = ["*"]


class TestingConfig(BaseConfig):
    """Testing settings; in-memory SQLite."""

    TESTING: bool = True
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///:memory:"
    SECRET_KEY: str = "test-secret"
    JWT_SECRET_KEY: str = "test-jwt-secret"


class ProductionConfig(BaseConfig):
    """Production settings; require env vars."""

    DEBUG: bool = False


_config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_settings(env: str | None = None) -> BaseConfig:
    """Return config for the given environment (default from FLASK_ENV)."""
    name = env or os.getenv("FLASK_ENV", "development")
    if name not in _config_by_name:
        name = "development"
    return _config_by_name[name]()
