"""Schemas for the API instruments module."""

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from .constants import InstrumentBrand, InstrumentType, ModelStr, SerialNumberStr
from .exceptions import InstrumentBrandError, InstrumentTypeError


class InstrumentBase(SQLModel):
    """Base schema for an instrument with shared fields and validation."""

    brand: InstrumentBrand = Field(index=True)
    type: InstrumentType = Field(index=True)
    model: ModelStr = Field(index=True)
    serial_number: SerialNumberStr = Field(index=True)

    @field_validator("brand", mode="before")
    @classmethod
    def validate_brand(cls, value: str | InstrumentBrand) -> InstrumentBrand:
        """Validate and convert the brand value to an InstrumentBrand enum.

        Args:
            value: The input value, which can be a string or InstrumentBrand.

        Returns:
            The corresponding InstrumentBrand enum member.

        Raises:
            InstrumentBrandError: If the value is not a valid brand.

        """
        if isinstance(value, InstrumentBrand):
            return value
        try:
            return InstrumentBrand(value)
        except ValueError as e:
            raise InstrumentBrandError(str(value)) from e

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, value: str | InstrumentType) -> InstrumentType:
        """Validate and convert the type value to an InstrumentType enum.

        Args:
            value: The input value, which can be a string or InstrumentType.

        Returns:
            The corresponding InstrumentType enum member.

        Raises:
            InstrumentTypeError: If the value is not a valid type.

        """
        if isinstance(value, InstrumentType):
            return value
        try:
            return InstrumentType(value)
        except ValueError as e:
            raise InstrumentTypeError(str(value)) from e


class InstrumentCreate(InstrumentBase):
    """Schema for creating a new instrument (API input)."""


class InstrumentUpdate(SQLModel):
    """Schema for updating an existing instrument (API input).

    All fields are optional to allow for partial updates.
    """

    brand: InstrumentBrand | None = Field(default=None)
    type: InstrumentType | None = Field(default=None)
    model: ModelStr | None = Field(default=None)
    serial_number: SerialNumberStr | None = Field(default=None)

    @field_validator("brand", mode="before")
    @classmethod
    def validate_brand(cls, value: str | InstrumentBrand | None) -> InstrumentBrand | None:
        """Validate and convert the brand value to an InstrumentBrand enum.

        Args:
            value: The input value, which can be a string or InstrumentBrand.

        Returns:
            The corresponding InstrumentBrand enum member.

        Raises:
            InstrumentBrandError: If the value is not a valid brand.

        """
        if isinstance(value, InstrumentBrand) or value is None:
            return value
        try:
            return InstrumentBrand(value)
        except ValueError as e:
            raise InstrumentBrandError(str(value)) from e

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, value: str | InstrumentType | None) -> InstrumentType | None:
        """Validate and convert the type value to an InstrumentType enum.

        Args:
            value: The input value, which can be a string or InstrumentType.

        Returns:
            The corresponding InstrumentType enum member.

        Raises:
            InstrumentTypeError: If the value is not a valid type.

        """
        if isinstance(value, InstrumentType) or value is None:
            return value
        try:
            return InstrumentType(value)
        except ValueError as e:
            raise InstrumentTypeError(str(value)) from e


class InstrumentRead(InstrumentBase):
    """Schema for representing a read-only instrument (API output).

    Includes the database-generated ID.
    """

    id: int
