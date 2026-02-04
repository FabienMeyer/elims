"""Constants for the temperature module."""

from typing import Annotated

from pydantic import Field

DeviceIdStr = Annotated[str, Field(min_length=1, max_length=100)]
TemperatureValue = Annotated[float, Field(ge=-273.15, le=1000.0)]
