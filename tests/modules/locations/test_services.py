"""Tests for the API locations module services.

These tests verify the service layer interface and error handling.
Integration tests would require a real database or more complex mocking.
"""

import inspect
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from elims.api.modules.locations import schemas, services
from elims.api.modules.locations.exceptions import (
    LocationAlreadyExistError,
    LocationNotFoundError,
)
from elims.api.modules.locations.models import Location
from elims.api.modules.locations.schemas import (
    LocationCreate,
    LocationRead,
    LocationUpdate,
)

# Constants for testing
EXPECTED_LOCATIONS_COUNT = 3


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create a mock async database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def sample_location_create() -> LocationCreate:
    """Create a sample location creation schema."""
    return LocationCreate(
        address="123 Main Street",
        postal_code="75001",
        city="Paris",
        state="Île-de-France",
        country="France",
    )


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


class TestLocationServiceCreate:
    """Tests for the create method of LocationService."""

    def test_location_service_initialization(self) -> None:
        """Test that LocationService can be instantiated."""
        assert schemas is not None
        assert hasattr(services, "LocationService")

    @pytest.mark.asyncio
    async def test_locations_services_create(self, mock_session: AsyncMock, sample_location_create: LocationCreate) -> None:
        """Test that LocationService has a create method."""
        service = services.LocationService(session=mock_session)

        assert hasattr(service, "create")
        assert inspect.iscoroutinefunction(service.create)

        # Mock the session methods
        mock_location = MagicMock(spec=Location)
        mock_location.address = sample_location_create.address
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Mock Location.model_validate to return our mock
        with patch.object(Location, "model_validate", return_value=mock_location), patch.object(LocationRead, "model_validate") as mock_read:
            mock_read.return_value = LocationRead(
                id=1,
                address=sample_location_create.address,
                postal_code=sample_location_create.postal_code,
                city=sample_location_create.city,
                state=sample_location_create.state,
                country=sample_location_create.country,
            )

            result = await service.create(sample_location_create)

            assert result is not None
            assert result.address == sample_location_create.address
            mock_session.add.assert_called_once_with(mock_location)
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once_with(mock_location)

    @pytest.mark.asyncio
    async def test_create_location_success(self, mock_session: AsyncMock, sample_location_create: LocationCreate) -> None:
        """Test successful creation of a location."""
        service = services.LocationService(session=mock_session)

        # Mock the session methods
        mock_location = MagicMock(spec=Location)
        mock_location.address = sample_location_create.address
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Mock Location.model_validate to return our mock
        with patch.object(Location, "model_validate", return_value=mock_location), patch.object(LocationRead, "model_validate") as mock_read:
            mock_read.return_value = LocationRead(
                id=1,
                address=sample_location_create.address,
                postal_code=sample_location_create.postal_code,
                city=sample_location_create.city,
                state=sample_location_create.state,
                country=sample_location_create.country,
            )

            result = await service.create(sample_location_create)

            assert result is not None
            assert result.address == sample_location_create.address
            mock_session.add.assert_called_once_with(mock_location)
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once_with(mock_location)

    @pytest.mark.asyncio
    async def test_create_location_duplicate_address(self, mock_session: AsyncMock, sample_location_create: LocationCreate) -> None:
        """Test creation fails when address, city, and postal_code already exist."""
        service = services.LocationService(session=mock_session)

        # Mock the session to raise IntegrityError
        mock_location = MagicMock(spec=Location)
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock(side_effect=IntegrityError("Duplicate entry", "INSERT", ValueError("Unique constraint violation")))
        mock_session.rollback = AsyncMock()

        with patch.object(Location, "model_validate", return_value=mock_location):
            with pytest.raises(LocationAlreadyExistError) as exc_info:
                await service.create(sample_location_create)

            # Error message should contain the combination of address, postal_code, and city
            assert sample_location_create.address in str(exc_info.value)
            assert sample_location_create.postal_code in str(exc_info.value)
            assert sample_location_create.city in str(exc_info.value)
            mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_location_success(self, mock_session: AsyncMock, sample_location_read: LocationRead) -> None:
        """Test successful retrieval of a location."""
        service = services.LocationService(session=mock_session)

        mock_location = MagicMock(spec=Location)
        mock_result = AsyncMock()
        mock_result.one_or_none = MagicMock(return_value=mock_location)
        mock_session.exec = AsyncMock(return_value=mock_result)

        with patch.object(LocationRead, "model_validate", return_value=sample_location_read):
            result = await service.get(1)

            assert result is not None
            assert result.id == sample_location_read.id
            mock_session.exec.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_location_not_found(self, mock_session: AsyncMock) -> None:
        """Test retrieval fails when location is not found."""
        service = services.LocationService(session=mock_session)

        mock_result = AsyncMock()
        mock_result.one_or_none = MagicMock(return_value=None)
        mock_session.exec = AsyncMock(return_value=mock_result)

        with pytest.raises(LocationNotFoundError) as exc_info:
            await service.get(999)

        assert "999" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_location_success(self, mock_session: AsyncMock) -> None:
        """Test successful update of a location."""
        service = services.LocationService(session=mock_session)

        # Setup mock location
        mock_location = MagicMock(spec=Location)
        mock_location.address = "123 Main Street"
        mock_result = AsyncMock()
        mock_result.one_or_none = MagicMock(return_value=mock_location)
        mock_session.exec = AsyncMock(return_value=mock_result)
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Create update data
        update_data = LocationUpdate(city="Lyon")

        with patch.object(LocationRead, "model_validate") as mock_read:
            mock_read.return_value = LocationRead(
                id=1,
                address="123 Main Street",
                postal_code="75001",
                city="Lyon",
                state="Auvergne",
                country="France",
            )

            result = await service.update(1, update_data)

            assert result is not None
            assert result.city == "Lyon"
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_location_not_found(self, mock_session: AsyncMock) -> None:
        """Test update fails when location is not found."""
        service = services.LocationService(session=mock_session)

        mock_result = AsyncMock()
        mock_result.one_or_none = MagicMock(return_value=None)
        mock_session.exec = AsyncMock(return_value=mock_result)

        update_data = LocationUpdate(city="Lyon")

        with pytest.raises(LocationNotFoundError) as exc_info:
            await service.update(999, update_data)

        assert "999" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_location_duplicate_address(self, mock_session: AsyncMock) -> None:
        """Test update fails when changing to a duplicate address."""
        service = services.LocationService(session=mock_session)

        # Setup mock location
        mock_location = MagicMock(spec=Location)
        mock_location.address = "123 Main Street"
        mock_result = AsyncMock()
        mock_result.one_or_none = MagicMock(return_value=mock_location)
        mock_session.exec = AsyncMock(return_value=mock_result)
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock(side_effect=IntegrityError("Duplicate entry", "INSERT", ValueError("Unique constraint violation")))
        mock_session.rollback = AsyncMock()

        update_data = LocationUpdate(address="456 Oak Avenue")

        with pytest.raises(LocationAlreadyExistError):
            await service.update(1, update_data)

        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_location_success(self, mock_session: AsyncMock) -> None:
        """Test successful deletion of a location."""
        service = services.LocationService(session=mock_session)

        mock_location = MagicMock(spec=Location)
        mock_result = AsyncMock()
        mock_result.one_or_none = MagicMock(return_value=mock_location)
        mock_session.exec = AsyncMock(return_value=mock_result)
        mock_session.delete = AsyncMock()
        mock_session.commit = AsyncMock()

        await service.delete(1)

        mock_session.delete.assert_called_once_with(mock_location)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_location_not_found(self, mock_session: AsyncMock) -> None:
        """Test deletion fails when location is not found."""
        service = services.LocationService(session=mock_session)

        mock_result = AsyncMock()
        mock_result.one_or_none = MagicMock(return_value=None)
        mock_session.exec = AsyncMock(return_value=mock_result)

        with pytest.raises(LocationNotFoundError) as exc_info:
            await service.delete(999)

        assert "999" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_gets_locations_empty(self, mock_session: AsyncMock) -> None:
        """Test listing all locations when database is empty."""
        service = services.LocationService(session=mock_session)

        # Mock the exec().all() pattern
        mock_result = AsyncMock()
        mock_result.all = MagicMock(return_value=[])
        mock_session.exec = AsyncMock(return_value=mock_result)

        result = await service.gets()

        assert result == []
        mock_session.exec.assert_called_once()

    @pytest.mark.asyncio
    async def test_gets_locations_multiple(self, mock_session: AsyncMock) -> None:
        """Test listing all locations with multiple records."""
        service = services.LocationService(session=mock_session)

        mock_locations = [MagicMock(spec=Location) for _ in range(EXPECTED_LOCATIONS_COUNT)]
        mock_result = AsyncMock()
        mock_result.all = MagicMock(return_value=mock_locations)
        mock_session.exec = AsyncMock(return_value=mock_result)

        expected_reads = [
            LocationRead(
                id=i + 1,
                address=f"{100 + i} Main Street",
                postal_code=f"{75000 + i:05d}",
                city="Paris" if i == 0 else "Lyon" if i == 1 else "Marseille",
                state="Ile-de-France" if i == 0 else "Provence" if i == 1 else "Alsace",
                country="France",
            )
            for i in range(EXPECTED_LOCATIONS_COUNT)
        ]

        with patch.object(LocationRead, "model_validate", side_effect=expected_reads):
            result = await service.gets()

            assert len(result) == EXPECTED_LOCATIONS_COUNT
            assert all(isinstance(item, LocationRead) for item in result)
