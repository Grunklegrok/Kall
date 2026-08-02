from fastapi.testclient import TestClient

from kall.main import app


def test_health_endpoint() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_operations_routes_are_registered() -> None:
    paths = {route.path for route in app.routes}
    assert "/health" in paths
    assert "/ready" in paths
