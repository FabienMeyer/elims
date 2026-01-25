"""ELIMS Common Package - MQTT Module - Subscriber."""

import ssl
from collections.abc import Callable
from threading import Event

import paho.mqtt.client as mqtt

# Import the helper for wildcard matching
from paho.mqtt.client import topic_matches_sub

from elims_common.logger.logger import logger
from elims_common.mqtt.config import MQTTConfig
from elims_common.mqtt.constants import MQTTConnectionFlags, MQTTReturnCode, MQTTTLSVersion
from elims_common.mqtt.exceptions import MQTTConnectionError
from elims_common.mqtt.messages import MQTTLogMessages
from elims_common.mqtt.utils import MQTTUtils


class MQTTSubscriber:
    """MQTT Subscriber for subscribing to topics and receiving messages."""

    def __init__(self, config: MQTTConfig) -> None:
        """Initialize the MQTT Subscriber."""
        self.config = config
        self._client = mqtt.Client(
            client_id=config.client_id,
            clean_session=config.clean_session,
            protocol=mqtt.MQTTv311,
        )

        if config.username and config.password:
            self._client.username_pw_set(config.username, config.password.get_secret_value())

        if config.use_tls:
            tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            if config.tls_version:
                tls_context.minimum_version = ssl.TLSVersion.TLSv1_3 if config.tls_version == MQTTTLSVersion.V1_3 else ssl.TLSVersion.TLSv1_2

            if config.certificate_authority_file:
                tls_context.load_verify_locations(cafile=str(config.certificate_authority_file))
            else:
                tls_context.load_default_certs()

            if config.certificate_file and config.key_file:
                tls_context.load_cert_chain(certfile=str(config.certificate_file), keyfile=str(config.key_file))

            if config.tls_insecure:
                tls_context.check_hostname = False
                tls_context.verify_mode = ssl.CERT_NONE
            else:
                tls_context.check_hostname = True
                tls_context.verify_mode = ssl.CERT_REQUIRED

            self._client.tls_set_context(tls_context)

        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message

        self._connected = False
        self._connection_error: MQTTConnectionError | None = None
        self._connect_event = Event()
        self._reconnect_attempts = 0
        self._should_reconnect = False
        self._subscriptions: dict[str, list[Callable[[str, str], None]]] = {}

    def _on_connect(self, _client: mqtt.Client | None, _userdata: object | None, flags: dict, rc: int) -> None:
        """Handle connection callback."""
        connection_flags = MQTTConnectionFlags.from_dict(flags)
        if rc == MQTTReturnCode.SUCCESS:
            self._connected = True
            logger.info(MQTTLogMessages.connected("Subscriber", session_present=connection_flags.session_present))
            for topic in self._subscriptions:
                self._client.subscribe(topic, qos=self.config.qos)
                logger.info(MQTTLogMessages.resubscribed(topic))
        else:
            self._connected = False
            # Error handling logic...
            self._connect_event.set()
        self._connect_event.set()

    def _on_message(self, _client: mqtt.Client | None, _userdata: object, msg: mqtt.MQTTMessage) -> None:
        """Handle message callback with wildcard support."""
        topic = msg.topic
        payload = msg.payload.decode("utf-8")

        # Log incoming message
        if self.config.log_payloads:
            sanitized = MQTTUtils.sanitize_payload_for_logging(payload, self.config.max_payload_log_length)
            logger.debug(MQTTLogMessages.message_received(topic, sanitized))
        else:
            logger.debug(f"Received message on {topic}")

        # REWRITTEN LOGIC: Check patterns instead of literal keys
        for pattern, callbacks in self._subscriptions.items():
            if topic_matches_sub(pattern, topic):
                for callback in callbacks:
                    callback(topic, payload)

    def connect(self, timeout: float = 5.0) -> None:
        """Connect to the MQTT broker with an optional timeout."""
        self._connection_error = None
        self._connect_event.clear()
        self._should_reconnect = True
        self._client.connect(self.config.broker_host, self.config.broker_port, self.config.keepalive)
        self._client.loop_start()
        if not self._connect_event.wait(timeout=timeout):
            self._client.loop_stop()
            msg = MQTTLogMessages.connection_timeout("Subscriber", timeout)
            raise MQTTConnectionError(msg)

    def subscribe(self, topic: str, callback: Callable[[str, str], None], qos: int | None = None) -> None:
        """Subscribe to a topic with a callback."""
        MQTTUtils.validate_topic(topic)
        if topic not in self._subscriptions:
            self._subscriptions[topic] = []
        self._subscriptions[topic].append(callback)
        if self._connected:
            self._client.subscribe(topic, qos=qos or self.config.qos)
            logger.info(MQTTLogMessages.subscribed(topic))

    def disconnect(self) -> None:
        """Disconnect from the MQTT broker."""
        self._should_reconnect = False
        self._client.loop_stop()
        self._client.disconnect()

    @property
    def is_connected(self) -> bool:
        """Check if the client is connected to the broker."""
        return self._connected
