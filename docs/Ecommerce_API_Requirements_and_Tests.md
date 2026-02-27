# E-Commerce Backend API
## Functional Requirements & Exhaustive Test Plan
*Backend Engineering Fundamentals – 6-Week Intensive | Week 5 & 6 Final Project*

---

# PART 1: FUNCTIONAL REQUIREMENTS

The following requirements are extracted from the Week 5 and Week 6 curricula. Each requirement is categorised by module and assigned a unique ID and priority.

---

## 1.1 User Management

| ID | Feature | Description | Priority |
|----|---------|-------------|----------|
| UM-01 | User Registration | Users can create a new account by providing email, password, and profile details. Email must be unique. | High |
| UM-02 | User Login | Registered users can authenticate using email and password. A JWT token is returned on success. | High |
| UM-03 | User Logout | Authenticated users can invalidate their current JWT session/token. | High |
| UM-04 | Profile Management | Authenticated users can view and update their profile information (name, address, etc.). | Medium |
| UM-05 | Password Reset | Users can request a password reset via email. A secure token-based reset flow is implemented. | Medium |
| UM-06 | Role-Based Access Control | The system supports two roles: Admin and Customer. Endpoints enforce role-based access appropriately. | High |
| UM-07 | Admin User Management | Admins can view, deactivate, and manage all user accounts. | Medium |

---

## 1.2 Product Management

| ID | Feature | Description | Priority |
|----|---------|-------------|----------|
| PM-01 | Create Product | Admins can create new products with name, description, price, stock quantity, category, and images. | High |
| PM-02 | Read Product | Any user (including unauthenticated) can view a single product by ID. | High |
| PM-03 | Update Product | Admins can update product details including price, description, and stock. | High |
| PM-04 | Delete Product | Admins can soft-delete or remove products from the catalog. | High |
| PM-05 | Product Image Upload | Admins can upload one or more images per product. | Medium |
| PM-06 | Categories & Subcategories | Products belong to a category and optionally a subcategory. Admins can manage the category tree. | High |
| PM-07 | Product Search | Users can search products by keyword, with results filtered by price range, category, and rating. | High |
| PM-08 | Pagination | All product listing endpoints return paginated results with configurable page size. | Medium |
| PM-09 | Product Reviews & Ratings | Authenticated customers can submit a review (text + star rating) for a product they have purchased. | Medium |
| PM-10 | Stock Management | System tracks and updates stock quantity on order placement. Out-of-stock products are flagged. | High |

---

## 1.3 Shopping Cart

| ID | Feature | Description | Priority |
|----|---------|-------------|----------|
| SC-01 | Add Item to Cart | Authenticated users can add a product with a specified quantity to their cart. | High |
| SC-02 | Update Cart Item | Users can update the quantity of an existing cart item. | High |
| SC-03 | Remove Cart Item | Users can remove a specific item from their cart. | High |
| SC-04 | View Cart | Users can retrieve all items currently in their cart along with totals. | High |
| SC-05 | Cart Quantity Validation | Adding or updating items validates available stock. Requests exceeding stock are rejected. | High |

---

## 1.4 Wishlist

| ID | Feature | Description | Priority |
|----|---------|-------------|----------|
| WL-01 | Add to Wishlist | Authenticated users can add a product to their wishlist. | Low |
| WL-02 | View Wishlist | Users can retrieve all products in their wishlist. | Low |
| WL-03 | Remove from Wishlist | Users can remove a product from their wishlist. | Low |

---

## 1.5 Order Management

| ID | Feature | Description | Priority |
|----|---------|-------------|----------|
| OM-01 | Create Order | Authenticated users can place an order from their current cart. Stock is decremented on order creation. | High |
| OM-02 | Order History | Users can view a list of all their past orders. | High |
| OM-03 | Order Detail | Users can view the full detail of a specific order including items, prices, and status. | High |
| OM-04 | Order Status Tracking | Orders have statuses: Pending, Processing, Shipped, Delivered, Cancelled. | High |
| OM-05 | Admin Order Management | Admins can view all orders, update order statuses, and manage fulfillment. | High |
| OM-06 | Order Confirmation Email | System sends an email notification to the customer upon successful order placement. | Medium |
| OM-07 | Payment Intent Simulation | A simulated payment intent is created on checkout (no real payment gateway). | Medium |

