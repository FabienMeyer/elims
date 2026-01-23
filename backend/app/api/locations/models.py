"""Models for the API locations module."""

from sqlmodel import Field

from .schemas import LocationBase


class Location(LocationBase, table=True):
    """Represents a physical laboratory location in the database.

    This model is used for database interactions (creation, retrieval, updates)
    and corresponds to the 'location' table.

    Attributes:
        id: The primary key of the location in the database.
        address: The physical address of the location.
        city: The city where the location is situated.
        country: The country where the location is situated.

    """

    id: int | None = Field(default=None, primary_key=True)
