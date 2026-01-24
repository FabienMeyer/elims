"""Test ELIMS Common Package - MQTT Module - Publisher."""

import json
from typing import Any
from unittest.mock import patch

import pytest
from elims_common.mqtt.config import MQTTConfig
from elims_common.mqtt.exceptions import MQTTConnectionError
from elims_common.mqtt.publisher import MQTTPublisher
from pydantic import SecretStr

# Constants for test configuration
DEFAULT_BROKER_PORT = 1883
DEFAULT_QOS = 1
HIGH_QOS = 2
DEFAULT_KEEPALIVE = 60


@pytest.fixture
def mqtt_config() -> MQTTConfig:
    """Create a test MQTT configuration."""
    return MQTTConfig(
        broker_host="localhost",
        broker_port=DEFAULT_BROKER_PORT,
        client_id="test_publisher",
    )


@patch("paho.mqtt.client.Client")
def test_publisher_initialization(_mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test MQTT publisher initialization."""
    publisher = MQTTPublisher(mqtt_config)
    assert publisher.config == mqtt_config
    assert not publisher.is_connected


@patch("paho.mqtt.client.Client")
def test_publisher_initialization_with_auth(mock_client: Any) -> None:
    """Test MQTT publisher initialization with authentication."""
    config = MQTTConfig(
        broker_host="localhost",
        username="testuser",
        password="testpass",  # noqa: S106
    )

    _ = MQTTPublisher(config)

    # Verify username_pw_set was called with correct values
    mock_client.return_value.username_pw_set.assert_called_once_with("testuser", "testpass")


@patch("paho.mqtt.client.Client")
def test_publisher_password_uses_secret_str(mock_client: Any) -> None:
    """Test that publisher properly handles SecretStr password."""
    config = MQTTConfig(
        broker_host="localhost",
        username="user",
        password="secret",  # noqa: S106
    )

    assert isinstance(config.password, SecretStr)

    _ = MQTTPublisher(config)

    # Should call with unwrapped password value
    mock_client.return_value.username_pw_set.assert_called_once_with("user", "secret")


@patch("paho.mqtt.client.Client")
def test_publisher_connect_success(mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test successful MQTT publisher connection."""
    publisher = MQTTPublisher(mqtt_config)

    # Mock the connection event
    def mock_connect(*_args: Any, **_kwargs: Any) -> None:
        # Simulate successful connection callback
        publisher._on_connect(None, None, {"session present": False}, 0)  # noqa: SLF001

    mock_client.return_value.connect.side_effect = mock_connect

    publisher.connect(timeout=1.0)

    assert publisher.is_connected
    mock_client.return_value.connect.assert_called_once_with(
        mqtt_config.broker_host,
        mqtt_config.broker_port,
        mqtt_config.keepalive,
    )
    mock_client.return_value.loop_start.assert_called_once()


@patch("paho.mqtt.client.Client")
def test_publisher_connect_timeout(_mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test MQTT publisher connection timeout."""
    publisher = MQTTPublisher(mqtt_config)

    # Don't trigger the callback - let it timeout
    with pytest.raises(MQTTConnectionError, match="timeout"):
        publisher.connect(timeout=0.1)

    assert not publisher.is_connected


@patch("paho.mqtt.client.Client")
def test_publisher_connect_failure(mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test MQTT publisher connection failure."""
    publisher = MQTTPublisher(mqtt_config)

    # Mock connection failure
    def mock_connect(*_args: Any, **_kwargs: Any) -> None:
        # Simulate failed connection callback
        publisher._on_connect(None, None, {}, 4)  # BAD_CREDENTIALS  # noqa: SLF001

    mock_client.return_value.connect.side_effect = mock_connect

    with pytest.raises(MQTTConnectionError, match="bad username or password"):
        publisher.connect(timeout=1.0)

    assert not publisher.is_connected


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
    published_payload = call_args[0][1]
    assert '"sensor"' in published_payload
    assert '"value"' in published_payload

    # Verify it's valid JSON
    parsed = json.loads(published_payload)
    assert parsed == data


@patch("paho.mqtt.client.Client")
def test_publisher_publish_bytes(mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test publishing bytes payload."""
    publisher = MQTTPublisher(mqtt_config)
    publisher._connected = True  # noqa: SLF001

    payload = b"\x01\x02\x03\x04"
    publisher.publish("test/topic", payload)

    mock_client.return_value.publish.assert_called_once_with("test/topic", payload, qos=DEFAULT_QOS, retain=False)


@patch("paho.mqtt.client.Client")
def test_publisher_publish_with_qos(mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test publishing with custom QoS."""
    publisher = MQTTPublisher(mqtt_config)
    publisher._connected = True  # noqa: SLF001

    publisher.publish("test/topic", "message", qos=HIGH_QOS)

    call_args = mock_client.return_value.publish.call_args
    assert call_args[1]["qos"] == HIGH_QOS


@patch("paho.mqtt.client.Client")
def test_publisher_publish_with_retain(mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test publishing with retain flag."""
    publisher = MQTTPublisher(mqtt_config)
    publisher._connected = True  # noqa: SLF001

    publisher.publish("test/topic", "message", retain=True)

    call_args = mock_client.return_value.publish.call_args
    assert call_args[1]["retain"] is True


@patch("paho.mqtt.client.Client")
def test_publisher_publish_not_connected(_mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test publishing when not connected raises error."""
    publisher = MQTTPublisher(mqtt_config)

    with pytest.raises(MQTTConnectionError, match="Not connected"):
        publisher.publish("test/topic", "message")


@patch("paho.mqtt.client.Client")
def test_publisher_publish_invalid_topic_empty(_mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test publishing to empty topic raises error."""
    publisher = MQTTPublisher(mqtt_config)
    publisher._connected = True  # noqa: SLF001

    with pytest.raises(ValueError, match="cannot be empty"):
        publisher.publish("", "message")


@patch("paho.mqtt.client.Client")
def test_publisher_publish_invalid_topic_wildcard(_mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test publishing to topic with wildcards raises error."""
    publisher = MQTTPublisher(mqtt_config)
    publisher._connected = True  # noqa: SLF001

    with pytest.raises(ValueError, match="Wildcards"):
        publisher.publish("sensor/+/temp", "message")

    with pytest.raises(ValueError, match="Wildcards"):
        publisher.publish("sensor/#", "message")


@patch("paho.mqtt.client.Client")
def test_publisher_on_connect_callback(_mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test publisher on_connect callback."""
    publisher = MQTTPublisher(mqtt_config)

    # Successful connection
    publisher._on_connect(None, None, {"session present": False}, 0)  # noqa: SLF001
    assert publisher.is_connected

    # Failed connection
    publisher._on_connect(None, None, {}, 4)  # BAD_CREDENTIALS  # noqa: SLF001
    assert not publisher.is_connected


@patch("paho.mqtt.client.Client")
def test_publisher_on_disconnect_callback(_mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test publisher on_disconnect callback."""
    publisher = MQTTPublisher(mqtt_config)
    publisher._connected = True  # noqa: SLF001

    # Clean disconnect
    publisher._on_disconnect(None, None, 0)  # noqa: SLF001
    assert not publisher.is_connected

    # Unexpected disconnect
    publisher._connected = True  # noqa: SLF001
    publisher._on_disconnect(None, None, 7)  # noqa: SLF001
    assert not publisher.is_connected


@patch("paho.mqtt.client.Client")
def test_publisher_on_publish_callback(_mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test publisher on_publish callback."""
    publisher = MQTTPublisher(mqtt_config)

    # Should not raise
    publisher._on_publish(None, None, 123)  # noqa: SLF001


@patch("paho.mqtt.client.Client")
def test_publisher_reconnection_config(_mock_client: Any) -> None:
    """Test publisher with reconnection configuration."""
    config = MQTTConfig(
        broker_host="localhost",
        reconnect_on_failure=True,
        reconnect_delay=10,
        max_reconnect_attempts=3,
    )

    publisher = MQTTPublisher(config)

    # Mock successful connection
    def mock_connect(*_args: Any, **_kwargs: Any) -> None:
        publisher._on_connect(None, None, {}, 0)  # noqa: SLF001

    publisher._client.connect.side_effect = mock_connect  # noqa: SLF001

    publisher.connect(timeout=1.0)

    # Verify reconnect_delay_set was called
    publisher._client.reconnect_delay_set.assert_called_once()  # noqa: SLF001


@patch("paho.mqtt.client.Client")
def test_publisher_tls_config(mock_client: Any, tmp_path: Any) -> None:
    """Test publisher with TLS configuration."""
    # Create fake cert files
    ca_file = tmp_path / "ca.crt"
    ca_file.write_text("fake ca")

    config = MQTTConfig(
        broker_host="localhost",
        use_tls=True,
        ca_certs=ca_file,
        tls_insecure=False,
    )

    MQTTPublisher(config)

    # Verify TLS was configured
    mock_client.return_value.tls_set_context.assert_called_once()


@patch("paho.mqtt.client.Client")
def test_publisher_is_connected_property(_mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test is_connected property."""
    publisher = MQTTPublisher(mqtt_config)

    assert publisher.is_connected is False

    publisher._connected = True  # noqa: SLF001
    assert publisher.is_connected is True


@patch("paho.mqtt.client.Client")
def test_publisher_payload_logging_disabled(mock_client: Any) -> None:
    """Test publishing with payload logging disabled."""
    config = MQTTConfig(
        broker_host="localhost",
        log_payloads=False,
    )

    publisher = MQTTPublisher(config)
    publisher._connected = True  # noqa: SLF001

    # Should publish without logging payload
    publisher.publish("test/topic", "sensitive data")
    mock_client.return_value.publish.assert_called_once()


@patch("paho.mqtt.client.Client")
def test_publisher_payload_logging_enabled(mock_client: Any) -> None:
    """Test publishing with payload logging enabled."""
    config = MQTTConfig(
        broker_host="localhost",
        log_payloads=True,
        max_payload_log_length=10,
    )

    publisher = MQTTPublisher(config)
    publisher._connected = True  # noqa: SLF001

    # Should publish and log sanitized payload
    long_payload = "A" * 100
    publisher.publish("test/topic", long_payload)
    mock_client.return_value.publish.assert_called_once()
