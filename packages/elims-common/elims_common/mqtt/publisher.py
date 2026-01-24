"""ELIMS Common Package - MQTT Module - Publisher."""

import json
import ssl
from threading import Event

import paho.mqtt.client as mqtt

from elims_common.logger.logger import logger
from elims_common.mqtt.codes import MQTTConnectionFlags, MQTTReturnCode, TLSVersion
from elims_common.mqtt.config import MQTTConfig
from elims_common.mqtt.exceptions import MQTTConnectionError
from elims_common.mqtt.messages import MQTTLogMessages
from elims_common.mqtt.utils import MQTTUtils


class MQTTPublisher:
    """MQTT Publisher for publishing messages to topics."""

    def __init__(self, config: MQTTConfig) -> None:
        """Initialize MQTT Publisher.

        Args:
            config: MQTT configuration

        """
        self.config = config
        self._client = mqtt.Client(
            client_id=config.client_id,
            clean_session=config.clean_session,
            protocol=mqtt.MQTTv311,
        )

        if config.username and config.password:
            self._client.username_pw_set(config.username, config.password.get_secret_value())

        # Configure TLS/SSL if enabled
        if config.use_tls:
            tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

            # Set TLS version
            if config.tls_version:
                tls_context.minimum_version = ssl.TLSVersion.TLSv1_3 if config.tls_version == TLSVersion.TLSv1_3 else ssl.TLSVersion.TLSv1_2

            # Load CA certificates
            if config.ca_certs:
                tls_context.load_verify_locations(cafile=str(config.ca_certs))
            else:
                tls_context.load_default_certs()

            # Load client certificate and key if provided
            if config.certfile and config.keyfile:
                tls_context.load_cert_chain(certfile=str(config.certfile), keyfile=str(config.keyfile))

            # Configure certificate verification
            if config.tls_insecure:
                tls_context.check_hostname = False
                tls_context.verify_mode = ssl.CERT_NONE
                logger.warning("Publisher TLS certificate verification disabled (insecure!)")
            else:
                tls_context.check_hostname = True
                tls_context.verify_mode = ssl.CERT_REQUIRED

            self._client.tls_set_context(tls_context)
            logger.info("Publisher TLS/SSL enabled")

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_publish = self._on_publish

        self._connected = False
        self._connection_error: MQTTConnectionError | None = None
        self._connect_event = Event()
        self._reconnect_attempts = 0
        self._should_reconnect = False

    def _on_connect(self, _client: mqtt.Client, _userdata: object, flags: dict, rc: int) -> None:
        """Handle connection callback when client connects to broker.

        Args:
            _client: MQTT client instance
            _userdata: User data
            flags: Response flags from broker (contains 'session present' key)
            rc: Connection result code

        """
        connection_flags = MQTTConnectionFlags.from_dict(flags)

        if rc == MQTTReturnCode.SUCCESS:
            self._connected = True
            self._connection_error = None
            logger.info(MQTTLogMessages.connected("Publisher", connection_flags.session_present))
        else:
            self._connected = False
            return_code = MQTTReturnCode(rc) if rc in MQTTReturnCode.__members__.values() else rc
            error_msg = return_code.get_message() if isinstance(return_code, MQTTReturnCode) else f"Unknown error (code {rc})"
            self._connection_error = MQTTConnectionError(MQTTLogMessages.connection_failed("Publisher", error_msg))
            logger.error(MQTTLogMessages.connection_failed("Publisher", error_msg))

        # Signal that connection attempt is complete
        self._connect_event.set()

    def _on_disconnect(self, _client: mqtt.Client, _userdata: object, rc: int) -> None:
        """Handle disconnection callback when client disconnects from broker.

        Args:
            _client: MQTT client instance
            _userdata: User data
            rc: Disconnection result code (0 = clean disconnect, non-zero = unexpected)

        """
        was_connected = self._connected
        self._connected = False

        if rc != 0:
            error_msg = MQTTLogMessages.unexpected_disconnect("Publisher", rc)
            self._connection_error = MQTTConnectionError(error_msg)
            logger.warning(error_msg)

            # Attempt auto-reconnect if enabled
            if self.config.reconnect_on_failure and self._should_reconnect:
                if self.config.max_reconnect_attempts == -1 or self._reconnect_attempts < self.config.max_reconnect_attempts:
                    self._reconnect_attempts += 1
                    logger.info(f"Publisher attempting reconnection {self._reconnect_attempts} " f"in {self.config.reconnect_delay} seconds")
                    # Note: paho-mqtt will handle reconnection with reconnect_delay_set
                else:
                    logger.error(f"Publisher max reconnection attempts ({self.config.max_reconnect_attempts}) reached")
                    self._should_reconnect = False
        else:
            self._connection_error = None
            if was_connected:
                logger.info(MQTTLogMessages.disconnected("Publisher"))

    def _on_publish(self, _client: mqtt.Client, _userdata: object, mid: int) -> None:
        """Handle publish callback when message is published."""
        logger.debug(f"Message published (mid: {mid})")

    def connect(self, timeout: float = 5.0) -> None:
        """Connect to MQTT broker and wait for connection to complete.

        Args:
            timeout: Maximum time in seconds to wait for connection (default: 5.0)

        Raises:
            MQTTConnectionError: If connection fails, times out, or connection callback reports an error

        """
        try:
            self._connection_error = None
            self._connect_event.clear()
            self._reconnect_attempts = 0
            self._should_reconnect = True

            # Configure automatic reconnection
            if self.config.reconnect_on_failure:
                self._client.reconnect_delay_set(min_delay=self.config.reconnect_delay, max_delay=self.config.reconnect_delay * 2)

            self._client.connect(
                self.config.broker_host,
                self.config.broker_port,
                self.config.keepalive,
            )
            self._client.loop_start()
            logger.info(MQTTLogMessages.connecting(self.config.broker_host, self.config.broker_port, "Publisher"))

            # Wait for connection callback to complete
            if not self._connect_event.wait(timeout=timeout):
                self._client.loop_stop()
                error_msg = MQTTLogMessages.connection_timeout("Publisher", timeout)
                logger.error(error_msg)
                self._raise_connection_error(error_msg)

            # Check if connection was successful
            if self._connection_error:
                self._client.loop_stop()
                self._raise_stored_error()

        except MQTTConnectionError:
            raise
        except Exception as e:
            error_msg = MQTTLogMessages.connection_error("Publisher", e)
            logger.error(error_msg)
            raise MQTTConnectionError(error_msg) from e

    def disconnect(self) -> None:
        """Disconnect from MQTT broker.

        Note:
            The disconnection is asynchronous. The _on_disconnect callback
            will be called when the disconnection completes.

        """
        self._should_reconnect = False
        self._client.loop_stop()
        self._client.disconnect()

    def publish(
        self,
        topic: str,
        payload: str | dict | bytes,
        qos: int | None = None,
        *,
        retain: bool = False,
    ) -> mqtt.MQTTMessageInfo:
        """Publish a message to a topic.

        Args:
            topic: Topic to publish to
            payload: Message payload (string, dict, or bytes)
            qos: Quality of Service level (overrides config if provided)
            retain: Retain flag (keyword-only)

        Returns:
            MQTTMessageInfo object

        Raises:
            MQTTConnectionError: If not connected to broker

        """
        if not self._connected:
            msg = "Not connected to MQTT broker"
            raise MQTTConnectionError(msg)

        # Validate topic
        MQTTUtils.validate_topic(topic)

        # Check for wildcards in publish topic
        if "+" in topic or "#" in topic:
            msg = "Wildcards (+, #) not allowed in publish topics"
            raise ValueError(msg)

        # Convert dict to JSON string
        if isinstance(payload, dict):
            payload = json.dumps(payload)

        qos_level = qos if qos is not None else self.config.qos

        result = self._client.publish(topic, payload, qos=qos_level, retain=retain)

        # Log with payload sanitization
        if self.config.log_payloads:
            sanitized = MQTTUtils.sanitize_payload_for_logging(payload, self.config.max_payload_log_length)
            logger.debug(MQTTLogMessages.publishing(topic, sanitized))
        else:
            logger.debug(f"Publishing to {topic}")

        return result

    def _raise_connection_error(self, error_msg: str) -> None:
        """Raise MQTTConnectionError with given message.

        Args:
            error_msg: Error message

        Raises:
            MQTTConnectionError: Always raises with the given message

        """
        raise MQTTConnectionError(error_msg)

    def _raise_stored_error(self) -> None:
        """Raise the stored connection error.

        Raises:
            MQTTConnectionError: The stored connection error

        """
        if self._connection_error:
            raise self._connection_error

    @property
    def is_connected(self) -> bool:
        """Check if publisher is connected."""
        return self._connected
