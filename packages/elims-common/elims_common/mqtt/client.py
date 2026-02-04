"""ELIMS Common Package - MQTT Module - Client."""

import ssl
from threading import Event

import paho.mqtt.client as mqtt

from elims_common.logger.logger import logger
from elims_common.mqtt.config import MQTTConfig
from elims_common.mqtt.constants import MQTTConnectionFlags, MQTTReturnCode
from elims_common.mqtt.exceptions import MQTTConnectionError
from elims_common.mqtt.messages import MQTTLogMessages


class MQTTClient:
    """Base class for MQTT clients with common functionality."""

    def __init__(self, config: MQTTConfig) -> None:
        """Initialize the base MQTT client.

        Args:
            config: MQTT configuration

        """
        self.config = config
        self.msg = MQTTLogMessages(config=config)
        self._setup_client()
        self._setup_authentication()
        self._setup_tls()
        self._setup_lwt()
        self._setup_callbacks()

        self._connected = False
        self._connection_error: MQTTConnectionError | None = None
        self._connect_event = Event()
        self._should_reconnect = False

    def _setup_client(self) -> None:
        """Configure MQTT client."""
        self._client = mqtt.Client(
            client_id=self.config.client_id,
            clean_session=self.config.clean_session,
            protocol=mqtt.MQTTv311,
        )
        self._client.reconnect_delay_set(
            min_delay=self.config.reconnect_delay,
            max_delay=self.config.reconnect_delay * 2,
        )
        logger.debug(self.msg.setup_client())

    def _setup_authentication(self) -> None:
        """Configure MQTT authentication."""
        self._client.username_pw_set(self.config.username, self.config.password.get_secret_value())
        logger.debug(self.msg.setup_authentication())

    def _setup_tls(self) -> None:
        """Configure MQTT TLS/SSL."""
        tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        tls_context.minimum_version = ssl.TLSVersion.TLSv1_3
        tls_context.check_hostname = True
        tls_context.verify_mode = ssl.CERT_REQUIRED
        tls_context.load_verify_locations(cafile=str(self.config.certificate_authority_file))
        tls_context.load_cert_chain(certfile=str(self.config.certificate_file), keyfile=str(self.config.key_file))
        self._client.tls_set_context(tls_context)
        logger.debug(self.msg.setup_tls())

    def _setup_lwt(self) -> None:
        """Configure Last Will and Testament."""
        self._client.will_set(
            topic=self.config.lwt_topic,
            payload=self.config.lwt_payload,
            qos=self.config.lwt_qos,
            retain=self.config.lwt_retain,
        )
        logger.debug(self.msg.setup_lwt())

    def _setup_callbacks(self) -> None:
        """Set up MQTT client callbacks. Override in subclasses to add more callbacks."""
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        logger.debug(self.msg.setup_callbacks())

    def _on_connect(self, _client: mqtt.Client | None, _userdata: object | None, flags: dict, rc: int) -> None:
        """Handle connection callback.

        Args:
            _client: MQTT client instance
            _userdata: User data (unused)
            flags: Connection flags including session_present
            rc: Connection return code

        """
        logger.debug(self.msg.connecting(rc))
        if rc == MQTTReturnCode.SUCCESS:
            self._connected = True
            self._connection_error = None
            session_present = MQTTConnectionFlags.from_dict(flags).session_present
            logger.info(self.msg.connected(session_present=session_present))
        else:
            self._connected = False
            self._connection_error = MQTTConnectionError(rc)
        self._connect_event.set()

    def _on_disconnect(self, _client: mqtt.Client | None, _userdata: object | None, rc: int) -> None:
        """Handle disconnection callback.

        Args:
            _client: MQTT client instance
            _userdata: User data (unused)
            rc: Disconnection return code (0 = clean disconnect)

        """
        was_connected = self._connected
        self._connected = False
        if rc != 0:
            if not self._connection_error:
                self._connection_error = MQTTConnectionError(rc)
            logger.warning(self.msg.unexpected_disconnect(rc))
        elif was_connected:
            logger.info(self.msg.disconnected())

    def check_timeout(self, timeout: float) -> None:
        """Check if connection attempt has timed out.

        Args:
            timeout: Time to wait for connection (seconds)

        """
        if not self._connect_event.wait(timeout):
            self._client.loop_stop()
            raise MQTTConnectionError(self.msg.connection_timeout(timeout))

    def check_connection(self) -> None:
        """Check if connection was successful after callbacks."""
        if not self._connected:
            self._client.loop_stop()
            raise self._connection_error or MQTTConnectionError(self.msg.connection_failed(msg="Unknown error"))

    def connect(self, timeout: float = 5.0) -> None:
        """Connect to the MQTT broker with an optional timeout.

        Args:
            timeout: Maximum time to wait for connection (seconds)

        Raises:
            MQTTConnectionError: If connection fails or times out

        """
        self._connection_error = None
        self._connected = False
        self._connect_event.clear()
        self._should_reconnect = True

        self._client.connect(self.config.broker_host, self.config.broker_port, self.config.keepalive)
        self._client.loop_start()
        self.check_timeout(timeout)
        self.check_connection()

    def disconnect(self) -> None:
        """Disconnect from the MQTT broker."""
        self._should_reconnect = False
        self._client.loop_stop()
        self._client.disconnect()

    @property
    def is_connected(self) -> bool:
        """Check if the client is connected to the broker."""
        return self._connected
