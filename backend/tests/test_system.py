"""System endpoint tests."""

from alembic import command
from alembic.config import Config
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


def test_readiness_does_not_depend_on_example_tables(client: TestClient, alembic_config: Config) -> None:
    """A database at the migration head is ready even after the example item table is gone."""
    command.downgrade(alembic_config, "base")
    command.stamp(alembic_config, "head")
    try:
        assert client.get("/ready").status_code == 200
    finally:
        # Leave an empty, consistently versioned schema for the fixture's teardown.
        command.stamp(alembic_config, "base")


def test_database_behind_the_migration_head_is_not_ready(client: TestClient, alembic_config: Config) -> None:
    """Tables alone are not enough: the database must record this build's migration revision."""
    command.stamp(alembic_config, "base")
    try:
        response = client.get("/ready")
        assert response.status_code == 503
        assert response.json() == {"detail": "Database is not ready"}
    finally:
        command.stamp(alembic_config, "head")
