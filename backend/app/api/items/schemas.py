"""Public item contracts."""

from sqlmodel import Field, SQLModel


class ItemCreate(SQLModel):
    """Payload used to create an item."""

    name: str = Field(min_length=1, max_length=120)


class ItemRead(ItemCreate):
    """Item returned by the API."""

    id: int
