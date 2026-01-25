"""Test ELIMS Common Package - MQTT Module - Subscriber."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from elims_common.mqtt.config import MQTTConfig
from elims_common.mqtt.exceptions import MQTTConnectionError
from elims_common.mqtt.subscriber import MQTTSubscriber
from pydantic import SecretStr

# Constants for test configuration
DEFAULT_BROKER_PORT = 1883
DEFAULT_QOS = 1
HIGH_QOS = 2


@pytest.fixture
def mqtt_config() -> MQTTConfig:
    """Create a test MQTT configuration."""
    return MQTTConfig(
        broker_host="localhost",
        broker_port=DEFAULT_BROKER_PORT,
        client_id="test_subscriber",
    )


@patch("paho.mqtt.client.Client")
def test_subscriber_initialization(_mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test MQTT subscriber initialization."""
    subscriber = MQTTSubscriber(mqtt_config)
    assert subscriber.config == mqtt_config
    assert not subscriber.is_connected


@patch("paho.mqtt.client.Client")
def test_subscriber_initialization_with_auth(mock_client: Any) -> None:
    """Test MQTT subscriber initialization with authentication."""
    config = MQTTConfig(
        broker_host="localhost",
        username="testuser",
        password="testpass",  # noqa: S106
    )

    _ = MQTTSubscriber(config)

    # Verify username_pw_set was called
    mock_client.return_value.username_pw_set.assert_called_once_with("testuser", "testpass")


@patch("paho.mqtt.client.Client")
def test_subscriber_password_uses_secret_str(mock_client: Any) -> None:
    """Test that subscriber properly handles SecretStr password."""
    config = MQTTConfig(
        broker_host="localhost",
        username="user",
        password="secret",  # noqa: S106
    )

    assert isinstance(config.password, SecretStr)

    _ = MQTTSubscriber(config)

    # Should call with unwrapped password value
    mock_client.return_value.username_pw_set.assert_called_once_with("user", "secret")


