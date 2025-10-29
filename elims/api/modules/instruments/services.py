"""Services for the API instruments module."""

from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from elims.api.modules.instruments.exceptions import (
    InstrumentAlreadyExistError,
    InstrumentNotFoundError,
)
from elims.api.modules.instruments.models import Instrument
from elims.api.modules.instruments.schemas import (
    InstrumentCreate,
    InstrumentPublic,
    InstrumentUpdate,
)


class InstrumentService:
    """Encapsulates CRUD operations for the Instrument model."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the service with an async database session.

        Args:
            session: The asynchronous database session.

        """
        self.session = session
        logger.debug(f"InstrumentService initialized with async session: {session}")

    async def create(self, instrument_data: InstrumentCreate) -> InstrumentPublic:
        """Create a new instrument in the database.

        Args:
            instrument_data: The data for the new instrument.

        Returns:
            The newly created instrument with its database ID.

        Raises:
            InstrumentAlreadyExistError: If an instrument with the same
                serial number already exists.

        """
        try:
            instrument = Instrument.model_validate(instrument_data)
            self.session.add(instrument)
            await self.session.commit()
            await self.session.refresh(instrument)
            logger.info(f"Created instrument with serial number: {instrument.serial_number}")
            return InstrumentPublic.model_validate(instrument)
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Failed to create instrument: {e}")
            raise InstrumentAlreadyExistError(instrument_data.serial_number) from e

    async def get(self, instrument_id: int) -> InstrumentPublic:
        """Retrieve an instrument by its ID.

        Args:
            instrument_id: The ID of the instrument to retrieve.

        Returns:
            The instrument if found.

        Raises:
            InstrumentNotFoundError: If the instrument is not found.

        """
        query = select(Instrument).where(Instrument.id == instrument_id)
        result = await self.session.exec(query)
        instrument = result.one_or_none()
        if not instrument:
            logger.warning(f"Instrument with ID {instrument_id} not found")
            raise InstrumentNotFoundError(instrument_id)
        logger.debug(f"Retrieved instrument with ID {instrument_id}")
        return InstrumentPublic.model_validate(instrument)

    async def update(self, instrument_id: int, instrument_data: InstrumentUpdate) -> InstrumentPublic:
        """Update an existing instrument.

        Args:
            instrument_id: The ID of the instrument to update.
            instrument_data: The new data for the instrument (partial updates allowed).

        Returns:
            The updated instrument.

        Raises:
            InstrumentNotFoundError: If the instrument is not found.
            InstrumentAlreadyExistError: If the serial number is changed to one
                that already exists.

        """
        query = select(Instrument).where(Instrument.id == instrument_id)
        result = await self.session.exec(query)
        db_instrument = result.one_or_none()
        if not db_instrument:
            logger.warning(f"Instrument with ID {instrument_id} not found for update")
            raise InstrumentNotFoundError(instrument_id)

        # Update only the fields that were provided
        update_data = instrument_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_instrument, key, value)

        try:
            self.session.add(db_instrument)
            await self.session.commit()
            await self.session.refresh(db_instrument)
            logger.info(f"Updated instrument with ID {instrument_id}")
            return InstrumentPublic.model_validate(db_instrument)
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Failed to update instrument with ID {instrument_id}: {e}")
            raise InstrumentAlreadyExistError(db_instrument.serial_number) from e

    async def delete(self, instrument_id: int) -> None:
        """Delete an instrument by its ID.

        Args:
            instrument_id: The ID of the instrument to delete.

        Raises:
            InstrumentNotFoundError: If the instrument is not found.

        """
        query = select(Instrument).where(Instrument.id == instrument_id)
        result = await self.session.exec(query)
        instrument = result.one_or_none()
        if not instrument:
            logger.warning(f"Instrument with ID {instrument_id} not found for deletion")
            raise InstrumentNotFoundError(instrument_id)

        await self.session.delete(instrument)
        await self.session.commit()
        logger.info(f"Deleted instrument with ID {instrument_id}")

    async def list_all(self) -> list[InstrumentPublic]:
        """Retrieve all instruments from the database.

        Returns:
            A list of all instruments.

        """
        query = select(Instrument)
        result = await self.session.exec(query)
        instruments = result.all()
        logger.debug(f"Retrieved {len(instruments)} instruments")
        return [InstrumentPublic.model_validate(instrument) for instrument in instruments]
