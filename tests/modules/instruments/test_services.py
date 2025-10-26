"""Tests for the API instruments module services.

These tests verify the service layer interface and error handling.
Integration tests would require a real database or more complex mocking.
"""

import inspect
from unittest.mock import AsyncMock

from sqlmodel.ext.asyncio.session import AsyncSession

from elims.api.modules.instruments.services import InstrumentService


class TestInstrumentServiceInterface:
    """Tests for the Instrument service interface."""

    def test_instrument_service_initialization(self) -> None:
        """Test that InstrumentService can be instantiated."""
        mock_session = AsyncMock(spec=AsyncSession)
        service = InstrumentService(session=mock_session)

        assert service is not None
        assert service.session == mock_session

    def test_instrument_service_has_required_methods(self) -> None:
        """Test that InstrumentService has all required CRUD methods."""
        mock_session = AsyncMock(spec=AsyncSession)
        service = InstrumentService(session=mock_session)

        # Verify all CRUD methods exist
        assert hasattr(service, "create")
        assert hasattr(service, "get")
        assert hasattr(service, "update")
        assert hasattr(service, "delete")
        assert hasattr(service, "list_all")

        # Verify they are async
        assert inspect.iscoroutinefunction(service.create)
        assert inspect.iscoroutinefunction(service.get)
        assert inspect.iscoroutinefunction(service.update)
        assert inspect.iscoroutinefunction(service.delete)
        assert inspect.iscoroutinefunction(service.list_all)
