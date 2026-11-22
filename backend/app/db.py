"""Async database engine and session dependency."""

from collections.abc import AsyncIterator
from typing import cast

from elims_database import Database
from fastapi import Request
from sqlmodel.ext.asyncio.session import AsyncSession


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Yield one database session per request."""
    database = cast(Database, request.app.state.database)
    async for session in database.sessions():
        yield session
