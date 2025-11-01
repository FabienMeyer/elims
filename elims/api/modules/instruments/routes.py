"""API routes for the API instruments module."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlmodel.ext.asyncio.session import AsyncSession

from elims.api.db import get_session
from elims.api.modules.instruments.exceptions import (
    InstrumentAlreadyExistError,
    InstrumentNotFoundError,
)
from elims.api.modules.instruments.schemas import (
    InstrumentCreate,
    InstrumentRead,
    InstrumentUpdate,
)
from elims.api.modules.instruments.services import InstrumentService

router_collection: APIRouter = APIRouter(prefix="/instruments", tags=["instruments"])
router_resource: APIRouter = APIRouter(prefix="/instrument", tags=["instrument"])


async def get_instrument_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> InstrumentService:
    """Instantiate and provide the InstrumentService.

    Args:
        session: The asynchronous database session.

    Returns:
        An instance of InstrumentService.

    """
    return InstrumentService(session=session)


@router_resource.post("/", status_code=status.HTTP_201_CREATED)
async def create_instrument(
    instrument_data: InstrumentCreate,
    service: Annotated[InstrumentService, Depends(get_instrument_service)],
) -> InstrumentRead:
    """Create a new instrument.

    Args:
        instrument_data: The instrument data for creation.
        service: The instrument service dependency.

    Returns:
        The created instrument with its database ID.

    Raises:
        HTTPException: If an instrument with the same serial number already exists.

    """
    try:
        return await service.create(instrument_data)
    except InstrumentAlreadyExistError as e:
        detail = str(e)
        logger.warning(f"Create instrument failed due to conflict: {detail}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from e


@router_resource.get("/{instrument_id}")
async def get_instrument(
    instrument_id: int,
    service: Annotated[InstrumentService, Depends(get_instrument_service)],
) -> InstrumentRead:
    """Get an instrument by its ID.

    Args:
        instrument_id: The ID of the instrument to retrieve.
        service: The instrument service dependency.

    Returns:
        The requested instrument.

    Raises:
        HTTPException: If the instrument is not found.

    """
    try:
        return await service.get(instrument_id)
    except InstrumentNotFoundError as e:
        detail = str(e)
        logger.warning(f"Get instrument failed: {detail}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail) from e


@router_resource.patch("/{instrument_id}")
async def update_instrument(
    instrument_id: int,
    instrument_data: InstrumentUpdate,
    service: Annotated[InstrumentService, Depends(get_instrument_service)],
) -> InstrumentRead:
    """Update an instrument (partial update).

    Args:
        instrument_id: The ID of the instrument to update.
        instrument_data: The instrument data to update (only provided fields are updated).
        service: The instrument service dependency.

    Returns:
        The updated instrument.

    Raises:
        HTTPException: If the instrument is not found or a conflict occurs.

    """
    try:
        return await service.update(instrument_id, instrument_data)
    except InstrumentNotFoundError as e:
        detail = str(e)
        logger.warning(f"Update instrument failed, not found: {detail}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail) from e
    except InstrumentAlreadyExistError as e:
        detail = str(e)
        logger.warning(f"Update instrument failed, conflict: {detail}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from e


@router_resource.delete("/{instrument_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_instrument(
    instrument_id: int,
    service: Annotated[InstrumentService, Depends(get_instrument_service)],
) -> None:
    """Delete an instrument by its ID.

    Args:
        instrument_id: The ID of the instrument to delete.
        service: The instrument service dependency.

    Raises:
        HTTPException: If the instrument is not found.

    """
    try:
        await service.delete(instrument_id)
    except InstrumentNotFoundError as e:
        detail = str(e)
        logger.warning(f"Delete instrument failed: {detail}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail) from e


@router_collection.get("/")
async def list_instruments(
    service: Annotated[InstrumentService, Depends(get_instrument_service)],
) -> list[InstrumentRead]:
    """List all instruments.

    Args:
        service: The instrument service dependency.

    Returns:
        A list of all instruments.

    """
    return await service.list_all()
