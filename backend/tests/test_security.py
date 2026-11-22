"""Production safeguards and log privacy."""

import json

import pytest
from app.application import create_app
from app.config import Settings
from fastapi.testclient import TestClient
from pydantic import ValidationError


def test_production_access_is_closed() -> None:
    """No business endpoint is usable in production before identity integration."""
    settings = Settings(environment="production", database_url="mysql+aiomysql://configured@localhost/app")
    with TestClient(create_app(settings)) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/api/v1/items/").status_code == 503


def test_production_rejects_development_database() -> None:
    """Development defaults cannot silently become a production deployment."""
    with pytest.raises(ValidationError):
        Settings(environment="production", database_url="sqlite+aiosqlite:///:memory:")


def test_logs_omit_sensitive_request_data(client: TestClient, capsys: pytest.CaptureFixture[str]) -> None:
    """Correlation is retained without logging headers, query strings or bodies."""
    capsys.readouterr()
    response = client.post(
        "/api/v1/items/?token=private-query",
        json={"name": "private-body"},
        headers={"Authorization": "Bearer private-token"},
    )
    output = capsys.readouterr().out
    assert response.status_code == 201
    assert all(value not in output for value in ("private-query", "private-body", "private-token"))
    event = json.loads(output.strip().splitlines()[-1])
    assert event["request_id"] == response.headers["X-Request-ID"]
    assert event["route"].endswith("/items/")
