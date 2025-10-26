"""Tests for the API instruments module models."""

import pytest
from pydantic import ValidationError

from elims.api.modules.instruments import models
from elims.api.modules.instruments.constants import InstrumentBrand, InstrumentType


class TestInstrumentModel:
    """Tests for the Instrument database model."""

    def test_instrument_module_exists(self) -> None:
        """Test that Instrument model can be imported."""
        assert models is not None
        assert hasattr(models, "Instrument")

    @pytest.mark.parametrize(
        "instrument",
        [
            {"brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456", "id": 1},
            {"brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456"},  # No ID
        ],
    )
    @pytest.mark.parametrize("brand", list(InstrumentBrand))
    @pytest.mark.parametrize("type", list(InstrumentType))
    def test_instrument_creation(self, instrument: dict[str, str | int | None], instrument_brand: InstrumentBrand, instrument_type: InstrumentType) -> None:
        """Test creating an instrument with and without ID."""
        instrument["brand"] = instrument_brand.value
        instrument["type"] = instrument_type.value
        instrument_model = models.Instrument.model_validate(instrument)

        if "id" in instrument:
            assert instrument_model.id == instrument["id"]
        else:
            assert instrument_model.id is None

        assert instrument_model.brand == InstrumentBrand(instrument["brand"])
        assert instrument_model.type == InstrumentType(instrument["type"])
        assert instrument_model.model == instrument["model"]
        assert instrument_model.serial_number == instrument["serial_number"]

    @pytest.mark.parametrize(
        "instrument",
        [
            {"brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456", "id": 1},
        ],
    )
    @pytest.mark.parametrize("invalid_brand", ["INVALID_BRAND"])
    def test_instrument_invalid_brand(self, instrument: dict[str, str | int | None], invalid_brand: str) -> None:
        """Test that valid model strings are accepted."""
        instrument["brand"] = invalid_brand
        with pytest.raises(ValidationError, match="Invalid instrument brand"):
            models.Instrument.model_validate(instrument)

    @pytest.mark.parametrize(
        "instrument",
        [
            {"brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456", "id": 1},
        ],
    )
    @pytest.mark.parametrize("invalid_type", ["INVALID_TYPE"])
    def test_instrument_invalid_type(self, instrument: dict[str, str | int | None], invalid_type: str) -> None:
        """Test that valid model strings are accepted."""
        instrument["type"] = invalid_type
        with pytest.raises(ValidationError, match="Invalid instrument type"):
            models.Instrument.model_validate(instrument)

    @pytest.mark.parametrize(
        "instrument",
        [
            {"brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456", "id": 1},
        ],
    )
    @pytest.mark.parametrize("invalid_model", ["Model 123", "Model@", "Model#", "Model/"])
    def test_instrument_invalid_model(self, instrument: dict[str, str | int | None], invalid_model: str) -> None:
        """Test that model strings with special characters are rejected in model."""
        instrument["model"] = invalid_model
        with pytest.raises(ValidationError, match="String should match pattern"):
            models.Instrument.model_validate(instrument)

    @pytest.mark.parametrize(
        "instrument",
        [
            {"brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456", "id": 1},
        ],
    )
    @pytest.mark.parametrize("invalid_serial", ["SN 123456", "SN@123", "SN#456", "SN/789"])
    def test_instrument_invalid_serial(self, instrument: dict[str, str | int | None], invalid_serial: str) -> None:
        """Test that serial numbers with special characters are rejected."""
        instrument["serial_number"] = invalid_serial
        with pytest.raises(ValidationError, match="String should match pattern"):
            models.Instrument.model_validate(instrument)

    @pytest.mark.parametrize(
        "instrument",
        [
            {"brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456", "id": 1},
        ],
    )
    def test_instrument_equality(self, instrument: dict[str, str | int | None]) -> None:
        """Test that two instruments with the same data are equal."""
        instrument1 = models.Instrument.model_validate(instrument)
        instrument2 = models.Instrument.model_validate(instrument)
        assert instrument1 == instrument2

    @pytest.mark.parametrize(
        "instrument",
        [
            {"brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456", "id": 1},
        ],
    )
    def test_instrument_inequality(self, instrument: dict[str, str | int | None]) -> None:
        """Test that instruments with different data are not equal."""
        instrument1 = models.Instrument.model_validate(instrument)
        instrument["id"] = 2
        instrument2 = models.Instrument.model_validate(instrument)
        assert instrument1 != instrument2
