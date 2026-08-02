from fastapi.testclient import TestClient

from app.core.dependencies import get_product_repository
from app.main import app
from app.repositories.product_repository import InMemoryProductRepository

client = TestClient(app)


def test_root_endpoint_returns_service_name():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"service": "ThreadIQ"}


def test_health_endpoint_returns_healthy_status():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_versioned_products_endpoint_returns_products_list():
    app.dependency_overrides[get_product_repository] = lambda: InMemoryProductRepository()
    try:
        response = client.get("/api/v1/products")
        assert response.status_code == 200
        payload = response.json()
        assert len(payload) == 1
        assert payload[0]["name"] == "Sample product"
        assert payload[0]["status"] == "active"
        assert payload[0]["id"]
    finally:
        app.dependency_overrides.clear()
