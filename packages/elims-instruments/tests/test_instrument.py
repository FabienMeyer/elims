"""Instrument entity tests."""

from elims_instruments import Instrument


def test_instrument() -> None:
    """Instrument preserves its identity."""
    assert Instrument(identifier="scope-1", name="Oscilloscope").identifier == "scope-1"
