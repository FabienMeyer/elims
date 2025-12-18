"""Schemas for the API users module."""

from pydantic import Field, field_validator
from sqlmodel import SQLModel

from .constants import EmailStr, UsernameStr, UserRole


class UserBase(SQLModel):
    """Base schema for a user with shared fields and validation."""

    username: UsernameStr = Field()
    email: EmailStr = Field()
    role: UserRole = Field(default=UserRole.admin, description="Role of the user in the system")
    hashed_password: str

    @field_validator("username", mode="before")
    @classmethod
    def validate_username(cls, value: str) -> UsernameStr:
        """Validate and convert the username to a UsernameStr.

        Args:
            value: The input username string.

        Returns:
            The validated UsernameStr.

        """
        return UsernameStr(value)


class UserCreate(SQLModel):
    """Schema for creating a new user (API input).

    Note: This accepts a plain password which will be hashed before storage.
    """

    username: UsernameStr = Field()
    email: EmailStr = Field()
    role: UserRole | None = Field(default=None)
    password: str = Field(..., min_length=8, description="Plain password (min 8 characters)")


class UserUpdate(SQLModel):
    """Schema for updating an existing user (API input).

    All fields are optional to allow for partial updates.
    """

    username: UsernameStr | None = Field(default=None)
    email: EmailStr | None = Field(default=None)
    role: UserRole | None = Field(default=None)
    password: str | None = Field(default=None, min_length=8, description="Plain password (min 8 characters)")


class UserRead(UserBase):
    """Schema for reading a user (API output).

    Includes the database-managed id field.
    """

    id: int
