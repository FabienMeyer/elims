"""ELIMS Common Package - MQTT Module - Client."""

import json
import ssl
from threading import Event

import paho.mqtt.client as mqtt

from elims_common.logger.logger import logger
from elims_common.mqtt.config import MQTTConfig
from elims_common.mqtt.constants import MQTTConnectionFlags, MQTTReturnCode, MQTTTLSVersion
from elims_common.mqtt.exceptions import MQTTConnectionError
from elims_common.mqtt.messages import MQTTLogMessages
from elims_common.mqtt.utils import MQTTUtils


class MQTTClient:
    """Base class for MQTT clients with common functionality."""

    def __init__(self, config: MQTTConfig, client_type: str) -> None:
        """Initialize the base MQTT client.

        Args:
            config: MQTT configuration
            client_type: Type of client ("Publisher" or "Subscriber") for logging

        """
        self.config = config
        self._client_type = client_type

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

    def _setup_auth(self) -> None:
        """Configure MQTT client authentication if credentials are provided."""
        if self.config.username and self.config.password:
            self._client.username_pw_set(
                self.config.username,
                self.config.password.get_secret_value(),
            )

    def _setup_tls(self) -> None:
        """Configure TLS/SSL settings for secure connections."""
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
            logger.warning(f"{self._client_type} TLS verification disabled (INSECURE)")
        else:
            tls_context.check_hostname = True
            tls_context.verify_mode = ssl.CERT_REQUIRED

        self._client.tls_set_context(tls_context)

    def _setup_lwt(self) -> None:
        """Configure Last Will and Testament (LWT) message."""
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
        """Set up MQTT client callbacks. Override in subclasses to add more callbacks."""
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect

    def _on_connect(self, _client: mqtt.Client | None, _userdata: object | None, flags: dict, rc: int) -> None:
        """Handle connection callback."""
        logger.debug(f"MQTT CONNACK rc={rc}")

        connection_flags = MQTTConnectionFlags.from_dict(flags)

        if rc == MQTTReturnCode.SUCCESS:
            self._connected = True
            self._connection_error = None
            logger.info(
                MQTTLogMessages.connected(
                    self._client_type,
                    session_present=connection_flags.session_present,
                )
            )
            self._on_connect_success(connection_flags)
        else:
            self._connected = False
            try:
                return_code = MQTTReturnCode(rc)
                error_msg = return_code.get_message()
            except ValueError:
                error_msg = f"Unknown error (code {rc})"

            self._connection_error = MQTTConnectionError(MQTTLogMessages.connection_failed(self._client_type, error_msg))
            logger.error(self._connection_error)

        self._connect_event.set()

    def _on_connect_success(self, connection_flags: MQTTConnectionFlags) -> None:
        """Handle successful connection. Override in subclasses for specific behavior."""

    def _on_disconnect(self, _client: mqtt.Client | None, _userdata: object | None, rc: int) -> None:
        """Handle disconnection callback."""
        was_connected = self._connected
        self._connected = False

        if rc != 0:
            if not self._connection_error:
                self._connection_error = MQTTConnectionError(MQTTLogMessages.unexpected_disconnect(self._client_type, rc))
            logger.warning(self._connection_error)
        elif was_connected:
            logger.info(MQTTLogMessages.disconnected(self._client_type))

    def _ensure_security_preconditions(self) -> None:
        """Validate security configuration before connecting."""
        if self.config.require_tls and not self.config.use_tls:
            msg = "TLS is required but use_tls is disabled"
            raise MQTTConnectionError(msg)

        if self.config.tls_insecure and not self.config.allow_insecure_tls:
            msg = "tls_insecure is not allowed in this environment"
            raise MQTTConnectionError(msg)

    def connect(self, timeout: float = 5.0) -> None:
        """Connect to the MQTT broker with an optional timeout."""
        self._ensure_security_preconditions()

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
                self._client_type,
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
            raise MQTTConnectionError(MQTTLogMessages.connection_timeout(self._client_type, timeout))

        if not self._connected:
            self._client.loop_stop()
            raise self._connection_error or MQTTConnectionError("MQTT connection failed")

    def disconnect(self) -> None:
        """Disconnect from the MQTT broker."""
        self._should_reconnect = False
        self._client.loop_stop()
        self._client.disconnect()

    @property
    def is_connected(self) -> bool:
        """Check if the client is connected to the broker."""
        return self._connected
