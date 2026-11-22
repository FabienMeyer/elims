"""Health and metadata endpoints."""

from typing import cast

from elims_database import Database
from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(tags=["system"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Return liveness status."""
    return {"status": "healthy"}


@router.get("/ready")
async def ready(request: Request) -> dict[str, str]:
    """Check database connectivity and the initial migration without exposing errors."""
    database = cast(Database, request.app.state.database)
    try:
        async with database.engine.connect() as connection:
            await connection.execute(text("SELECT id FROM item LIMIT 0"))
    except SQLAlchemyError as error:
        raise HTTPException(status_code=503, detail="Database is not ready") from error
    return {"status": "ready"}
