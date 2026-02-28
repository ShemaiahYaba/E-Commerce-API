"""Order API tests: create from cart, list, get, admin status update."""

import pytest


@pytest.fixture
def cart_with_items(client, customer_headers, admin_headers):
    """Create category, product, add to cart; return product_id."""
    cat_r = client.post(
        "/api/v1/categories",
        json={"name": "OrderCat"},
        headers=admin_headers,
    )
    cat_id = cat_r.get_json()["data"]["id"]
    prod_r = client.post(
        "/api/v1/products",
        json={
            "name": "OrderProduct",
            "price": 29.99,
            "stock": 5,
            "sku": "ORD-001",
            "category_id": cat_id,
        },
        headers=admin_headers,
    )
    product_id = prod_r.get_json()["data"]["id"]
    client.post(
        "/api/v1/cart/items",
        json={"product_id": product_id, "quantity": 2},
        headers=customer_headers,
    )
    return product_id


def test_create_order_empty_cart(client, customer_headers):
    r = client.post("/api/v1/orders", headers=customer_headers)
    assert r.status_code == 400


def test_create_order_success(client, customer_headers, cart_with_items):
    r = client.post("/api/v1/orders", headers=customer_headers)
    assert r.status_code == 201
    data = r.get_json()["data"]
    assert "id" in data
    assert data["status"] == "pending"
    assert float(data["total"]) == 2 * 29.99
    assert "payment_intent_id" in data
    assert len(data["order_items"]) == 1


def test_list_orders(client, customer_headers, cart_with_items):
    client.post("/api/v1/orders", headers=customer_headers)
    r = client.get("/api/v1/orders", headers=customer_headers)
    assert r.status_code == 200
    data = r.get_json()["data"]
    assert "orders" in data
    assert len(data["orders"]) >= 1


def test_get_order(client, customer_headers, cart_with_items):
    create_r = client.post("/api/v1/orders", headers=customer_headers)
    order_id = create_r.get_json()["data"]["id"]
    r = client.get(f"/api/v1/orders/{order_id}", headers=customer_headers)
    assert r.status_code == 200
    assert r.get_json()["data"]["id"] == order_id


def test_update_order_status_admin(client, customer_headers, admin_headers, cart_with_items):
    create_r = client.post("/api/v1/orders", headers=customer_headers)
    order_id = create_r.get_json()["data"]["id"]

    r = client.put(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "shipped"},
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert r.get_json()["data"]["status"] == "shipped"


def test_update_order_status_forbidden_for_customer(client, customer_headers, cart_with_items):
    create_r = client.post("/api/v1/orders", headers=customer_headers)
    order_id = create_r.get_json()["data"]["id"]
    r = client.put(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "shipped"},
        headers=customer_headers,
    )
    assert r.status_code == 403
