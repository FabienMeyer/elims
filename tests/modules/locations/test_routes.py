"""Tests routes for the API locations module.

This file contains tests for location API routes.
"""

from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from elims.api.modules.locations import routes
from elims.api.modules.locations.exceptions import (
    LocationAlreadyExistError,
    LocationNotFoundError,
)
from elims.api.modules.locations.schemas import (
    LocationCreate,
    LocationRead,
    LocationUpdate,
)
from elims.api.modules.locations.services import LocationService

# Constants for testing
EXPECTED_LOCATIONS_COUNT = 3


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create a mock async database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_service() -> AsyncMock:
    """Create a mock LocationService."""
    return AsyncMock()


@pytest.fixture
def sample_location_read() -> LocationRead:
    """Create a sample location read schema with ID."""
    return LocationRead(
        id=1,
        address="123 Main Street",
        postal_code="75001",
        city="Paris",
        state="Île-de-France",
        country="France",
    )


class TestLocationRoutesExist:
    """Tests for the existence of routes."""

    def test_routes_module_exists(self) -> None:
        """Test that routes module can be imported."""
        assert routes is not None
        assert hasattr(routes, "router_collection")
        assert hasattr(routes, "router_resource")
        assert hasattr(routes, "get_location_service")

    @pytest.mark.asyncio
    async def test_get_location_service_dependency(self) -> None:
        """Test that get_location_service returns a LocationService instance."""
        mock_session = AsyncMock(spec=AsyncSession)
        service = await routes.get_location_service(mock_session)

        assert isinstance(service, LocationService)
        assert service.session is mock_session


class TestCreateLocationRoutes:
    """Tests for create location endpoints."""

    @pytest.mark.asyncio
    async def test_create_location_success(self, mock_service: AsyncMock, sample_location_read: LocationRead) -> None:
        """Test successful single location creation."""
        location_data = LocationCreate(
            address="123 Main Street",
            postal_code="75001",
            city="Paris",
            state="Île-de-France",
            country="France",
        )

        mock_service.create.return_value = sample_location_read

        result = await routes.create_location(location_data, mock_service)

        assert result is not None
        assert result.id == sample_location_read.id
        mock_service.create.assert_called_once_with(location_data)

    @pytest.mark.asyncio
    async def test_create_location_conflict(self, mock_service: AsyncMock) -> None:
        """Test creation fails on duplicate location with same address, city, and postal code."""
        location_data = LocationCreate(
            address="123 Main Street",
            postal_code="75001",
            city="Paris",
            state="Île-de-France",
            country="France",
        )

        # Duplicate error when same address, city, and postal_code already exist
        mock_service.create.side_effect = LocationAlreadyExistError("123 Main Street, 75001, Paris")

        with pytest.raises(HTTPException) as exc_info:
            await routes.create_location(location_data, mock_service)

        assert exc_info.value.status_code == status.HTTP_409_CONFLICT


class TestGetLocationRoutes:
    """Tests for get location endpoints."""

    @pytest.mark.asyncio
    async def test_get_location_success(self, mock_service: AsyncMock, sample_location_read: LocationRead) -> None:
        """Test successful retrieval of a single location."""
        mock_service.get.return_value = sample_location_read

        result = await routes.get_location(1, mock_service)

        assert result is not None
        assert result.id == sample_location_read.id
        mock_service.get.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_location_not_found(self, mock_service: AsyncMock) -> None:
        """Test retrieval fails when location not found."""
        mock_service.get.side_effect = LocationNotFoundError(999)

        with pytest.raises(HTTPException) as exc_info:
            await routes.get_location(999, mock_service)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_locations_success(self, mock_service: AsyncMock) -> None:
        """Test successful listing of all locations."""
        all_locations = [
            LocationRead(
                id=i + 1,
                address=f"{100 + i} Main Street",
                postal_code=f"{75000 + i:05d}",
                city="Paris",
                state="Île-de-France",
                country="France",
            )
            for i in range(EXPECTED_LOCATIONS_COUNT)
        ]

        mock_service.gets.return_value = all_locations

        result = await routes.get_locations(mock_service)

        assert len(result) == EXPECTED_LOCATIONS_COUNT
        assert all(isinstance(item, LocationRead) for item in result)
        mock_service.gets.assert_called_once()


class TestUpdateLocationRoutes:
    """Tests for update location endpoints."""

    @pytest.mark.asyncio
    async def test_update_location_success(self, mock_service: AsyncMock) -> None:
        """Test successful update of a single location."""
        update_data = LocationUpdate(address="456 Oak Avenue")

        updated_read = LocationRead(
            id=1,
            address="456 Oak Avenue",
            postal_code="75001",
            city="Paris",
            state="Île-de-France",
            country="France",
        )

        mock_service.update.return_value = updated_read

        result = await routes.update_location(1, update_data, mock_service)

        assert result is not None
        assert result.address == "456 Oak Avenue"
        mock_service.update.assert_called_once_with(1, update_data)

    @pytest.mark.asyncio
    async def test_update_location_not_found(self, mock_service: AsyncMock) -> None:
        """Test update fails when location not found."""
        update_data = LocationUpdate(address="456 Oak Avenue")
        mock_service.update.side_effect = LocationNotFoundError(999)

        with pytest.raises(HTTPException) as exc_info:
            await routes.update_location(999, update_data, mock_service)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_location_conflict(self, mock_service: AsyncMock) -> None:
        """Test update fails on location conflict."""
        update_data = LocationUpdate(address="999 New Street")
        mock_service.update.side_effect = LocationAlreadyExistError("999 New Street")

        with pytest.raises(HTTPException) as exc_info:
            await routes.update_location(1, update_data, mock_service)

        assert exc_info.value.status_code == status.HTTP_409_CONFLICT


class TestDeleteLocationRoutes:
    """Tests for delete location endpoints."""

    @pytest.mark.asyncio
    async def test_delete_location_success(self, mock_service: AsyncMock) -> None:
        """Test successful deletion of a single location."""
        mock_service.delete.return_value = None

        await routes.delete_location(1, mock_service)

        mock_service.delete.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_delete_location_not_found(self, mock_service: AsyncMock) -> None:
        """Test deletion fails when location not found."""
        mock_service.delete.side_effect = LocationNotFoundError(999)

        with pytest.raises(HTTPException) as exc_info:
            await routes.delete_location(999, mock_service)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
