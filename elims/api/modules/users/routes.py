"""API routes for the API users module."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlmodel.ext.asyncio.session import AsyncSession

from elims.api.db import get_session
from elims.api.modules.users.exceptions import (
    UserAlreadyExistError,
    UserNotFoundError,
)
from elims.api.modules.users.schemas import UserCreate, UserRead, UserUpdate
from elims.api.modules.users.services import UserService

router_collection: APIRouter = APIRouter(prefix="/users", tags=["users"])
router_resource: APIRouter = APIRouter(prefix="/user", tags=["user"])


async def get_user_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserService:
    """Instantiate and provide the UserService.

    Args:
        session: The asynchronous database session.

    Returns:
        An instance of UserService.

    """
    return UserService(session=session)


@router_resource.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserRead:
    """Create a new user.

    Args:
        user_data: The user data for creation.
        service: The user service dependency.

    Returns:
        The created user with its database ID.

    Raises:
        HTTPException: If a user with the same name or email already exists.

    """
    try:
        return await service.create(user_data)
    except UserAlreadyExistError as e:
        detail = str(e)
        logger.warning(f"Create user failed: {detail}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from e


@router_resource.get("/{user_id}")
async def get_user(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserRead:
    """Retrieve a user by ID.

    Args:
        user_id: The ID of the user to retrieve.
        service: The user service dependency.

    Returns:
        The retrieved user.

    Raises:
        HTTPException: If the user is not found.

    """
    try:
        return await service.get(user_id)
    except UserNotFoundError as e:
        detail = str(e)
        logger.warning(f"Get user failed: {detail}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail) from e


@router_resource.patch("/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserRead:
    """Update an existing user.

    Args:
        user_id: The ID of the user to update.
        user_data: The updated user data.
        service: The user service dependency.

    Returns:
        The updated user.

    Raises:
        HTTPException: If the user is not found.

    """
    try:
        return await service.update(user_id, user_data)
    except UserNotFoundError as e:
        detail = str(e)
        logger.warning(f"Update user failed: {detail}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail) from e
    except UserAlreadyExistError as e:
        detail = str(e)
        logger.warning(f"Update user failed: {detail}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from e


@router_resource.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
) -> None:
    """Delete a user by ID.

    Args:
        user_id: The ID of the user to delete.
        service: The user service dependency.

    Raises:
        HTTPException: If the user is not found.

    """
    try:
        await service.delete(user_id)
    except UserNotFoundError as e:
        detail = str(e)
        logger.warning(f"Delete user failed: {detail}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail) from e


@router_collection.get("/")
async def get_users(
    service: Annotated[UserService, Depends(get_user_service)],
) -> list[UserRead]:
    """Retrieve all users.

    Args:
        service: The user service dependency.

    Returns:
        A list of all users.

    """
    return await service.gets()
