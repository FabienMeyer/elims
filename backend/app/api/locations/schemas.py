"""Schemas for the API locations module."""

from sqlmodel import Field, SQLModel

from .constants import AddressStr, CityStr, CountryStr, PostalCodeStr, StateStr


class LocationBase(SQLModel):
    """Base schema for a location with shared fields."""

    address: AddressStr = Field(index=True)
    postal_code: PostalCodeStr = Field(index=True)
    city: CityStr = Field(index=True)
    state: StateStr = Field(index=True)
    country: CountryStr = Field(index=True)


class LocationCreate(LocationBase):
    """Schema for creating a new location (API input)."""


class LocationUpdate(SQLModel):
    """Schema for updating an existing location (API input).

    All fields are optional to allow for partial updates.
    """

    address: AddressStr | None = Field(default=None)
    postal_code: PostalCodeStr | None = Field(default=None)
    city: CityStr | None = Field(default=None)
    state: StateStr | None = Field(default=None)
    country: CountryStr | None = Field(default=None)


class LocationRead(LocationBase):
    """Schema for reading a location (API output).

    Includes the database-managed id field.
    """

    id: int
