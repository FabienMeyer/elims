"""Test elims module."""

import pytest

from elims import elims


@pytest.fixture
def fx_say_hello() -> str:
    """Sample pytest fixture."""
    return "World"


def test_say_hello(fx_say_hello: str) -> None:
    """Test say_hello function."""
    assert "Hello World" in elims.say_hello(fx_say_hello)
