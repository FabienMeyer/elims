"""FastAPI application for the ELIMS project."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from elims.api.db import create_db_and_tables
from elims.api.logger import configure_logging
from elims.api.routers import router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:  # noqa: ARG001 - app required by FastAPI signature
    """Application lifespan to initialize and tear down resources."""
    configure_logging()
    logger.info("Application startup beginning...")
    await create_db_and_tables()
    logger.info("Application startup complete.")
    yield
    logger.info("Application shutdown complete.")


app = FastAPI(
    title="Instrument Management API (Refactored)",
    version="1.0.0",
    description="A simple API for managing laboratory instruments using SQLModel and FastAPI.",
    lifespan=lifespan,
)


app.include_router(router)
