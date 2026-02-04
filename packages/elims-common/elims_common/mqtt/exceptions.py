"""ELIMS Common Package - MQTT Module - Exceptions."""

from elims_common.logger.logger import logger
from elims_common.mqtt.constants import MQTTReturnCode


class MQTTError(Exception):
    """Base exception for MQTT-related errors."""


class MQTTLWTTopicError(MQTTError):
    """Exception raised for invalid MQTT LWT topics."""

    def __init__(self, msg: str) -> None:
        """Initialize MQTT LWT topic error.

        Args:
            msg: Error message
            topic: Invalid MQTT topic

        """
        logger.error(msg)
        super().__init__(msg)


class MQTTConnectionError(MQTTError):
    """Exception raised when MQTT connection fails."""

    def __init__(self, rc: int) -> None:
        """Initialize MQTT connection authentication error.

        Args:
            rc: MQTT return code

        """
        msg = self.msg.connection_failed(MQTTReturnCode.get_message(rc))
        logger.error(msg)
        super().__init__(msg)


class MQTTPublishError(MQTTError):
    """Exception raised when publishing a message fails."""

    def __init__(
        self,
        message: str,
        *,
        topic: str | None = None,
        qos: int | None = None,
        payload_size: int | None = None,
    ) -> None:
        """Initialize MQTT publish error.

        Args:
            message: Error message
            topic: MQTT topic
            qos: Quality of Service level (0, 1, or 2)
            payload_size: Size of the payload in bytes

        """
        self.topic = topic
        self.qos = qos
        self.payload_size = payload_size

        # Build detailed error message
        parts = [message]
        if topic:
            parts.append(f"topic={topic}")
        if qos is not None:
            parts.append(f"qos={qos}")
        if payload_size is not None:
            parts.append(f"payload_size={payload_size}")

        full_message = parts[0] if len(parts) == 1 else f"{parts[0]} ({', '.join(parts[1:])})"
        super().__init__(full_message)


class MQTTSubscribeError(MQTTError):
    """Exception raised when subscribing to a topic fails."""

    def __init__(
        self,
        message: str,
        *,
        topic: str | None = None,
        qos: int | None = None,
        granted_qos: int | None = None,
    ) -> None:
        """Initialize MQTT subscribe error.

        Args:
            message: Error message
            topic: MQTT topic or topic filter
            qos: Requested Quality of Service level (0, 1, or 2)
            granted_qos: Quality of Service level granted by broker

        """
        self.topic = topic
        self.qos = qos
        self.granted_qos = granted_qos

        # Build detailed error message
        parts = [message]
        if topic:
            parts.append(f"topic={topic}")
        if qos is not None:
            parts.append(f"qos={qos}")
        if granted_qos is not None:
            parts.append(f"granted_qos={granted_qos}")

        full_message = parts[0] if len(parts) == 1 else f"{parts[0]} ({', '.join(parts[1:])})"
        super().__init__(full_message)
