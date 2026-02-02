"""ELIMS Common Package - MQTT Module - Subscriber."""

from collections.abc import Callable

import paho.mqtt.client as mqtt
from paho.mqtt.client import topic_matches_sub

from elims_common.logger.logger import logger
from elims_common.mqtt.client import MQTTClient
from elims_common.mqtt.config import MQTTConfig
from elims_common.mqtt.constants import MQTTConnectionFlags
from elims_common.mqtt.messages import MQTTLogMessages
from elims_common.mqtt.utils import MQTTUtils


class MQTTSubscriber(MQTTClient):
    """MQTT Subscriber for subscribing to topics and receiving messages."""

    def __init__(self, config: MQTTConfig) -> None:
        """Initialize the MQTT Subscriber."""
        self._subscriptions: dict[str, list[Callable[[str, str], None]]] = {}
        super().__init__(config, "Subscriber")

    def _setup_callbacks(self) -> None:
        """Set up MQTT client callbacks."""
        super()._setup_callbacks()
        self._client.on_message = self._on_message

    def _on_connect_success(self, _connection_flags: MQTTConnectionFlags) -> None:
        """Handle successful connection by resubscribing to topics."""
        for topic in self._subscriptions:
            self._client.subscribe(topic, qos=self.config.qos)
            logger.info(MQTTLogMessages.resubscribed(topic))

    def _on_message(self, _client: mqtt.Client | None, _userdata: object, msg: mqtt.MQTTMessage) -> None:
        """Handle message callback with wildcard support."""
        topic = msg.topic
        if len(msg.payload) > self.config.max_payload_bytes:
            logger.warning(f"Dropped message on {topic}: payload too large " f"({len(msg.payload)} bytes, max {self.config.max_payload_bytes})")
            return

        payload = msg.payload.decode("utf-8")

        if self.config.log_payloads:
            sanitized = MQTTUtils.sanitize_payload_for_logging(payload, self.config.max_payload_log_length)
            logger.debug(MQTTLogMessages.message_received(topic, sanitized))
        else:
            logger.debug(f"Received message on {topic}")

        for pattern, callbacks in self._subscriptions.items():
            if topic_matches_sub(pattern, topic):
                for callback in callbacks:
                    callback(topic, payload)

    def subscribe(self, topic: str, callback: Callable[[str, str], None], qos: int | None = None) -> None:
        """Subscribe to a topic with a callback."""
        MQTTUtils.validate_topic(topic)
        if topic not in self._subscriptions:
            self._subscriptions[topic] = []
        self._subscriptions[topic].append(callback)
        if self._connected:
            self._client.subscribe(topic, qos=qos or self.config.qos)
            logger.info(MQTTLogMessages.subscribed(topic))
