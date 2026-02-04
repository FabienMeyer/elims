"""ELIMS - Electronic Laboratory Instrument Management System - Backend API."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from app.config import settings
from app.db import create_db_and_tables
from app.mqtt.subscriber import start_subscriber_thread
from app.routers import router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan manager."""
    # Startup: Create database tables
    await create_db_and_tables()
    subscriber_thread, subscriber_stop_event = start_subscriber_thread()
    yield
    # Shutdown: Cleanup resources
    subscriber_stop_event.set()
    subscriber_thread.join(timeout=5)


app = FastAPI(
    title="ELIMS",
    version="0.0.1",
    description="ELIMS - Electronic Laboratory Instrument Management System - Backend API.",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "ELIMS API", "version": "0.0.1", "environment": settings.environment.value}