---

## 1.6 Admin Dashboard & Statistics

| ID | Feature | Description | Priority |
|----|---------|-------------|----------|
| AD-01 | Dashboard Statistics | Admins can view summary statistics: total users, total orders, revenue, and popular products. | Medium |
| AD-02 | Inventory Tracking | Admins can view a report of current stock levels and low-stock alerts. | Medium |

---

## 1.7 Technical & Cross-Cutting Requirements

| ID | Feature | Description | Priority |
|----|---------|-------------|----------|
| TR-01 | JWT Authentication | All protected endpoints require a valid JWT Bearer token in the Authorization header. | High |
| TR-02 | Input Validation | All endpoints validate and sanitize incoming request data using Marshmallow schemas. | High |
| TR-03 | Error Handling | Global custom error handlers return structured JSON error responses with appropriate HTTP codes. | High |
| TR-04 | API Documentation | All endpoints are documented via Swagger/OpenAPI, accessible at /docs. | Medium |
| TR-05 | Test Coverage | Unit and integration test suite achieves a minimum of 70% code coverage. | High |
| TR-06 | Docker Containerisation | Application and database are containerised with Docker and docker-compose. | Medium |
| TR-07 | Database Migrations | Database schema changes are managed via migration files (e.g. Flask-Migrate/Alembic). | High |
| TR-08 | Environment Configuration | All secrets and environment-specific values are loaded from .env. A .env.example is provided. | High |
| TR-09 | Logging | Application events and errors are logged with appropriate levels (INFO, WARNING, ERROR). | Medium |
| TR-10 | Production Deployment | Application is deployed to a production environment (e.g. Heroku, Render, Railway, AWS). | Medium |

---

# PART 2: EXHAUSTIVE TEST LIST

All tests are categorised as **U** (Unit), **I** (Integration), or **E2E** (End-to-End). The list below covers happy paths, edge cases, and error scenarios to achieve the required 70%+ coverage.

---

## 2.1 Authentication & User Management Tests

| TC ID | Test Case | Description / Steps | Expected Result | Type |
|-------|-----------|---------------------|-----------------|------|
| TC-UM-01 | Register – Valid | POST /auth/register with valid email, password, name. | 201 Created | I |
| TC-UM-02 | Register – Duplicate Email | POST /auth/register with an already-registered email. | 409 Conflict | I |
| TC-UM-03 | Register – Missing Fields | POST /auth/register omitting required fields (email or password). | 400 Bad Request | I |
| TC-UM-04 | Register – Invalid Email Format | POST /auth/register with malformed email string. | 400 Bad Request | U |
| TC-UM-05 | Register – Weak Password | POST /auth/register with password below minimum length/complexity. | 400 Bad Request | U |
| TC-UM-06 | Login – Valid Credentials | POST /auth/login with correct email and password. Expect JWT token. | 200 OK + token | I |
| TC-UM-07 | Login – Wrong Password | POST /auth/login with correct email but wrong password. | 401 Unauthorized | I |
| TC-UM-08 | Login – Unknown Email | POST /auth/login with email not in database. | 401 Unauthorized | I |
| TC-UM-09 | Login – Missing Body | POST /auth/login with empty request body. | 400 Bad Request | I |
| TC-UM-10 | Logout – Valid Token | POST /auth/logout with valid JWT. Token is invalidated. | 200 OK | I |
| TC-UM-11 | Logout – No Token | POST /auth/logout without Authorization header. | 401 Unauthorized | I |
| TC-UM-12 | Get Profile – Authenticated | GET /users/me with valid JWT. Returns current user profile. | 200 OK + profile | I |
| TC-UM-13 | Get Profile – No Token | GET /users/me without token. | 401 Unauthorized | I |
| TC-UM-14 | Update Profile – Valid | PUT /users/me with valid updated fields. | 200 OK + updated | I |
| TC-UM-15 | Update Profile – Invalid Field | PUT /users/me with an unexpected/invalid field type. | 400 Bad Request | U |
| TC-UM-16 | Password Reset – Request | POST /auth/password-reset with valid email. Email is sent. | 200 OK | I |
| TC-UM-17 | Password Reset – Unknown Email | POST /auth/password-reset with unregistered email. | 200 OK (no leak) | I |
| TC-UM-18 | Password Reset – Confirm Valid Token | POST /auth/password-reset/confirm with valid token and new password. | 200 OK | I |
| TC-UM-19 | Password Reset – Expired Token | POST /auth/password-reset/confirm with an expired reset token. | 400 Bad Request | I |
| TC-UM-20 | Admin – List Users | GET /admin/users as Admin role. Returns paginated user list. | 200 OK | I |
| TC-UM-21 | Admin – List Users as Customer | GET /admin/users with Customer JWT. | 403 Forbidden | I |
| TC-UM-22 | JWT – Expired Token | Access any protected endpoint with an expired JWT. | 401 Unauthorized | U |
| TC-UM-23 | JWT – Tampered Token | Access protected endpoint with a forged/modified JWT. | 401 Unauthorized | U |

