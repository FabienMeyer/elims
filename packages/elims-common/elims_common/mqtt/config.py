"""ELIMS Common Package - MQTT Module - Configuration."""

from pathlib import Path

from pydantic import BaseModel, Field, SecretStr, field_validator

from elims_common.mqtt.codes import TLSVersion


class MQTTConfig(BaseModel):
    """Configuration for MQTT connection."""

    # Broker connection
    broker_host: str = Field(default="localhost", description="MQTT broker hostname")
    broker_port: int = Field(default=1883, ge=1, le=65535, description="MQTT broker port")

    # Authentication
    username: str | None = Field(default=None, description="MQTT username")
    password: SecretStr | None = Field(default=None, description="MQTT password")
    client_id: str | None = Field(default=None, description="MQTT client ID")

    # Connection settings
    keepalive: int = Field(default=60, ge=1, description="Keepalive interval in seconds")
    clean_session: bool = Field(default=True, description="Clean session flag")
    qos: int = Field(default=1, ge=0, le=2, description="Quality of Service level (0, 1, or 2)")

    # TLS/SSL settings
    use_tls: bool = Field(default=False, description="Enable TLS/SSL encryption")
    ca_certs: Path | None = Field(default=None, description="Path to CA certificates file")
    certfile: Path | None = Field(default=None, description="Path to client certificate file")
    keyfile: Path | None = Field(default=None, description="Path to client private key file")
    tls_version: TLSVersion = Field(default=TLSVersion.TLSv1_2, description="TLS protocol version")
    tls_insecure: bool = Field(default=False, description="Skip certificate verification (insecure!)")

    # Reconnection settings
    reconnect_on_failure: bool = Field(default=True, description="Auto-reconnect on connection loss")
    reconnect_delay: int = Field(default=5, ge=1, description="Delay between reconnection attempts (seconds)")
    max_reconnect_attempts: int = Field(default=10, ge=-1, description="Max reconnection attempts (-1 for infinite)")

    # Logging security
    log_payloads: bool = Field(default=False, description="Log message payloads (may expose sensitive data)")
    max_payload_log_length: int = Field(default=100, ge=0, description="Max payload length in logs (0 for no limit)")

    @field_validator("ca_certs", "certfile", "keyfile")
    @classmethod
    def validate_file_exists(cls, v: Path | None) -> Path | None:
        """Validate that TLS certificate files exist if provided."""
        if v is not None and not v.exists():
            msg = f"Certificate file not found: {v}"
            raise ValueError(msg)
        return v
