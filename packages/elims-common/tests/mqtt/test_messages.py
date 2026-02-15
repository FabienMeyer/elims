"""Test ELIMS Common Package - MQTT Module - Log Messages."""

from elims_common.mqtt.messages import MQTTLogMessages


def test_connecting_message() -> None:
    """Test connecting log message."""
    msg = MQTTLogMessages.connecting("localhost", 8883, "Publisher")
    assert "Publisher" in msg
    assert "localhost:8883" in msg
    assert "Connecting" in msg or "connecting" in msg


def test_connected_message() -> None:
    """Test connected log message."""
    # Without session
    msg = MQTTLogMessages.connected("Publisher", session_present=False)
    assert "Publisher" in msg
    assert "connected" in msg.lower()

    # With session
    msg = MQTTLogMessages.connected("Subscriber", session_present=True)
    assert "Subscriber" in msg
    assert "session" in msg.lower()


def test_connection_failed_message() -> None:
    """Test connection failed log message."""
    msg = MQTTLogMessages.connection_failed("Publisher", "Bad credentials")
    assert "Publisher" in msg
    assert "Bad credentials" in msg
    assert "failed" in msg.lower()


def test_connection_timeout_message() -> None:
    """Test connection timeout log message."""
    msg = MQTTLogMessages.connection_timeout("Subscriber", 5.0)
    assert "Subscriber" in msg
    assert "5.0" in msg
    assert "timeout" in msg.lower()


def test_connection_error_message() -> None:
    """Test connection error log message."""
    error = Exception("Network error")
    msg = MQTTLogMessages.connection_error("Publisher", error)
    assert "Publisher" in msg
    assert "Network error" in msg


def test_disconnected_message() -> None:
    """Test disconnected log message."""
    msg = MQTTLogMessages.disconnected("Publisher")
    assert "Publisher" in msg
    assert "disconnect" in msg.lower()


def test_unexpected_disconnect_message() -> None:
    """Test unexpected disconnect log message."""
    msg = MQTTLogMessages.unexpected_disconnect("Subscriber", 7)
    assert "Subscriber" in msg
    assert "7" in msg
    assert "unexpected" in msg.lower()


def test_published_message() -> None:
    """Test published log message."""
    msg = MQTTLogMessages.published("sensor/temp", "22.5")
    assert "sensor/temp" in msg
    assert "22.5" in msg


def test_publishing_message() -> None:
    """Test publishing log message."""
    msg = MQTTLogMessages.publishing("sensor/temp", "22.5")
    assert "sensor/temp" in msg
    assert "22.5" in msg


def test_subscribed_message() -> None:
    """Test subscribed log message."""
    msg = MQTTLogMessages.subscribed("sensor/#", 1)
    assert "sensor/#" in msg
    assert "1" in msg


def test_resubscribed_message() -> None:
    """Test resubscribed log message."""
    msg = MQTTLogMessages.resubscribed("sensor/#")
    assert "sensor/#" in msg
    assert "re-subscribed" in msg.lower()


def test_unsubscribed_message() -> None:
    """Test unsubscribed log message."""
    msg = MQTTLogMessages.unsubscribed("sensor/#")
    assert "sensor/#" in msg
    assert "unsubscrib" in msg.lower()


def test_message_received_message() -> None:
    """Test message received log message."""
    msg = MQTTLogMessages.message_received("sensor/temp", "22.5")
    assert "sensor/temp" in msg
    assert "22.5" in msg


def test_callback_error_message() -> None:
    """Test callback error log message."""
    error = ValueError("Invalid value")
    msg = MQTTLogMessages.callback_error("sensor/temp", error)
    assert "sensor/temp" in msg
    assert "Invalid value" in msg
    assert "callback" in msg.lower()


def test_all_messages_return_strings() -> None:
    """Test that all message methods return strings."""
    error = Exception("test")

    messages = [
        MQTTLogMessages.connecting("host", 8883, "Publisher"),
        MQTTLogMessages.connected("Publisher", session_present=False),
        MQTTLogMessages.connection_failed("Publisher", "error"),
        MQTTLogMessages.connection_timeout("Publisher", 5.0),
        MQTTLogMessages.connection_error("Publisher", error),
        MQTTLogMessages.disconnected("Publisher"),
        MQTTLogMessages.unexpected_disconnect("Publisher", 1),
        MQTTLogMessages.published("topic", "payload"),
        MQTTLogMessages.publishing("topic", "payload"),
        MQTTLogMessages.subscribed("topic", 1),
        MQTTLogMessages.resubscribed("topic"),
        MQTTLogMessages.unsubscribed("topic"),
        MQTTLogMessages.message_received("topic", "payload"),
        MQTTLogMessages.callback_error("topic", error),
    ]

    for msg in messages:
        assert isinstance(msg, str)
        assert len(msg) > 0
