"""SQLModel engine and session lifecycle."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession


class Database:
    """Own an asynchronous engine and create isolated sessions."""

    def __init__(self, url: str, *, echo: bool = False, pool_pre_ping: bool = True) -> None:
        """Configure the engine without opening a connection."""
        self.engine: AsyncEngine = create_async_engine(url, echo=echo, pool_pre_ping=pool_pre_ping)
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def sessions(self) -> AsyncIterator[AsyncSession]:
        """Yield one session and always close it afterwards."""
        async with self.session_factory() as session:
            yield session

    async def dispose(self) -> None:
        """Release all pooled connections."""
        await self.engine.dispose()
