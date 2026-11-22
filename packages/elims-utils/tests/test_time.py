"""Tests for time utilities."""

from datetime import UTC

from elims_utils import utc_now


def test_utc_now_is_timezone_aware() -> None:
    """The generated timestamp uses UTC explicitly."""
    assert utc_now().tzinfo is UTC