---

## 2.2 Product Management Tests

| TC ID | Test Case | Description / Steps | Expected Result | Type |
|-------|-----------|---------------------|-----------------|------|
| TC-PM-01 | Create Product – Admin Valid | POST /products as Admin with all required fields. | 201 Created | I |
| TC-PM-02 | Create Product – Customer Forbidden | POST /products as Customer JWT. | 403 Forbidden | I |
| TC-PM-03 | Create Product – Missing Name | POST /products without 'name' field. | 400 Bad Request | U |
| TC-PM-04 | Create Product – Negative Price | POST /products with price = -5. | 400 Bad Request | U |
| TC-PM-05 | Create Product – Zero Stock | POST /products with stock = 0. Product created but marked out-of-stock. | 201 Created | I |
| TC-PM-06 | Get Product – Valid ID | GET /products/:id for existing product. | 200 OK + product | I |
| TC-PM-07 | Get Product – Not Found | GET /products/:id for non-existent ID. | 404 Not Found | I |
| TC-PM-08 | Get Product – Invalid ID Format | GET /products/abc (non-integer ID). | 400 Bad Request | U |
| TC-PM-09 | List Products – Paginated | GET /products?page=1&per_page=10. Returns first page. | 200 OK + list | I |
| TC-PM-10 | List Products – Filter by Category | GET /products?category_id=2. Returns only products in that category. | 200 OK | I |
| TC-PM-11 | List Products – Filter by Price Range | GET /products?min_price=10&max_price=50. | 200 OK | I |
| TC-PM-12 | List Products – Search Keyword | GET /products?q=laptop returns matching products. | 200 OK | I |
| TC-PM-13 | List Products – No Results | GET /products?q=xyznonexistent returns empty list. | 200 OK + [] | I |
| TC-PM-14 | Update Product – Admin Valid | PUT /products/:id as Admin with valid fields. | 200 OK | I |
| TC-PM-15 | Update Product – Non-existent | PUT /products/99999 as Admin. | 404 Not Found | I |
| TC-PM-16 | Delete Product – Admin Valid | DELETE /products/:id as Admin. | 200 OK / 204 | I |
| TC-PM-17 | Delete Product – Customer Forbidden | DELETE /products/:id as Customer. | 403 Forbidden | I |
| TC-PM-18 | Upload Product Image – Valid | POST /products/:id/images with valid image file. | 200 OK | I |
| TC-PM-19 | Upload Product Image – Invalid Type | POST /products/:id/images with a .exe file. | 400 Bad Request | U |
| TC-PM-20 | Create Category – Admin | POST /categories with valid name. | 201 Created | I |
| TC-PM-21 | Create Subcategory | POST /categories with parent_id set. | 201 Created | I |
| TC-PM-22 | Submit Review – Valid | POST /products/:id/reviews as Customer who ordered item. | 201 Created | I |
| TC-PM-23 | Submit Review – Not Purchased | POST /products/:id/reviews for a product never ordered. | 403 Forbidden | I |
| TC-PM-24 | Submit Review – Invalid Rating | POST /products/:id/reviews with rating = 6. | 400 Bad Request | U |
| TC-PM-25 | Get Product Reviews | GET /products/:id/reviews returns list of reviews. | 200 OK | I |

---

## 2.3 Shopping Cart Tests

