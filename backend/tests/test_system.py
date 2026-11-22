"""System endpoint tests."""

from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    """Health endpoint reports a live application."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_metrics(client: TestClient) -> None:
    """Prometheus can scrape application metrics."""
    client.get("/health")
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "http_requests_total" in response.text


def test_readiness(client: TestClient) -> None:
    """Readiness requires the migrated database and is reachable through the proxy."""
    assert client.get("/api/ready").json() == {"status": "ready"}
