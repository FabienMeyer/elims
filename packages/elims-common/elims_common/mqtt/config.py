"""ELIMS Common Package - MQTT Module - Configuration."""

from ipaddress import AddressValueError, IPv4Address, IPv6Address
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field, SecretStr, field_validator

from elims_common.mqtt.constants import MQTTTLSVersion

Username = Annotated[str, Field(min_length=3, pattern="^[a-zA-Z0-9_-]+$")]
ClientID = Annotated[str, Field(min_length=1, pattern="^[a-zA-Z0-9_-]+$")]


class MQTTConfig(BaseModel):
    """Configuration for MQTT connection."""

    # Broker connection
    broker_host: str = Field(default="localhost", description="MQTT broker hostname")
    broker_port: int = Field(default=1883, ge=1, le=65535, description="MQTT broker port")

    # Authentication
    username: Username | None = Field(default=None, description="MQTT username")
    password: SecretStr | None = Field(default=None, description="MQTT password")
    client_id: ClientID | None = Field(default=None, description="MQTT client ID")

    # Connection settings
    keepalive: int = Field(default=60, ge=1, le=3600, description="Keepalive interval in seconds")
    clean_session: bool = Field(default=True, description="Clean session flag")
    qos: int = Field(default=1, ge=0, le=2, description="Quality of Service level (0, 1, or 2)")

    # TLS/SSL settings
    use_tls: bool = Field(default=False, description="Enable TLS/SSL encryption")
    certificate_authority_file: Path | None = Field(default=None, description="Path to CA certificates file")
    certificate_file: Path | None = Field(default=None, description="Path to client certificate file")
    key_file: Path | None = Field(default=None, description="Path to client private key file")
    tls_version: MQTTTLSVersion | None = Field(default=None, description="TLS protocol version")
    tls_insecure: bool = Field(default=False, description="Skip certificate verification (insecure!)")

    # Reconnection settings
    reconnect_on_failure: bool = Field(default=True, description="Auto-reconnect on connection loss")
    reconnect_delay: int = Field(default=5, ge=1, description="Delay between reconnection attempts (seconds)")
    max_reconnect_attempts: int = Field(default=-1, ge=-1, description="Max reconnection attempts (-1 for infinite)")

    # Logging security
    log_payloads: bool = Field(default=False, description="Log message payloads (may expose sensitive data)")
    max_payload_log_length: int = Field(default=100, ge=0, description="Max payload length in logs (0 for no limit)")

    @field_validator("broker_host")
    @classmethod
    def validate_broker_host(cls, v: str) -> str:
        """Validate that broker_host is a valid IP address or hostname."""
        if not v or not v.strip():
            msg = "broker_host cannot be empty"
            raise ValueError(msg)

        # Try to parse as IPv4 or IPv6, otherwise accept as hostname
        try:
            IPv4Address(v)
        except AddressValueError:
            pass
        else:
            return v

        try:
            IPv6Address(v)
        except AddressValueError:
            pass
        else:
            return v

        # If not an IP address, validate as hostname
        # Basic hostname validation: alphanumeric, hyphens, dots, underscores
        if not all(c.isalnum() or c in ".-_" for c in v):
            msg = f"broker_host must be a valid IP address or hostname, got: {v}"
            raise ValueError(msg)

        return v

    @field_validator("certificate_authority_file", "certificate_file", "key_file")
    @classmethod
    def validate_file_exists(cls, v: Path | None) -> Path | None:
        """Validate that TLS certificate files exist if provided."""
        if v is not None and not v.exists():
            msg = f"Certificate file not found: {v}"
            raise ValueError(msg)
        return v
