"""Tests constants for the API instruments module."""

import pytest

from elims.api.modules.instruments.constants import InstrumentBrand, InstrumentType


class TestInstrumentBrand:
    """Tests for the InstrumentBrand enum."""

    @pytest.mark.parametrize("instrument_brand", list(InstrumentBrand))
    def test_instrument_brand_informal_representation(self, instrument_brand: InstrumentBrand) -> None:
        """Test informal string representation of InstrumentBrand enum members."""
        informal_str = {
            InstrumentBrand.ANRITSU: "Anritsu",
            InstrumentBrand.KEYSIGHT: "Keysight",
            InstrumentBrand.TELEDYNE_LECROY: "Teledyne LeCroy",
            InstrumentBrand.TEKTRONIX: "Tektronix",
        }
        assert str(instrument_brand) == informal_str[instrument_brand]

    @pytest.mark.parametrize("instrument_brand", list(InstrumentBrand))
    def test_instrument_brand_official_representation(self, instrument_brand: InstrumentBrand) -> None:
        """Test official string representation of InstrumentBrand enum members."""
        official_str = {
            InstrumentBrand.ANRITSU: "ANRITSU: AN",
            InstrumentBrand.KEYSIGHT: "KEYSIGHT: KS",
            InstrumentBrand.TELEDYNE_LECROY: "TELEDYNE_LECROY: TC",
            InstrumentBrand.TEKTRONIX: "TEKTRONIX: TE",
        }
        assert repr(instrument_brand) == official_str[instrument_brand]

    def test_instrument_brand_choices(self) -> None:
        """Test the choices method of InstrumentBrand enum."""
        expected_choices = ["Anritsu", "Keysight", "Teledyne LeCroy", "Tektronix"]
        assert InstrumentBrand.choices() == expected_choices


class TestInstrumentType:
    """Tests for the InstrumentType enum."""

    @pytest.mark.parametrize("instrument_type", list(InstrumentType))
    def test_instrument_type_informal_representation(self, instrument_type: InstrumentType) -> None:
        """Test informal string representation of InstrumentType enum members."""
        informal_str = {
            InstrumentType.BIT_ERROR_RATE_TESTER: "Bit Error Rate Tester",
            InstrumentType.DIGITAL_MULTIMETER: "Digital Multimeter",
            InstrumentType.ELECTRICAL_SIGNAL_GENERATOR: "Electrical Signal Generator",
            InstrumentType.OSCILLOSCOPE: "Oscilloscope",
            InstrumentType.POWER_SUPPLY: "Power Supply",
            InstrumentType.SPECTRUM_ANALYZER: "Spectrum Analyzer",
            InstrumentType.TEMPERATURE_UNIT: "Temperature Unit",
            InstrumentType.VECTOR_NETWORK_ANALYZER: "Vector Network Analyzer",
        }
        assert str(instrument_type) == informal_str[instrument_type]

    @pytest.mark.parametrize("instrument_type", list(InstrumentType))
    def test_instrument_type_official_representation(self, instrument_type: InstrumentType) -> None:
        """Test official string representation of InstrumentType enum members."""
        official_str = {
            InstrumentType.BIT_ERROR_RATE_TESTER: "BIT_ERROR_RATE_TESTER: BERT",
            InstrumentType.DIGITAL_MULTIMETER: "DIGITAL_MULTIMETER: DMM",
            InstrumentType.ELECTRICAL_SIGNAL_GENERATOR: "ELECTRICAL_SIGNAL_GENERATOR: ESG",
            InstrumentType.OSCILLOSCOPE: "OSCILLOSCOPE: OSC",
            InstrumentType.POWER_SUPPLY: "POWER_SUPPLY: PWR",
            InstrumentType.SPECTRUM_ANALYZER: "SPECTRUM_ANALYZER: SA",
            InstrumentType.TEMPERATURE_UNIT: "TEMPERATURE_UNIT: TU",
            InstrumentType.VECTOR_NETWORK_ANALYZER: "VECTOR_NETWORK_ANALYZER: VNA",
        }
        assert repr(instrument_type) == official_str[instrument_type]

    def test_instrument_type_choices(self) -> None:
        """Test the choices method of InstrumentType enum."""
        expected_choices = [
            "Bit Error Rate Tester",
            "Digital Multimeter",
            "Electrical Signal Generator",
            "Oscilloscope",
            "Power Supply",
            "Spectrum Analyzer",
            "Temperature Unit",
            "Vector Network Analyzer",
        ]
        assert InstrumentType.choices() == expected_choices
