"""API routes for the API instruments module."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlmodel.ext.asyncio.session import AsyncSession

from elims.api.db import get_session
from elims.api.modules.instruments.exceptions import (
    InstrumentAlreadyExistsError,
    InstrumentNotFoundError,
)
from elims.api.modules.instruments.schemas import (
    InstrumentCreate,
    InstrumentPublic,
    InstrumentUpdate,
)
from elims.api.modules.instruments.services import InstrumentService

router = APIRouter(prefix="/instruments", tags=["instruments"])


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


async def create_instrument(
    instrument: InstrumentCreate,
    service: Annotated[InstrumentService, Depends(get_instrument_service)],
) -> InstrumentPublic:
    """Create a new instrument.

    Args:
        instrument: The instrument data for creation.
        service: The instrument service dependency.

    Returns:
        The created instrument.

    Raises:
        HTTPException: If an instrument with the same serial number already exists.

    """
    try:
        db_instrument = await service.create(instrument)
    except InstrumentAlreadyExistsError as e:
        detail = str(e)
        logger.warning(f"Creation failed due to conflict: {detail}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from e
    else:
        return InstrumentPublic.model_validate(db_instrument)


async def read_all_instruments(
    service: Annotated[InstrumentService, Depends(get_instrument_service)],
) -> list[InstrumentPublic]:
    """Retrieve a list of all instruments.

    Args:
        service: The instrument service dependency.

    Returns:
        A list of all instruments.

    """
    instruments = await service.get_all()
    return [InstrumentPublic.model_validate(i) for i in instruments]


async def read_instrument(instrument_id: int, service: Annotated[InstrumentService, Depends(get_instrument_service)]) -> InstrumentPublic:
    """Retrieve a single instrument by its unique ID.

    Args:
        instrument_id: The ID of the instrument to retrieve.
        service: The instrument service dependency.

    Returns:
        The requested instrument.

    Raises:
        HTTPException: If the instrument is not found.

    """
    instrument = await service.get_by_id(instrument_id)
    if instrument is None:
        logger.warning(f"Read failed: Instrument ID {instrument_id} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrument with ID {instrument_id} not found",
        )
    return InstrumentPublic.model_validate(instrument)


async def update_instrument(
    instrument_id: int,
    instrument: InstrumentUpdate,
    service: Annotated[InstrumentService, Depends(get_instrument_service)],
) -> InstrumentPublic:
    """Update an existing instrument.

    Partial updates are allowed.

    Args:
        instrument_id: The ID of the instrument to update.
        instrument: The instrument data for the update.
        service: The instrument service dependency.

    Returns:
        The updated instrument.

    Raises:
        HTTPException: If the instrument is not found or a conflict occurs.

    """
    try:
        updated_instrument = await service.update(instrument_id, instrument)
    except InstrumentNotFoundError as e:
        detail = str(e)
        logger.warning(f"Update failed: {detail}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail) from e
    except InstrumentAlreadyExistsError as e:
        detail = str(e)
        logger.warning(f"Update failed due to conflict: {detail}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from e
    else:
        return InstrumentPublic.model_validate(updated_instrument)


async def delete_instrument(instrument_id: int, service: Annotated[InstrumentService, Depends(get_instrument_service)]) -> None:
    """Delete an instrument by ID.

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
        logger.warning(f"Deletion failed: {detail}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail) from e


router.add_api_route("/", create_instrument, methods=["POST"], status_code=status.HTTP_201_CREATED)
router.add_api_route("/", read_all_instruments, methods=["GET"])
router.add_api_route("/{instrument_id}", read_instrument, methods=["GET"])
router.add_api_route("/{instrument_id}", update_instrument, methods=["PATCH"])
router.add_api_route("/{instrument_id}", delete_instrument, methods=["DELETE"], status_code=status.HTTP_204_NO_CONTENT)
