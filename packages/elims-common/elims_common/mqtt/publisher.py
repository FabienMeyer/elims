"""ELIMS Common Package - MQTT Module - Publisher."""

import json

import paho.mqtt.client as mqtt

from elims_common.logger.logger import logger
from elims_common.mqtt.client import MQTTClient
from elims_common.mqtt.config import MQTTConfig
from elims_common.mqtt.exceptions import MQTTConnectionError
from elims_common.mqtt.messages import MQTTLogMessages
from elims_common.mqtt.utils import MQTTUtils


class MQTTPublisher(MQTTClient):
    """MQTT Publisher for publishing messages to topics."""

    def __init__(self, config: MQTTConfig) -> None:
        """Initialize the MQTT Publisher."""
        super().__init__(config, "Publisher")

    def _setup_callbacks(self) -> None:
        """Set up MQTT client callbacks."""
        super()._setup_callbacks()
        self._client.on_publish = self._on_publish

    def _on_publish(self, _client: mqtt.Client | None, _userdata: object | None, mid: int) -> None:
        """Handle publish callback."""
        logger.debug(f"Message published (mid={mid})")

    def publish(
        self,
        topic: str,
        payload: str | dict[str, object] | bytes,
        qos: int | None = None,
        *,
        retain: bool = False,
    ) -> mqtt.MQTTMessageInfo:
        """Publish a message to a topic."""
        if not self._connected:
            msg = MQTTLogMessages.publish_failed_not_connected(topic)
            logger.error(msg)
            raise MQTTConnectionError(msg)

        MQTTUtils.validate_topic(topic)

        if "+" in topic or "#" in topic:
            msg = MQTTLogMessages.publish_failed_wildcards(topic)
            logger.error(msg)
            raise ValueError(msg)

        if isinstance(payload, dict):
            payload = json.dumps(payload)

        payload_bytes = payload if isinstance(payload, bytes) else str(payload).encode("utf-8")
        if len(payload_bytes) > self.config.max_payload_bytes:
            msg = f"Payload too large: {len(payload_bytes)} bytes (max {self.config.max_payload_bytes})"
            logger.error(msg)
            raise ValueError(msg)

        qos_level = qos if qos is not None else self.config.qos

        result = self._client.publish(
            topic,
            payload,
            qos=qos_level,
            retain=retain,
        )

        if self.config.log_payloads:
            sanitized = MQTTUtils.sanitize_payload_for_logging(
                payload,
                self.config.max_payload_log_length,
            )
            logger.debug(MQTTLogMessages.publishing(topic, sanitized))
        else:
            logger.debug(f"Publishing to {topic}")

        return result
