"""Verify migration URLs with encoded credentials, without opening a connection."""

from io import StringIO
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from app.config import get_settings


def test_encoded_credentials_survive_migration_config(monkeypatch: pytest.MonkeyPatch) -> None:
    backend = Path(__file__).resolve().parents[1]
    output = StringIO()
    config = Config(str(backend / "alembic.ini"), output_buffer=output)
    config.set_main_option("script_location", str(backend / "app/alembic"))
    url = "mysql+aiomysql://app:sample%40%25value@localhost/app"
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("DATABASE_URL", url)
    get_settings.cache_clear()
    try:
        command.upgrade(config, "head", sql=True)
        assert config.get_main_option("sqlalchemy.url") == url.replace("mysql+aiomysql", "mysql+pymysql")
        assert "CREATE TABLE item" in output.getvalue()
    finally:
        get_settings.cache_clear()
