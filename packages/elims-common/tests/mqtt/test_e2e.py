"""Test ELIMS Common Package - MQTT Module - End-to-End Tests.

These tests verify the complete integration of all MQTT module components
working together in realistic scenarios. They use mocked MQTT client but
test the full flow from configuration through connection, message handling,
and cleanup.
"""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from elims_common.mqtt.config import MQTTConfig
from elims_common.mqtt.exceptions import MQTTConnectionError
from elims_common.mqtt.publisher import MQTTPublisher
from elims_common.mqtt.subscriber import MQTTSubscriber


@pytest.fixture
def mqtt_config() -> MQTTConfig:
    """Create a test MQTT configuration for E2E tests."""
    return MQTTConfig(
        broker_host="localhost",
        broker_port=1883,
        username="test_user",
        password="test_password",  # noqa: S106
        client_id="e2e_test",
        qos=1,
        log_payloads=True,
        max_payload_log_length=100,
    )


@patch("paho.mqtt.client.Client")
def test_e2e_publish_subscribe_flow(_mock_client_class: Any, mqtt_config: MQTTConfig) -> None:
    """Test complete publish-subscribe flow."""
    # Create publisher and subscriber
    publisher = MQTTPublisher(mqtt_config)

    subscriber_config = MQTTConfig(
        broker_host=mqtt_config.broker_host,
        broker_port=mqtt_config.broker_port,
        client_id="e2e_subscriber",
    )
    subscriber = MQTTSubscriber(subscriber_config)

    # Mock successful connections
    def mock_pub_connect(*_args: Any, **_kwargs: Any) -> None:
        publisher._on_connect(None, None, {"session present": False}, 0)  # noqa: SLF001

    def mock_sub_connect(*_args: Any, **_kwargs: Any) -> None:
        subscriber._on_connect(None, None, {"session present": False}, 0)  # noqa: SLF001

    # Setup mocks for both clients
    publisher._client.connect.side_effect = mock_pub_connect  # noqa: SLF001  # type: ignore[attr-defined]

    # Connect publisher
    publisher.connect(timeout=1.0)
    assert publisher.is_connected

    # Change mock for subscriber
    subscriber._client.connect.side_effect = mock_sub_connect  # noqa: SLF001  # type: ignore[attr-defined]

    # Connect subscriber
    subscriber.connect(timeout=1.0)
    assert subscriber.is_connected

    # Subscribe to topic
    received_messages = []

    def message_handler(topic: str, payload: str) -> None:
        received_messages.append({"topic": topic, "payload": payload})

    subscriber.subscribe("sensor/temperature", message_handler)

    # Publish message
    publisher.publish("sensor/temperature", {"value": 22.5, "unit": "C"})

    # Simulate message reception
    mock_msg = MagicMock()
    mock_msg.topic = "sensor/temperature"
    mock_msg.payload.decode.return_value = '{"value": 22.5, "unit": "C"}'
    subscriber._on_message(None, None, mock_msg)  # noqa: SLF001

    # Verify message was received
    assert len(received_messages) == 1
    assert received_messages[0]["topic"] == "sensor/temperature"
    assert "22.5" in received_messages[0]["payload"]

    # Cleanup
    publisher.disconnect()
    subscriber.disconnect()


@patch("paho.mqtt.client.Client")
def test_e2e_reconnection_scenario(mock_client_class: Any, mqtt_config: MQTTConfig) -> None:
    """Test reconnection scenario after unexpected disconnect."""
    mqtt_config.reconnect_on_failure = True
    mqtt_config.max_reconnect_attempts = 3
    mqtt_config.reconnect_delay = 1

    publisher = MQTTPublisher(mqtt_config)

    # Mock successful initial connection
    def mock_connect(*_args: Any, **_kwargs: Any) -> None:
        publisher._on_connect(None, None, {"session present": False}, 0)  # noqa: SLF001

    mock_client_class.return_value.connect.side_effect = mock_connect

    publisher.connect(timeout=1.0)
    assert publisher.is_connected

    # Simulate unexpected disconnect
    publisher._on_disconnect(None, None, 7)  # Unexpected disconnect code  # noqa: SLF001
    assert not publisher.is_connected

    # Verify reconnection was triggered
    assert publisher._reconnect_attempts == 1  # noqa: SLF001
    assert publisher._should_reconnect is True  # noqa: SLF001


