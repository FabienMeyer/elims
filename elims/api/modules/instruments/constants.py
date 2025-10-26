"""Constants for the API instruments module."""

from enum import Enum
from typing import Annotated

from pydantic import Field


class InstrumentBrand(Enum):
    """Enumeration of instrument brands."""

    ANRITSU = "AN"
    KEYSIGHT = "KS"
    TELEDYNE_LECROY = "TC"
    TEKTRONIX = "TE"

    def __str__(self) -> str:
        """Get the informal string representation of the instrument brand."""
        return {
            InstrumentBrand.ANRITSU: "Anritsu",
            InstrumentBrand.KEYSIGHT: "Keysight",
            InstrumentBrand.TELEDYNE_LECROY: "Teledyne LeCroy",
            InstrumentBrand.TEKTRONIX: "Tektronix",
        }[self]

    def __repr__(self) -> str:
        """Get the official string representation of the instrument brand."""
        return f"{self.name}: {self.value}"

    @staticmethod
    def choices() -> list[str]:
        """Get a list of all instrument brand display names.

        Returns:
            A list of strings representing the full names of the brands.

        """
        return [str(instrument_brand) for instrument_brand in InstrumentBrand]


class InstrumentType(Enum):
    """Enumeration of instrument types."""

    BIT_ERROR_RATE_TESTER = "BERT"
    DIGITAL_MULTIMETER = "DMM"
    ELECTRICAL_SIGNAL_GENERATOR = "ESG"
    OSCILLOSCOPE = "OSC"
    POWER_SUPPLY = "PWR"
    SPECTRUM_ANALYZER = "SA"
    TEMPERATURE_UNIT = "TU"
    VECTOR_NETWORK_ANALYZER = "VNA"

    def __str__(self) -> str:
        """Get the informal string representation of the instrument type."""
        return {
            InstrumentType.BIT_ERROR_RATE_TESTER: "Bit Error Rate Tester",
            InstrumentType.DIGITAL_MULTIMETER: "Digital Multimeter",
            InstrumentType.ELECTRICAL_SIGNAL_GENERATOR: "Electrical Signal Generator",
            InstrumentType.OSCILLOSCOPE: "Oscilloscope",
            InstrumentType.POWER_SUPPLY: "Power Supply",
            InstrumentType.SPECTRUM_ANALYZER: "Spectrum Analyzer",
            InstrumentType.TEMPERATURE_UNIT: "Temperature Unit",
            InstrumentType.VECTOR_NETWORK_ANALYZER: "Vector Network Analyzer",
        }[self]

    def __repr__(self) -> str:
        """Get the official string representation of the instrument type."""
        return f"{self.name}: {self.value}"

    @staticmethod
    def choices() -> list[str]:
        """Get a list of all instrument type display names.

        Returns:
            A list of strings representing the full names of the types.

        """
        return [str(instrument_type) for instrument_type in InstrumentType]


ModelStr = Annotated[str, Field(pattern=r"^[A-Za-z0-9_-]+$")]
"""Type alias for instrument model strings with validation."""

SerialNumberStr = Annotated[str, Field(pattern=r"^[A-Za-z0-9_-]+$")]
"""Type alias for instrument serial number strings with validation."""
