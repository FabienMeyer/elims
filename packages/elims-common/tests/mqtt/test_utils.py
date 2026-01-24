"""Test ELIMS Common Package - MQTT Module - Utilities."""

import pytest
from elims_common.mqtt.utils import MQTTUtils


def test_sanitize_string_payload() -> None:
    """Test sanitizing string payload."""
    payload = "Hello MQTT"
    result = MQTTUtils.sanitize_payload_for_logging(payload, max_length=100)
    assert result == "Hello MQTT"


def test_sanitize_long_payload() -> None:
    """Test sanitizing payload that exceeds max length."""
    payload = "A" * 200
    result = MQTTUtils.sanitize_payload_for_logging(payload, max_length=100)
    assert result.startswith("A" * 100)
    assert "..." in result
    assert "200 bytes total" in result


def test_sanitize_no_length_limit() -> None:
    """Test sanitizing payload with no length limit."""
    payload = "A" * 200
    result = MQTTUtils.sanitize_payload_for_logging(payload, max_length=0)
    assert result == "A" * 200
    assert "..." not in result


def test_sanitize_bytes_payload() -> None:
    """Test sanitizing bytes payload."""
    payload = b"Hello MQTT"
    result = MQTTUtils.sanitize_payload_for_logging(payload, max_length=100)
    assert result == "Hello MQTT"


def test_sanitize_long_bytes_payload() -> None:
    """Test sanitizing long bytes payload."""
    payload = b"B" * 200
    result = MQTTUtils.sanitize_payload_for_logging(payload, max_length=100)
    assert result.startswith("B" * 100)
    assert "..." in result
    assert "200 bytes total" in result


def test_sanitize_binary_data() -> None:
    """Test sanitizing non-UTF8 binary data."""
    payload = b"\x80\x81\x82\x83"
    result = MQTTUtils.sanitize_payload_for_logging(payload, max_length=100)
    assert result == "<binary data, 4 bytes>"


def test_sanitize_empty_payload() -> None:
    """Test sanitizing empty payload."""
    result = MQTTUtils.sanitize_payload_for_logging("", max_length=100)
    assert result == ""

    result = MQTTUtils.sanitize_payload_for_logging(b"", max_length=100)
    assert result == ""


def test_validate_topic_valid() -> None:
    """Test validating valid topics."""
    # Should not raise
    MQTTUtils.validate_topic("sensor/temperature")
    MQTTUtils.validate_topic("home/living_room/light")
    MQTTUtils.validate_topic("device123/status")
    MQTTUtils.validate_topic("sensor/#")  # Wildcards are OK for validation
    MQTTUtils.validate_topic("sensor/+/temp")


def test_validate_topic_empty() -> None:
    """Test validating empty topic."""
    with pytest.raises(ValueError, match="cannot be empty"):
        MQTTUtils.validate_topic("")


def test_validate_topic_too_long() -> None:
    """Test validating topic that is too long."""
    long_topic = "a" * 65536
    with pytest.raises(ValueError, match="too long"):
        MQTTUtils.validate_topic(long_topic)


def test_validate_topic_null_character() -> None:
    """Test validating topic with null character."""
    with pytest.raises(ValueError, match="null character"):
        MQTTUtils.validate_topic("sensor/temp\0/value")


def test_validate_topic_max_length() -> None:
    """Test validating topic at max length boundary."""
    # Should not raise at exactly 65535
    max_topic = "a" * 65535
    MQTTUtils.validate_topic(max_topic)


def test_validate_topic_with_special_chars() -> None:
    """Test validating topics with special characters."""
    # Should not raise for valid special characters
    MQTTUtils.validate_topic("sensor/temp-1")
    MQTTUtils.validate_topic("sensor/temp_2")
    MQTTUtils.validate_topic("sensor/temp.3")
    MQTTUtils.validate_topic("$SYS/broker/status")  # $ is valid


def test_utils_class_is_static() -> None:
    """Test that MQTTUtils class contains only static methods."""
    # Should not need to instantiate
    # All methods should be callable on class directly
    assert callable(MQTTUtils.sanitize_payload_for_logging)
    assert callable(MQTTUtils.validate_topic)

    # Can still instantiate if needed (though not typical usage)
    utils = MQTTUtils()
    assert callable(utils.sanitize_payload_for_logging)
