"""Health and metadata endpoints."""

from typing import cast

from elims_database import Database
from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.exc import SQLAlchemyError

from app.api.system.services import schema_is_current

router = APIRouter(tags=["system"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Return liveness status."""
    return {"status": "healthy"}


@router.get("/ready")
async def ready(request: Request) -> dict[str, str]:
    """Report ready when the database is reachable and at this build's migration revision, without exposing errors."""
    database = cast(Database, request.app.state.database)
    try:
        current = await schema_is_current(database.engine)
    except SQLAlchemyError as error:
        raise HTTPException(status_code=503, detail="Database is not ready") from error
    if not current:
        raise HTTPException(status_code=503, detail="Database is not ready")
    return {"status": "ready"}
