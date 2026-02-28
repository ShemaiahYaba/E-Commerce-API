"""Review API tests: list, create (purchaser only), delete."""

import pytest


@pytest.fixture
def product_for_review(client, admin_headers):
    """Create category and product; return product_id."""
    cat_r = client.post(
        "/api/v1/categories",
        json={"name": "ReviewCat"},
        headers=admin_headers,
    )
    cat_id = cat_r.get_json()["data"]["id"]
    prod_r = client.post(
        "/api/v1/products",
        json={
            "name": "ReviewProduct",
            "price": 1.0,
            "stock": 10,
            "sku": "REV-001",
            "category_id": cat_id,
        },
        headers=admin_headers,
    )
    return prod_r.get_json()["data"]["id"]


def test_list_reviews_empty(client, product_for_review):
    r = client.get(f"/api/v1/products/{product_for_review}/reviews")
    assert r.status_code == 200
    data = r.get_json()["data"]
    assert "reviews" in data
    assert isinstance(data["reviews"], list)


def test_create_review_requires_purchase(client, customer_headers, product_for_review):
    """User who never bought the product cannot review."""
    r = client.post(
        f"/api/v1/products/{product_for_review}/reviews",
        json={"rating": 5, "comment": "Great!"},
        headers=customer_headers,
    )
    assert r.status_code in (400, 403)  # business rule: must have purchased


def test_create_review_after_purchase(client, customer_headers, admin_headers, product_for_review):
    """Purchase product then create review."""
    client.post(
        "/api/v1/cart/items",
        json={"product_id": product_for_review, "quantity": 1},
        headers=customer_headers,
    )
    client.post("/api/v1/orders", headers=customer_headers)

    r = client.post(
        f"/api/v1/products/{product_for_review}/reviews",
        json={"rating": 5, "comment": "Great product!"},
        headers=customer_headers,
    )
    assert r.status_code == 201
    data = r.get_json()["data"]
    assert data["rating"] == 5
    assert "comment" in data


def test_list_reviews_after_create(client, customer_headers, admin_headers, product_for_review):
    client.post(
        "/api/v1/cart/items",
        json={"product_id": product_for_review, "quantity": 1},
        headers=customer_headers,
    )
    client.post("/api/v1/orders", headers=customer_headers)
    client.post(
        f"/api/v1/products/{product_for_review}/reviews",
        json={"rating": 4, "comment": "Good"},
        headers=customer_headers,
    )

    r = client.get(f"/api/v1/products/{product_for_review}/reviews")
    assert r.status_code == 200
    reviews = r.get_json()["data"]["reviews"]
    assert len(reviews) >= 1
