"""Tests routes for the API instruments module.

This file contains tests for instrument API routes.
"""

from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from elims.modules.instruments import routes
from elims.modules.instruments.constants import InstrumentBrand, InstrumentType
from elims.modules.instruments.exceptions import (
    InstrumentAlreadyExistError,
    InstrumentNotFoundError,
)
from elims.modules.instruments.schemas import (
    InstrumentCreate,
    InstrumentRead,
    InstrumentUpdate,
)
from elims.modules.instruments.services import InstrumentService

# Constants for testing
EXPECTED_INSTRUMENTS_COUNT = 3


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create a mock async database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_service() -> AsyncMock:
    """Create a mock InstrumentService."""
    return AsyncMock()


@pytest.fixture
def sample_instrument_read() -> InstrumentRead:
    """Create a sample instrument read schema with ID."""
    return InstrumentRead(
        id=1,
        brand=InstrumentBrand.ANRITSU,
        type=InstrumentType.SPECTRUM_ANALYZER,
        model="MS2023A",
        serial_number="SN123456",
    )


class TestInstrumentRoutesExist:
    """Tests for the existence of routes."""

    def test_routes_module_exists(self) -> None:
        """Test that routes module can be imported."""
        assert routes is not None
        assert hasattr(routes, "router_collection")
        assert hasattr(routes, "router_resource")
        assert hasattr(routes, "get_instrument_service")

    @pytest.mark.asyncio
    async def test_get_instrument_service_dependency(self) -> None:
        """Test that get_instrument_service returns an InstrumentService instance."""
        mock_session = AsyncMock(spec=AsyncSession)
        service = await routes.get_instrument_service(mock_session)

        assert isinstance(service, InstrumentService)
        assert service.session is mock_session


class TestCreateInstrumentRoutes:
    """Tests for create instrument endpoints."""

    @pytest.mark.asyncio
    async def test_create_instrument_success(self, mock_service: AsyncMock, sample_instrument_read: InstrumentRead) -> None:
        """Test successful single instrument creation."""
        instrument_data = InstrumentCreate(
            brand=InstrumentBrand.ANRITSU,
            type=InstrumentType.SPECTRUM_ANALYZER,
            model="MS2023A",
            serial_number="SN123456",
        )

        mock_service.create.return_value = sample_instrument_read

        result = await routes.create_instrument(instrument_data, mock_service)

        assert result is not None
        assert result.id == sample_instrument_read.id
        mock_service.create.assert_called_once_with(instrument_data)

    @pytest.mark.asyncio
    async def test_create_instrument_conflict(self, mock_service: AsyncMock) -> None:
        """Test creation fails on duplicate serial number."""
        instrument_data = InstrumentCreate(
            brand=InstrumentBrand.ANRITSU,
            type=InstrumentType.SPECTRUM_ANALYZER,
            model="MS2023A",
            serial_number="SN123456",
        )

        mock_service.create.side_effect = InstrumentAlreadyExistError("SN123456")

        with pytest.raises(HTTPException) as exc_info:
            await routes.create_instrument(instrument_data, mock_service)

        assert exc_info.value.status_code == status.HTTP_409_CONFLICT


class TestGetInstrumentRoutes:
    """Tests for get instrument endpoints."""

    @pytest.mark.asyncio
    async def test_get_instrument_success(self, mock_service: AsyncMock, sample_instrument_read: InstrumentRead) -> None:
        """Test successful retrieval of a single instrument."""
        mock_service.get.return_value = sample_instrument_read

        result = await routes.get_instrument(1, mock_service)

        assert result is not None
        assert result.id == sample_instrument_read.id
        mock_service.get.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_instrument_not_found(self, mock_service: AsyncMock) -> None:
        """Test retrieval fails when instrument not found."""
        mock_service.get.side_effect = InstrumentNotFoundError(999)

        with pytest.raises(HTTPException) as exc_info:
            await routes.get_instrument(999, mock_service)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_gets_instruments_success(self, mock_service: AsyncMock) -> None:
        """Test successful listing of all instruments."""
        all_instruments = [
            InstrumentRead(
                id=i + 1,
                brand=InstrumentBrand.ANRITSU,
                type=InstrumentType.SPECTRUM_ANALYZER,
                model=f"MS202{i}A",
                serial_number=f"SN{i:06d}",
            )
            for i in range(EXPECTED_INSTRUMENTS_COUNT)
        ]

        mock_service.gets.return_value = all_instruments

        result = await routes.gets_instruments(mock_service)

        assert len(result) == EXPECTED_INSTRUMENTS_COUNT
        assert all(isinstance(item, InstrumentRead) for item in result)
        mock_service.gets.assert_called_once()


class TestUpdateInstrumentRoutes:
    """Tests for update instrument endpoints."""

    @pytest.mark.asyncio
    async def test_update_instrument_success(self, mock_service: AsyncMock) -> None:
        """Test successful update of a single instrument."""
        update_data = InstrumentUpdate(model="MS2024A")

        updated_read = InstrumentRead(
            id=1,
            brand=InstrumentBrand.ANRITSU,
            type=InstrumentType.SPECTRUM_ANALYZER,
            model="MS2024A",
            serial_number="SN123456",
        )

        mock_service.update.return_value = updated_read

        result = await routes.update_instrument(1, update_data, mock_service)

        assert result is not None
        assert result.model == "MS2024A"
        mock_service.update.assert_called_once_with(1, update_data)

    @pytest.mark.asyncio
    async def test_update_instrument_not_found(self, mock_service: AsyncMock) -> None:
        """Test update fails when instrument not found."""
        update_data = InstrumentUpdate(model="MS2024A")
        mock_service.update.side_effect = InstrumentNotFoundError(999)

        with pytest.raises(HTTPException) as exc_info:
            await routes.update_instrument(999, update_data, mock_service)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_instrument_conflict(self, mock_service: AsyncMock) -> None:
        """Test update fails on serial number conflict."""
        update_data = InstrumentUpdate(serial_number="SN999999")
        mock_service.update.side_effect = InstrumentAlreadyExistError("SN999999")

        with pytest.raises(HTTPException) as exc_info:
            await routes.update_instrument(1, update_data, mock_service)

        assert exc_info.value.status_code == status.HTTP_409_CONFLICT


class TestDeleteInstrumentRoutes:
    """Tests for delete instrument endpoints."""

    @pytest.mark.asyncio
    async def test_delete_instrument_success(self, mock_service: AsyncMock) -> None:
        """Test successful deletion of a single instrument."""
        mock_service.delete.return_value = None

        await routes.delete_instrument(1, mock_service)

        mock_service.delete.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_delete_instrument_not_found(self, mock_service: AsyncMock) -> None:
        """Test deletion fails when instrument not found."""
        mock_service.delete.side_effect = InstrumentNotFoundError(999)

        with pytest.raises(HTTPException) as exc_info:
            await routes.delete_instrument(999, mock_service)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
