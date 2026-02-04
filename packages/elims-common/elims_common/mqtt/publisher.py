"""ELIMS Common Package - MQTT Module - Publisher."""

import json

import paho.mqtt.client as mqtt

from elims_common.logger.logger import logger
from elims_common.mqtt.client import MQTTClient
from elims_common.mqtt.config import MQTTConfig
from elims_common.mqtt.exceptions import MQTTConnectionError


class MQTTPublisher(MQTTClient):
    """MQTT Publisher for publishing messages to topics."""

    def __init__(self, config: MQTTConfig) -> None:
        """Initialize the MQTT Publisher.

        Args:
            config: MQTT configuration

        """
        super().__init__(config)

    def _setup_callbacks(self) -> None:
        """Set up MQTT client callbacks."""
        super()._setup_callbacks()
        self._client.on_publish = self._on_publish

    def _on_publish(self, _client: mqtt.Client | None, _userdata: object | None, mid: int) -> None:
        """Handle publish callback.

        Args:
            _client: MQTT client instance
            _userdata: User data (unused)
            mid: Message ID

        """
        logger.debug(self.msg.published(mid))

    def publish(
        self,
        topic: str,
        payload: str | dict[str, object] | bytes,
        *,
        retain: bool = False,
    ) -> mqtt.MQTTMessageInfo:
        """Publish a message to a topic.

        Args:
            topic: MQTT topic to publish to (no wildcards)
            payload: Message payload (string, dict, or bytes)
            qos: Quality of Service level (defaults to config.qos)
            retain: Whether to retain the message on broker

        Returns:
            MQTTMessageInfo with publish result

        Raises:
            MQTTConnectionError: If not connected
            ValueError: If topic has wildcards or payload too large

        """
        if isinstance(payload, dict):
            payload = json.dumps(payload)
        payload_bytes = payload if isinstance(payload, bytes) else str(payload).encode("utf-8")
        payload_bytes = self.validate_payload(payload)
        return self._client.publish(topic, payload_bytes, qos=self.config.qos, retain=retain)

    def validate_publish(self, topic: str) -> None:
        """Validate connection and topic before publishing.

        Args:
            topic: MQTT topic

        Raises:
            MQTTConnectionError: If not connected
            ValueError: If topic contains wildcards

        """
        if not self._connected:
            raise MQTTConnectionError(self.msg.publish_failed_not_connected(topic))
        MQTTConfig.validate_topic_base(topic)
        if "+" in topic or "#" in topic:
            raise ValueError(self.msg.publish_failed_wildcards(topic))

    def validate_payload(self, payload: str | dict[str, object] | bytes) -> bytes:
        """Convert and validate payload to bytes.

        Args:
            payload: Payload in any supported format

        Returns:
            Payload as bytes

        Raises:
            ValueError: If payload exceeds max size

        """
        if isinstance(payload, dict):
            payload = json.dumps(payload)
        payload_bytes = payload if isinstance(payload, bytes) else str(payload).encode("utf-8")
        if len(payload_bytes) > self.config.max_payload_size:
            raise ValueError(self.msg.publish_failed_payload_too_large(payload_bytes))
        return payload_bytes
