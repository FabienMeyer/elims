"""Models for the temperature module."""

from datetime import datetime

from sqlmodel import Field

from .schemas import TemperatureBase


class Temperature(TemperatureBase, table=True):
    """Represents a temperature reading in the database.

    This model is used for database interactions (creation, retrieval, updates)
    and corresponds to the 'temperature' table.

    Attributes:
        id: The primary key of the temperature record in the database.
        device_id: The unique identifier of the device reporting the temperature.
        temperature: The temperature value in Celsius.
        timestamp: The timestamp when the temperature was recorded (from sensor or current time).

    """

    __tablename__ = "temperature"

    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
