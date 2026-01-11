"""Tests schemas for the API instruments module.

This file contains placeholder tests for schemas.
More comprehensive schema validation tests can be added as needed.
"""

import pytest
from pydantic import ValidationError

from elims.modules.instruments import schemas
from elims.modules.instruments.constants import InstrumentBrand, InstrumentType


class TestInstrumentBaseSchemas:
    """Tests for the Instrument API schema."""

    def test_schemas_module_exists(self) -> None:
        """Test that schemas module can be imported."""
        assert schemas is not None
        assert hasattr(schemas, "InstrumentBase")

    @pytest.mark.parametrize(
        "instrument",
        [
            {"brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456"},
        ],
    )
    @pytest.mark.parametrize("instrument_brand", list(InstrumentBrand))
    @pytest.mark.parametrize("instrument_type", list(InstrumentType))
    def test_instrument_base_create(self, instrument: dict[str, str | int | None], instrument_brand: InstrumentBrand, instrument_type: InstrumentType) -> None:
        """Test that InstrumentBase schema can be instantiated."""
        instrument["brand"] = instrument_brand.value
        instrument["type"] = instrument_type.value
        instrument_schema = schemas.InstrumentBase.model_validate(instrument)

        assert instrument_schema.brand == InstrumentBrand(instrument["brand"])
        assert instrument_schema.type == InstrumentType(instrument["type"])
        assert instrument_schema.model == instrument["model"]
        assert instrument_schema.serial_number == instrument["serial_number"]

    @pytest.mark.parametrize(
        "instrument",
        [
            {"brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456"},
        ],
    )
    @pytest.mark.parametrize("invalid_brand", ["INVALID_BRAND"])
    def test_instrument_invalid_brand(self, instrument: dict[str, str | int | None], invalid_brand: str) -> None:
        """Test that valid model strings are accepted."""
        instrument["brand"] = invalid_brand
        with pytest.raises(ValidationError, match="Invalid instrument brand"):
            schemas.InstrumentBase.model_validate(instrument)

    @pytest.mark.parametrize(
        "instrument",
        [
            {"brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456"},
        ],
    )
    @pytest.mark.parametrize("invalid_type", ["INVALID_TYPE"])
    def test_instrument_invalid_type(self, instrument: dict[str, str | int | None], invalid_type: str) -> None:
        """Test that valid model strings are accepted."""
        instrument["type"] = invalid_type
        with pytest.raises(ValidationError, match="Invalid instrument type"):
            schemas.InstrumentBase.model_validate(instrument)

    @pytest.mark.parametrize(
        "instrument",
        [
            {"brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456"},
        ],
    )
    @pytest.mark.parametrize("invalid_model", ["Model 123", "Model@", "Model#", "Model/"])
    def test_instrument_invalid_model(self, instrument: dict[str, str | int | None], invalid_model: str) -> None:
        """Test that model strings with special characters are rejected in model."""
        instrument["model"] = invalid_model
        with pytest.raises(ValidationError, match="String should match pattern"):
            schemas.InstrumentBase.model_validate(instrument)

    @pytest.mark.parametrize(
        "instrument",
        [
            {"brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456"},
        ],
    )
    @pytest.mark.parametrize("invalid_serial", ["SN 123456", "SN@123", "SN#456", "SN/789"])
    def test_instrument_invalid_serial(self, instrument: dict[str, str | int | None], invalid_serial: str) -> None:
        """Test that serial numbers with special characters are rejected."""
        instrument["serial_number"] = invalid_serial
        with pytest.raises(ValidationError, match="String should match pattern"):
            schemas.InstrumentBase.model_validate(instrument)

    @pytest.mark.parametrize(
        "instrument",
        [
            {"brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456"},
        ],
    )
    def test_instrument_equality(self, instrument: dict[str, str | int | None]) -> None:
        """Test that two instruments with the same data are equal."""
        instrument1 = schemas.InstrumentBase.model_validate(instrument)
        instrument2 = schemas.InstrumentBase.model_validate(instrument)
        assert instrument1 == instrument2

    @pytest.mark.parametrize(
        "instrument",
        [
            {"brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456"},
        ],
    )
    def test_instrument_inequality(self, instrument: dict[str, str | int | None]) -> None:
        """Test that instruments with different data are not equal."""
        instrument1 = schemas.InstrumentBase.model_validate(instrument)
        instrument["model"] = "UXS"
        instrument2 = schemas.InstrumentBase.model_validate(instrument)
        assert instrument1 != instrument2


class TestInstrumentCreateSchemas:
    """Tests for the InstrumentCreate API schema."""

    def test_schemas_module_exists(self) -> None:
        """Test that schemas module can be imported."""
        assert schemas is not None
        assert hasattr(schemas, "InstrumentCreate")


