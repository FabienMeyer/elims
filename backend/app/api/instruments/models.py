"""Models for the API instruments module."""

from sqlmodel import Field

from .constants import SerialNumberStr
from .schemas import InstrumentBase


class Instrument(InstrumentBase, table=True):
    """Represents an instrument in the database.

    This model is used for database interactions (creation, retrieval, updates)
    and corresponds to the 'instrument' table.

    Attributes:
        id: The primary key of the instrument in the database.
        serial_number: The unique serial number of the instrument.

    """

    id: int | None = Field(default=None, primary_key=True)
    serial_number: SerialNumberStr = Field(index=True, unique=True)
