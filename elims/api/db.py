"""Database module for handling connections and session management."""

from collections.abc import AsyncGenerator

from loguru import logger
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from elims.config import settings

base_url = settings.db_url
async_url = base_url.replace("sqlite:///", "sqlite+aiosqlite:///") if base_url.startswith("sqlite:///") else base_url

engine = create_async_engine(async_url, echo=settings.sql_echo, future=True)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def create_db_and_tables() -> None:
    """Initialize the database and create tables asynchronously."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info(f"Database tables created for URL: {base_url}")


async def get_session() -> AsyncGenerator[AsyncSession]:
    """FastAPI dependency that yields an async database session."""
    async with SessionLocal() as session:
        yield session
