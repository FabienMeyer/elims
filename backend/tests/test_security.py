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


def test_missing_environment_is_rejected_without_echoing_secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    """A deployment that omits ENVIRONMENT must not start open, and the error must not print the database password."""
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    # Short enough that Pydantic would print it whole rather than truncating the middle.
    monkeypatch.setenv("DATABASE_URL", "mysql+aiomysql://e:private-pw@db/e")
    with pytest.raises(ValidationError) as error:
        Settings(_env_file=None)
    assert "environment" in str(error.value)
    assert "private-pw" not in str(error.value)


def test_settings_text_hides_database_password() -> None:
    """Printing or logging the settings object must not expose the database password."""
    settings = Settings(environment="test", database_url="mysql+aiomysql://e:private-pw@db/e")
    assert "private-pw" not in repr(settings)
    assert "private-pw" not in str(settings)
    assert "private-pw" not in settings.model_dump_json()


@pytest.mark.parametrize("origins", ["*", "http://localhost:5173, *"])
def test_wildcard_cors_origin_is_rejected(origins: str) -> None:
    """An any-origin CORS policy would let every website call the API from a user's browser."""
    with pytest.raises(ValidationError, match="BACKEND_CORS_ORIGINS"):
        Settings(environment="test", backend_cors_origins=origins)


def test_cors_never_grants_credentialed_access(client: TestClient) -> None:
    """No route uses cookies, so allowed origins get CORS access without credentials."""
    response = client.get("/health", headers={"Origin": "http://localhost:5173", "Cookie": "session=1"})
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "access-control-allow-credentials" not in response.headers


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
