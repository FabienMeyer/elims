"""Persistent item model."""

from sqlmodel import Field, SQLModel


class Item(SQLModel, table=True):
    """Minimal example entity."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=120, index=True)
