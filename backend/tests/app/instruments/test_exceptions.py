"""Tests for the API instruments module exceptions."""

import pytest
from app.api.instruments.constants import InstrumentBrand, InstrumentType
from app.api.instruments.exceptions import (
    InstrumentAlreadyExistError,
    InstrumentBrandError,
    InstrumentNotFoundError,
    InstrumentTypeError,
)


class TestInstrumentExceptions:
    """Tests for the instrument exceptions."""

    def test_instrument_brand_error(self) -> None:
        """Test that InstrumentBrandError is raised with the correct message."""
        invalid_brand = "invalid_brand"
        with pytest.raises(InstrumentBrandError) as exc_info:
            raise InstrumentBrandError(invalid_brand)
        allowed = ", ".join(InstrumentBrand.choices())
        expected_msg = f"Invalid instrument brand: '{invalid_brand}'. Allowed: {allowed}."
        assert str(exc_info.value) == expected_msg

    def test_instrument_type_error(self) -> None:
        """Test that InstrumentTypeError is raised with the correct message."""
        invalid_type = "invalid_type"
        with pytest.raises(InstrumentTypeError) as exc_info:
            raise InstrumentTypeError(invalid_type)
        allowed = ", ".join(InstrumentType.choices())
        expected_msg = f"Invalid instrument type: '{invalid_type}'. Allowed: {allowed}."
        assert str(exc_info.value) == expected_msg

    def test_instrument_not_found_error(self) -> None:
        """Test that InstrumentNotFoundError is raised with the correct message."""
        instrument_id = 123
        with pytest.raises(InstrumentNotFoundError) as exc_info:
            raise InstrumentNotFoundError(instrument_id)
        assert str(exc_info.value) == f"Instrument with ID {instrument_id} not found."

    def test_instrument_already_exist_error(self) -> None:
        """Test that InstrumentAlreadyExistError is raised with the correct message."""
        serial_number = "SN123"
        with pytest.raises(InstrumentAlreadyExistError) as exc_info:
            raise InstrumentAlreadyExistError(serial_number)
        assert str(exc_info.value) == f"Instrument with serial number '{serial_number}' already exists."
