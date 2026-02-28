# E-Commerce API

REST API for e-commerce: users, products, categories, cart, orders, reviews, wishlist, admin. Built with Flask, SQLite, Alembic, Pydantic, Uvicorn, and Swagger.

## Stack

- **Database:** SQLite (file-based; in-memory for tests)
- **Migrations:** Flask-Migrate (Alembic)
- **Server:** Uvicorn (ASGI) or Flask dev server
- **Validation:** Pydantic schemas
- **API docs:** Swagger at `/docs` (Flasgger)
- **Webdocs:** Minimal Jinja + Tailwind UI at `/web/docs`

## Quick start

```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Unix: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional; set FLASK_APP=run:app for flask commands
flask db upgrade       # create DB tables (required before first run)
python scripts/seed.py # optional seed data (admin@example.com / admin123)
python run.py          # runs with Uvicorn by default
```

**First-time setup:** If you see `no such table: users`, the database has no tables yet. Run `flask db upgrade` (with `FLASK_APP=run:app` in `.env` or in the shell), then start the app again.

- API base: `http://localhost:5000/api/v1/`
- Health: `GET /api/v1/health`
- Swagger UI: `GET /docs`
- Webdocs: `GET /web/docs`

## Project structure

- `app.py` – application factory
- `database.py` – Flask-SQLAlchemy, Flask-Migrate
- `config/` – settings (Pydantic)
- `models/` – SQLAlchemy models
- `schemas/` – Pydantic request/response
- `routes/` – API blueprints
- `services/` – business logic
- `utils/` – security, responses
- `tests/` – pytest

## Migrations

```bash
export FLASK_APP=app.py
flask db migrate -m "Description"
flask db upgrade
```

## Tests

```bash
pip install pytest pytest-flask pytest-cov
pytest
pytest --cov=. --cov-report=html
```
