"""Application factory for E-Commerce API."""

import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flasgger import Swagger

from config import get_settings
from config.swagger import SWAGGER_TEMPLATE
from database import db, migrate
from error_handlers import register_error_handlers
from routes import register_blueprints
from routes.webdocs import webdocs_bp


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask app."""
    env = config_name or os.getenv("FLASK_ENV", "development")
    settings = get_settings(env)

    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    if settings.cors_origins_list:
        app.config["CORS_ORIGINS"] = settings.cors_origins_list

    db.init_app(app)
    migrate.init_app(app, db)
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_revoked(jwt_header, jwt_payload):
        from services.auth_service import is_token_revoked
        jti = jwt_payload.get("jti")
        return jti and is_token_revoked(jti)

    CORS(app, origins=settings.cors_origins_list or ["*"], supports_credentials=True)

    Swagger(
        app,
        template=SWAGGER_TEMPLATE,
        config={
            "headers": [],
            "specs": [{"endpoint": "apispec", "route": "/apispec.json", "rule_filter": lambda r: True, "model_filter": lambda m: True}],
            "static_url_path": "/flasgger_static",
            "swagger_ui": True,
            "specs_route": "/docs",
        },
    )

    register_blueprints(app)
    app.register_blueprint(webdocs_bp)
    register_error_handlers(app)

    with app.app_context():
        from models import (  # noqa: F401 - register models for migrate
            User,
            Category,
            Product,
            ProductImage,
            CartItem,
            Order,
            OrderItem,
            Review,
            WishlistItem,
        )

    return app
