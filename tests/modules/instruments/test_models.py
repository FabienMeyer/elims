"""Tests constants for the API instruments module."""

import pytest

from elims.api.modules.instruments.constants import InstrumentBrand, InstrumentType
from elims.api.modules.instruments.models import Instrument


class TestInstrumentModel:
    """Tests for the Instrument data model."""

    @pytest.mark.parametrize("brand", list(InstrumentBrand))
    @pytest.mark.parametrize("instrument_type", list(InstrumentType))
    def test_instrument_creation(self, brand: InstrumentBrand, instrument_type: InstrumentType) -> None:
        """Test creating an instrument with valid data."""
        instrument = Instrument(brand=brand, type=instrument_type, model="Model123", serial_number="SN123456")
        assert instrument.brand == brand
        assert instrument.type == instrument_type
        assert instrument.model == "Model123"
        assert instrument.serial_number == "SN123456"
        assert instrument.id is None

    def test_instrument_brand_validation(self) -> None:
        """Test that invalid instrument brands raise validation errors."""
        Instrument(brand="InvalidBrand", type=InstrumentType.OSCILLOSCOPE, model="Model123", serial_number="SN123456")
