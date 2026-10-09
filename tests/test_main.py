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
        assert "items" in payload
        assert len(payload["items"]) == 1
        assert payload["items"][0]["name"] == "Sample product"
        assert payload["items"][0]["status"] == "active"
        assert payload["total"] == 1
        assert payload["limit"] == 20
        assert payload["offset"] == 0
    finally:
        app.dependency_overrides.clear()


def test_products_pagination_and_filtering():
    repo = InMemoryProductRepository()
    from app.models.product import Product
    repo.create(Product(name="Navy Blue Jeans", category="Denim"))
    repo.create(Product(name="Crimson Red Dress", category="Dresses"))

    app.dependency_overrides[get_product_repository] = lambda: repo
    try:
        # Test limit and offset
        res = client.get("/api/v1/products?limit=1&offset=0")
        assert res.status_code == 200
        data = res.json()
        assert len(data["items"]) == 1
        assert data["limit"] == 1

        # Test search query filter
        res = client.get("/api/v1/products?q=Jeans")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 1
        assert "Jeans" in data["items"][0]["name"]

        # Test category filter
        res = client.get("/api/v1/products?category=Dresses")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 1
        assert "Dress" in data["items"][0]["name"]
    finally:
        app.dependency_overrides.clear()


def test_background_jobs_dispatch_and_polling():
    from app.core.config import settings
    from app.core.dependencies import get_job_repository
    from app.repositories.job_repository import InMemoryJobRepository

    settings.async_jobs = True
    product_repo = InMemoryProductRepository()
    job_repo = InMemoryJobRepository()

    app.dependency_overrides[get_product_repository] = lambda: product_repo
    app.dependency_overrides[get_job_repository] = lambda: job_repo
    try:
        res = client.post("/api/v1/products", json={"name": "Async Black Leather Jacket"})
        assert res.status_code == 201
        data = res.json()
        assert data["name"] == "Async Black Leather Jacket"
        assert data["latest_job_id"] is not None

        # Poll the job
        job_res = client.get(f"/api/v1/jobs/{data['latest_job_id']}")
        assert job_res.status_code == 200
        job_data = job_res.json()
        assert job_data["id"] == data["latest_job_id"]
        assert job_data["status"] in ("PENDING", "RUNNING", "COMPLETED")
    finally:
        settings.async_jobs = False
        app.dependency_overrides.clear()


def test_delete_product_endpoint():

    repo = InMemoryProductRepository()
    app.dependency_overrides[get_product_repository] = lambda: repo
    try:
        from app.models.product import Product
        p = repo.create(Product(name="Item To Delete"))

        # Delete product
        del_res = client.delete(f"/api/v1/products/{p.id}")
        assert del_res.status_code == 204

        # Confirm 404 on get
        get_res = client.get(f"/api/v1/products/{p.id}")
        assert get_res.status_code == 404
    finally:
        app.dependency_overrides.clear()