| TC ID | Test Case | Description / Steps | Expected Result | Type |
|-------|-----------|---------------------|-----------------|------|
| TC-SC-01 | Add Item – Valid | POST /cart/items with valid product_id and quantity. | 201 Created | I |
| TC-SC-02 | Add Item – Out of Stock | POST /cart/items for a product with stock = 0. | 400 Bad Request | I |
| TC-SC-03 | Add Item – Exceeds Stock | POST /cart/items with quantity > available stock. | 400 Bad Request | I |
| TC-SC-04 | Add Item – Unauthenticated | POST /cart/items without JWT. | 401 Unauthorized | I |
| TC-SC-05 | Add Item – Invalid Product ID | POST /cart/items with non-existent product_id. | 404 Not Found | I |
| TC-SC-06 | Add Item – Duplicate Item | POST /cart/items for a product already in cart. Quantity should increment. | 200 OK | I |
| TC-SC-07 | View Cart – Valid | GET /cart returns all items for authenticated user. | 200 OK + items | I |
| TC-SC-08 | View Cart – Empty | GET /cart when cart has no items. | 200 OK + [] | I |
| TC-SC-09 | Update Cart Item – Valid | PUT /cart/items/:id with new quantity. | 200 OK | I |
| TC-SC-10 | Update Cart Item – Zero Quantity | PUT /cart/items/:id with quantity = 0. Item should be removed. | 200 OK | I |
| TC-SC-11 | Update Cart Item – Not Found | PUT /cart/items/9999. | 404 Not Found | I |
| TC-SC-12 | Remove Cart Item – Valid | DELETE /cart/items/:id. | 200 OK / 204 | I |
| TC-SC-13 | Remove Cart Item – Wrong User | DELETE /cart/items/:id belonging to a different user. | 403 Forbidden | I |
| TC-SC-14 | Cart Total Calculation | Verify cart total = sum(item.price * item.quantity). Unit test on service layer. | Correct total | U |

---

## 2.4 Wishlist Tests

| TC ID | Test Case | Description / Steps | Expected Result | Type |
|-------|-----------|---------------------|-----------------|------|
| TC-WL-01 | Add to Wishlist – Valid | POST /wishlist with valid product_id. | 201 Created | I |
| TC-WL-02 | Add to Wishlist – Duplicate | POST /wishlist for product already wishlisted. | 200 OK / 409 | I |
| TC-WL-03 | View Wishlist | GET /wishlist returns user's wishlist items. | 200 OK | I |
| TC-WL-04 | Remove from Wishlist | DELETE /wishlist/:product_id. | 200 OK / 204 | I |
| TC-WL-05 | Wishlist – Unauthenticated | GET /wishlist without JWT. | 401 Unauthorized | I |

---

## 2.5 Order Management Tests

| TC ID | Test Case | Description / Steps | Expected Result | Type |
|-------|-----------|---------------------|-----------------|------|
| TC-OM-01 | Create Order – Valid Cart | POST /orders from a cart with valid items. | 201 Created | I |
| TC-OM-02 | Create Order – Empty Cart | POST /orders when cart is empty. | 400 Bad Request | I |
| TC-OM-03 | Create Order – Stock Decremented | After POST /orders, product stock decreases by ordered quantity. | Stock updated | I |
| TC-OM-04 | Create Order – Insufficient Stock at Checkout | Cart item quantity exceeds stock at time of order. | 400 Bad Request | I |
| TC-OM-05 | Create Order – Cart Cleared After Order | After successful order, user's cart is empty. | Cart = [] | I |
| TC-OM-06 | Get Order – Valid ID (owner) | GET /orders/:id by the customer who placed it. | 200 OK + order | I |
| TC-OM-07 | Get Order – Another User | GET /orders/:id by a different customer. | 403 Forbidden | I |
| TC-OM-08 | Get Order – Not Found | GET /orders/99999. | 404 Not Found | I |
| TC-OM-09 | Order History | GET /orders returns list of current user's orders. | 200 OK + list | I |
| TC-OM-10 | Admin – List All Orders | GET /admin/orders as Admin. | 200 OK + all orders | I |
| TC-OM-11 | Admin – Update Order Status | PUT /admin/orders/:id/status with new status. | 200 OK | I |
| TC-OM-12 | Admin – Invalid Status Transition | PUT /admin/orders/:id/status with invalid status string. | 400 Bad Request | U |
| TC-OM-13 | Payment Intent Simulation | POST /orders creates a simulated payment_intent_id. | Contains intent ID | I |
| TC-OM-14 | Order Confirmation Email | Verify email notification function is called on order creation. | Email triggered | U |

