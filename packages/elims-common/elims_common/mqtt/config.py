"""ELIMS Common Package - MQTT Module - Configuration."""

from ipaddress import AddressValueError, IPv4Address, IPv6Address
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, SecretStr, ValidationInfo, field_validator

from elims_common.mqtt.constants import MQTT_MAX_TOPIC_LENGTH

Username = Annotated[str, Field(min_length=3, pattern="^[a-zA-Z0-9_-]+$")]
ClientID = Annotated[str, Field(min_length=1, pattern="^[a-zA-Z0-9_-]+$")]


class MQTTConfig(BaseModel):
    """Configuration for MQTT connection."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Broker connection
    broker_host: str = Field(default="localhost", description="MQTT broker hostname")
    broker_port: int = Field(default=1883, ge=1, le=65535, description="MQTT broker port")

    # Authentication
    username: Username = Field(description="MQTT username")
    password: SecretStr = Field(description="MQTT password")
    client_id: ClientID = Field(description="MQTT client ID")
    client_type: str = Field(description="Type of MQTT client")

    # TLS/SSL settings
    certificate_authority_file: Path = Field(description="Path to CA certificates file")
    certificate_file: Path = Field(description="Path to client certificate file")
    key_file: Path = Field(description="Path to client private key file")

    # Connection settings
    keepalive: int = Field(default=60, ge=1, le=3600, description="Keepalive interval in seconds")
    clean_session: bool = Field(default=True, description="Clean session flag")
    qos: int = Field(default=1, ge=0, le=2, description="Quality of Service level (0, 1, or 2)")

    # Last Will and Testament (LWT)
    lwt_topic: str = Field(description="LWT topic for unexpected disconnects")
    lwt_payload: str | bytes | dict[str, object] | None = Field(default=None, description="LWT payload")
    lwt_qos: int = Field(default=1, ge=0, le=2, description="LWT QoS level")
    lwt_retain: bool = Field(default=True, description="Retain LWT message")

    # Reconnection settings
    reconnect_on_failure: bool = Field(default=True, description="Auto-reconnect on connection loss")
    reconnect_delay: int = Field(default=5, ge=1, description="Delay between reconnection attempts (seconds)")

    max_payload_size: int = Field(default=268435455, ge=1, description="Maximum MQTT payload size in bytes (default 256 MB)")

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
    def validate_file_exists(cls, v: Path) -> Path:
        """Validate that TLS certificate files exist if provided."""
        if not v.exists():
            msg = f"Certificate file not found: {v}"
            raise ValueError(msg)
        return v

    @field_validator("client_id")
    @classmethod
    def validate_client_id(cls, v: str, info: ValidationInfo) -> str:
        """Validate client_id when required."""
        if info.data.get("require_client_id", True) and not v:
            msg = "client_id is required"
            raise ValueError(msg)
        return v

    @classmethod
    def validate_topic(cls, v: str) -> str:
        """Validate that LWT topic is a valid MQTT topic without wildcards."""
        if not v or not v.strip():
            msg = "Topic cannot be empty"
            raise ValueError(msg)
        if len(v) > MQTT_MAX_TOPIC_LENGTH:
            msg = f"Topic too long: {len(v)} bytes (max {MQTT_MAX_TOPIC_LENGTH})"
            raise ValueError(msg)
        if "\0" in v:
            msg = "Topic cannot contain null character"
            raise ValueError(msg)
        return v

    @field_validator("lwt_topic")
    @classmethod
    def validate_lwt_topic(cls, v: str) -> str:
        """Validate LWT topic."""
        cls.validate_topic(v)
        if "+" in v or "#" in v:
            msg = "LWT topic cannot contain wildcards (+ or #)"
            raise ValueError(msg)
        return v

    @field_validator("lwt_payload")
    @classmethod
    def validate_lwt_payload(cls, v: str | bytes | dict[str, object] | None) -> str | bytes | dict[str, object] | None:
        """Validate LWT payload type."""
        if v is None:
            return v
        if isinstance(v, str | bytes):
            return v
        if isinstance(v, dict):
            return v
        msg = f"lwt_payload must be a string, bytes, or dict, got: {type(v)}"
        raise ValueError(msg)
