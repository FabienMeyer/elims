"""ELIMS Common Package - MQTT Module - Log Messages."""


class MQTTLogMessages:
    """Standardized log messages for MQTT operations."""

    # Connection messages
    @staticmethod
    def connecting(broker_host: str, broker_port: int, client_type: str = "Client") -> str:
        """Generate connecting log message."""
        return f"{client_type} connecting to MQTT broker at {broker_host}:{broker_port}"

    @staticmethod
    def connected(client_type: str = "Client", *, session_present: bool = False) -> str:
        """Generate connected log message."""
        return f"{client_type} connected to MQTT broker (session present: {session_present})"

    @staticmethod
    def connection_failed(client_type: str = "Client", error_msg: str = "") -> str:
        """Generate connection failed log message."""
        return f"{client_type} failed to connect: {error_msg}"

    @staticmethod
    def connection_timeout(client_type: str = "Client", timeout: float = 0.0) -> str:
        """Generate connection timeout log message."""
        return f"{client_type} connection timeout after {timeout} seconds"

    @staticmethod
    def connection_error(client_type: str = "Client", error: Exception | None = None) -> str:
        """Generate connection error log message."""
        return f"{client_type} failed to connect to MQTT broker: {error}"

    # Disconnection messages
    @staticmethod
    def disconnected(client_type: str = "Client") -> str:
        """Generate disconnected log message."""
        return f"{client_type} disconnected from MQTT broker"

    @staticmethod
    def unexpected_disconnect(client_type: str = "Client", code: int = 0) -> str:
        """Generate unexpected disconnection log message."""
        return f"{client_type} unexpected disconnection (code {code})"

    # Publish messages
    @staticmethod
    def published(topic: str, mid: int | str) -> str:
        """Generate message published log message."""
        return f"Message published to {topic} (mid: {mid})"

    @staticmethod
    def publishing(topic: str, payload: str | bytes) -> str:
        """Generate publishing log message."""
        return f"Publishing to {topic}: {payload!r}"

    # Subscribe messages
    @staticmethod
    def subscribed(topic: str, qos: int | None = None) -> str:
        """Generate subscribed log message."""
        if qos is not None:
            return f"Subscribed to {topic} (QoS: {qos})"
        return f"Subscribed to {topic}"

    @staticmethod
    def resubscribed(topic: str) -> str:
        """Generate re-subscribed log message."""
        return f"Re-subscribed to {topic}"

    @staticmethod
    def unsubscribed(topic: str) -> str:
        """Generate unsubscribed log message."""
        return f"Unsubscribed from {topic}"

    # Message handling
    @staticmethod
    def message_received(topic: str, payload: str) -> str:
        """Generate message received log message."""
        return f"Received message on {topic}: {payload}"

    @staticmethod
    def callback_error(topic: str, error: Exception | None = None) -> str:
        """Generate callback error log message."""
        if error:
            return f"Error in callback for {topic}: {error}"
        return f"Error in callback for {topic}"
