"""Tests schemas for the API locations module.

This file contains tests for location API schemas.
"""

import pytest
from pydantic import ValidationError

from elims.modules.locations import schemas


class TestLocationBaseSchemas:
    """Tests for the LocationBase API schema."""

    def test_schemas_module_exists(self) -> None:
        """Test that schemas module can be imported."""
        assert schemas is not None
        assert hasattr(schemas, "LocationBase")

    @pytest.mark.parametrize(
        "location",
        [
            {
                "address": "123 Main Street",
                "postal_code": "75001",
                "city": "Paris",
                "state": "Île-de-France",
                "country": "France",
            },
        ],
    )
    def test_location_base_create(self, location: dict[str, str]) -> None:
        """Test that LocationBase schema can be instantiated."""
        location_schema = schemas.LocationBase.model_validate(location)

        assert location_schema.address == location["address"]
        assert location_schema.postal_code == location["postal_code"]
        assert location_schema.city == location["city"]
        assert location_schema.state == location["state"]
        assert location_schema.country == location["country"]

    @pytest.mark.parametrize(
        "location",
        [
            {
                "address": "123 Main Street",
                "postal_code": "75001",
                "city": "Paris",
                "state": "Île-de-France",
                "country": "France",
            },
        ],
    )
    @pytest.mark.parametrize("invalid_address", ["1", "123@Main", "123/Main"])
    def test_location_invalid_address(self, location: dict[str, str], invalid_address: str) -> None:
        """Test that address with invalid characters are rejected."""
        location["address"] = invalid_address
        with pytest.raises(ValidationError, match="String should"):
            schemas.LocationBase.model_validate(location)

    @pytest.mark.parametrize(
        "location",
        [
            {
                "address": "123 Main Street",
                "postal_code": "75001",
                "city": "Paris",
                "state": "Île-de-France",
                "country": "France",
            },
        ],
    )
    @pytest.mark.parametrize("invalid_postal_code", ["7", "75@01", "75/01"])
    def test_location_invalid_postal_code(self, location: dict[str, str], invalid_postal_code: str) -> None:
        """Test that postal codes with invalid characters are rejected."""
        location["postal_code"] = invalid_postal_code
        with pytest.raises(ValidationError, match="String should"):
            schemas.LocationBase.model_validate(location)

    @pytest.mark.parametrize(
        "location",
        [
            {
                "address": "123 Main Street",
                "postal_code": "75001",
                "city": "Paris",
                "state": "Île-de-France",
                "country": "France",
            },
        ],
    )
    @pytest.mark.parametrize("invalid_city", ["P", "Paris123", "Paris@"])
    def test_location_invalid_city(self, location: dict[str, str], invalid_city: str) -> None:
        """Test that city with invalid characters are rejected."""
        location["city"] = invalid_city
        with pytest.raises(ValidationError, match="String should"):
            schemas.LocationBase.model_validate(location)

    @pytest.mark.parametrize(
        "location",
        [
            {
                "address": "123 Main Street",
                "postal_code": "75001",
                "city": "Paris",
                "state": "Île-de-France",
                "country": "France",
            },
        ],
    )
    @pytest.mark.parametrize("invalid_state", ["F", "State123", "State@"])
    def test_location_invalid_state(self, location: dict[str, str], invalid_state: str) -> None:
        """Test that state with invalid characters are rejected."""
        location["state"] = invalid_state
        with pytest.raises(ValidationError, match="String should"):
            schemas.LocationBase.model_validate(location)

    @pytest.mark.parametrize(
        "location",
        [
            {
                "address": "123 Main Street",
                "postal_code": "75001",
                "city": "Paris",
                "state": "Île-de-France",
                "country": "France",
            },
        ],
    )
    @pytest.mark.parametrize("invalid_country", ["F", "France123", "France@"])
    def test_location_invalid_country(self, location: dict[str, str], invalid_country: str) -> None:
        """Test that country with invalid characters are rejected."""
        location["country"] = invalid_country
        with pytest.raises(ValidationError, match="String should"):
            schemas.LocationBase.model_validate(location)

    @pytest.mark.parametrize(
        "location",
        [
            {
                "address": "123 Main Street",
                "postal_code": "75001",
                "city": "Paris",
                "state": "Île-de-France",
                "country": "France",
            },
        ],
    )
    def test_location_equality(self, location: dict[str, str]) -> None:
        """Test that two locations with the same data are equal."""
        location1 = schemas.LocationBase.model_validate(location)
        location2 = schemas.LocationBase.model_validate(location)
        assert location1 == location2

    @pytest.mark.parametrize(
        "location",
        [
            {
                "address": "123 Main Street",
                "postal_code": "75001",
                "city": "Paris",
                "state": "Île-de-France",
                "country": "France",
            },
        ],
    )
    def test_location_inequality(self, location: dict[str, str]) -> None:
        """Test that locations with different data are not equal."""
        location1 = schemas.LocationBase.model_validate(location)
        location["city"] = "Lyon"
        location2 = schemas.LocationBase.model_validate(location)
        assert location1 != location2


