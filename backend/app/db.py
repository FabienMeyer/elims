"""Async database engine and session dependency."""

from collections.abc import AsyncIterator
from typing import cast

from elims_database import Database
from fastapi import Request
from sqlmodel.ext.asyncio.session import AsyncSession


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Yield one database session per request.

    The session context is opened here rather than by iterating another generator: FastAPI throws endpoint
    errors into this generator, and only a context held in this frame is closed before the error response.
    """
    database = cast(Database, request.app.state.database)
    async with database.session_factory() as session:
        yield session
