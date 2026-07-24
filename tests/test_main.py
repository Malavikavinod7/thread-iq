from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint_returns_service_name():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"service": "ThreadIQ"}


def test_health_endpoint_returns_healthy_status():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
