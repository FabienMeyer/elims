"""Test ELIMS Common Package - MQTT Module - Exceptions."""

import pytest
from elims_common.mqtt.exceptions import (
    MQTTConnectionError,
    MQTTError,
    MQTTPublishError,
    MQTTSubscribeError,
)

# ===== Basic Exception Tests =====


@pytest.mark.parametrize(
    ("exception_class", "message"),
    [
        (MQTTError, "Test error"),
        (MQTTConnectionError, "Connection failed"),
        (MQTTPublishError, "Publish failed"),
        (MQTTSubscribeError, "Subscribe failed"),
    ],
)
def test_mqtt_exception_message(exception_class: type[Exception], message: str) -> None:
    """Test MQTT exception messages."""
    error = exception_class(message)
    assert str(error) == message
    assert isinstance(error, Exception)


@pytest.mark.parametrize(
    "exception_class",
    [MQTTConnectionError, MQTTPublishError, MQTTSubscribeError],
)
def test_mqtt_exception_inherits_from_mqtt_error(exception_class: type[Exception]) -> None:
    """Test that specific MQTT exceptions inherit from MQTTError."""
    error = exception_class("test")
    assert isinstance(error, MQTTError)
    assert isinstance(error, Exception)


# ===== Context Attributes Tests =====


@pytest.mark.parametrize(
    ("broker_host", "broker_port", "return_code", "client_id", "expected_in_message"),
    [
        ("192.168.1.1", 8883, 5, "client-123", ["192.168.1.1:8883", "client_id=client-123", "return_code=5"]),
        ("mqtt.example.com", 8883, None, None, ["mqtt.example.com:8883"]),
        ("127.0.0.1", None, 4, None, ["127.0.0.1:8883", "return_code=4"]),
        (None, None, None, "test-client", ["client_id=test-client"]),
    ],
)
def test_mqtt_connection_error_with_context(
    broker_host: str | None,
    broker_port: int | None,
    return_code: int | None,
    client_id: str | None,
    expected_in_message: list[str],
) -> None:
    """Test MQTTConnectionError with context attributes."""
    error = MQTTConnectionError(
        "Connection failed",
        broker_host=broker_host,
        broker_port=broker_port,
        return_code=return_code,
        client_id=client_id,
    )

    # Check attributes
    assert error.broker_host == broker_host
    assert error.broker_port == broker_port
    assert error.return_code == return_code
    assert error.client_id == client_id

    # Check message contains expected parts
    error_message = str(error)
    assert "Connection failed" in error_message
    for expected_part in expected_in_message:
        assert expected_part in error_message


@pytest.mark.parametrize(
    ("topic", "qos", "payload_size", "expected_in_message"),
    [
        ("sensors/temperature", 1, 256, ["topic=sensors/temperature", "qos=1", "payload_size=256"]),
        ("home/living/light", 2, None, ["topic=home/living/light", "qos=2"]),
        (None, None, 1024, ["payload_size=1024"]),
        (None, 0, None, ["qos=0"]),
    ],
)
def test_mqtt_publish_error_with_context(
    topic: str | None,
    qos: int | None,
    payload_size: int | None,
    expected_in_message: list[str],
) -> None:
    """Test MQTTPublishError with context attributes."""
    error = MQTTPublishError(
        "Publish failed",
        topic=topic,
        qos=qos,
        payload_size=payload_size,
    )

    # Check attributes
    assert error.topic == topic
    assert error.qos == qos
    assert error.payload_size == payload_size

    # Check message contains expected parts
    error_message = str(error)
    assert "Publish failed" in error_message
    for expected_part in expected_in_message:
        assert expected_part in error_message


@pytest.mark.parametrize(
    ("topic", "qos", "granted_qos", "expected_in_message"),
    [
        ("sensors/#", 2, 1, ["topic=sensors/#", "qos=2", "granted_qos=1"]),
        ("home/+/temperature", 1, None, ["topic=home/+/temperature", "qos=1"]),
        (None, None, 0, ["granted_qos=0"]),
        (None, 2, None, ["qos=2"]),
    ],
)
def test_mqtt_subscribe_error_with_context(
    topic: str | None,
    qos: int | None,
    granted_qos: int | None,
    expected_in_message: list[str],
) -> None:
    """Test MQTTSubscribeError with context attributes."""
    error = MQTTSubscribeError(
        "Subscribe failed",
        topic=topic,
        qos=qos,
        granted_qos=granted_qos,
    )

    # Check attributes
    assert error.topic == topic
    assert error.qos == qos
    assert error.granted_qos == granted_qos

    # Check message contains expected parts
    error_message = str(error)
    assert "Subscribe failed" in error_message
    for expected_part in expected_in_message:
        assert expected_part in error_message


# ===== Exception Hierarchy Tests =====


@pytest.mark.parametrize(
    "exception_class",
    [MQTTConnectionError, MQTTPublishError, MQTTSubscribeError],
)
def test_exception_hierarchy(exception_class: type[Exception]) -> None:
    """Test exception hierarchy is correct."""
    assert issubclass(exception_class, MQTTError)
    assert issubclass(exception_class, Exception)


def test_base_mqtt_error_hierarchy() -> None:
    """Test MQTTError inherits from Exception."""
    assert issubclass(MQTTError, Exception)


# ===== Exception Catching Tests =====


@pytest.mark.parametrize(
    "exception_class",
    [MQTTConnectionError, MQTTPublishError, MQTTSubscribeError],
)
def test_exception_catching_specific(exception_class: type[Exception]) -> None:
    """Test that specific exceptions can be caught."""
    msg = "test"
    with pytest.raises(exception_class):
        raise exception_class(msg)


@pytest.mark.parametrize(
    "exception_class",
    [MQTTConnectionError, MQTTPublishError, MQTTSubscribeError],
)
def test_exception_catching_as_mqtt_error(exception_class: type[Exception]) -> None:
    """Test that specific exceptions can be caught as base MQTTError."""
    msg = "test"
    with pytest.raises(MQTTError):
        raise exception_class(msg)


@pytest.mark.parametrize(
    "exception_class",
    [MQTTConnectionError, MQTTPublishError, MQTTSubscribeError],
)
def test_exception_catching_as_exception(exception_class: type[Exception]) -> None:
    """Test that specific exceptions can be caught as Exception."""
    msg = "test"
    with pytest.raises(Exception):  # noqa: B017, PT011
        raise exception_class(msg)


# ===== Exception Chaining Tests =====


@pytest.mark.parametrize(
    ("exception_class", "error_message"),
    [
        (MQTTConnectionError, "Connection failed"),
        (MQTTPublishError, "Publish failed"),
        (MQTTSubscribeError, "Subscribe failed"),
    ],
)
def test_exception_with_chained_cause(exception_class: type[Exception], error_message: str) -> None:
    """Test exceptions with chained causes."""
    original_error = ValueError("Original error")

    with pytest.raises(exception_class, match=error_message) as exc_info:
        raise exception_class(error_message) from original_error

    assert exc_info.value.__cause__ == original_error
    assert isinstance(exc_info.value.__cause__, ValueError)
