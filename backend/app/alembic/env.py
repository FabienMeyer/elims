"""Alembic runtime configuration."""

import importlib
import pkgutil
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

import app.api
from app.config import get_settings

# Import every app.api.<domain>.models module. A model that is not imported is invisible to autogenerate:
# its new table is never migrated, and its existing table looks dropped.
for module in pkgutil.walk_packages(app.api.__path__, f"{app.api.__name__}."):
    if module.name.rsplit(".", 1)[-1] == "models":
        importlib.import_module(module.name)

config = context.config
driver, separator, address = get_settings().database_url.get_secret_value().partition(":")
sync_driver = {"mysql+aiomysql": "mysql+pymysql", "sqlite+aiosqlite": "sqlite"}.get(driver, driver)
config.set_main_option("sqlalchemy.url", f"{sync_driver}{separator}{address}".replace("%", "%%"))
if config.config_file_name:
    fileConfig(config.config_file_name)
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations without a live connection."""
    context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations with a synchronous migration connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_offline() if context.is_offline_mode() else run_migrations_online()
