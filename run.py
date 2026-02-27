"""Run the app with Uvicorn (ASGI) or Flask dev server."""

import os
from asgiref.wsgi import WsgiToAsgi

from app import create_app

app = create_app()

# ASGI app for Uvicorn
asgi_app = WsgiToAsgi(app)

# Default 5001: Windows often reserves 5000 (WinError 10013). Override with PORT=5000 in .env if needed.
_DEFAULT_PORT = 5001

if __name__ == "__main__":
    port = int(os.getenv("PORT", _DEFAULT_PORT))
    use_uvicorn = os.getenv("USE_UVICORN", "1") == "1"
    if use_uvicorn:
        import uvicorn
        uvicorn.run(
            "run:asgi_app",
            host="0.0.0.0",
            port=port,
            reload=os.getenv("FLASK_ENV") == "development",
        )
    else:
        app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", False))
