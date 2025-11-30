"""Constants for the API locations module."""

from typing import Annotated

from pydantic import Field

AddressStr = Annotated[str, Field(min_length=2, max_length=200, pattern=r"^[A-Za-z0-9\s,.'-]+$")]
"""Type alias for address strings with validation."""

PostalCodeStr = Annotated[str, Field(min_length=2, max_length=10, pattern=r"^[0-9-]+$")]
"""Type alias for postal code strings with validation."""

CityStr = Annotated[str, Field(min_length=2, max_length=85, pattern=r"^[A-Za-z\s'-]+$")]
"""Type alias for city strings with validation."""

StateStr = Annotated[str, Field(min_length=2, max_length=30, pattern=r"^[A-Za-zÀ-ÿ\s'-]+$")]
"""Type alias for state strings with validation."""

CountryStr = Annotated[str, Field(min_length=2, max_length=31, pattern=r"^[A-Za-z\s'-]+$")]
"""Type alias for country strings with validation."""
