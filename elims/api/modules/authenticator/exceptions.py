"""Exceptions for the API authenticator module."""


class AuthenticatorCredentialsInvalidError(Exception):
    """Exception raised when credentials are invalid."""

    def __init__(self) -> None:
        """Initialize the exception."""
        super().__init__("Could not validate credentials")


class AuthenticatorScopesInsufficientError(Exception):
    """Exception raised when user lacks required scopes."""

    def __init__(self) -> None:
        """Initialize the exception."""
        super().__init__("Not enough permissions")
