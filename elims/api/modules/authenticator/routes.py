"""API routes for the API authenticator module."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlmodel.ext.asyncio.session import AsyncSession

from elims.api.db import get_session
from elims.api.modules.authenticator.exceptions import AuthenticatorCredentialsInvalidError
from elims.api.modules.authenticator.schemas import Token, TokenRequest
from elims.api.modules.authenticator.services import AuthenticatorService
from elims.api.modules.users.services import UserService

router_collection: APIRouter = APIRouter(prefix="/authentications", tags=["authentications"])
router_resource: APIRouter = APIRouter(prefix="/authentication", tags=["authentication"])


@router_resource.post("/token", status_code=status.HTTP_200_OK)
async def login_for_access_token(
    token_request: TokenRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Token:
    """Endpoint to obtain an access token.

    Args:
        token_request: The token request containing username and password.
        session: The asynchronous database session.

    Returns:
        Token response with access token and token type.

    Raises:
        HTTPException: If credentials are invalid.

    """
    try:
        user_service = UserService(session=session)
        user = await user_service.get_by_username(token_request.username)

        authenticator_service = AuthenticatorService(
            session=session,
            user=user,
            password=user.hashed_password if user else "",
        )
        authenticator_service.validate_credentials(token_request.password)
        access_token = authenticator_service.create_access_token({"sub": user.username, "scopes": []})
        return Token(access_token=access_token, token_type="bearer")  # noqa: S106
    except AuthenticatorCredentialsInvalidError as e:
        detail = str(e)
        logger.warning(f"Login failed: {detail}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
