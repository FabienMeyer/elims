"""Services for the API users module."""

from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from elims.api.modules.authenticator.services import PasswordHasher
from elims.api.modules.users.exceptions import (
    UserAlreadyExistError,
    UserNotFoundError,
)
from elims.api.modules.users.models import User
from elims.api.modules.users.schemas import UserCreate, UserRead, UserUpdate


class UserService:
    """Encapsulates CRUD operations for the User model."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the service with an async database session.

        Args:
            session: The asynchronous database session.

        """
        self.session = session
        logger.debug(f"UserService initialized with async session: {session}")

    async def create(self, user_data: UserCreate) -> UserRead:
        """Create a new user in the database.

        Args:
            user_data: The data for the new user.

        Returns:
            The newly created user with its database ID.

        Raises:
            UserAlreadyExistError: If a user with the same
                username or email already exists.

        """
        try:
            # Hash the password before storing
            hashed_password = PasswordHasher.get_password_hash(user_data.password)
            user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
            )
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            logger.info(f"Created user with ID: {user.id}")
            return UserRead.model_validate(user)
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Failed to create user: {e}")
            raise UserAlreadyExistError(user_data.username, user_data.email) from e

    async def get(self, user_id: int) -> UserRead:
        """Retrieve a user by its ID.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            The user with the specified ID.

        Raises:
            UserNotFoundError: If no user with the given ID exists.

        """
        query = select(User).where(User.id == user_id)
        result = await self.session.exec(query)
        user = result.one_or_none()
        if user is None:
            logger.warning(f"User with ID {user_id} not found.")
            raise UserNotFoundError(user_id)
        logger.info(f"Retrieved user with ID: {user_id}")
        return UserRead.model_validate(user)

    async def update(self, user_id: int, user_data: UserUpdate) -> UserRead:
        """Update an existing user in the database.

        Args:
            user_id: The ID of the user to update.
            user_data: The updated data for the user.

        Returns:
            The updated user.

        Raises:
            UserNotFoundError: If no user with the given ID exists.
            UserAlreadyExistError: If updating the user results in a
                username or email conflict.

        """
        query = select(User).where(User.id == user_id)
        result = await self.session.exec(query)
        user = result.one_or_none()
        if user is None:
            logger.warning(f"User with ID {user_id} not found for update.")
            raise UserNotFoundError(user_id)

        update_data = user_data.model_dump(exclude_unset=True)
        # Hash password if provided
        if getattr(user_data, "password", None) is not None:
            update_data["hashed_password"] = PasswordHasher.get_password_hash(update_data.pop("password"))

        for key, value in update_data.items():
            setattr(user, key, value)

        try:
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            logger.info(f"Updated user with ID: {user_id}")
            return UserRead.model_validate(user)
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Failed to update user: {e}")
            username = update_data.get("username", user.username)
            email = update_data.get("email", user.email)
            raise UserAlreadyExistError(username, email) from e

    async def delete(self, user_id: int) -> None:
        """Delete a user from the database.

        Args:
            user_id: The ID of the user to delete.

        Raises:
            UserNotFoundError: If no user with the given ID exists.

        """
        query = select(User).where(User.id == user_id)
        result = await self.session.exec(query)
        user = result.one_or_none()
        if user is None:
            logger.warning(f"User with ID {user_id} not found for deletion.")
            raise UserNotFoundError(user_id)

        await self.session.delete(user)
        await self.session.commit()
        logger.info(f"Deleted user with ID: {user_id}")

    async def gets(self) -> list[UserRead]:
        """Retrieve all users from the database.

        Returns:
            A list of all users.

        """
        query = select(User)
        result = await self.session.exec(query)
        users = result.all()
        logger.info(f"Retrieved {len(users)} users from the database.")
        return [UserRead.model_validate(user) for user in users]

    async def get_by_username(self, username: str) -> UserRead:
        """Retrieve a user by their username.

        Args:
            username: The username to search for.

        Returns:
            The user with the specified username.

        Raises:
            UserNotFoundByUsernameError: If no user with the given username exists.

        """
        query = select(User).where(User.username == username)
        result = await self.session.exec(query)
        user = result.one_or_none()
        if user is None:
            logger.warning(f"User with username {username} not found.")
            raise UserNotFoundError(None, username)
        logger.info(f"Retrieved user with username: {username}")
        return UserRead.model_validate(user)
