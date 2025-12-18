"""Services for the API authenticator module."""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from pwdlib import PasswordHash
from sqlmodel.ext.asyncio.session import AsyncSession

from elims.api.modules.authenticator.exceptions import (
    AuthenticatorCredentialsInvalidError,
    AuthenticatorScopesInsufficientError,
)
from elims.api.modules.users.schemas import UserRead
from elims.api.modules.users.services import UserService
from elims.config import settings


class PasswordHasher:
    """Encapsulates password hashing operations."""

    PASSWORD_HASH = PasswordHash.recommended()

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a plain password.

        Args:
            password: The plain password to hash.

        Returns:
            The hashed password.

        """
        encoded: str = PasswordHasher.PASSWORD_HASH.hash(password)
        return encoded

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a plain password against its hashed version.

        Args:
            password: The plain password to verify.
            hashed_password: The hashed password to verify against.

        Returns:
            True if the password is valid, False otherwise.

        """
        is_valid: bool = PasswordHasher.PASSWORD_HASH.verify(password, hashed_password)
        return is_valid


class AuthenticatorService:
    """Encapsulates Authenticator operations."""

    OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="token")

    def __init__(self, session: AsyncSession, user: UserRead, password: str) -> None:
        """Initialize the AuthenticatorService."""
        self.session = session
        self.user = user
        self.password = password

    def is_password_valid(self, password: str) -> bool:
        """Verify a plain password against its hashed version.

        Args:
            password: The plain password to verify.

        Returns:
            True if the password is valid, False otherwise.

        """
        return PasswordHasher.verify_password(password, self.user.hashed_password)

    def create_access_token(self, payload: dict[str, str | list[str]]) -> str:
        """Create an OAuth2 access token.

        Args:
            payload: The token payload containing sub and scopes.

        Returns:
            The encoded JWT token as a string.

        """
        to_encode: dict[str, Any] = payload.copy()
        expire = datetime.now(UTC) + timedelta(minutes=settings.token_access_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt: str = jwt.encode(to_encode, settings.token_secret_key, algorithm=settings.token_algorithm)
        return encoded_jwt

    async def get_current_user(self, security_scopes: SecurityScopes, token: str) -> UserRead:
        """Decode the JWT token to retrieve the current user.

        Args:
            security_scopes: The required scopes for the current operation.
            token: The JWT token.

        Returns:
            The user object extracted from the token.

        Raises:
            AuthenticatorCredentialsInvalidError: If the token is invalid or expired.
            AuthenticatorScopesInsufficientError: If user lacks required scopes.

        """
        try:
            payload = jwt.decode(
                token,
                settings.token_secret_key,
                algorithms=[settings.token_algorithm],
            )
            username: str | None = payload.get("sub")
            scope: list[str] = payload.get("scopes", [])
            if username is None:
                raise AuthenticatorCredentialsInvalidError
        except jwt.PyJWTError:
            raise AuthenticatorCredentialsInvalidError from None

        for required_scope in security_scopes.scopes:
            if required_scope not in scope:
                raise AuthenticatorScopesInsufficientError

        user_service = UserService(session=self.session)
        return await user_service.get_by_username(username)

    def validate_credentials(self, password: str) -> None:
        """Validate user credentials.

        Args:
            user: The user object from the database.
            authenticator_service: The authenticator service instance.
            password: The password to validate.

        Raises:
            AuthenticatorCredentialsInvalidError: If user not found or password is invalid.

        """
        if not self.is_password_valid(password):
            raise AuthenticatorCredentialsInvalidError