class TestInstrumentUpdateSchemas:
    """Tests for the Instrument API schema."""

    def test_schemas_module_exists(self) -> None:
        """Test that schemas module can be imported."""
        assert schemas is not None
        assert hasattr(schemas, "InstrumentUpdate")

    @pytest.mark.parametrize(
        "instrument",
        [
            {"brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456"},
            {"brand": "None", "type": "OSC", "model": "UXR", "serial_number": "SN123456"},
            {"brand": "KS", "type": "None", "model": "UXR", "serial_number": "SN123456"},
            {"brand": "KS", "type": "OSC", "model": "None", "serial_number": "SN123456"},
            {"brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "None"},
        ],
    )
    @pytest.mark.parametrize("instrument_brand", list(InstrumentBrand))
    @pytest.mark.parametrize("instrument_type", list(InstrumentType))
    def test_instrument_base_creation(self, instrument: dict[str, str | int | None], instrument_brand: InstrumentBrand, instrument_type: InstrumentType) -> None:
        """Test that InstrumentBase schema can be instantiated."""
        instrument["brand"] = instrument_brand.value
        instrument["type"] = instrument_type.value
        instrument_schema = schemas.InstrumentUpdate.model_validate(instrument)

        assert instrument_schema.brand == InstrumentBrand(instrument["brand"])
        assert instrument_schema.type == InstrumentType(instrument["type"])
        assert instrument_schema.model == instrument["model"]
        assert instrument_schema.serial_number == instrument["serial_number"]

    @pytest.mark.parametrize(
        "instrument",
        [
            {"brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456"},
        ],
    )
    @pytest.mark.parametrize("invalid_brand", ["INVALID_BRAND"])
    def test_instrument_invalid_brand(self, instrument: dict[str, str | int | None], invalid_brand: str) -> None:
        """Test that valid model strings are accepted."""
        instrument["brand"] = invalid_brand
        with pytest.raises(ValidationError, match="Invalid instrument brand"):
            schemas.InstrumentUpdate.model_validate(instrument)

    @pytest.mark.parametrize(
        "instrument",
        [
            {"brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456"},
        ],
    )
    @pytest.mark.parametrize("invalid_type", ["INVALID_TYPE"])
    def test_instrument_invalid_type(self, instrument: dict[str, str | int | None], invalid_type: str) -> None:
        """Test that valid model strings are accepted."""
        instrument["type"] = invalid_type
        with pytest.raises(ValidationError, match="Invalid instrument type"):
            schemas.InstrumentUpdate.model_validate(instrument)

    @pytest.mark.parametrize(
        "instrument",
        [
            {"brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456"},
        ],
    )
    @pytest.mark.parametrize("invalid_model", ["Model 123", "Model@", "Model#", "Model/"])
    def test_instrument_invalid_model(self, instrument: dict[str, str | int | None], invalid_model: str) -> None:
        """Test that model strings with special characters are rejected in model."""
        instrument["model"] = invalid_model
        with pytest.raises(ValidationError, match="String should match pattern"):
            schemas.InstrumentUpdate.model_validate(instrument)

    @pytest.mark.parametrize(
        "instrument",
        [
            {"brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456"},
        ],
    )
    @pytest.mark.parametrize("invalid_serial", ["SN 123456", "SN@123", "SN#456", "SN/789"])
    def test_instrument_invalid_serial(self, instrument: dict[str, str | int | None], invalid_serial: str) -> None:
        """Test that serial numbers with special characters are rejected."""
        instrument["serial_number"] = invalid_serial
        with pytest.raises(ValidationError, match="String should match pattern"):
            schemas.InstrumentUpdate.model_validate(instrument)

    @pytest.mark.parametrize(
        "instrument",
        [
            {"brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456"},
        ],
    )
    def test_instrument_equality(self, instrument: dict[str, str | int | None]) -> None:
        """Test that two instruments with the same data are equal."""
        instrument1 = schemas.InstrumentUpdate.model_validate(instrument)
        instrument2 = schemas.InstrumentUpdate.model_validate(instrument)
        assert instrument1 == instrument2

    @pytest.mark.parametrize(
        "instrument",
        [
            {"brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456"},
        ],
    )
    def test_instrument_inequality(self, instrument: dict[str, str | int | None]) -> None:
        """Test that instruments with different data are not equal."""
        instrument1 = schemas.InstrumentUpdate.model_validate(instrument)
        instrument["model"] = "UXS"
        instrument2 = schemas.InstrumentUpdate.model_validate(instrument)
        assert instrument1 != instrument2


class TestInstrumentReadSchemas:
    """Tests for the InstrumentRead API schema."""

    def test_schemas_module_exists(self) -> None:
        """Test that schemas module can be imported."""
        assert schemas is not None
        assert hasattr(schemas, "InstrumentRead")

    @pytest.mark.parametrize(
        "instrument",
        [
            {"id": 1, "brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456"},
        ],
    )
    @pytest.mark.parametrize("instrument_brand", list(InstrumentBrand))
    @pytest.mark.parametrize("instrument_type", list(InstrumentType))
    def test_instrument_read_create(self, instrument: dict[str, str | int | None], instrument_brand: InstrumentBrand, instrument_type: InstrumentType) -> None:
        """Test that InstrumentRead schema can be instantiated with ID."""
        instrument["brand"] = instrument_brand.value
        instrument["type"] = instrument_type.value
        instrument_schema = schemas.InstrumentRead.model_validate(instrument)

        assert instrument_schema.id == instrument["id"]
        assert instrument_schema.brand == InstrumentBrand(instrument["brand"])
        assert instrument_schema.type == InstrumentType(instrument["type"])
        assert instrument_schema.model == instrument["model"]
        assert instrument_schema.serial_number == instrument["serial_number"]

    def test_instrument_read_has_id_field(self) -> None:
        """Test that InstrumentRead has an id field."""
        assert hasattr(schemas.InstrumentRead, "model_fields")
        assert "id" in schemas.InstrumentRead.model_fields

    @pytest.mark.parametrize(
        "instrument",
        [
            {"id": 1, "brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456"},
            {"id": 999, "brand": "KS", "type": "OSC", "model": "UXR", "serial_number": "SN123456"},
        ],
    )
    def test_instrument_read_different_ids(self, instrument: dict[str, str | int | None]) -> None:
        """Test that InstrumentRead schemas with different IDs are not equal."""
        read1 = schemas.InstrumentRead.model_validate(instrument)
        instrument["id"] = 2
        read2 = schemas.InstrumentRead.model_validate(instrument)
        assert read1 != read2


class TestInstrumentUpdateValidation:
    """Tests for InstrumentUpdate validation edge cases."""

    def test_instrument_update_all_none(self) -> None:
        """Test that InstrumentUpdate can be created with all None values."""
        update = schemas.InstrumentUpdate()
        assert update.brand is None
        assert update.type is None
        assert update.model is None
        assert update.serial_number is None

    def test_instrument_update_partial_fields(self) -> None:
        """Test that InstrumentUpdate accepts partial field updates."""
        update = schemas.InstrumentUpdate(model="MS2024A")
        assert update.model == "MS2024A"
        assert update.brand is None
        assert update.type is None
        assert update.serial_number is None

    def test_instrument_update_with_enum_types(self) -> None:
        """Test that InstrumentUpdate accepts enum types directly."""
        update = schemas.InstrumentUpdate(
            brand=InstrumentBrand.ANRITSU,
            type=InstrumentType.SPECTRUM_ANALYZER,
        )
        assert update.brand == InstrumentBrand.ANRITSU
        assert update.type == InstrumentType.SPECTRUM_ANALYZER

    def test_instrument_update_with_string_enums(self) -> None:
        """Test that InstrumentUpdate converts string enums."""
        update = schemas.InstrumentUpdate(
            brand="AN",
            type="OSC",
        )
        assert update.brand == InstrumentBrand.ANRITSU
        assert update.type == InstrumentType.OSCILLOSCOPE

    def test_instrument_update_invalid_brand_with_none(self) -> None:
        """Test that None is accepted for optional brand field in update."""
        update = schemas.InstrumentUpdate(brand=None)
        assert update.brand is None

    def test_instrument_update_invalid_type_with_none(self) -> None:
        """Test that None is accepted for optional type field in update."""
        update = schemas.InstrumentUpdate(type=None)
        assert update.type is None


class TestInstrumentCreateValidation:
    """Tests for InstrumentCreate validation."""

    def test_instrument_create_with_valid_data(self) -> None:
        """Test creating instrument with all valid data."""
        create = schemas.InstrumentCreate(
            brand=InstrumentBrand.ANRITSU,
            type=InstrumentType.SPECTRUM_ANALYZER,
            model="MS2023A",
            serial_number="SN123456",
        )
        assert create.brand == InstrumentBrand.ANRITSU
        assert create.type == InstrumentType.SPECTRUM_ANALYZER
        assert create.model == "MS2023A"
        assert create.serial_number == "SN123456"

    def test_instrument_create_with_string_enums(self) -> None:
        """Test that InstrumentCreate converts string values to enums."""
        create = schemas.InstrumentCreate(
            brand="AN",
            type="OSC",
            model="UXR",
            serial_number="SN123456",
        )
        assert create.brand == InstrumentBrand.ANRITSU
        assert create.type == InstrumentType.OSCILLOSCOPE
        assert create.model == "UXR"
        assert create.serial_number == "SN123456"

    @pytest.mark.parametrize("instrument_type", list(InstrumentType))
    @pytest.mark.parametrize("instrument_brand", list(InstrumentBrand))
    def test_instrument_create_all_combinations(self, instrument_brand: InstrumentBrand, instrument_type: InstrumentType) -> None:
        """Test that InstrumentCreate works with all brand and type combinations."""
        create = schemas.InstrumentCreate(
            brand=instrument_brand,
            type=instrument_type,
            model="MS2023A",
            serial_number="SN123456",
        )
        assert create.brand == instrument_brand
        assert create.type == instrument_type
