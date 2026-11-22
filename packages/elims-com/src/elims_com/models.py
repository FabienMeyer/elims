"""Communication models."""

from datetime import datetime
from uuid import UUID, uuid4

from elims_utils import utc_now
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Transport-neutral message exchanged between components."""

    id: UUID = Field(default_factory=uuid4)
    subject: str = Field(min_length=1)
    payload: dict[str, object] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
