"""Tests for the API locations module models."""

import pytest
from pydantic import ValidationError

from elims.modules.locations import models


class TestLocationModel:
    """Tests for the Location database model."""

    def test_location_module_exists(self) -> None:
        """Test that Location model can be imported."""
        assert models is not None
        assert hasattr(models, "Location")

    @pytest.mark.parametrize(
        "location",
        [
            {"address": "Avenue d'Echallens 24", "postal_code": "1000", "city": "Lausanne", "state": "Vaud", "country": "Switzerland", "id": 1},
            {"address": "Avenue d'Echallens 24", "postal_code": "1000", "city": "Lausanne", "state": "Vaud", "country": "Switzerland"},  # No ID
        ],
    )
    def test_location_creation(self, location: dict[str, str | int | None]) -> None:
        """Test creating a location with and without ID."""
        location_model = models.Location.model_validate(location)

        if "id" in location:
            assert location_model.id == location["id"]
        else:
            assert location_model.id is None

        assert location_model.address == location["address"]
        assert location_model.postal_code == location["postal_code"]
        assert location_model.city == location["city"]
        assert location_model.state == location["state"]
        assert location_model.country == location["country"]

    @pytest.mark.parametrize(
        "location",
        [
            {"address": "Avenue d'Echallens 24", "postal_code": "1000", "city": "Lausanne", "state": "Vaud", "country": "Switzerland", "id": 1},
        ],
    )
    @pytest.mark.parametrize(
        "invalid_address",
        [
            "",  # Empty string - violates min_length=2
            "A",  # Too short - violates min_length=2
            "A" * 201,  # Too long - violates max_length=200
            "123@Main#St!",  # Invalid characters - violates pattern
            "Main St & 2nd Ave",  # Invalid character & - violates pattern
            "Main St (apt 5)",  # Invalid characters () - violates pattern
        ],
    )
    def test_location_invalid_address(self, location: dict[str, str], invalid_address: str) -> None:
        """Test that invalid address strings are rejected."""
        location["address"] = invalid_address
        with pytest.raises(ValidationError, match="address"):
            models.Location.model_validate(location)

    @pytest.mark.parametrize(
        "location",
        [
            {"address": "Avenue d'Echallens 24", "postal_code": "1000", "city": "Lausanne", "state": "Vaud", "country": "Switzerland", "id": 1},
        ],
    )
    @pytest.mark.parametrize(
        "invalid_postal_code",
        [
            "",  # Empty string - violates min_length=2
            "1",  # Too short - violates min_length=2
            "1" * 21,  # Too long - violates max_length=20
            "12@34",  # Invalid characters - violates pattern
            "AB-CD",  # Invalid character - - violates pattern
            "12 34",  # Invalid character space - violates pattern
        ],
    )
    def test_location_invalid_postal_code(self, location: dict[str, str], invalid_postal_code: str) -> None:
        """Test that invalid postal_code strings are rejected."""
        location["postal_code"] = invalid_postal_code
        with pytest.raises(ValidationError, match="postal_code"):
            models.Location.model_validate(location)

    @pytest.mark.parametrize(
        "location",
        [
            {"address": "Avenue d'Echallens 24", "postal_code": "1000", "city": "Lausanne", "state": "Vaud", "country": "Switzerland", "id": 1},
        ],
    )
    @pytest.mark.parametrize(
        "invalid_city",
        [
            "",  # Empty string - violates min_length=2
            "A",  # Too short - violates min_length=2
            "A" * 101,  # Too long - violates max_length=100
            "City@123",  # Invalid characters - violates pattern
            "City & Town",  # Invalid character & - violates pattern
            "City (region)",  # Invalid characters () - violates pattern
        ],
    )
    def test_location_invalid_city(self, location: dict[str, str], invalid_city: str) -> None:
        """Test that invalid city strings are rejected."""
        location["city"] = invalid_city
        with pytest.raises(ValidationError, match="city"):
            models.Location.model_validate(location)

    @pytest.mark.parametrize(
        "location",
        [
            {"address": "Avenue d'Echallens 24", "postal_code": "1000", "city": "Lausanne", "state": "Vaud", "country": "Switzerland", "id": 1},
        ],
    )
    @pytest.mark.parametrize(
        "invalid_state",
        [
            "",  # Empty string - violates min_length=2
            "A",  # Too short - violates min_length=2
            "A" * 101,  # Too long - violates max_length=100
            "State@123",  # Invalid characters - violates pattern
            "State & Province",  # Invalid character & - violates pattern
            "State (region)",  # Invalid characters () - violates pattern
        ],
    )
    def test_location_invalid_state(self, location: dict[str, str], invalid_state: str) -> None:
        """Test that invalid state strings are rejected."""
        location["state"] = invalid_state
        with pytest.raises(ValidationError, match="state"):
            models.Location.model_validate(location)

    @pytest.mark.parametrize(
        "location",
        [
            {"address": "Avenue d'Echallens 24", "postal_code": "1000", "city": "Lausanne", "state": "Vaud", "country": "Switzerland", "id": 1},
        ],
    )
    @pytest.mark.parametrize(
        "invalid_country",
        [
            "",  # Empty string - violates min_length=2
            "A",  # Too short - violates min_length=2
            "A" * 101,  # Too long - violates max_length=100
            "Country@123",  # Invalid characters - violates pattern
            "Country & Nation",  # Invalid character & - violates pattern
            "Country (region)",  # Invalid characters () - violates pattern
        ],
    )
    def test_location_invalid_country(self, location: dict[str, str], invalid_country: str) -> None:
        """Test that invalid country strings are rejected."""
        location["country"] = invalid_country
        with pytest.raises(ValidationError, match="country"):
            models.Location.model_validate(location)
