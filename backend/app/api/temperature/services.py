"""Service layer for temperature operations."""

from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from .exceptions import TemperatureNotFoundError
from .models import Temperature
from .schemas import TemperatureCreate, TemperatureRead


class TemperatureService:
    """Service class for temperature-related database operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the service with a database session.

        Args:
            session: The asynchronous database session.

        """
        self.session = session
        logger.debug(f"TemperatureService initialized with async session: {session}")

    async def create(self, temperature_data: TemperatureCreate) -> Temperature:
        """Create a new temperature record.

        Args:
            temperature_data: The temperature data for creation.

        Returns:
            The created temperature record with its database ID.

        """
        try:
            # Create Temperature instance from input data
            temperature = Temperature.model_validate(temperature_data)

            # If timestamp is provided in the data, use it; otherwise, default_factory will be used
            if temperature_data.timestamp is not None:
                temperature.timestamp = temperature_data.timestamp

            self.session.add(temperature)
            await self.session.commit()
            await self.session.refresh(temperature)
            logger.info(f"Created temperature record: id={temperature.id}, device={temperature.device_id}, temp={temperature.temperature}°C, timestamp={temperature.timestamp}")
            return TemperatureRead.model_validate(temperature)
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Failed to create temperature record: {e}")
            raise

    async def get(self, temperature_id: int) -> TemperatureRead:
        """Retrieve a temperature record by its ID.

        Args:
            temperature_id: The ID of the temperature record to retrieve.

        Returns:
            The requested temperature record.

        Raises:
            TemperatureNotFoundError: If the temperature record is not found.

        """
        query = select(Temperature).where(Temperature.id == temperature_id)
        result = await self.session.execute(query)
        temperature = result.scalar_one_or_none()
        if not temperature:
            logger.warning(f"Instrument with ID {temperature_id} not found")
            raise TemperatureNotFoundError(temperature_id)
        logger.debug(f"Retrieved temperature with ID {temperature_id}")
        return TemperatureRead.model_validate(temperature)

    async def gets(self) -> list[TemperatureRead]:
        """Retrieve temperature records with optional filters.

        Returns:
            A list of temperature records matching the filters.

        """
        query = select(Temperature)
        result = await self.session.execute(query)
        temperatures = result.scalars().all()
        logger.debug(f"Retrieved {len(temperatures)} temperatures")
        return [TemperatureRead.model_validate(temperature) for temperature in temperatures]

    async def delete(self, temperature_id: int) -> None:
        """Delete a temperature record by its ID.

        Args:
            temperature_id: The ID of the temperature record to delete.

        Raises:
            TemperatureNotFoundError: If the temperature record is not found.

        """
        query = select(Temperature).where(Temperature.id == temperature_id)
        result = await self.session.execute(query)
        temperature = result.scalar_one_or_none()
        if not temperature:
            logger.warning(f"Temperature with ID {temperature_id} not found for deletion")
            raise TemperatureNotFoundError(temperature_id)

        await self.session.delete(temperature)
        await self.session.commit()
        logger.info(f"Deleted temperature with ID {temperature_id}")
