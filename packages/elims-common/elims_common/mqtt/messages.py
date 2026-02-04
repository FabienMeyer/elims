"""ELIMS Common Package - MQTT Module - Log Messages."""

from elims_common.mqtt.config import MQTTConfig


class MQTTLogMessages:
    """Standardized log messages for MQTT operations."""

    def __init__(self, config: MQTTConfig) -> None:
        """Initialize log message generator for a specific MQTT client."""
        self.config = config

    def setup_client(self) -> str:
        """Generate MQTT client setup log message."""
        return f"[MQTT CLIENT SETUP] | CLIENT: {self.config.client_type:<10} | ID: {self.config.client_id}"

    def setup_authentication(self) -> str:
        """Generate MQTT authentication setup log message."""
        return f"[MQTT AUTH SETUP] | CLIENT: {self.config.client_type:<10} | ID: {self.config.client_id}"

    def setup_tls(self) -> str:
        """Generate MQTT TLS setup log message."""
        return f"[MQTT TLS SETUP] | CLIENT: {self.config.client_type:<10} | ID: {self.config.client_id}"

    def setup_lwt(self) -> str:
        """Generate MQTT LWT setup log message."""
        msg = f"Topic: {self.config.lwt_topic}, Payload: {self.config.lwt_payload}, QoS: {self.config.lwt_qos}, Retain: {self.config.lwt_retain}"
        return f"[MQTT LWT SETUP] | CLIENT: {self.config.client_type:<10} | ID: {self.config.client_id} | MSG: {msg}"

    def setup_callbacks(self) -> str:
        """Generate MQTT callbacks setup log message."""
        return f"[MQTT CALLBACKS SETUP] | CLIENT: {self.config.client_type:<10} | ID: {self.config.client_id}"

    def connecting(self, rc: int) -> str:
        """Generate MQTT CONNACK received log message."""
        return f"[MQTT CONNACK] | BROKER: {self.config.broker_host}:{self.config.broker_port} | CLIENT: {self.config.client_type:<10} | RC: {rc}"

    def connected(self, *, session_present: bool) -> str:
        """Generate MQTT connected log message."""
        return f"[MQTT CONNECTED] | BROKER: {self.config.broker_host}:{self.config.broker_port} | CLIENT: {self.config.client_type:<10} | SESSION: {session_present}"

    def connection_timeout(self, timeout: float) -> str:
        """Generate connection timeout log message."""
        return f"[MQTT TIMEOUT] | BROKER: {self.config.broker_host}:{self.config.broker_port} | CLIENT: {self.config.client_type:<10} | TIMEOUT: {timeout}s"

    def connection_failed(self, msg: str) -> str:
        """Generate MQTT connection failed log message."""
        return f"[MQTT CONNECT FAILED] | BROKER: {self.config.broker_host}:{self.config.broker_port} | CLIENT: {self.config.client_type:<10} | ERROR: {msg}"

    def unexpected_disconnect(self, rc: int) -> str:
        """Generate unexpected disconnection log message."""
        return f"[MQTT DISCONNECT] | BROKER: {self.config.broker_host}:{self.config.broker_port} | CLIENT: {self.config.client_type:<10} | RC: {rc}"

    def disconnected(self) -> str:
        """Generate clean disconnection log message."""
        return f"[MQTT DISCONNECTED] | BROKER: {self.config.broker_host}:{self.config.broker_port} | CLIENT: {self.config.client_type:<10}"

    def invalid_json_payload(self, topic: str, payload: str) -> str:
        """Generate invalid JSON payload log message."""
        return f"[INVALID JSON] | TOPIC: {topic:<30} | PAYLOAD: {payload}"

    def subscribed(self, topic: str) -> str:
        """Generate subscribed log message."""
        return f"[SUBSCRIBE] | CLIENT: {self.config.client_type:<10} | TOPIC: {topic}"

    def unsubscribed(self, topic: str) -> str:
        """Generate unsubscribed log message."""
        return f"[UNSUBSCRIBE] | CLIENT: {self.config.client_type:<10} | TOPIC: {topic}"

    def unsubscription_failed(self, topic: str) -> str:
        """Generate unsubscription failed log message."""
        return f"[UNSUBSCRIBE FAILED] | CLIENT: {self.config.client_type:<10} | TOPIC: {topic}"

    def published(self, mid: int) -> str:
        """Generate published log message."""
        return f"[PUBLISH] | CLIENT: {self.config.client_type:<10} | MID: {mid}"

    def publishing(self, topic: str, payload: str | None = None) -> str:
        """Generate publishing log message."""
        if payload:
            return f"[PUBLISH] | TOPIC: {topic:<30} | PAYLOAD: {payload}"
        return f"[PUBLISH] | TOPIC: {topic}"

    def publish_failed_not_connected(self, topic: str) -> str:
        """Generate publish failed message for disconnected client."""
        return f"[PUBLISH FAILED] | TOPIC: {topic} | REASON: Client not connected"

    def publish_failed_wildcards(self, topic: str) -> str:
        """Generate publish failed message for wildcard topics."""
        return f"[PUBLISH FAILED] | TOPIC: {topic} | REASON: Wildcards not allowed in publish topics"
