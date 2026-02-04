"""ELIMS Common Package - MQTT Module - Subscriber."""

from collections.abc import Callable

import paho.mqtt.client as mqtt
from paho.mqtt.client import topic_matches_sub

from elims_common.logger.logger import logger
from elims_common.mqtt.client import MQTTClient
from elims_common.mqtt.config import MQTTConfig
from elims_common.mqtt.constants import MQTTReturnCode


class MQTTSubscriber(MQTTClient):
    """MQTT Subscriber for subscribing to topics and receiving messages."""

    def __init__(self, config: MQTTConfig) -> None:
        """Initialize the MQTT Subscriber."""
        self._subscriptions: dict[str, list[Callable[[str, str], None]]] = {}
        super().__init__(config)

    def _setup_callbacks(self) -> None:
        """Set up MQTT client callbacks."""
        super()._setup_callbacks()
        self._client.on_message = self._on_message

    def _on_connect(self, _client: mqtt.Client | None, _userdata: object | None, flags: dict, rc: int) -> None:
        """Handle connection callback and resubscribe on success."""
        super()._on_connect(_client, _userdata, flags, rc)
        if rc == MQTTReturnCode.SUCCESS:
            self.resubscribe_all()

    def _on_message(self, _client: mqtt.Client | None, _userdata: object | None, msg: mqtt.MQTTMessage) -> None:
        """Handle message callback with wildcard support.

        Args:
            _client: MQTT client instance
            _userdata: User data (unused)
            msg: MQTT message

        """
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        self.invoke_callbacks(topic, payload)

    def invoke_callbacks(self, topic: str, payload: str) -> None:
        """Invoke all callbacks matching the topic pattern.

        Args:
            topic: Message topic
            payload: Message payload string

        """
        for pattern, callbacks in self._subscriptions.items():
            if topic_matches_sub(pattern, topic):
                for callback in callbacks:
                    callback(topic, payload)

    def resubscribe_all(self) -> None:
        """Resubscribe to all stored topics."""
        for topic in self._subscriptions:
            self._client.subscribe(topic, qos=self.config.qos)
            logger.info(self.msg.subscribed(topic))

    def subscribe(self, topic: str, callback: Callable[[str, str], None]) -> None:
        """Subscribe to a topic with a callback.

        Args:
            topic: MQTT topic to subscribe to (wildcards allowed)
            callback: Callback function called when message is received
            qos: Quality of Service level (defaults to config.qos)

        """
        MQTTConfig.validate_topic(topic)

        if topic not in self._subscriptions:
            self._subscriptions[topic] = []
        self._subscriptions[topic].append(callback)

        if self._connected:
            self._client.subscribe(topic, qos=self.config.qos)
            logger.info(self.msg.subscribed(topic))

    def unsubscribe(self, topic: str, callback: Callable[[str, str], None]) -> None:
        """Unsubscribe a callback from a topic.

        Args:
            topic: MQTT topic to unsubscribe from
            callback: Callback function to remove

        """
        if topic in self._subscriptions:
            try:
                self._subscriptions[topic].remove(callback)
                if not self._subscriptions[topic]:
                    del self._subscriptions[topic]
                    if self._connected:
                        self._client.unsubscribe(topic)
                        logger.info(self.msg.unsubscribed(topic))
            except ValueError:
                logger.warning(self.msg.unsubscription_failed(topic))
