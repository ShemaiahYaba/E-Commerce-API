"""Environment-based configuration."""

import os
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict



def _parse_cors_origins(v: str | List[str]) -> List[str]:
    """Accept comma-separated string or list from env."""
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        return [x.strip() for x in v.split(",") if x.strip()]
    return []


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
    # Comma-separated in .env (e.g. CORS_ORIGINS=http://localhost:3000,http://localhost:5000)
    CORS_ORIGINS: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        """CORS_ORIGINS as a list (from comma-separated string in .env)."""
        return _parse_cors_origins(self.CORS_ORIGINS)

    def __init__(self, **kwargs):  # type: ignore[no-untyped-def]
        super().__init__(**kwargs)


class DevelopmentConfig(BaseConfig):
    """Development settings."""

    DEBUG: bool = True
    CORS_ORIGINS: str = "*"  # allowed as single value; _parse_cors_origins returns ["*"]


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
    
    settings = _config_by_name[name]()
    
    # Fix Fly.io providing 'postgres://' instead of 'postgresql://'
    if settings.DATABASE_URL and settings.DATABASE_URL.startswith("postgres://"):
        settings.DATABASE_URL = settings.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        
    return settings
