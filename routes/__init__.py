"""API blueprints under /api/v1."""

from .info import info_bp
from .auth import auth_bp
from .users import users_bp
from .categories import categories_bp
from .products import products_bp
from .cart import cart_bp
from .orders import orders_bp
from .reviews import reviews_bp
from .wishlist import wishlist_bp
from .admin import admin_bp


def register_blueprints(app) -> None:
    """Register all API blueprints with app."""
    app.register_blueprint(info_bp, url_prefix="/api/v1")
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(wishlist_bp)
    app.register_blueprint(admin_bp)
