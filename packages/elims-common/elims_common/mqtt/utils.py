"""ELIMS Common Package - MQTT Module - Utilities."""

# MQTT protocol constants
MQTT_MAX_TOPIC_LENGTH = 65535


class MQTTUtils:
    """Utility methods for MQTT operations."""

    @staticmethod
    def sanitize_payload_for_logging(payload: str | bytes, max_length: int = 100) -> str:
        """Sanitize payload for safe logging.

        Args:
            payload: The payload to sanitize
            max_length: Maximum length to log (0 for no limit)

        Returns:
            Sanitized payload string safe for logging

        """
        # Convert bytes to string
        if isinstance(payload, bytes):
            try:
                payload_str = payload.decode("utf-8")
            except UnicodeDecodeError:
                return f"<binary data, {len(payload)} bytes>"
        else:
            payload_str = str(payload)

        # Truncate if needed
        if max_length > 0 and len(payload_str) > max_length:
            return f"{payload_str[:max_length]}... ({len(payload_str)} bytes total)"

        return payload_str

    @staticmethod
    def validate_topic(topic: str) -> None:
        """Validate MQTT topic string.

        Args:
            topic: Topic to validate

        Raises:
            ValueError: If topic is invalid

        """
        if not topic:
            msg = "Topic cannot be empty"
            raise ValueError(msg)

        if len(topic) > MQTT_MAX_TOPIC_LENGTH:
            msg = f"Topic too long: {len(topic)} bytes (max {MQTT_MAX_TOPIC_LENGTH})"
            raise ValueError(msg)

        # Check for invalid null character
        if "\0" in topic:
            msg = "Topic cannot contain null character"
            raise ValueError(msg)

        # Wildcards only valid for subscription, not publishing
        # This will be checked in the publish method
