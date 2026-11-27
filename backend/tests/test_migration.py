"""Migration configuration, model discovery, and schema consistency."""

import subprocess
import sys
from io import StringIO
from pathlib import Path

import app.api  # noqa: F401 - configures the metadata that every domain model shares
import pytest
from alembic import command
from alembic.config import Config
from app.config import get_settings
from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Table
from sqlmodel import SQLModel


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


def test_shared_metadata_names_constraints_deterministically() -> None:
    """MariaDB and SQLite name unnamed constraints differently; later migrations must drop them by a known name."""
    metadata = MetaData(naming_convention=SQLModel.metadata.naming_convention)
    Table("parent", metadata, Column("id", Integer, primary_key=True))
    child = Table(
        "child",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("code", String(5), unique=True),
        Column("parent_id", ForeignKey("parent.id")),
    )
    assert {constraint.name for constraint in child.constraints} == {
        "pk_child",
        "uq_child_code",
        "fk_child_parent_id_parent",
    }


def test_models_match_migrations(migrated_database: str) -> None:
    """`alembic check`, run as operators run it, sees every domain model and no drift from the migrations.

    A fresh process matters: this test session has already imported the models, which would hide a model
    that env.py fails to discover.
    """
    backend = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "check"], cwd=backend, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stdout + result.stderr
