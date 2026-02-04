"""Exceptions for the temperature module."""


class TemperatureNotFoundError(Exception):
    """Raised when a temperature record is not found in the database."""

    def __init__(self, temperature_id: int) -> None:
        """Initialize the exception.

        Args:
            temperature_id: The ID of the temperature that was not found.

        """
        self.temperature_id = temperature_id
        super().__init__(f"Temperature with id {temperature_id} not found.")
