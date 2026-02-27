"""Run the app with Uvicorn (ASGI) or Flask dev server."""

import os
from asgiref.wsgi import WsgiToAsgi

from app import create_app

app = create_app()

# ASGI app for Uvicorn
asgi_app = WsgiToAsgi(app)

if __name__ == "__main__":
    use_uvicorn = os.getenv("USE_UVICORN", "1") == "1"
    if use_uvicorn:
        import uvicorn
        uvicorn.run(
            "run:asgi_app",
            host="0.0.0.0",
            port=5000,
            reload=os.getenv("FLASK_ENV") == "development",
        )
    else:
        app.run(host="0.0.0.0", port=5000, debug=app.config.get("DEBUG", False))
