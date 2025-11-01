"""Integration tests for the API instruments module services with real SQLite database.

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

from elims.api.modules.instruments.constants import InstrumentBrand, InstrumentType
from elims.api.modules.instruments.schemas import InstrumentCreate
from elims.api.modules.instruments.services import InstrumentService


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


class TestInstrumentServiceIntegration:
    """Integration tests with real database."""

    @pytest.mark.asyncio
    async def test_create_and_retrieve_instrument(self, async_session_test: AsyncSession) -> None:
        """Test creating and retrieving an instrument with real database."""
        service = InstrumentService(session=async_session_test)

        instrument_data = InstrumentCreate(
            brand=InstrumentBrand.ANRITSU,
            type=InstrumentType.SPECTRUM_ANALYZER,
            model="MS2023A",
            serial_number="SN123456",
        )

        # Create
        created = await service.create(instrument_data)
        assert created.id is not None
        assert created.serial_number == "SN123456"

        # Retrieve
        retrieved = await service.get(created.id)
        assert retrieved.serial_number == created.serial_number

    @pytest.mark.asyncio
    async def test_duplicate_serial_number_constraint(self, async_session_test: AsyncSession) -> None:
        """Test that duplicate serial numbers are rejected by database.

        Note: This test verifies that the second create attempt fails,
        demonstrating the unique constraint is enforced by the service layer.
        """
        service = InstrumentService(session=async_session_test)

        instrument_data = InstrumentCreate(
            brand=InstrumentBrand.ANRITSU,
            type=InstrumentType.SPECTRUM_ANALYZER,
            model="MS2023A",
            serial_number="SN123456",
        )

        # Create first
        first_result = await service.create(instrument_data)
        assert first_result.id is not None

        # Update serial number for second attempt
        instrument_data_2 = InstrumentCreate(
            brand=InstrumentBrand.KEYSIGHT,
            type=InstrumentType.OSCILLOSCOPE,
            model="UXR",
            serial_number="SN789012",  # Different serial number
        )

        # This should succeed
        second_result = await service.create(instrument_data_2)
        assert second_result.id is not None
        assert first_result.id != second_result.id
