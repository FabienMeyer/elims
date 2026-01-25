"""ELIMS Common Package - MQTT Module - Publisher."""

import json
import ssl
from threading import Event

import paho.mqtt.client as mqtt

from elims_common.logger.logger import logger
from elims_common.mqtt.config import MQTTConfig
from elims_common.mqtt.constants import (
    MQTTConnectionFlags,
    MQTTReturnCode,
    MQTTTLSVersion,
)
from elims_common.mqtt.exceptions import MQTTConnectionError
from elims_common.mqtt.messages import MQTTLogMessages
from elims_common.mqtt.utils import MQTTUtils


class MQTTPublisher:
    """MQTT Publisher for publishing messages to topics."""

    def __init__(self, config: MQTTConfig) -> None:
        """Initialize the MQTT Publisher."""
        self.config = config

        self._client = mqtt.Client(
            client_id=config.client_id,
            clean_session=config.clean_session,
            protocol=mqtt.MQTTv311,
        )

        # --- AUTH ---
        if config.username and config.password:
            self._client.username_pw_set(
                config.username,
                config.password.get_secret_value(),
            )

        # --- TLS ---
        if config.use_tls:
            tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

            if config.tls_version:
                tls_context.minimum_version = ssl.TLSVersion.TLSv1_3 if config.tls_version == MQTTTLSVersion.V1_3 else ssl.TLSVersion.TLSv1_2

            if config.certificate_authority_file:
                tls_context.load_verify_locations(cafile=str(config.certificate_authority_file))
            else:
                tls_context.load_default_certs()

            if config.certificate_file and config.key_file:
                tls_context.load_cert_chain(
                    certfile=str(config.certificate_file),
                    keyfile=str(config.key_file),
                )

            if config.tls_insecure:
                tls_context.check_hostname = False
                tls_context.verify_mode = ssl.CERT_NONE
                logger.warning("Publisher TLS verification disabled (INSECURE)")
            else:
                tls_context.check_hostname = True
                tls_context.verify_mode = ssl.CERT_REQUIRED

            self._client.tls_set_context(tls_context)

        # --- CALLBACKS ---
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_publish = self._on_publish

        self._connected = False
        self._connection_error: MQTTConnectionError | None = None
        self._connect_event = Event()
        self._should_reconnect = False
        self._reconnect_attempts = 0

    # ------------------------------------------------------------------ #
    # CALLBACKS
    # ------------------------------------------------------------------ #

    def _on_connect(self, _client: mqtt.Client | None, _userdata: object | None, flags: dict, rc: int) -> None:
        """Handle connection callback."""
        logger.debug(f"MQTT CONNACK rc={rc}")

        self._connect_event.set()

        if rc == MQTTReturnCode.SUCCESS:
            self._connected = True
            self._connection_error = None

            connection_flags = MQTTConnectionFlags.from_dict(flags)
            logger.info(
                MQTTLogMessages.connected(
                    "Publisher",
                    session_present=connection_flags.session_present,
                )
            )
            return

        # --- AUTH / CONNECT FAILURE ---
        self._connected = False

        try:
            return_code = MQTTReturnCode(rc)
            error_msg = return_code.get_message()
        except ValueError:
            error_msg = f"Unknown error (code {rc})"

        self._connection_error = MQTTConnectionError(MQTTLogMessages.connection_failed("Publisher", error_msg))

        logger.error(self._connection_error)

    def _on_disconnect(self, _client: mqtt.Client | None, _userdata: object | None, rc: int) -> None:
        """Handle disconnection callback."""
        was_connected = self._connected
        self._connected = False

        if rc != 0:
            # Do NOT overwrite an existing connection error
            if not self._connection_error:
                self._connection_error = MQTTConnectionError(MQTTLogMessages.unexpected_disconnect("Publisher", rc))
            logger.warning(self._connection_error)

        elif was_connected:
            logger.info(MQTTLogMessages.disconnected("Publisher"))

    def _on_publish(self, _client: mqtt.Client | None, _userdata: object | None, mid: int) -> None:
        """Handle publish callback."""
        logger.debug(f"Message published (mid={mid})")

    # ------------------------------------------------------------------ #
    # CONNECTION CONTROL
    # ------------------------------------------------------------------ #

    def connect(self, timeout: float = 5.0) -> None:
        """Connect to the MQTT broker with an optional timeout."""
        self._connection_error = None
        self._connected = False
        self._connect_event.clear()
        self._should_reconnect = True
        self._reconnect_attempts = 0

        if self.config.reconnect_on_failure:
            self._client.reconnect_delay_set(
                min_delay=self.config.reconnect_delay,
                max_delay=self.config.reconnect_delay * 2,
            )

        logger.info(
            MQTTLogMessages.connecting(
                self.config.broker_host,
                self.config.broker_port,
                "Publisher",
            )
        )

        self._client.connect(
            self.config.broker_host,
            self.config.broker_port,
            self.config.keepalive,
        )

        self._client.loop_start()

        if not self._connect_event.wait(timeout):
            self._client.loop_stop()
            raise MQTTConnectionError(MQTTLogMessages.connection_timeout("Publisher", timeout))

        if not self._connected:
            self._client.loop_stop()
            raise self._connection_error or MQTTConnectionError("MQTT connection failed")

    def disconnect(self) -> None:
        """Disconnect from the MQTT broker."""
        self._should_reconnect = False
        self._client.loop_stop()
        self._client.disconnect()

    # ------------------------------------------------------------------ #
    # PUBLISH
    # ------------------------------------------------------------------ #

    def publish(
        self,
        topic: str,
        payload: str | dict | bytes,
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

    # ------------------------------------------------------------------ #

    @property
    def is_connected(self) -> bool:
        """Check if the client is connected to the broker."""
        return self._connected
