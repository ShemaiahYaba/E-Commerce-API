# E-Commerce API

A production-ready REST API for e-commerce applications, built with Flask. Supports user authentication, product catalog management, shopping cart, order processing with simulated payments, product reviews, wishlists, and an admin dashboard.

## Features

- **Auth** – JWT-based registration, login, logout, token revocation, and password reset via email
- **Products** – Full CRUD with search, category filtering, price/rating filters, and image uploads
- **Categories** – Hierarchical product categorisation
- **Cart** – Per-user cart with quantity management and running total
- **Orders** – Checkout from cart, order history, simulated Stripe payment intents
- **Reviews** – Purchaser-only reviews with rating and pagination
- **Wishlist** – Add/remove products, view with full product details
- **Admin** – Dashboard stats, inventory management, user management, order management
- **Email notifications** – Password reset and order confirmation via SMTP (Resend by default)
- **Rate limiting** – Per-scope in-memory rate limits on sensitive endpoints
- **API docs** – Swagger UI at `/docs`, web docs at `/web/docs`

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Flask 3 |
| Database | PostgreSQL (production) / SQLite in-memory (tests) |
| ORM | SQLAlchemy 2 + Flask-SQLAlchemy |
| Migrations | Flask-Migrate (Alembic) |
| Auth | Flask-JWT-Extended (Bearer tokens) |
| Validation | Pydantic v2 + pydantic-settings |
| Server | Uvicorn (ASGI via asgiref) |
| API docs | Flasgger (Swagger UI) |
| Email | Flask-Mail (Resend SMTP by default) |
| Deployment | Fly.io (Docker) |

## Quick Start (Local)

**Prerequisites:** Python 3.11+, a running PostgreSQL instance (or use Docker below)

```bash
# 1. Clone and create virtual environment
git clone <repo-url>
cd E-Commerce-API
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env          # then edit .env with your values

# 4. Run database migrations
export FLASK_APP=run:app
flask db upgrade

# 5. (Optional) Seed the database
python scripts/seed.py        # creates admin@example.com / admin123

# 6. Start the server
python run.py                 # runs on http://localhost:5000
```

### Endpoints

| URL | Description |
|---|---|
| `http://localhost:5000/api/v1/` | API base |
| `http://localhost:5000/api/v1/health` | Health check |
| `http://localhost:5000/docs` | Swagger UI |
| `http://localhost:5000/web/docs` | Web documentation |

## Docker

```bash
# Build and run with docker-compose
docker-compose up --build

# The container runs migrations automatically before starting
```

The `docker-compose.yml` mounts a named volume for persistent SQLite data in containerised local development. For production, set `DATABASE_URL` to your PostgreSQL connection string.

## Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```env
FLASK_ENV=development

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce

# Security (generate strong random values for production)
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# CORS (comma-separated origins, or * to allow all)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Email (defaults to Resend SMTP)
MAIL_SERVER=smtp.resend.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=resend
MAIL_PASSWORD=your-resend-api-key
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
```

## API Reference

All endpoints are prefixed with `/api/v1`. Protected endpoints require an `Authorization: Bearer <token>` header. Admin endpoints additionally require the user to have the admin role.

### Authentication

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | — | Register a new user |
| POST | `/auth/login` | — | Login, returns access + refresh tokens |
| POST | `/auth/logout` | Required | Invalidate current token |
| GET | `/auth/me` | Required | Get current user profile |
| POST | `/auth/password-reset` | — | Request a password reset email |
| POST | `/auth/password-reset/confirm` | — | Confirm reset with token + new password |

**Register / Login request body:**
```json
{ "email": "user@example.com", "password": "secret", "first_name": "Jane", "last_name": "Doe" }
```

**Token response:**
```json
{ "access_token": "...", "refresh_token": "...", "token_type": "Bearer", "user": { ... } }
```

---

### Products

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/products` | — | List products (search, filter, paginate) |
| GET | `/products/:id` | — | Get a single product |
| POST | `/products` | Admin | Create a product |
| PUT | `/products/:id` | Admin | Update a product |
| DELETE | `/products/:id` | Admin | Delete a product |
| POST | `/products/:id/images` | Admin | Add an image (URL or file upload) |

**Query params for `GET /products`:**

| Param | Type | Description |
|---|---|---|
| `q` | string | Full-text search on name/description |
| `category_id` | integer | Filter by category |
| `min_price` / `max_price` | float | Price range filter |
| `min_rating` | float | Minimum average rating |
| `in_stock_only` | boolean | Exclude out-of-stock products |
| `page` / `per_page` | integer | Pagination (default: page 1, 20 per page) |

---