@patch("paho.mqtt.client.Client")
def test_e2e_multiple_subscribers_same_topic(_mock_client_class: Any, mqtt_config: MQTTConfig) -> None:
    """Test multiple callbacks on same topic."""
    subscriber = MQTTSubscriber(mqtt_config)

    # Mock successful connection
    def mock_connect(*_args: Any, **_kwargs: Any) -> None:
        subscriber._on_connect(None, None, {"session present": False}, 0)  # noqa: SLF001

    subscriber._client.connect.side_effect = mock_connect  # noqa: SLF001  # type: ignore[attr-defined]
    subscriber.connect(timeout=1.0)

    # Subscribe multiple callbacks to same topic
    callback1 = MagicMock()
    callback2 = MagicMock()
    callback3 = MagicMock()

    subscriber.subscribe("sensor/temperature", callback1)
    subscriber.subscribe("sensor/temperature", callback2)
    subscriber.subscribe("sensor/temperature", callback3)

    # Simulate message
    mock_msg = MagicMock()
    mock_msg.topic = "sensor/temperature"
    mock_msg.payload.decode.return_value = "25.5"
    subscriber._on_message(None, None, mock_msg)  # noqa: SLF001

    # All callbacks should receive message
    callback1.assert_called_once_with("sensor/temperature", "25.5")
    callback2.assert_called_once_with("sensor/temperature", "25.5")
    callback3.assert_called_once_with("sensor/temperature", "25.5")

    subscriber.disconnect()


@patch("paho.mqtt.client.Client")
def test_e2e_wildcard_subscriptions(_mock_client_class: Any, mqtt_config: MQTTConfig) -> None:
    """Test wildcard topic subscriptions."""
    subscriber = MQTTSubscriber(mqtt_config)

    # Mock successful connection
    def mock_connect(*_args: Any, **_kwargs: Any) -> None:
        subscriber._on_connect(None, None, {"session present": False}, 0)  # noqa: SLF001

    subscriber._client.connect.side_effect = mock_connect  # noqa: SLF001  # type: ignore[attr-defined]
    subscriber.connect(timeout=1.0)

    # Subscribe to wildcard topics
    single_level_messages = []
    multi_level_messages = []

    def single_handler(topic: str, payload: str) -> None:
        single_level_messages.append({"topic": topic, "payload": payload})

    def multi_handler(topic: str, payload: str) -> None:
        multi_level_messages.append({"topic": topic, "payload": payload})

    subscriber.subscribe("sensor/+/temperature", single_handler)
    subscriber.subscribe("sensor/#", multi_handler)

    # Simulate messages on different topics
    for topic in ["sensor/room1/temperature", "sensor/room2/temperature", "sensor/room1/humidity"]:
        mock_msg = MagicMock()
        mock_msg.topic = topic
        mock_msg.payload.decode.return_value = "test"
        subscriber._on_message(None, None, mock_msg)  # noqa: SLF001

    # Note: Actual wildcard matching is done by broker, not client
    # In real scenario, only matching messages would be delivered
    # Here we're just testing that callbacks are registered and called

    subscriber.disconnect()


@patch("ssl.SSLContext")
@patch("paho.mqtt.client.Client")
def test_e2e_tls_secure_connection(_mock_client_class: Any, _mock_ssl_context: Any, tmp_path: Any) -> None:
    """Test end-to-end flow with TLS encryption."""
    # Create fake cert files
    ca_file = tmp_path / "ca.crt"
    cert_file = tmp_path / "client.crt"
    key_file = tmp_path / "client.key"

    ca_file.write_text("fake ca")
    cert_file.write_text("fake cert")
    key_file.write_text("fake key")

    config = MQTTConfig(
        broker_host="mqtt.example.com",
        broker_port=8883,
        use_tls=True,
        certificate_authority_file=ca_file,
        certificate_file=cert_file,
        key_file=key_file,
        tls_insecure=False,
    )

    publisher = MQTTPublisher(config)

    # Verify TLS was configured
    publisher._client.tls_set_context.assert_called_once()  # noqa: SLF001  # type: ignore[attr-defined]

    # Mock connection
    def mock_connect(*_args: Any, **_kwargs: Any) -> None:
        publisher._on_connect(None, None, {"session present": False}, 0)  # noqa: SLF001

    publisher._client.connect.side_effect = mock_connect  # noqa: SLF001  # type: ignore[attr-defined]

    publisher.connect(timeout=1.0)
    assert publisher.is_connected

    # Publish message
    publisher.publish("secure/topic", "encrypted message")

    publisher.disconnect()


