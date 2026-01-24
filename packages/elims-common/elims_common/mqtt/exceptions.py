"""ELIMS Common Package - MQTT Module - Exceptions."""


class MQTTError(Exception):
    """Base exception for MQTT-related errors."""


class MQTTConnectionError(MQTTError):
    """Exception raised when MQTT connection fails or is not established."""


class MQTTPublishError(MQTTError):
    """Exception raised when publishing a message fails."""


class MQTTSubscribeError(MQTTError):
    """Exception raised when subscribing to a topic fails."""