class TestLocationCreateSchemas:
    """Tests for the LocationCreate API schema."""

    def test_schemas_module_exists(self) -> None:
        """Test that schemas module can be imported."""
        assert schemas is not None
        assert hasattr(schemas, "LocationCreate")


class TestLocationUpdateSchemas:
    """Tests for the LocationUpdate API schema."""

    def test_schemas_module_exists(self) -> None:
        """Test that schemas module can be imported."""
        assert schemas is not None
        assert hasattr(schemas, "LocationUpdate")

    @pytest.mark.parametrize(
        "location",
        [
            {
                "address": "123 Main Street",
                "postal_code": "75001",
                "city": "Paris",
                "state": "Île-de-France",
                "country": "France",
            },
        ],
    )
    def test_location_update_create(self, location: dict[str, str]) -> None:
        """Test that LocationUpdate schema can be instantiated."""
        location_schema = schemas.LocationUpdate.model_validate(location)
        assert location_schema.address == location["address"]
        assert location_schema.postal_code == location["postal_code"]
        assert location_schema.city == location["city"]
        assert location_schema.state == location["state"]
        assert location_schema.country == location["country"]

    @pytest.mark.parametrize(
        "location",
        [
            {
                "address": "123 Main Street",
                "postal_code": "75001",
                "city": "Paris",
                "state": "Île-de-France",
                "country": "France",
            },
        ],
    )
    @pytest.mark.parametrize("invalid_address", ["1", "123@Main", "123/Main"])
    def test_location_update_invalid_address(self, location: dict[str, str], invalid_address: str) -> None:
        """Test that address with invalid characters are rejected."""
        location["address"] = invalid_address
        with pytest.raises(ValidationError, match="String should"):
            schemas.LocationUpdate.model_validate(location)

    @pytest.mark.parametrize(
        "location",
        [
            {
                "address": "123 Main Street",
                "postal_code": "75001",
                "city": "Paris",
                "state": "Île-de-France",
                "country": "France",
            },
        ],
    )
    @pytest.mark.parametrize("invalid_postal_code", ["7", "75@01", "75/01"])
    def test_location_update_invalid_postal_code(self, location: dict[str, str], invalid_postal_code: str) -> None:
        """Test that postal code with invalid characters are rejected."""
        location["postal_code"] = invalid_postal_code
        with pytest.raises(ValidationError, match="String should"):
            schemas.LocationUpdate.model_validate(location)

    @pytest.mark.parametrize(
        "location",
        [
            {
                "address": "123 Main Street",
                "postal_code": "75001",
                "city": "Paris",
                "state": "Île-de-France",
                "country": "France",
            },
        ],
    )
    @pytest.mark.parametrize("invalid_city", ["P", "Paris123", "Paris@"])
    def test_location_update_invalid_city(self, location: dict[str, str], invalid_city: str) -> None:
        """Test that city with invalid characters are rejected."""
        location["city"] = invalid_city
        with pytest.raises(ValidationError, match="String should"):
            schemas.LocationUpdate.model_validate(location)

    @pytest.mark.parametrize(
        "location",
        [
            {
                "address": "123 Main Street",
                "postal_code": "75001",
                "city": "Paris",
                "state": "Île-de-France",
                "country": "France",
            },
        ],
    )
    @pytest.mark.parametrize("invalid_state", ["F", "State123", "State@"])
    def test_location_update_invalid_state(self, location: dict[str, str], invalid_state: str) -> None:
        """Test that state with invalid characters are rejected."""
        location["state"] = invalid_state
        with pytest.raises(ValidationError, match="String should"):
            schemas.LocationUpdate.model_validate(location)

    @pytest.mark.parametrize(
        "location",
        [
            {
                "address": "123 Main Street",
                "postal_code": "75001",
                "city": "Paris",
                "state": "Île-de-France",
                "country": "France",
            },
        ],
    )
    @pytest.mark.parametrize("invalid_country", ["F", "France123", "France@"])
    def test_location_update_invalid_country(self, location: dict[str, str], invalid_country: str) -> None:
        """Test that country with invalid characters are rejected."""
        location["country"] = invalid_country
        with pytest.raises(ValidationError, match="String should"):
            schemas.LocationUpdate.model_validate(location)

    @pytest.mark.parametrize(
        "location",
        [
            {
                "address": "123 Main Street",
                "postal_code": "75001",
                "city": "Paris",
                "state": "Île-de-France",
                "country": "France",
            },
        ],
    )
    def test_location_update_equality(self, location: dict[str, str]) -> None:
        """Test that two location updates with the same data are equal."""
        location1 = schemas.LocationUpdate.model_validate(location)
        location2 = schemas.LocationUpdate.model_validate(location)
        assert location1 == location2

    @pytest.mark.parametrize(
        "location",
        [
            {
                "address": "123 Main Street",
                "postal_code": "75001",
                "city": "Paris",
                "state": "Île-de-France",
                "country": "France",
            },
        ],
    )
    def test_location_update_inequality(self, location: dict[str, str]) -> None:
        """Test that location updates with different data are not equal."""
        location1 = schemas.LocationUpdate.model_validate(location)
        location["city"] = "Lyon"
        location2 = schemas.LocationUpdate.model_validate(location)
        assert location1 != location2


