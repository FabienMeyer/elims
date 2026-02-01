"""ELIMS Common Package - MQTT Module - Subscriber."""

import json
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

        self._setup_auth()
        self._setup_tls()
        self._setup_lwt()
        self._setup_callbacks()

        self._connected = False
        self._connection_error: MQTTConnectionError | None = None
        self._connect_event = Event()
        self._reconnect_attempts = 0
        self._should_reconnect = False
        self._subscriptions: dict[str, list[Callable[[str, str], None]]] = {}

    def _setup_auth(self) -> None:
        if self.config.username and self.config.password:
            self._client.username_pw_set(
                self.config.username,
                self.config.password.get_secret_value(),
            )

    def _setup_tls(self) -> None:
        if not self.config.use_tls:
            return

        tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        if self.config.tls_version:
            tls_context.minimum_version = ssl.TLSVersion.TLSv1_3 if self.config.tls_version == MQTTTLSVersion.V1_3 else ssl.TLSVersion.TLSv1_2

        if self.config.certificate_authority_file:
            tls_context.load_verify_locations(cafile=str(self.config.certificate_authority_file))
        else:
            tls_context.load_default_certs()

        if self.config.certificate_file and self.config.key_file:
            tls_context.load_cert_chain(
                certfile=str(self.config.certificate_file),
                keyfile=str(self.config.key_file),
            )

        if self.config.tls_insecure:
            tls_context.check_hostname = False
            tls_context.verify_mode = ssl.CERT_NONE
        else:
            tls_context.check_hostname = True
            tls_context.verify_mode = ssl.CERT_REQUIRED

        self._client.tls_set_context(tls_context)

    def _setup_lwt(self) -> None:
        lwt_topic = self.config.lwt_topic
        lwt_payload = self.config.lwt_payload

        if lwt_topic is None and lwt_payload is None and self.config.client_id:
            lwt_topic = f"devices/{self.config.client_id}/status"
            lwt_payload = {"status": "offline"}

        if not lwt_topic or lwt_payload is None:
            return

        MQTTUtils.validate_topic(lwt_topic)
        if "+" in lwt_topic or "#" in lwt_topic:
            msg = MQTTLogMessages.publish_failed_wildcards(lwt_topic)
            raise ValueError(msg)

        if isinstance(lwt_payload, dict):
            lwt_payload = json.dumps(lwt_payload)

        self._client.will_set(
            lwt_topic,
            payload=lwt_payload,
            qos=self.config.lwt_qos,
            retain=self.config.lwt_retain,
        )

    def _setup_callbacks(self) -> None:
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message

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
        if len(msg.payload) > self.config.max_payload_bytes:
            logger.warning(f"Dropped message on {topic}: payload too large " f"({len(msg.payload)} bytes, max {self.config.max_payload_bytes})")
            return

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
        self._ensure_security_preconditions()

        self._connection_error = None
        self._connect_event.clear()
        self._should_reconnect = True
        self._client.connect(self.config.broker_host, self.config.broker_port, self.config.keepalive)
        self._client.loop_start()
        if not self._connect_event.wait(timeout=timeout):
            self._client.loop_stop()
            msg = MQTTLogMessages.connection_timeout("Subscriber", timeout)
            raise MQTTConnectionError(msg)

    def _ensure_security_preconditions(self) -> None:
        if self.config.require_tls and not self.config.use_tls:
            msg = "TLS is required but use_tls is disabled"
            raise MQTTConnectionError(msg)

        if self.config.tls_insecure and not self.config.allow_insecure_tls:
            msg = "tls_insecure is not allowed in this environment"
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
