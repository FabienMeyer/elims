"""API routes for the API authenticator module."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from elims.api.db import get_session
from elims.api.modules.authenticator.exceptions import HTTP_401_UNAUTHORIZED
from elims.api.modules.authenticator.schemas import TokenRequest
from elims.api.modules.authenticator.services import AuthenticatorService
from elims.api.modules.users.services import UserService

router_collection: APIRouter = APIRouter(prefix="/authentications", tags=["authentications"])
router_resource: APIRouter = APIRouter(prefix="/authentication", tags=["authentication"])


@router_resource.post("/token")
async def login_for_access_token(
    token_request: TokenRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, str]:
    """Endpoint to obtain an access token."""
    user_service = UserService(session=session)
    user = await user_service.get_by_username(token_request.username)

    if not user:
        raise HTTP_401_UNAUTHORIZED

    authenticator_service = AuthenticatorService(
        session=session,
        user=user,
        password=user.hashed_password,
    )

    if not authenticator_service.is_password_valid(token_request.password):
        raise HTTP_401_UNAUTHORIZED

    access_token = authenticator_service.create_access_token({"sub": user.username, "scopes": []})
    return {"access_token": access_token, "token_type": "bearer"}
