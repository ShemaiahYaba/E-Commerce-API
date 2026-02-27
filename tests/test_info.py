"""Tests for info (health, root) routes."""

import pytest


def test_health(client):
    """GET /api/v1/health returns 200 and status ok."""
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    data = r.get_json()
    assert data["success"] is True
    assert data["data"]["status"] == "ok"


def test_root(client):
    """GET /api/v1/ returns API name and version."""
    r = client.get("/api/v1/")
    assert r.status_code == 200
    data = r.get_json()
    assert data["success"] is True
    assert data["data"]["name"] == "E-Commerce API"
    assert data["data"]["version"] == "1.0"
