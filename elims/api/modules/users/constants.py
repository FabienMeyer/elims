"""Constants for the API users module."""

from enum import StrEnum
from typing import Annotated

from pydantic import Field


class UserRole(StrEnum):
    """Enumeration of user roles within the system."""

    admin = "admin"
    user = "user"
    guest = "guest"


UsernameStr = Annotated[str, Field(min_length=2, max_length=50, pattern=r"^[A-Za-z0-9]+$")]
"""Type alias for username strings with validation."""

EmailStr = Annotated[str, Field(min_length=5, max_length=100, pattern=r"^[\w\.-]+@[\w\.-]+\.\w{2,}$")]
"""Type alias for email strings with validation."""
