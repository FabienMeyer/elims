"""Isolated database and HTTP client for API tests."""

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from app.application import create_app
from app.config import Settings, get_settings
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """Exercise the actual Alembic migration before testing the API."""
    database_url = os.environ.get(
        "TEST_DATABASE_URL",
        f"sqlite+aiosqlite:///{(tmp_path / 'test.db').as_posix()}",
    )
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("DATABASE_URL", database_url)
    get_settings.cache_clear()
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    config.set_main_option("script_location", str(Path(__file__).parents[1] / "app/alembic"))
    # A shared integration database must start empty for every test, just like
    # the temporary SQLite database used by the default test path.
    if not database_url.startswith("sqlite"):
        command.downgrade(config, "base")
    command.upgrade(config, "head")
    try:
        with TestClient(create_app(Settings(environment="test", database_url=database_url))) as test_client:
            yield test_client
    finally:
        if not database_url.startswith("sqlite"):
            command.downgrade(config, "base")
        get_settings.cache_clear()
