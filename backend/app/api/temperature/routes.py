"""API routes for the temperature module."""

from typing import Annotated

from app.db import get_session
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlmodel.ext.asyncio.session import AsyncSession

from .exceptions import TemperatureNotFoundError
from .schemas import TemperatureCreate, TemperatureRead
from .services import TemperatureService

router_collection: APIRouter = APIRouter(prefix="/temperatures", tags=["temperatures"])
router_resource: APIRouter = APIRouter(prefix="/temperature", tags=["temperature"])


async def get_temperature_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TemperatureService:
    """Instantiate and provide the TemperatureService.

    Args:
        session: The asynchronous database session.

    Returns:
        An instance of TemperatureService.

    """
    return TemperatureService(session=session)


@router_resource.post("/", status_code=status.HTTP_201_CREATED)
async def create_temperature(
    temperature_data: TemperatureCreate,
    service: Annotated[TemperatureService, Depends(get_temperature_service)],
) -> TemperatureRead:
    """Create a new temperature record.

    Args:
        temperature_data: The temperature data for creation.
        service: The temperature service dependency.

    Returns:
        The created temperature record with its database ID and timestamp.

    """
    temperature = await service.create(temperature_data)
    return TemperatureRead.model_validate(temperature)


@router_resource.get("/{temperature_id}")
async def get_temperature(
    temperature_id: int,
    service: Annotated[TemperatureService, Depends(get_temperature_service)],
) -> TemperatureRead:
    """Retrieve a temperature record by its ID.

    Args:
        temperature_id: The ID of the temperature record to retrieve.
        service: The temperature service dependency.

    Returns:
        The requested temperature record.

    Raises:
        HTTPException: If the temperature record is not found.

    """
    try:
        return await service.get(temperature_id)
    except TemperatureNotFoundError as e:
        detail = str(e)
        logger.warning(f"Get temperature failed: {detail}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail) from e


@router_resource.delete("/{temperature_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_temperature(
    temperature_id: int,
    service: Annotated[TemperatureService, Depends(get_temperature_service)],
) -> None:
    """Delete a temperature record by its ID.

    Args:
        temperature_id: The ID of the temperature record to delete.
        service: The temperature service dependency.

    Raises:
        HTTPException: If the temperature record is not found.

    """
    try:
        await service.delete(temperature_id)
    except TemperatureNotFoundError as e:
        detail = str(e)
        logger.warning(f"Delete temperature failed: {detail}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail) from e


@router_collection.get("/")
async def gets_temperatures(
    service: Annotated[TemperatureService, Depends(get_temperature_service)],
) -> list[TemperatureRead]:
    """List all temperature records."""
    return await service.gets()
