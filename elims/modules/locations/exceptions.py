"""Exceptions for the API locations module."""


class LocationNotFoundError(Exception):
    """Exception raised when a location is not found in the database."""

    def __init__(self, location_id: int) -> None:
        """Initialize the exception.

        Args:
            location_id: The ID of the location that was not found.

        """
        super().__init__(f"Location with ID {location_id} not found.")


class LocationAlreadyExistError(Exception):
    """Exception raised when a location with a given name already exists."""

    def __init__(self, name: str) -> None:
        """Initialize the exception.

        Args:
            name: The name that already exists.

        """
        super().__init__(f"Location with name '{name}' already exists.")
