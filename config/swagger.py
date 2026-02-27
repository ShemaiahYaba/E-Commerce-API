"""Swagger/OpenAPI config for /docs."""

SWAGGER_TEMPLATE = {
    "info": {
        "title": "E-Commerce API",
        "version": "1.0",
        "description": "REST API for e-commerce: auth, users, products, categories, cart, orders, reviews, wishlist, admin.",
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "JWT: Bearer <access_token>",
        }
    },
    "security": [{"Bearer": []}],
    "tags": [
        {"name": "info", "description": "Health and root"},
        {"name": "auth", "description": "Register, login, logout, password reset"},
        {"name": "users", "description": "Profile, admin user management"},
        {"name": "categories", "description": "Category CRUD"},
        {"name": "products", "description": "Product CRUD, search, images"},
        {"name": "cart", "description": "Cart items"},
        {"name": "orders", "description": "Orders"},
        {"name": "reviews", "description": "Product reviews"},
        {"name": "wishlist", "description": "Wishlist"},
        {"name": "admin", "description": "Admin stats and inventory"},
    ],
}
