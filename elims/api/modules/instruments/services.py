"""Services for the API instruments module."""

from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from elims.api.modules.instruments.exceptions import (
    InstrumentAlreadyExistsError,
    InstrumentNotFoundError,
)
from elims.api.modules.instruments.models import Instrument
from elims.api.modules.instruments.schemas import InstrumentCreate, InstrumentUpdate


class InstrumentService:
    """Encapsulates CRUD operations for the Instrument model."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the service with an async database session.

        Args:
            session: The asynchronous database session.

        """
        self.session = session
        logger.debug(f"InstrumentService initialized with async session: {session}")

    async def create(self, instrument_create: InstrumentCreate) -> Instrument:
        """Create a new instrument in the database.

        Args:
            instrument_create: The data for the new instrument.

        Returns:
            The newly created instrument.

        Raises:
            InstrumentAlreadyExistsException: If an instrument with the same
                serial number already exists.

        """
        db_instrument = Instrument.model_validate(instrument_create)
        try:
            self.session.add(db_instrument)
            await self.session.commit()
            await self.session.refresh(db_instrument)
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"IntegrityError creating instrument: {e}")
            raise InstrumentAlreadyExistsError(db_instrument.serial_number) from e
        else:
            logger.info(f"Created instrument ID: {db_instrument.id}")
            return db_instrument

    async def get_by_id(self, instrument_id: int) -> Instrument | None:
        """Read a single instrument by ID.

        Args:
            instrument_id: The ID of the instrument to retrieve.

        Returns:
            The instrument if found, otherwise None.

        """
        statement = select(Instrument).where(Instrument.id == instrument_id)
        result = await self.session.exec(statement)
        instrument = result.first()
        if not instrument:
            logger.warning(f"Attempted to read non-existent instrument ID: {instrument_id}")
            return None
        return instrument

    async def get_all(self) -> list[Instrument]:
        """Retrieve all instruments.

        Returns:
            A list of all instruments.

        """
        logger.debug("Retrieving all instruments asynchronously.")
        result = await self.session.exec(select(Instrument))
        return list(result.all())

    async def update(self, instrument_id: int, instrument_update: InstrumentUpdate) -> Instrument:
        """Update an existing instrument.

        Args:
            instrument_id: The ID of the instrument to update.
            instrument_update: The data to update the instrument with.

        Returns:
            The updated instrument.

        Raises:
            InstrumentNotFoundException: If the instrument is not found.
            InstrumentAlreadyExistsException: If the update would cause a
                duplicate serial number.

        """
        db_instrument = await self.get_by_id(instrument_id)
        if not db_instrument:
            raise InstrumentNotFoundError(instrument_id)

        update_data = instrument_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_instrument, key, value)

        try:
            self.session.add(db_instrument)
            await self.session.commit()
            await self.session.refresh(db_instrument)
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"IntegrityError updating instrument ID {instrument_id}: {e}")
            serial_number = update_data.get("serial_number") or db_instrument.serial_number
            raise InstrumentAlreadyExistsError(serial_number) from e
        else:
            logger.info(f"Updated instrument ID: {db_instrument.id}")
            return db_instrument

    async def delete(self, instrument_id: int) -> None:
        """Delete an instrument by ID.

        Args:
            instrument_id: The ID of the instrument to delete.

        Raises:
            InstrumentNotFoundException: If the instrument is not found.

        """
        instrument = await self.get_by_id(instrument_id)
        if not instrument:
            raise InstrumentNotFoundError(instrument_id)

        await self.session.delete(instrument)
        await self.session.commit()
        logger.warning(f"Deleted instrument ID: {instrument_id}")
