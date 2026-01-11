"""Tests for the API locations module exceptions."""

import pytest

from elims.modules.locations.exceptions import LocationAlreadyExistError, LocationNotFoundError


class TestLocationExceptions:
    """Tests for the location exceptions."""

    def test_location_not_found_error(self) -> None:
        """Test that LocationNotFoundError is raised with the correct message."""
        location_id = 456
        with pytest.raises(LocationNotFoundError) as exc_info:
            raise LocationNotFoundError(location_id)
        assert str(exc_info.value) == f"Location with ID {location_id} not found."

    def test_location_already_exist_error(self) -> None:
        """Test that LocationAlreadyExistError is raised with the correct message."""
        location_name = "Test Location"
        with pytest.raises(LocationAlreadyExistError) as exc_info:
            raise LocationAlreadyExistError(location_name)
        assert str(exc_info.value) == f"Location with name '{location_name}' already exists."
