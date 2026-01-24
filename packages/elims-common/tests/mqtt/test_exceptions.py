"""Test ELIMS Common Package - MQTT Module - Exceptions."""

import pytest
from elims_common.mqtt.exceptions import (
    MQTTConnectionError,
    MQTTError,
    MQTTPublishError,
    MQTTSubscribeError,
)


def test_mqtt_error_base() -> None:
    """Test base MQTT error exception."""
    error = MQTTError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)


def test_mqtt_connection_error() -> None:
    """Test MQTT connection error exception."""
    error = MQTTConnectionError("Connection failed")
    assert str(error) == "Connection failed"
    assert isinstance(error, MQTTError)
    assert isinstance(error, Exception)


def test_mqtt_publish_error() -> None:
    """Test MQTT publish error exception."""
    error = MQTTPublishError("Publish failed")
    assert str(error) == "Publish failed"
    assert isinstance(error, MQTTError)
    assert isinstance(error, Exception)


def test_mqtt_subscribe_error() -> None:
    """Test MQTT subscribe error exception."""
    error = MQTTSubscribeError("Subscribe failed")
    assert str(error) == "Subscribe failed"
    assert isinstance(error, MQTTError)
    assert isinstance(error, Exception)


def test_exception_hierarchy() -> None:
    """Test exception hierarchy is correct."""
    # All specific errors inherit from MQTTError
    assert issubclass(MQTTConnectionError, MQTTError)
    assert issubclass(MQTTPublishError, MQTTError)
    assert issubclass(MQTTSubscribeError, MQTTError)

    # MQTTError inherits from Exception
    assert issubclass(MQTTError, Exception)


def test_exception_catching() -> None:
    """Test that exceptions can be caught at different levels."""
    # Catch specific exception
    msg = "test"
    with pytest.raises(MQTTConnectionError):
        raise MQTTConnectionError(msg)

    # Catch as base MQTTError
    with pytest.raises(MQTTError):
        raise MQTTConnectionError(msg)

    # Catch as Exception
    with pytest.raises(Exception):  # noqa: B017, PT011
        raise MQTTConnectionError(msg)


def test_exception_with_chained_cause() -> None:
    """Test exceptions with chained causes."""
    original_msg = "Original error"
    connection_msg = "Connection failed"
    original_error = ValueError(original_msg)

    with pytest.raises(MQTTConnectionError, match=connection_msg) as exc_info:
        raise MQTTConnectionError(connection_msg) from original_error

    # Verify cause outside the with block
    assert exc_info.value.__cause__ == original_error
    assert isinstance(exc_info.value.__cause__, ValueError)
