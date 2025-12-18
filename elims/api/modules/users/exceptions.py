"""Exceptions for the API users module."""


class UserNotFoundError(Exception):
    """Exception raised when a User is not found in the database."""

    def __init__(self, user_id: None | int, username: None | str = None) -> None:
        """Initialize the exception.

        Args:
            user_id: The ID of the User that was not found.
            username: The username of the User that was not found.

        """
        super().__init__(f"User with ID {user_id} / username {username} not found.")


class UserAlreadyExistError(Exception):
    """Exception raised when a User with a given name already exists."""

    def __init__(self, username: str, email: str) -> None:
        """Initialize the exception.

        Args:
            username: The username that already exists.
            email: The email that already exists.

        """
        super().__init__(f"User with name '{username}' and email '{email}' already exists.")