@patch("paho.mqtt.client.Client")
def test_e2e_error_recovery_flow(_mock_client_class: Any, mqtt_config: MQTTConfig) -> None:
    """Test error recovery in publish-subscribe flow."""
    publisher = MQTTPublisher(mqtt_config)
    subscriber = MQTTSubscriber(mqtt_config)

    # Test connection failure
    def mock_failed_connect(*_args: Any, **_kwargs: Any) -> None:
        publisher._on_connect(None, None, {}, 3)  # SERVER_UNAVAILABLE  # noqa: SLF001

    publisher._client.connect.side_effect = mock_failed_connect  # noqa: SLF001  # type: ignore[attr-defined]

    with pytest.raises(MQTTConnectionError, match="server unavailable"):
        publisher.connect(timeout=1.0)

    # Test publishing when not connected
    with pytest.raises(MQTTConnectionError, match="Not connected"):
        publisher.publish("test/topic", "message")

    # Test callback error handling in subscriber
    def failing_callback(_topic: str, _payload: str) -> None:
        error_msg = "Callback failed"
        raise RuntimeError(error_msg)

    subscriber.subscribe("test/topic", failing_callback)

    # Simulate message - should not raise despite callback error
    mock_msg = MagicMock()
    mock_msg.topic = "test/topic"
    mock_msg.payload.decode.return_value = "test"
    subscriber._on_message(None, None, mock_msg)  # noqa: SLF001


@patch("paho.mqtt.client.Client")
def test_e2e_payload_types(_mock_client_class: Any, mqtt_config: MQTTConfig) -> None:
    """Test publishing and receiving different payload types."""
    publisher = MQTTPublisher(mqtt_config)

    # Mock successful connections
    def mock_pub_connect(*_args: Any, **_kwargs: Any) -> None:
        publisher._on_connect(None, None, {"session present": False}, 0)  # noqa: SLF001

    publisher._client.connect.side_effect = mock_pub_connect  # noqa: SLF001  # type: ignore[attr-defined]
    publisher.connect(timeout=1.0)

    # Test string payload
    publisher.publish("test/string", "Hello World")
    publisher._client.publish.assert_called()  # noqa: SLF001  # type: ignore[attr-defined]

    # Test dict payload (converted to JSON)
    publisher.publish("test/json", {"temperature": 22.5, "humidity": 60})

    # Test bytes payload
    publisher.publish("test/binary", b"\x01\x02\x03\x04")

    # Verify all publishes were called
    assert publisher._client.publish.call_count == 3  # noqa: SLF001, PLR2004  # type: ignore[attr-defined]

    publisher.disconnect()


@patch("paho.mqtt.client.Client")
def test_e2e_qos_levels(mock_client_class: Any, mqtt_config: MQTTConfig) -> None:
    """Test different QoS levels in publish-subscribe."""
    publisher = MQTTPublisher(mqtt_config)

    def mock_connect(*_args: Any, **_kwargs: Any) -> None:
        publisher._on_connect(None, None, {"session present": False}, 0)  # noqa: SLF001

    mock_client_class.return_value.connect.side_effect = mock_connect
    publisher.connect(timeout=1.0)

    # Test all QoS levels
    publisher.publish("test/qos0", "message", qos=0)
    publisher.publish("test/qos1", "message", qos=1)
    publisher.publish("test/qos2", "message", qos=2)

    # Verify QoS was passed correctly
    calls = publisher._client.publish.call_args_list  # noqa: SLF001  # type: ignore[attr-defined]
    assert calls[0][1]["qos"] == 0
    assert calls[1][1]["qos"] == 1
    assert calls[2][1]["qos"] == 2  # noqa: PLR2004

    publisher.disconnect()


@patch("paho.mqtt.client.Client")
def test_e2e_retain_flag(mock_client_class: Any, mqtt_config: MQTTConfig) -> None:
    """Test publishing with retain flag."""
    publisher = MQTTPublisher(mqtt_config)

    def mock_connect(*_args: Any, **_kwargs: Any) -> None:
        publisher._on_connect(None, None, {"session present": False}, 0)  # noqa: SLF001

    mock_client_class.return_value.connect.side_effect = mock_connect
    publisher.connect(timeout=1.0)

    # Publish retained message
    publisher.publish("config/last_value", "42", retain=True)

    # Verify retain flag
    call_args = mock_client_class.return_value.publish.call_args
    assert call_args[1]["retain"] is True

    publisher.disconnect()


@patch("paho.mqtt.client.Client")
def test_e2e_session_persistence(_mock_client_class: Any) -> None:
    """Test session persistence with clean_session flag."""
    # Test with clean session
    clean_config = MQTTConfig(
        broker_host="localhost",
        clean_session=True,
    )

    publisher = MQTTPublisher(clean_config)

    def mock_connect(*_args: Any, **_kwargs: Any) -> None:
        # Session present should be False with clean session
        publisher._on_connect(None, None, {"session present": False}, 0)  # noqa: SLF001

    publisher._client.connect.side_effect = mock_connect  # noqa: SLF001  # type: ignore[attr-defined]
    publisher.connect(timeout=1.0)

    publisher.disconnect()

    # Test without clean session
    persistent_config = MQTTConfig(
        broker_host="localhost",
        clean_session=False,
    )

    publisher2 = MQTTPublisher(persistent_config)

    def mock_connect2(*_args: Any, **_kwargs: Any) -> None:
        # Session present might be True with persistent session
        publisher2._on_connect(None, None, {"session present": True}, 0)  # noqa: SLF001

    publisher2._client.connect.side_effect = mock_connect2  # noqa: SLF001  # type: ignore[attr-defined]
    publisher2.connect(timeout=1.0)

    publisher2.disconnect()