### Categories

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/categories` | — | List all categories |
| GET | `/categories/:id` | — | Get a category |
| POST | `/categories` | Admin | Create a category |
| PUT | `/categories/:id` | Admin | Update a category |
| DELETE | `/categories/:id` | Admin | Delete a category |

---

### Cart

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/cart` | Required | View cart with items and total |
| POST | `/cart/items` | Required | Add item (`product_id`, `quantity`) |
| PUT | `/cart/items/:id` | Required | Update item quantity (set 0 to remove) |
| DELETE | `/cart/items/:id` | Required | Remove a specific item |
| DELETE | `/cart` | Required | Clear entire cart |

---

### Orders

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/orders` | Required | Create order from current cart |
| GET | `/orders` | Required | List current user's orders (paginated) |
| GET | `/orders/:id` | Required | Get a specific order (owner only) |
| PUT | `/orders/:id/status` | Admin | Update order status |
| POST | `/orders/payment-intent` | Required | Create a simulated payment intent |

**Order statuses:** `pending`, `processing`, `shipped`, `delivered`, `cancelled`

**Payment flow:**
1. `POST /orders/payment-intent` — returns a simulated `payment_intent_id` and total amount
2. `POST /orders` — creates the order and clears the cart

---

### Reviews

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/products/:id/reviews` | — | List reviews for a product (paginated) |
| POST | `/products/:id/reviews` | Required | Submit a review (must have purchased product) |
| DELETE | `/products/:id/reviews/:review_id` | Admin | Delete a review |

---

### Wishlist

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/wishlist` | Required | Get wishlist with product details |
| POST | `/wishlist` | Required | Add product to wishlist (`product_id`) |
| DELETE | `/wishlist/:id` | Required | Remove item from wishlist |

---

### Admin

All admin endpoints require an authenticated admin user.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/admin/stats` | Dashboard: total users, orders, revenue, popular products |
| GET | `/admin/inventory` | Stock levels; filter low stock by threshold |
| GET | `/admin/orders` | List all orders (paginated) |
| POST | `/admin/orders/:id/cancel` | Cancel an order and restore stock |
| DELETE | `/admin/orders/:id` | Hard-delete an order |
| GET | `/admin/users` | List all users (paginated) |
| GET | `/admin/users/:id` | Get a user by ID |

---

### Users

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/users/me` | Required | Get current user profile |
| PUT | `/users/me` | Required | Update profile |
| PUT | `/users/me/password` | Required | Change password |

---

## Database Migrations

```bash
export FLASK_APP=run:app

# Create a new migration after model changes
flask db migrate -m "describe your change"

# Apply pending migrations
flask db upgrade

# Downgrade one step
flask db downgrade
```

## Running Tests

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=. --cov-report=html

# Run a specific test file
pytest tests/test_auth.py -v
```

Tests use an in-memory SQLite database and do not require a running PostgreSQL instance.

## Project Structure

```
E-Commerce-API/
├── app.py              # Application factory
├── run.py              # Entry point (Uvicorn + ASGI wrapper)
├── config/
│   ├── settings.py     # Pydantic-settings config (dev/test/prod)
│   ├── database.py     # SQLAlchemy + Migrate init
│   ├── mail.py         # Flask-Mail init
│   └── swagger.py      # Swagger/Flasgger template
├── models/             # SQLAlchemy ORM models
├── schemas/            # Pydantic request/response schemas
├── routes/             # Flask blueprints (one per resource)
├── services/           # Business logic layer
├── middleware/
│   ├── auth.py         # admin_required decorator
│   └── rate_limit.py   # In-memory rate limiter
├── errors/             # Custom exception types + error handlers
├── utils/              # Response helpers, security utilities
├── migrations/         # Alembic migration scripts
├── tests/              # pytest test suite
├── scripts/
│   ├── seed.py         # Database seed script
│   └── setup_db.sh     # DB setup for Fly.io release command
├── templates/          # Jinja2 email and web doc templates
├── Dockerfile
├── docker-compose.yml
├── fly.toml            # Fly.io deployment config
└── requirements.txt
```

## Deploying to Fly.io

The project includes a `fly.toml` configured for Fly.io. Database migrations run automatically via the `release_command` before traffic is switched to new instances.

```bash
# First-time setup
fly launch

# Set required secrets
fly secrets set SECRET_KEY=<value> JWT_SECRET_KEY=<value> DATABASE_URL=<value>
fly secrets set MAIL_PASSWORD=<your-resend-api-key>

# Deploy
fly deploy
```

## Default Seed Credentials

After running `python scripts/seed.py`:

| Role | Email | Password |
|---|---|---|
| Admin | `admin@example.com` | `admin123` |
