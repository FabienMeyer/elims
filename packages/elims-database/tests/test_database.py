"""Database lifecycle tests."""

from sqlalchemy import text

from elims_database import Database


async def test_database_yields_working_session() -> None:
    """A session can execute a query and the engine can be disposed."""
    database = Database("sqlite+aiosqlite:///:memory:")
    async for session in database.sessions():
        result = await session.exec(text("SELECT 1"))
        assert result.scalar_one() == 1
    await database.dispose()