@patch("paho.mqtt.client.Client")
def test_subscriber_connect_success(mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test successful MQTT subscriber connection."""
    subscriber = MQTTSubscriber(mqtt_config)

    # Mock the connection event
    def mock_connect(*_args: Any, **_kwargs: Any) -> None:
        # Simulate successful connection callback
        subscriber._on_connect(None, None, {"session present": False}, 0)  # noqa: SLF001

    mock_client.return_value.connect.side_effect = mock_connect

    subscriber.connect(timeout=1.0)

    assert subscriber.is_connected
    mock_client.return_value.loop_start.assert_called_once()


@patch("paho.mqtt.client.Client")
def test_subscriber_connect_timeout(_mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test MQTT subscriber connection timeout."""
    subscriber = MQTTSubscriber(mqtt_config)

    # Don't trigger the callback - let it timeout
    with pytest.raises(MQTTConnectionError, match="timeout"):
        subscriber.connect(timeout=0.1)

    assert not subscriber.is_connected


@patch("paho.mqtt.client.Client")
def test_subscriber_subscribe(mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test MQTT subscriber subscription."""
    subscriber = MQTTSubscriber(mqtt_config)
    subscriber._connected = True  # noqa: SLF001

    callback = MagicMock()
    subscriber.subscribe("test/topic", callback)

    mock_client.return_value.subscribe.assert_called_once_with("test/topic", qos=DEFAULT_QOS)


@patch("paho.mqtt.client.Client")
def test_subscriber_subscribe_with_qos(mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test MQTT subscriber subscription with custom QoS."""
    subscriber = MQTTSubscriber(mqtt_config)
    subscriber._connected = True  # noqa: SLF001

    callback = MagicMock()
    subscriber.subscribe("test/topic", callback, qos=HIGH_QOS)

    mock_client.return_value.subscribe.assert_called_once_with("test/topic", qos=HIGH_QOS)


@patch("paho.mqtt.client.Client")
def test_subscriber_subscribe_not_connected(mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test subscribing when not connected stores callback."""
    subscriber = MQTTSubscriber(mqtt_config)

    callback = MagicMock()
    subscriber.subscribe("test/topic", callback)

    # Should store subscription but not call client.subscribe
    mock_client.return_value.subscribe.assert_not_called()

    # Subscription should be stored
    assert "test/topic" in subscriber._subscriptions  # noqa: SLF001


@patch("paho.mqtt.client.Client")
def test_subscriber_unsubscribe(mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test MQTT subscriber unsubscription."""
    subscriber = MQTTSubscriber(mqtt_config)
    subscriber._connected = True  # noqa: SLF001

    callback = MagicMock()
    subscriber.subscribe("test/topic", callback)
    subscriber.unsubscribe("test/topic")

    mock_client.return_value.unsubscribe.assert_called_once_with("test/topic")


@patch("paho.mqtt.client.Client")
def test_subscriber_unsubscribe_not_connected(mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test unsubscribing when not connected removes from local storage."""
    subscriber = MQTTSubscriber(mqtt_config)

    callback = MagicMock()
    subscriber.subscribe("test/topic", callback)
    subscriber.unsubscribe("test/topic")

    # Should remove from subscriptions
    assert "test/topic" not in subscriber._subscriptions  # noqa: SLF001

    # Should not call client.unsubscribe
    mock_client.return_value.unsubscribe.assert_not_called()


@patch("paho.mqtt.client.Client")
def test_subscriber_message_callback(_mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test MQTT subscriber message callback."""
    subscriber = MQTTSubscriber(mqtt_config)

    callback = MagicMock()
    subscriber.subscribe("test/topic", callback)

    # Simulate receiving a message
    mock_msg = MagicMock()
    mock_msg.topic = "test/topic"
    mock_msg.payload.decode.return_value = "test message"

    subscriber._on_message(None, None, mock_msg)  # noqa: SLF001

    callback.assert_called_once_with("test/topic", "test message")


@patch("paho.mqtt.client.Client")
def test_subscriber_multiple_callbacks(_mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test MQTT subscriber with multiple callbacks for same topic."""
    subscriber = MQTTSubscriber(mqtt_config)

    callback1 = MagicMock()
    callback2 = MagicMock()

    subscriber.subscribe("test/topic", callback1)
    subscriber.subscribe("test/topic", callback2)

    # Simulate receiving a message
    mock_msg = MagicMock()
    mock_msg.topic = "test/topic"
    mock_msg.payload.decode.return_value = "test message"

    subscriber._on_message(None, None, mock_msg)  # noqa: SLF001

    callback1.assert_called_once_with("test/topic", "test message")
    callback2.assert_called_once_with("test/topic", "test message")


@patch("paho.mqtt.client.Client")
def test_subscriber_message_no_callback(_mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test receiving message on unsubscribed topic."""
    subscriber = MQTTSubscriber(mqtt_config)

    # Simulate receiving a message on topic with no callback
    mock_msg = MagicMock()
    mock_msg.topic = "unknown/topic"
    mock_msg.payload.decode.return_value = "test message"

    # Should not raise, just log
    subscriber._on_message(None, None, mock_msg)  # noqa: SLF001


@patch("paho.mqtt.client.Client")
def test_subscriber_callback_exception_handling(_mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test that callback exceptions are caught and logged."""
    subscriber = MQTTSubscriber(mqtt_config)

    def failing_callback(_topic: str, _payload: str) -> None:
        error_msg = "Callback error"
        raise ValueError(error_msg)

    subscriber.subscribe("test/topic", failing_callback)

    # Simulate receiving a message
    mock_msg = MagicMock()
    mock_msg.topic = "test/topic"
    mock_msg.payload.decode.return_value = "test message"

    # Should not raise, should log error
    subscriber._on_message(None, None, mock_msg)  # noqa: SLF001


@patch("paho.mqtt.client.Client")
def test_subscriber_resubscribe_on_reconnect(_mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test that subscriber resubscribes to topics on reconnection."""
    subscriber = MQTTSubscriber(mqtt_config)

    # Add subscriptions
    callback = MagicMock()
    subscriber._subscriptions["topic1"] = [callback]  # noqa: SLF001
    subscriber._subscriptions["topic2"] = [callback]  # noqa: SLF001

    # Simulate reconnection
    subscriber._on_connect(None, None, {"session present": False}, 0)  # noqa: SLF001

    # Should resubscribe to all topics
    assert subscriber._client.subscribe.call_count == 2  # noqa: PLR2004, SLF001  # type: ignore[attr-defined]


@patch("paho.mqtt.client.Client")
def test_subscriber_on_disconnect_callback(_mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test subscriber on_disconnect callback."""
    subscriber = MQTTSubscriber(mqtt_config)
    subscriber._connected = True  # noqa: SLF001

    # Clean disconnect
    subscriber._on_disconnect(None, None, 0)  # noqa: SLF001
    assert not subscriber.is_connected

    # Unexpected disconnect
    subscriber._connected = True  # noqa: SLF001
    subscriber._on_disconnect(None, None, 7)  # noqa: SLF001
    assert not subscriber.is_connected


@patch("paho.mqtt.client.Client")
def test_subscriber_is_connected_property(_mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test is_connected property."""
    subscriber = MQTTSubscriber(mqtt_config)

    assert subscriber.is_connected is False

    subscriber._connected = True  # noqa: SLF001
    assert subscriber.is_connected is True


@patch("paho.mqtt.client.Client")
def test_subscriber_payload_logging_disabled(_mock_client: Any) -> None:
    """Test receiving message with payload logging disabled."""
    config = MQTTConfig(
        broker_host="localhost",
        log_payloads=False,
    )

    subscriber = MQTTSubscriber(config)
    callback = MagicMock()
    subscriber.subscribe("test/topic", callback)

    # Simulate receiving a message
    mock_msg = MagicMock()
    mock_msg.topic = "test/topic"
    mock_msg.payload.decode.return_value = "sensitive data"

    subscriber._on_message(None, None, mock_msg)  # noqa: SLF001
    callback.assert_called_once_with("test/topic", "sensitive data")


@patch("paho.mqtt.client.Client")
def test_subscriber_payload_logging_enabled(_mock_client: Any) -> None:
    """Test receiving message with payload logging enabled."""
    config = MQTTConfig(
        broker_host="localhost",
        log_payloads=True,
        max_payload_log_length=10,
    )

    subscriber = MQTTSubscriber(config)
    callback = MagicMock()
    subscriber.subscribe("test/topic", callback)

    # Simulate receiving a message
    mock_msg = MagicMock()
    mock_msg.topic = "test/topic"
    mock_msg.payload.decode.return_value = "A" * 100

    subscriber._on_message(None, None, mock_msg)  # noqa: SLF001
    callback.assert_called_once_with("test/topic", "A" * 100)
