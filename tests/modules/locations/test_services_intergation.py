"""Integration tests for the API locations module services with real SQLite database.

These tests verify the service layer works with actual database constraints
and transactions, using an in-memory SQLite database for fast testing.
"""

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from elims.modules.locations.schemas import LocationCreate, LocationUpdate
from elims.modules.locations.services import LocationService

# Constants for testing
EXPECTED_LOCATIONS_COUNT_IN_TEST = 2


@pytest_asyncio.fixture
async def async_session_test() -> AsyncGenerator[AsyncSession]:
    """Create an in-memory SQLite database for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = AsyncSession(engine, expire_on_commit=False)
    yield async_session
    await async_session.close()
    await engine.dispose()


class TestLocationServiceIntegration:
    """Integration tests with real database."""

    @pytest.mark.asyncio
    async def test_create_and_retrieve_location(self, async_session_test: AsyncSession) -> None:
        """Test creating and retrieving a location with real database."""
        service = LocationService(session=async_session_test)

        location_data = LocationCreate(
            address="123 Main Street",
            postal_code="75001",
            city="Paris",
            state="Île-de-France",
            country="France",
        )

        # Create
        created = await service.create(location_data)
        assert created.id is not None
        assert created.address == "123 Main Street"

        # Retrieve
        retrieved = await service.get(created.id)
        assert retrieved.address == created.address

    @pytest.mark.asyncio
    async def test_create_multiple_locations(self, async_session_test: AsyncSession) -> None:
        """Test creating multiple locations with real database."""
        service = LocationService(session=async_session_test)

        location_data_1 = LocationCreate(
            address="123 Main Street",
            postal_code="75001",
            city="Paris",
            state="Île-de-France",
            country="France",
        )

        location_data_2 = LocationCreate(
            address="456 Oak Avenue",
            postal_code="69001",
            city="Lyon",
            state="Auvergne",
            country="France",
        )

        # Create first
        first_result = await service.create(location_data_1)
        assert first_result.id is not None

        # Create second
        second_result = await service.create(location_data_2)
        assert second_result.id is not None
        assert first_result.id != second_result.id

    @pytest.mark.asyncio
    async def test_get_all_locations(self, async_session_test: AsyncSession) -> None:
        """Test retrieving all locations from the database."""
        service = LocationService(session=async_session_test)

        location_data_1 = LocationCreate(
            address="123 Main Street",
            postal_code="75001",
            city="Paris",
            state="Île-de-France",
            country="France",
        )

        location_data_2 = LocationCreate(
            address="456 Oak Avenue",
            postal_code="69001",
            city="Lyon",
            state="Auvergne",
            country="France",
        )

        # Create two locations
        await service.create(location_data_1)
        await service.create(location_data_2)

        # Retrieve all
        all_locations = await service.gets()
        assert len(all_locations) == EXPECTED_LOCATIONS_COUNT_IN_TEST

    @pytest.mark.asyncio
    async def test_update_location(self, async_session_test: AsyncSession) -> None:
        """Test updating a location with real database."""
        service = LocationService(session=async_session_test)

        location_data = LocationCreate(
            address="123 Main Street",
            postal_code="75001",
            city="Paris",
            state="Île-de-France",
            country="France",
        )

        # Create
        created = await service.create(location_data)
        location_id = created.id

        # Update
        update_data = LocationUpdate(city="Lyon", state="Auvergne")
        updated = await service.update(location_id, update_data)

        assert updated.city == "Lyon"
        assert updated.state == "Auvergne"
        assert updated.address == "123 Main Street"  # Unchanged field

    @pytest.mark.asyncio
    async def test_delete_location(self, async_session_test: AsyncSession) -> None:
        """Test deleting a location with real database."""
        service = LocationService(session=async_session_test)

        location_data = LocationCreate(
            address="123 Main Street",
            postal_code="75001",
            city="Paris",
            state="Île-de-France",
            country="France",
        )

        # Create
        created = await service.create(location_data)
        location_id = created.id

        # Delete
        await service.delete(location_id)

        # Verify it's deleted
        all_locations = await service.gets()
        assert len(all_locations) == 0
