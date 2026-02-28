"""Application factory for E-Commerce API."""

import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flasgger import Swagger

from config import get_settings
from config.swagger import SWAGGER_TEMPLATE
from config.database import db, migrate          # ← moved into config/
from config.mail import mail                     # ← mail config
from errors.handlers import register_error_handlers  # ← moved into errors/
from routes import register_blueprints
from routes.web import register_web_blueprints   # ← modular web sub-blueprints


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask app."""
    env = config_name or os.getenv("FLASK_ENV", "development")
    settings = get_settings(env)

    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    
    # Mail settings
    app.config["MAIL_SERVER"] = settings.MAIL_SERVER
    app.config["MAIL_PORT"] = settings.MAIL_PORT
    app.config["MAIL_USE_TLS"] = settings.MAIL_USE_TLS
    app.config["MAIL_USE_SSL"] = settings.MAIL_USE_SSL
    app.config["MAIL_USERNAME"] = settings.MAIL_USERNAME
    app.config["MAIL_PASSWORD"] = settings.MAIL_PASSWORD
    app.config["MAIL_DEFAULT_SENDER"] = settings.MAIL_DEFAULT_SENDER
    
    if settings.cors_origins_list:
        app.config["CORS_ORIGINS"] = settings.cors_origins_list

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    jwt = JWTManager(app)

    @app.before_request
    def normalize_authorization_header():
        """Accept token with or without 'Bearer ' prefix."""
        from flask import request
        auth = request.headers.get("Authorization")
        if auth and not auth.strip().lower().startswith("bearer "):
            request.environ["HTTP_AUTHORIZATION"] = f"Bearer {auth.strip()}"

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
            "specs": [{"endpoint": "apispec", "route": "/apispec.json",
                        "rule_filter": lambda r: True, "model_filter": lambda m: True}],
            "static_url_path": "/flasgger_static",
            "swagger_ui": True,
            "specs_route": "/docs",
            "auth": {},
        },
    )

    register_blueprints(app)       # API blueprints
    register_web_blueprints(app)   # Web UI blueprints (modular)
    register_error_handlers(app)

    with app.app_context():
        from models import (  # noqa: F401 – register models for flask-migrate
            User, Category, Product, ProductImage,
            CartItem, Order, OrderItem, Review, WishlistItem,
        )


    return app
