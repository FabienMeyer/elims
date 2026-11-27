"""Request-scoped database sessions return their connection when the request ends."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import pytest
from app.db import get_session
from elims_database import Database
from fastapi import FastAPI, Request
from sqlalchemy import text


@pytest.fixture
async def database(tmp_path: Path) -> AsyncIterator[Database]:
    """A file database, so the engine uses a pool that counts checked-out connections."""
    database = Database(f"sqlite+aiosqlite:///{(tmp_path / 'sessions.db').as_posix()}")
    yield database
    await database.dispose()


def request_for(database: Database) -> Request:
    application = FastAPI()
    application.state.database = database
    return Request({"type": "http", "app": application})


async def test_session_is_released_after_a_successful_request(database: Database) -> None:
    """FastAPI drives generator dependencies as async context managers."""
    async with asynccontextmanager(get_session)(request_for(database)) as session:
        await session.exec(text("SELECT 1"))
        assert database.engine.pool.checkedout() == 1
    assert database.engine.pool.checkedout() == 0


async def test_session_is_released_before_an_error_response(database: Database) -> None:
    """An endpoint error is thrown into the dependency; the connection must return to the pool at once."""
    with pytest.raises(RuntimeError, match="endpoint failed"):
        async with asynccontextmanager(get_session)(request_for(database)) as session:
            await session.exec(text("SELECT 1"))
            raise RuntimeError("endpoint failed")
    assert database.engine.pool.checkedout() == 0
