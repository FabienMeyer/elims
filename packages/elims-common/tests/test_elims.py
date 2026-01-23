"""Test ELIMS Common Package."""

from elims_common.elims_common import get_version, hello_common


class TestElimsCommon:
    """Tests for elims-common package."""

    def test_get_version(self) -> None:
        """Test that get_version returns a valid version string."""
        version = get_version()
        assert isinstance(version, str)
        assert version == "0.0.1"

    def test_hello_common(self) -> None:
        """Test that hello_common returns the expected greeting."""
        message = hello_common()
        assert isinstance(message, str)
        assert message == "Hello from ELIMS Common!"
        assert "ELIMS" in message
