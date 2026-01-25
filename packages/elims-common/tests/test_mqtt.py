"""Tests for MQTT publisher and subscriber."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from elims_common import MQTTConfig, MQTTPublisher, MQTTSubscriber
from elims_common.mqtt.exceptions import MQTTConnectionError

# Constants for test configuration
DEFAULT_BROKER_PORT = 1883
SECURE_BROKER_PORT = 8883
DEFAULT_QOS = 1
HIGH_QOS = 2
DEFAULT_KEEPALIVE = 60


@pytest.fixture
def mqtt_config() -> MQTTConfig:
    """Create a test MQTT configuration."""
    return MQTTConfig(
        broker_host="localhost",
        broker_port=DEFAULT_BROKER_PORT,
        client_id="test_client",
    )


def test_mqtt_config_defaults() -> None:
    """Test MQTT config with default values."""
    config = MQTTConfig()
    assert config.broker_host == "localhost"
    assert config.broker_port == DEFAULT_BROKER_PORT
    assert config.qos == DEFAULT_QOS
    assert config.keepalive == DEFAULT_KEEPALIVE


def test_mqtt_config_custom() -> None:
    """Test MQTT config with custom values."""
    config = MQTTConfig(
        broker_host="mqtt.example.com",
        broker_port=SECURE_BROKER_PORT,
        username="user",
        password="pass",  # noqa: S106
        qos=HIGH_QOS,
    )
    assert config.broker_host == "mqtt.example.com"
    assert config.broker_port == SECURE_BROKER_PORT
    assert config.username == "user"
    assert config.password.get_secret_value() == "pass"
    assert config.qos == HIGH_QOS


@patch("paho.mqtt.client.Client")
def test_publisher_initialization(_mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test MQTT publisher initialization."""
    publisher = MQTTPublisher(mqtt_config)
    assert publisher.config == mqtt_config
    assert not publisher.is_connected


@patch("paho.mqtt.client.Client")
def test_publisher_connect(mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test MQTT publisher connection."""
    publisher = MQTTPublisher(mqtt_config)

    # Mock successful connection callback
    def mock_connect(*_args: Any, **_kwargs: Any) -> None:
        # Simulate the on_connect callback being triggered
        publisher._on_connect(None, None, {"session present": False}, 0)  # noqa: SLF001

    mock_client.return_value.connect.side_effect = mock_connect

    publisher.connect()

    mock_client.return_value.connect.assert_called_once_with(
        mqtt_config.broker_host,
        mqtt_config.broker_port,
        mqtt_config.keepalive,
    )
    mock_client.return_value.loop_start.assert_called_once()


@patch("paho.mqtt.client.Client")
def test_publisher_disconnect(mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test MQTT publisher disconnection."""
    publisher = MQTTPublisher(mqtt_config)
    publisher.disconnect()

    mock_client.return_value.loop_stop.assert_called_once()
    mock_client.return_value.disconnect.assert_called_once()


@patch("paho.mqtt.client.Client")
def test_publisher_publish_string(mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test publishing a string message."""
    publisher = MQTTPublisher(mqtt_config)
    publisher._connected = True  # noqa: SLF001

    publisher.publish("test/topic", "Hello MQTT")

    mock_client.return_value.publish.assert_called_once_with("test/topic", "Hello MQTT", qos=DEFAULT_QOS, retain=False)


@patch("paho.mqtt.client.Client")
def test_publisher_publish_dict(mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test publishing a dictionary message."""
    publisher = MQTTPublisher(mqtt_config)
    publisher._connected = True  # noqa: SLF001

    data = {"sensor": "temp", "value": 23.5}
    publisher.publish("test/topic", data)

    # Check that the dict was converted to JSON
    call_args = mock_client.return_value.publish.call_args
    assert call_args[0][0] == "test/topic"
    assert '"sensor"' in call_args[0][1]
    assert '"value"' in call_args[0][1]


@patch("paho.mqtt.client.Client")
def test_publisher_publish_not_connected(_mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test publishing when not connected raises error."""
    publisher = MQTTPublisher(mqtt_config)

    with pytest.raises(MQTTConnectionError, match="Not connected"):
        publisher.publish("test/topic", "message")


@patch("paho.mqtt.client.Client")
def test_subscriber_initialization(_mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test MQTT subscriber initialization."""
    subscriber = MQTTSubscriber(mqtt_config)
    assert subscriber.config == mqtt_config
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
def test_subscriber_unsubscribe(mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test MQTT subscriber unsubscription."""
    subscriber = MQTTSubscriber(mqtt_config)
    subscriber._connected = True  # noqa: SLF001

    callback = MagicMock()
    subscriber.subscribe("test/topic", callback)
    subscriber.unsubscribe("test/topic")

    mock_client.return_value.unsubscribe.assert_called_once_with("test/topic")


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
def test_publisher_with_auth(mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test MQTT publisher with authentication."""
    from pydantic import SecretStr

    mqtt_config.username = "testuser"
    mqtt_config.password = SecretStr("testpass")

    _ = MQTTPublisher(mqtt_config)

    mock_client.return_value.username_pw_set.assert_called_once_with("testuser", "testpass")


@patch("paho.mqtt.client.Client")
def test_subscriber_with_auth(mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test MQTT subscriber with authentication."""
    from pydantic import SecretStr

    mqtt_config.username = "testuser"
    mqtt_config.password = SecretStr("testpass")

    _ = MQTTSubscriber(mqtt_config)

    mock_client.return_value.username_pw_set.assert_called_once_with("testuser", "testpass")
