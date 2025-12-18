"""Models for the API users module."""

from sqlmodel import Field

from .constants import EmailStr, UsernameStr, UserRole
from .schemas import UserBase


class User(UserBase, table=True):
    """Represents a user in the database.

    This model is used for database interactions (creation, retrieval, updates)
    and corresponds to the 'user' table.

    Attributes:
        id: The primary key of the user in the database.
        username: The unique username of the user.
        email: The email address of the user.
        role: The role of the user in the system.

    """

    id: int | None = Field(default=None, primary_key=True)
    username: UsernameStr = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    role: UserRole = Field(index=True, unique=True)
