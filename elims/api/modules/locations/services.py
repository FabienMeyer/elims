"""Services for the API locations module."""

from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from elims.api.modules.locations.exceptions import (
    LocationAlreadyExistError,
    LocationNotFoundError,
)
from elims.api.modules.locations.models import Location
from elims.api.modules.locations.schemas import LocationCreate, LocationRead, LocationUpdate


class LocationService:
    """Encapsulates CRUD operations for the Location model."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the service with an async database session.

        Args:
            session: The asynchronous database session.

        """
        self.session = session
        logger.debug(f"LocationService initialized with async session: {session}")

    async def create(self, location_data: LocationCreate) -> LocationRead:
        """Create a new location in the database.

        Args:
            location_data: The data for the new location.

        Returns:
            The newly created location with its database ID.

        Raises:
            LocationAlreadyExistError: If a location with the same
                address, postal_code, and city already exists.

        """
        try:
            location = Location.model_validate(location_data)
            self.session.add(location)
            await self.session.commit()
            await self.session.refresh(location)
            logger.info(f"Created location with ID: {location.id}")
            return LocationRead.model_validate(location)
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Failed to create location: {e}")
            # Include address, postal_code, and city in error message to identify the composite key
            location_identifier = f"{location_data.address}, {location_data.postal_code}, {location_data.city}"
            raise LocationAlreadyExistError(location_identifier) from e

    async def get(self, location_id: int) -> LocationRead:
        """Retrieve a location by its ID.

        Args:
            location_id: The ID of the location to retrieve.

        Returns:
            The location with the specified ID.

        Raises:
            LocationNotFoundError: If no location with the given ID exists.

        """
        query = select(Location).where(Location.id == location_id)
        result = await self.session.exec(query)
        location = result.one_or_none()
        if not location:
            logger.warning(f"Location with ID {location_id} not found.")
            raise LocationNotFoundError(location_id)
        logger.debug(f"Retrieved location with ID: {location_id}")
        return LocationRead.model_validate(location)

    async def update(self, location_id: int, location_data: LocationUpdate) -> LocationRead:
        """Update an existing location in the database.

        Args:
            location_id: The ID of the location to update.
            location_data: The updated data for the location.

        Returns:
            The updated location.

        Raises:
            LocationNotFoundError: If no location with the given ID exists.
            LocationAlreadyExistError: If the update would result in a duplicate
                address, postal_code, and city combination.

        """
        query = select(Location).where(Location.id == location_id)
        result = await self.session.exec(query)
        location = result.one_or_none()
        if not location:
            logger.warning(f"Location with ID {location_id} not found for update.")
            raise LocationNotFoundError(location_id)

        update_data = location_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(location, key, value)

        try:
            self.session.add(location)
            await self.session.commit()
            await self.session.refresh(location)
            logger.info(f"Updated location with ID: {location_id}")
            return LocationRead.model_validate(location)
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Failed to update location with ID {location_id}: {e}")
            # Include composite key components in error message
            address = update_data.get("address", location.address)
            postal_code = update_data.get("postal_code", location.postal_code)
            city = update_data.get("city", location.city)
            location_identifier = f"{address}, {postal_code}, {city}"
            raise LocationAlreadyExistError(location_identifier) from e

    async def delete(self, location_id: int) -> None:
        """Delete a location from the database.

        Args:
            location_id: The ID of the location to delete.

        Raises:
            LocationNotFoundError: If no location with the given ID exists.

        """
        query = select(Location).where(Location.id == location_id)
        result = await self.session.exec(query)
        location = result.one_or_none()
        if not location:
            logger.warning(f"Location with ID {location_id} not found for deletion.")
            raise LocationNotFoundError(location_id)

        await self.session.delete(location)
        await self.session.commit()
        logger.info(f"Deleted location with ID: {location_id}")

    async def gets(self) -> list[LocationRead]:
        """Retrieve all locations from the database.

        Returns:
            A list of all locations.

        """
        query = select(Location)
        result = await self.session.exec(query)
        locations = result.all()
        logger.info(f"Retrieved {len(locations)} locations from the database.")
        return [LocationRead.model_validate(location) for location in locations]
