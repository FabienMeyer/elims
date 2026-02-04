"""Schemas for the temperature module."""

from datetime import datetime

from sqlmodel import Field, SQLModel

from .constants import DeviceIdStr, TemperatureValue


class TemperatureBase(SQLModel):
    """Base schema for temperature data with shared fields."""

    device_id: DeviceIdStr = Field(index=True, description="Unique identifier for the device")
    temperature: TemperatureValue = Field(description="Temperature value in Celsius")
    timestamp: datetime = Field(description="Timestamp when the temperature was recorded")


class TemperatureCreate(TemperatureBase):
    """Schema for creating a new temperature record (API input).

    Timestamp is required and should be provided by the sensor.
    """


class TemperatureRead(TemperatureBase):
    """Schema for reading a temperature record (API output).

    Includes the database-managed id field.
    """

    id: int
    timestamp: datetime
