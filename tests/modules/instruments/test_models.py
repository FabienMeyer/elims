"""Tests for the API instruments module models."""

import pytest

from elims.api.modules.instruments.constants import InstrumentBrand, InstrumentType
from elims.api.modules.instruments.models import Instrument


class TestInstrumentModel:
    """Tests for the Instrument database model."""

    def test_instrument_creation_with_all_fields(self) -> None:
        """Test creating an instrument with all fields."""
        instrument = Instrument(
            id=1,
            brand=InstrumentBrand.KEYSIGHT,
            type=InstrumentType.OSCILLOSCOPE,
            model="UXR",
            serial_number="SN123456",
        )
        assert instrument.id == 1
        assert instrument.brand == InstrumentBrand.KEYSIGHT
        assert instrument.type == InstrumentType.OSCILLOSCOPE
        assert instrument.model == "UXR"
        assert instrument.serial_number == "SN123456"

    def test_instrument_creation_without_id(self) -> None:
        """Test creating an instrument without an ID (new record)."""
        instrument = Instrument(
            brand=InstrumentBrand.TEKTRONIX,
            type=InstrumentType.DIGITAL_MULTIMETER,
            model="DMM4050",
            serial_number="DMM-001",
        )
        assert instrument.id is None
        assert instrument.brand == InstrumentBrand.TEKTRONIX
        assert instrument.type == InstrumentType.DIGITAL_MULTIMETER
        assert instrument.model == "DMM4050"
        assert instrument.serial_number == "DMM-001"

    @pytest.mark.parametrize("brand", list(InstrumentBrand))
    @pytest.mark.parametrize("instrument_type", list(InstrumentType))
    def test_instrument_creation_all_combinations(self, brand: InstrumentBrand, instrument_type: InstrumentType) -> None:
        """Test creating instruments with all combinations of brands and types."""
        instrument = Instrument(
            brand=brand,
            type=instrument_type,
            model="TestModel",
            serial_number="SN-TEST-001",
        )
        assert instrument.brand == brand
        assert instrument.type == instrument_type
        assert instrument.model == "TestModel"
        assert instrument.serial_number == "SN-TEST-001"

    def test_instrument_model_pattern_validation_valid(self) -> None:
        """Test that valid model strings are accepted."""
        valid_models = ["UXR", "E4448A", "Model-123", "Model_456", "MDC-8430A"]
        for model in valid_models:
            instrument = Instrument(
                brand=InstrumentBrand.KEYSIGHT,
                type=InstrumentType.OSCILLOSCOPE,
                model=model,
                serial_number="SN-001",
            )
            assert instrument.model == model

    def test_instrument_model_pattern_validation_invalid(self) -> None:
        """Test that model strings with special characters are accepted in model."""
        # Note: Pattern validation occurs at InstrumentBase schema level
        # At the SQLModel level, any string is accepted
        invalid_models = ["Model 123", "Model@", "Model#", "Model/"]
        for model in invalid_models:
            instrument = Instrument(
                brand=InstrumentBrand.KEYSIGHT,
                type=InstrumentType.OSCILLOSCOPE,
                model=model,
                serial_number="SN-001",
            )
            assert instrument.model == model

    def test_instrument_serial_number_pattern_validation_valid(self) -> None:
        """Test that valid serial numbers are accepted."""
        valid_serials = ["SN123456", "SN-123-456", "SN_ABC_123", "ABC-DEF-123"]
        for serial in valid_serials:
            instrument = Instrument(
                brand=InstrumentBrand.TEKTRONIX,
                type=InstrumentType.DIGITAL_MULTIMETER,
                model="DMM4050",
                serial_number=serial,
            )
            assert instrument.serial_number == serial

    def test_instrument_serial_number_pattern_validation_invalid(self) -> None:
        """Test that serial numbers with special characters are accepted in model."""
        # Note: Pattern validation occurs at InstrumentBase schema level
        # At the SQLModel level, any string is accepted
        invalid_serials = ["SN 123456", "SN@123", "SN#456", "SN/789"]
        for serial in invalid_serials:
            instrument = Instrument(
                brand=InstrumentBrand.TEKTRONIX,
                type=InstrumentType.DIGITAL_MULTIMETER,
                model="DMM4050",
                serial_number=serial,
            )
            assert instrument.serial_number == serial

    def test_instrument_equality(self) -> None:
        """Test that two instruments with the same data are equal."""
        instrument1 = Instrument(
            id=1,
            brand=InstrumentBrand.KEYSIGHT,
            type=InstrumentType.OSCILLOSCOPE,
            model="UXR",
            serial_number="SN123456",
        )
        instrument2 = Instrument(
            id=1,
            brand=InstrumentBrand.KEYSIGHT,
            type=InstrumentType.OSCILLOSCOPE,
            model="UXR",
            serial_number="SN123456",
        )
        assert instrument1 == instrument2

    def test_instrument_inequality(self) -> None:
        """Test that instruments with different data are not equal."""
        instrument1 = Instrument(
            id=1,
            brand=InstrumentBrand.KEYSIGHT,
            type=InstrumentType.OSCILLOSCOPE,
            model="UXR",
            serial_number="SN123456",
        )
        instrument2 = Instrument(
            id=2,
            brand=InstrumentBrand.TEKTRONIX,
            type=InstrumentType.DIGITAL_MULTIMETER,
            model="DMM4050",
            serial_number="DMM-001",
        )
        assert instrument1 != instrument2

    def test_instrument_repr(self) -> None:
        """Test that instrument has a string representation."""
        instrument = Instrument(
            id=1,
            brand=InstrumentBrand.KEYSIGHT,
            type=InstrumentType.OSCILLOSCOPE,
            model="UXR",
            serial_number="SN123456",
        )
        repr_str = repr(instrument)
        assert "Instrument" in repr_str or "id" in repr_str
