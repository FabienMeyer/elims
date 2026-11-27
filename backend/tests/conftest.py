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
def alembic_config() -> Config:
    """Alembic configuration for the backend migrations, independent of the working directory."""
    backend = Path(__file__).parents[1]
    config = Config(str(backend / "alembic.ini"))
    config.set_main_option("script_location", str(backend / "app/alembic"))
    return config


@pytest.fixture
def migrated_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, alembic_config: Config) -> Iterator[str]:
    """Migrate an isolated database to head with the actual Alembic migrations and return its URL."""
    database_url = os.environ.get(
        "TEST_DATABASE_URL",
        f"sqlite+aiosqlite:///{(tmp_path / 'test.db').as_posix()}",
    )
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("DATABASE_URL", database_url)
    get_settings.cache_clear()
    # A shared integration database must start empty for every test, just like
    # the temporary SQLite database used by the default test path.
    if not database_url.startswith("sqlite"):
        command.downgrade(alembic_config, "base")
    command.upgrade(alembic_config, "head")
    try:
        yield database_url
    finally:
        if not database_url.startswith("sqlite"):
            command.downgrade(alembic_config, "base")
        get_settings.cache_clear()


@pytest.fixture
def client(migrated_database: str) -> Iterator[TestClient]:
    """HTTP client for an application backed by the migrated database."""
    with TestClient(create_app(Settings(environment="test", database_url=migrated_database))) as test_client:
        yield test_client
