"""Exceptions for the API instruments module."""

from .constants import InstrumentBrand, InstrumentType


class InstrumentBrandError(ValueError):
    """Exception raised for an invalid instrument brand."""

    def __init__(self, value: str) -> None:
        """Initialize the exception.

        Args:
            value: The invalid brand value that was provided.

        """
        message = f"Invalid instrument brand: '{value}'. " f"Allowed: {', '.join(InstrumentBrand.choices())}."
        super().__init__(message)


class InstrumentTypeError(ValueError):
    """Exception raised for an invalid instrument type."""

    def __init__(self, value: str) -> None:
        """Initialize the exception.

        Args:
            value: The invalid type value that was provided.

        """
        message = f"Invalid instrument type: '{value}'. " f"Allowed: {', '.join(InstrumentType.choices())}."
        super().__init__(message)


class InstrumentNotFoundError(Exception):
    """Exception raised when an instrument is not found in the database."""

    def __init__(self, instrument_id: int) -> None:
        """Initialize the exception.

        Args:
            instrument_id: The ID of the instrument that was not found.

        """
        super().__init__(f"Instrument with ID {instrument_id} not found.")


class InstrumentAlreadyExistsError(Exception):
    """Exception raised when an instrument with a given serial number already exists."""

    def __init__(self, serial_number: str) -> None:
        """Initialize the exception.

        Args:
            serial_number: The serial number that already exists.

        """
        super().__init__(f"Instrument with serial number '{serial_number}' already exists.")