class TestLocationReadSchemas:
    """Tests for the LocationRead API schema."""

    def test_schemas_module_exists(self) -> None:
        """Test that schemas module can be imported."""
        assert schemas is not None
        assert hasattr(schemas, "LocationRead")

    @pytest.mark.parametrize(
        "location",
        [
            {
                "id": 1,
                "address": "123 Main Street",
                "postal_code": "75001",
                "city": "Paris",
                "state": "Île-de-France",
                "country": "France",
            },
        ],
    )
    def test_location_read_create(self, location: dict[str, str | int]) -> None:
        """Test that LocationRead schema can be instantiated."""
        location_schema = schemas.LocationRead.model_validate(location)
        assert location_schema.id == location["id"]
        assert location_schema.address == location["address"]
        assert location_schema.postal_code == location["postal_code"]
        assert location_schema.city == location["city"]
        assert location_schema.state == location["state"]
        assert location_schema.country == location["country"]

    def test_location_read_has_id_field(self) -> None:
        """Test that LocationRead schema has an id field."""
        assert hasattr(schemas.LocationRead, "model_fields")
        assert "id" in schemas.LocationRead.model_fields

    @pytest.mark.parametrize(
        "location",
        [
            {
                "id": 1,
                "address": "123 Main Street",
                "postal_code": "75001",
                "city": "Paris",
                "state": "Île-de-France",
                "country": "France",
            },
        ],
    )
    def test_location_read_equality(self, location: dict[str, str | int]) -> None:
        """Test that two location reads with the same data are equal."""
        location1 = schemas.LocationRead.model_validate(location)
        location["id"] = 2
        location2 = schemas.LocationRead.model_validate(location)
        assert location1 != location2


class TestLocationUpdateValidation:
    """Tests for validation in the LocationUpdate API schema."""

    def test_location_update_all_none(self) -> None:
        """Test that LocationUpdate schema can be instantiated with partial fields."""
        update = schemas.LocationUpdate()
        assert update.address is None
        assert update.postal_code is None
        assert update.city is None
        assert update.state is None
        assert update.country is None

    def test_location_update_partial_fields(self) -> None:
        """Test that LocationUpdate schema can be instantiated with partial fields."""
        update = schemas.LocationUpdate(address="456 Another St", city="Lyon")
        assert update.address == "456 Another St"
        assert update.postal_code is None
        assert update.city == "Lyon"
        assert update.state is None
        assert update.country is None

    def test_location_update_invalid_partial(self) -> None:
        """Test that invalid partial fields in LocationUpdate are rejected."""
        with pytest.raises(ValidationError, match="String should"):
            schemas.LocationUpdate(address="1")


class TestLocationCreateValidation:
    """Tests for validation in the LocationCreate API schema."""

    def test_location_create_with_valid_data(self) -> None:
        """Test that LocationCreate schema accepts valid data."""
        location = schemas.LocationCreate(
            address="789 New St",
            postal_code="69001",
            city="Lyon",
            state="Auvergne",
            country="France",
        )
        assert location.address == "789 New St"
        assert location.postal_code == "69001"
        assert location.city == "Lyon"
        assert location.state == "Auvergne"
        assert location.country == "France"