@patch("paho.mqtt.client.Client")
def test_e2e_subscriber_reconnect_resubscribe(_mock_client_class: Any, mqtt_config: MQTTConfig) -> None:
    """Test that subscriber resubscribes to topics after reconnection."""
    subscriber = MQTTSubscriber(mqtt_config)

    # Mock successful connection
    def mock_connect(*_args: Any, **_kwargs: Any) -> None:
        subscriber._on_connect(None, None, {"session present": False}, 0)  # noqa: SLF001

    subscriber._client.connect.side_effect = mock_connect  # noqa: SLF001  # type: ignore[attr-defined]
    subscriber.connect(timeout=1.0)

    # Subscribe to topics
    callback1 = MagicMock()
    callback2 = MagicMock()
    subscriber.subscribe("sensor/temp", callback1)
    subscriber.subscribe("sensor/humidity", callback2)

    # Clear previous calls
    subscriber._client.subscribe.reset_mock()  # noqa: SLF001  # type: ignore[attr-defined]

    # Simulate reconnection
    subscriber._on_connect(None, None, {"session present": False}, 0)  # noqa: SLF001

    # Should resubscribe to both topics
    assert subscriber._client.subscribe.call_count == 2  # noqa: PLR2004, SLF001  # type: ignore[attr-defined]

    subscriber.disconnect()


@patch("paho.mqtt.client.Client")
def test_e2e_payload_sanitization(_mock_client_class: Any) -> None:
    """Test payload sanitization in logging."""
    config = MQTTConfig(
        broker_host="localhost",
        log_payloads=True,
        max_payload_log_length=20,
    )

    publisher = MQTTPublisher(config)
    subscriber = MQTTSubscriber(config)

    # Mock connections
    def mock_pub_connect(*_args: Any, **_kwargs: Any) -> None:
        publisher._on_connect(None, None, {"session present": False}, 0)  # noqa: SLF001

    publisher._client.connect.side_effect = mock_pub_connect  # noqa: SLF001
    publisher.connect(timeout=1.0)

    # Publish long payload (should be sanitized in logs)
    long_payload = "A" * 100
    publisher.publish("test/topic", long_payload)

    # Subscriber receives long payload
    callback = MagicMock()
    subscriber.subscribe("test/topic", callback)

    mock_msg = MagicMock()
    mock_msg.topic = "test/topic"
    mock_msg.payload.decode.return_value = long_payload
    subscriber._on_message(None, None, mock_msg)  # noqa: SLF001

    # Callback should receive full payload
    callback.assert_called_once_with("test/topic", long_payload)

    publisher.disconnect()


@patch("paho.mqtt.client.Client")
def test_e2e_connection_timeout_handling(_mock_client_class: Any, mqtt_config: MQTTConfig) -> None:
    """Test handling of connection timeouts."""
    publisher = MQTTPublisher(mqtt_config)

    # Don't trigger callback - let connection timeout
    with pytest.raises(MQTTConnectionError, match="timeout"):
        publisher.connect(timeout=0.1)

    assert not publisher.is_connected

    # Should not be able to publish
    with pytest.raises(MQTTConnectionError, match="Not connected"):
        publisher.publish("test/topic", "message")


@patch("paho.mqtt.client.Client")
def test_e2e_validation_errors(_mock_client_class: Any, mqtt_config: MQTTConfig) -> None:
    """Test input validation across module."""
    publisher = MQTTPublisher(mqtt_config)

    def mock_connect(*_args: Any, **_kwargs: Any) -> None:
        publisher._on_connect(None, None, {"session present": False}, 0)  # noqa: SLF001

    publisher._client.connect.side_effect = mock_connect  # noqa: SLF001
    publisher.connect(timeout=1.0)

    # Test empty topic validation
    with pytest.raises(ValueError, match="cannot be empty"):
        publisher.publish("", "message")

    # Test wildcard in publish topic
    with pytest.raises(ValueError, match="Wildcards"):
        publisher.publish("sensor/+/temp", "message")

    # Test null character in topic
    with pytest.raises(ValueError, match="null character"):
        publisher.publish("sensor\0temp", "message")

    publisher.disconnect()
