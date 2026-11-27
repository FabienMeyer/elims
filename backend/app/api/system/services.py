"""Readiness checks."""

from functools import lru_cache
from pathlib import Path

from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

MIGRATIONS = Path(__file__).resolve().parents[2] / "alembic"


@lru_cache
def expected_revisions() -> frozenset[str]:
    """Return the migration heads shipped with this build."""
    return frozenset(ScriptDirectory(str(MIGRATIONS)).get_heads())


def recorded_revisions(connection: Connection) -> frozenset[str]:
    """Return the revisions recorded in the database; empty when it was never migrated."""
    return frozenset(MigrationContext.configure(connection).get_current_heads())


async def schema_is_current(engine: AsyncEngine) -> bool:
    """Return whether the database is migrated to exactly this build's migration heads."""
    async with engine.connect() as connection:
        return await connection.run_sync(recorded_revisions) == expected_revisions()
