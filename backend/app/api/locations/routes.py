"""API routes for the API locations module."""

from typing import Annotated

from app.api.locations.exceptions import (
    LocationAlreadyExistError,
    LocationNotFoundError,
)
from app.api.locations.schemas import LocationCreate, LocationRead, LocationUpdate
from app.api.locations.services import LocationService
from app.db import get_session
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlmodel.ext.asyncio.session import AsyncSession

router_collection: APIRouter = APIRouter(prefix="/locations", tags=["locations"])
router_resource: APIRouter = APIRouter(prefix="/location", tags=["location"])


async def get_location_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LocationService:
    """Instantiate and provide the LocationService.

    Args:
        session: The asynchronous database session.

    Returns:
        An instance of LocationService.

    """
    return LocationService(session=session)


@router_resource.post("/", status_code=status.HTTP_201_CREATED)
async def create_location(
    location_data: LocationCreate,
    service: Annotated[LocationService, Depends(get_location_service)],
) -> LocationRead:
    """Create a new location.

    Args:
        location_data: The location data for creation.
        service: The location service dependency.

    Returns:
        The created location with its database ID.

    Raises:
        HTTPException: If a location with the same name already exists.

    """
    try:
        return await service.create(location_data)
    except LocationAlreadyExistError as e:
        detail = str(e)
        logger.warning(f"Create location failed: {detail}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from e


@router_resource.get("/{location_id}")
async def get_location(
    location_id: int,
    service: Annotated[LocationService, Depends(get_location_service)],
) -> LocationRead:
    """Retrieve a location by its ID.

    Args:
        location_id: The ID of the location to retrieve.
        service: The location service dependency.

    Returns:
        The requested location.

    Raises:
        HTTPException: If the location is not found.

    """
    try:
        return await service.get(location_id)
    except LocationNotFoundError as e:
        detail = str(e)
        logger.warning(f"Get location failed: {detail}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail) from e


@router_resource.patch("/{location_id}")
async def update_location(
    location_id: int,
    location_data: LocationUpdate,
    service: Annotated[LocationService, Depends(get_location_service)],
) -> LocationRead:
    """Update an existing location.

    Args:
        location_id: The ID of the location to update.
        location_data: The updated location data.
        service: The location service dependency.

    Returns:
        The updated location.

    Raises:
        HTTPException: If the location is not found or if a location
            with the same name already exists.

    """
    try:
        return await service.update(location_id, location_data)
    except LocationNotFoundError as e:
        detail = str(e)
        logger.warning(f"Update location failed: {detail}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail) from e
    except LocationAlreadyExistError as e:
        detail = str(e)
        logger.warning(f"Update location failed due to conflict: {detail}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from e


@router_resource.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: int,
    service: Annotated[LocationService, Depends(get_location_service)],
) -> None:
    """Delete a location by its ID.

    Args:
        location_id: The ID of the location to delete.
        service: The location service dependency.

    Raises:
        HTTPException: If the location is not found.

    """
    try:
        await service.delete(location_id)
    except LocationNotFoundError as e:
        detail = str(e)
        logger.warning(f"Delete location failed: {detail}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail) from e


@router_collection.get("/")
async def get_locations(
    service: Annotated[LocationService, Depends(get_location_service)],
) -> list[LocationRead]:
    """Retrieve all locations.

    Args:
        service: The location service dependency.

    Returns:
        A list of all locations.

    """
    return await service.gets()