---

## 2.6 Admin Dashboard Tests

| TC ID | Test Case | Description / Steps | Expected Result | Type |
|-------|-----------|---------------------|-----------------|------|
| TC-AD-01 | Dashboard Stats – Admin | GET /admin/stats as Admin. Returns user count, order count, revenue. | 200 OK | I |
| TC-AD-02 | Dashboard Stats – Customer Forbidden | GET /admin/stats as Customer. | 403 Forbidden | I |
| TC-AD-03 | Inventory Report | GET /admin/inventory returns product stock levels. | 200 OK | I |
| TC-AD-04 | Low Stock Alert | Products with stock below threshold appear in low-stock section. | Correct list | U |

---

## 2.7 Input Validation & Error Handling Tests

| TC ID | Test Case | Description / Steps | Expected Result | Type |
|-------|-----------|---------------------|-----------------|------|
| TC-VAL-01 | Missing Required Field | Send any POST/PUT request without a documented required field. | 400 + error detail | U |
| TC-VAL-02 | Wrong Field Type | Send string where integer is expected (e.g. price: 'abc'). | 400 Bad Request | U |
| TC-VAL-03 | Extra Unknown Fields | Send extra unexpected fields in payload. Should be stripped or rejected. | 200/400 | U |
| TC-VAL-04 | SQL Injection Attempt | Send SQL injection string in search or ID param. | 400 or safe 200 | I |
| TC-VAL-05 | XSS Payload in String Field | Send `<script>alert(1)</script>` in product name. | Stored safely / 400 | I |
| TC-VAL-06 | Extremely Long String | Send a 10,000 character string in a name field. | 400 Bad Request | U |
| TC-VAL-07 | Negative Quantity | Send quantity = -1 in cart or order. | 400 Bad Request | U |
| TC-VAL-08 | Global 404 Handler | Request a completely unknown route. | 404 JSON response | I |
| TC-VAL-09 | Global 405 Handler | Use wrong HTTP method on a known route (e.g. GET on POST-only). | 405 JSON response | I |
| TC-VAL-10 | Global 500 Handler | Trigger an internal server error. Verify structured error response. | 500 JSON response | U |

---

## 2.8 Technical / Infrastructure Tests

| TC ID | Test Case | Description / Steps | Expected Result | Type |
|-------|-----------|---------------------|-----------------|------|
| TC-TR-01 | Database Connection | App starts and connects to PostgreSQL successfully. | No DB error on boot | I |
| TC-TR-02 | Migrations Run | Running `flask db upgrade` produces correct schema. | Schema matches models | I |
| TC-TR-03 | Environment Variables Loaded | App fails with clear error if required env var (e.g. SECRET_KEY) is missing. | Error on startup | U |
| TC-TR-04 | Logging – Request Logged | Each HTTP request produces an INFO log entry. | Log entry present | U |
| TC-TR-05 | Logging – Error Logged | A 500 error produces an ERROR log entry. | Log entry present | U |
| TC-TR-06 | Docker Build | `docker-compose up` starts app and DB without errors. | App reachable on port | E2E |
| TC-TR-07 | Swagger Docs Accessible | GET /docs returns the Swagger UI HTML. | 200 OK | I |
| TC-TR-08 | Test Coverage Report | Running `pytest --cov` produces >= 70% coverage. | >= 70% | U |

---

# PART 3: SUMMARY

| Module | Requirements | Test Cases | Coverage Focus |
|--------|-------------|------------|----------------|
| User Management | 7 | 23 | Auth, RBAC, JWT |
| Product Management | 10 | 25 | CRUD, Search, Stock |
| Shopping Cart | 5 | 14 | Validation, Stock Checks |
| Wishlist | 3 | 5 | CRUD |
| Order Management | 7 | 14 | Stock, Status, Email |
| Admin Dashboard | 2 | 4 | Access Control |
| Validation & Errors | 3 | 10 | Edge Cases |
| Technical / Infra | 10 | 8 | Config, Logs, Docker |
| **TOTAL** | **47** | **103** | — |

---

*Legend: U = Unit Test | I = Integration Test | E2E = End-to-End Test*
