"""Tests for the API instruments module services.

These tests verify the service layer interface and error handling.
Integration tests would require a real database or more complex mocking.
"""

import inspect
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from elims.api.modules.instruments import schemas, services
from elims.api.modules.instruments.constants import InstrumentBrand, InstrumentType
from elims.api.modules.instruments.exceptions import (
    InstrumentAlreadyExistError,
    InstrumentNotFoundError,
)
from elims.api.modules.instruments.models import Instrument
from elims.api.modules.instruments.schemas import (
    InstrumentCreate,
    InstrumentRead,
    InstrumentUpdate,
)

# Constants for testing
EXPECTED_INSTRUMENTS_COUNT = 3


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create a mock async database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def sample_instrument_create() -> InstrumentCreate:
    """Create a sample instrument creation schema."""
    return InstrumentCreate(
        brand=InstrumentBrand.ANRITSU,
        type=InstrumentType.SPECTRUM_ANALYZER,
        model="MS2023A",
        serial_number="SN123456",
    )


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


class TestInstrumentServiceCreate:
    """Tests for the create method of InstrumentService."""

    def test_instrument_service_initialization(self) -> None:
        """Test that InstrumentService can be instantiated."""
        assert schemas is not None
        assert hasattr(services, "InstrumentService")

    @pytest.mark.asyncio
    async def test_instruments_services_create(self, mock_session: AsyncMock, sample_instrument_create: InstrumentCreate) -> None:
        """Test that InstrumentService has a create method."""
        service = services.InstrumentService(session=mock_session)

        assert hasattr(service, "create")
        assert inspect.iscoroutinefunction(service.create)

        # Mock the session methods
        mock_instrument = MagicMock(spec=Instrument)
        mock_instrument.serial_number = sample_instrument_create.serial_number
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Mock Instrument.model_validate to return our mock
        with patch.object(Instrument, "model_validate", return_value=mock_instrument), patch.object(InstrumentRead, "model_validate") as mock_read:
            mock_read.return_value = InstrumentRead(
                id=1,
                brand=sample_instrument_create.brand,
                type=sample_instrument_create.type,
                model=sample_instrument_create.model,
                serial_number=sample_instrument_create.serial_number,
            )

            result = await service.create(sample_instrument_create)

            assert result is not None
            assert result.serial_number == sample_instrument_create.serial_number
            mock_session.add.assert_called_once_with(mock_instrument)
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once_with(mock_instrument)

    @pytest.mark.asyncio
    async def test_create_instrument_success(self, mock_session: AsyncMock, sample_instrument_create: InstrumentCreate) -> None:
        """Test successful creation of an instrument."""
        service = services.InstrumentService(session=mock_session)

        # Mock the session methods
        mock_instrument = MagicMock(spec=Instrument)
        mock_instrument.serial_number = sample_instrument_create.serial_number
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Mock Instrument.model_validate to return our mock
        with patch.object(Instrument, "model_validate", return_value=mock_instrument), patch.object(InstrumentRead, "model_validate") as mock_read:
            mock_read.return_value = InstrumentRead(
                id=1,
                brand=sample_instrument_create.brand,
                type=sample_instrument_create.type,
                model=sample_instrument_create.model,
                serial_number=sample_instrument_create.serial_number,
            )

            result = await service.create(sample_instrument_create)

            assert result is not None
            assert result.serial_number == sample_instrument_create.serial_number
            mock_session.add.assert_called_once_with(mock_instrument)
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once_with(mock_instrument)

    @pytest.mark.asyncio
    async def test_create_instrument_duplicate_serial_number(self, mock_session: AsyncMock, sample_instrument_create: InstrumentCreate) -> None:
        """Test creation fails when serial number already exists."""
        service = services.InstrumentService(session=mock_session)

        # Mock the session to raise IntegrityError
        mock_instrument = MagicMock(spec=Instrument)
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock(side_effect=IntegrityError("Duplicate entry", "INSERT", ValueError("Unique constraint violation")))
        mock_session.rollback = AsyncMock()

        with patch.object(Instrument, "model_validate", return_value=mock_instrument):
            with pytest.raises(InstrumentAlreadyExistError) as exc_info:
                await service.create(sample_instrument_create)

            assert sample_instrument_create.serial_number in str(exc_info.value)
            mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_instrument_success(self, mock_session: AsyncMock, sample_instrument_read: InstrumentRead) -> None:
        """Test successful retrieval of an instrument."""
        service = services.InstrumentService(session=mock_session)

        mock_instrument = MagicMock(spec=Instrument)
        mock_result = AsyncMock()
        mock_result.one_or_none = MagicMock(return_value=mock_instrument)
        mock_session.exec = AsyncMock(return_value=mock_result)

        with patch.object(InstrumentRead, "model_validate", return_value=sample_instrument_read):
            result = await service.get(1)

            assert result is not None
            assert result.id == sample_instrument_read.id
            mock_session.exec.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_instrument_not_found(self, mock_session: AsyncMock) -> None:
        """Test retrieval fails when instrument is not found."""
        service = services.InstrumentService(session=mock_session)

        mock_result = AsyncMock()
        mock_result.one_or_none = MagicMock(return_value=None)
        mock_session.exec = AsyncMock(return_value=mock_result)

        with pytest.raises(InstrumentNotFoundError) as exc_info:
            await service.get(999)

        assert "999" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_instrument_success(self, mock_session: AsyncMock) -> None:
        """Test successful update of an instrument."""
        service = services.InstrumentService(session=mock_session)

        # Setup mock instrument
        mock_instrument = MagicMock(spec=Instrument)
        mock_instrument.serial_number = "SN123456"
        mock_result = AsyncMock()
        mock_result.one_or_none = MagicMock(return_value=mock_instrument)
        mock_session.exec = AsyncMock(return_value=mock_result)
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Create update data
        update_data = InstrumentUpdate(model="MS2024A")

        with patch.object(InstrumentRead, "model_validate") as mock_read:
            mock_read.return_value = InstrumentRead(
                id=1,
                brand=InstrumentBrand.ANRITSU,
                type=InstrumentType.SPECTRUM_ANALYZER,
                model="MS2024A",
                serial_number="SN123456",
            )

            result = await service.update(1, update_data)

            assert result is not None
            assert result.model == "MS2024A"
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_instrument_not_found(self, mock_session: AsyncMock) -> None:
        """Test update fails when instrument is not found."""
        service = services.InstrumentService(session=mock_session)

        mock_result = AsyncMock()
        mock_result.one_or_none = MagicMock(return_value=None)
        mock_session.exec = AsyncMock(return_value=mock_result)

        update_data = InstrumentUpdate(model="MS2024A")

        with pytest.raises(InstrumentNotFoundError) as exc_info:
            await service.update(999, update_data)

        assert "999" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_instrument_duplicate_serial_number(self, mock_session: AsyncMock) -> None:
        """Test update fails when changing to a duplicate serial number."""
        service = services.InstrumentService(session=mock_session)

        # Setup mock instrument
        mock_instrument = MagicMock(spec=Instrument)
        mock_instrument.serial_number = "SN789012"
        mock_result = AsyncMock()
        mock_result.one_or_none = MagicMock(return_value=mock_instrument)
        mock_session.exec = AsyncMock(return_value=mock_result)
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock(side_effect=IntegrityError("Duplicate entry", "INSERT", ValueError("Unique constraint violation")))
        mock_session.rollback = AsyncMock()

        update_data = InstrumentUpdate(serial_number="SN789012")

        with pytest.raises(InstrumentAlreadyExistError):
            await service.update(1, update_data)

        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_instrument_success(self, mock_session: AsyncMock) -> None:
        """Test successful deletion of an instrument."""
        service = services.InstrumentService(session=mock_session)

        mock_instrument = MagicMock(spec=Instrument)
        mock_result = AsyncMock()
        mock_result.one_or_none = MagicMock(return_value=mock_instrument)
        mock_session.exec = AsyncMock(return_value=mock_result)
        mock_session.delete = AsyncMock()
        mock_session.commit = AsyncMock()

        await service.delete(1)

        mock_session.delete.assert_called_once_with(mock_instrument)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_instrument_not_found(self, mock_session: AsyncMock) -> None:
        """Test deletion fails when instrument is not found."""
        service = services.InstrumentService(session=mock_session)

        mock_result = AsyncMock()
        mock_result.one_or_none = MagicMock(return_value=None)
        mock_session.exec = AsyncMock(return_value=mock_result)

        with pytest.raises(InstrumentNotFoundError) as exc_info:
            await service.delete(999)

        assert "999" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_gets_instruments_empty(self, mock_session: AsyncMock) -> None:
        """Test listing all instruments when database is empty."""
        service = services.InstrumentService(session=mock_session)

        mock_result = AsyncMock()
        mock_result.all = MagicMock(return_value=[])
        mock_session.exec = AsyncMock(return_value=mock_result)

        result = await service.gets()

        assert result == []
        mock_session.exec.assert_called_once()

    @pytest.mark.asyncio
    async def test_gets_instruments_multiple(self, mock_session: AsyncMock) -> None:
        """Test listing all instruments with multiple records."""
        service = services.InstrumentService(session=mock_session)

        mock_instruments = [MagicMock(spec=Instrument) for _ in range(EXPECTED_INSTRUMENTS_COUNT)]
        mock_result = AsyncMock()
        mock_result.all = MagicMock(return_value=mock_instruments)
        mock_session.exec = AsyncMock(return_value=mock_result)

        expected_reads = [
            InstrumentRead(
                id=i + 1,
                brand=InstrumentBrand.ANRITSU,
                type=InstrumentType.SPECTRUM_ANALYZER,
                model=f"MS202{i}A",
                serial_number=f"SN{i:06d}",
            )
            for i in range(EXPECTED_INSTRUMENTS_COUNT)
        ]

        with patch.object(InstrumentRead, "model_validate", side_effect=expected_reads):
            result = await service.gets()

            assert len(result) == EXPECTED_INSTRUMENTS_COUNT
            assert all(isinstance(item, InstrumentRead) for item in result)
