"""TEST ELIMS - Electronic Laboratory Instrument Management System - Raspberry Package."""

from elims_raspberry.elims_raspberry import get_version, hello_raspberry


class TestElimsRaspberry:
    """Tests for elims-raspberry package."""

    def test_get_version(self) -> None:
        """Test that get_version returns a valid version string."""
        version = get_version()
        assert isinstance(version, str)
        assert version == "0.0.1"

    def test_hello_raspberry(self) -> None:
        """Test that hello_raspberry returns the expected greeting."""
        message = hello_raspberry()
        assert isinstance(message, str)
        assert message == "Hello from ELIMS Raspberry!"
        assert "ELIMS" in message
        assert "Raspberry" in message
