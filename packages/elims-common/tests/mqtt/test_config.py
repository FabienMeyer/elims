"""Test ELIMS Common Package - MQTT Module - Configuration."""

from pathlib import Path

import pytest
from elims_common.mqtt.codes import TLSVersion
from elims_common.mqtt.config import MQTTConfig
from pydantic import SecretStr, ValidationError

# Constants for test configuration
DEFAULT_BROKER_PORT = 1883
SECURE_BROKER_PORT = 8883
DEFAULT_QOS = 1
HIGH_QOS = 2
DEFAULT_KEEPALIVE = 60


def test_mqtt_config_defaults() -> None:
    """Test MQTT config with default values."""
    config = MQTTConfig()
    assert config.broker_host == "localhost"
    assert config.broker_port == DEFAULT_BROKER_PORT
    assert config.qos == DEFAULT_QOS
    assert config.keepalive == DEFAULT_KEEPALIVE
    assert config.clean_session is True
    assert config.username is None
    assert config.password is None
    assert config.client_id is None


def test_mqtt_config_custom() -> None:
    """Test MQTT config with custom values."""
    config = MQTTConfig(
        broker_host="mqtt.example.com",
        broker_port=SECURE_BROKER_PORT,
        username="user",
        password="pass",  # noqa: S106
        qos=HIGH_QOS,
    )
    assert config.broker_host == "mqtt.example.com"
    assert config.broker_port == SECURE_BROKER_PORT
    assert config.username == "user"
    assert isinstance(config.password, SecretStr)
    assert config.password.get_secret_value() == "pass"
    assert config.qos == HIGH_QOS


def test_mqtt_config_password_security() -> None:
    """Test that password is properly secured with SecretStr."""
    config = MQTTConfig(
        broker_host="localhost",
        username="user",
        password="secret_password",  # noqa: S106
    )

    # Password should be SecretStr
    assert isinstance(config.password, SecretStr)

    # Password should be masked in repr
    config_repr = repr(config)
    assert "secret_password" not in config_repr
    assert "**********" in config_repr

    # Password accessible via get_secret_value()
    assert config.password.get_secret_value() == "secret_password"


def test_mqtt_config_port_validation() -> None:
    """Test port number validation."""
    # Valid ports
    MQTTConfig(broker_port=1)
    MQTTConfig(broker_port=65535)
    MQTTConfig(broker_port=1883)

    # Invalid ports
    with pytest.raises(ValidationError, match="greater than or equal to 1"):
        MQTTConfig(broker_port=0)

    with pytest.raises(ValidationError, match="less than or equal to 65535"):
        MQTTConfig(broker_port=65536)


def test_mqtt_config_qos_validation() -> None:
    """Test QoS level validation."""
    # Valid QoS levels
    MQTTConfig(qos=0)
    MQTTConfig(qos=1)
    MQTTConfig(qos=2)

    # Invalid QoS levels
    with pytest.raises(ValidationError, match="less than or equal to 2"):
        MQTTConfig(qos=3)

    with pytest.raises(ValidationError):
        MQTTConfig(qos=-1)


def test_mqtt_config_keepalive_validation() -> None:
    """Test keepalive interval validation."""
    # Valid keepalive
    MQTTConfig(keepalive=1)
    MQTTConfig(keepalive=300)

    # Invalid keepalive
    with pytest.raises(ValidationError, match="greater than or equal to 1"):
        MQTTConfig(keepalive=0)


def test_mqtt_config_tls_defaults() -> None:
    """Test TLS configuration defaults."""
    config = MQTTConfig()
    assert config.use_tls is False
    assert config.ca_certs is None
    assert config.certfile is None
    assert config.keyfile is None
    assert config.tls_version is None
    assert config.tls_insecure is False


def test_mqtt_config_tls_enabled() -> None:
    """Test TLS configuration when enabled."""
    config = MQTTConfig(
        use_tls=True,
        tls_version=TLSVersion.TLSv1_3,
        tls_insecure=False,
    )
    assert config.use_tls is True
    assert config.tls_version == TLSVersion.TLSv1_3
    assert config.tls_insecure is False


def test_mqtt_config_tls_version_values() -> None:
    """Test TLS version enum values."""
    assert TLSVersion.TLSv1_2 == 2  # noqa: PLR2004
    assert TLSVersion.TLSv1_3 == 3  # noqa: PLR2004

    # Can use in config
    config = MQTTConfig(tls_version=TLSVersion.TLSv1_2)
    assert config.tls_version == 2  # noqa: PLR2004


def test_mqtt_config_file_validation(tmp_path: Path) -> None:
    """Test certificate file path validation."""
    # Create temporary certificate files
    ca_file = tmp_path / "ca.crt"
    cert_file = tmp_path / "client.crt"
    key_file = tmp_path / "client.key"

    ca_file.write_text("fake ca cert")
    cert_file.write_text("fake cert")
    key_file.write_text("fake key")

    # Valid file paths
    config = MQTTConfig(
        use_tls=True,
        ca_certs=ca_file,
        certfile=cert_file,
        keyfile=key_file,
    )
    assert config.ca_certs == ca_file
    assert config.certfile == cert_file
    assert config.keyfile == key_file

    # Invalid file path
    with pytest.raises(ValidationError, match="File does not exist"):
        MQTTConfig(ca_certs=Path("/nonexistent/ca.crt"))


def test_mqtt_config_reconnection_defaults() -> None:
    """Test reconnection configuration defaults."""
    config = MQTTConfig()
    assert config.reconnect_on_failure is True
    assert config.reconnect_delay == 5  # noqa: PLR2004
    assert config.max_reconnect_attempts == -1


def test_mqtt_config_reconnection_custom() -> None:
    """Test reconnection configuration with custom values."""
    config = MQTTConfig(
        reconnect_on_failure=False,
        reconnect_delay=10,
        max_reconnect_attempts=5,
    )
    assert config.reconnect_on_failure is False
    assert config.reconnect_delay == 10  # noqa: PLR2004
    assert config.max_reconnect_attempts == 5  # noqa: PLR2004


def test_mqtt_config_reconnection_validation() -> None:
    """Test reconnection delay validation."""
    # Valid delays
    MQTTConfig(reconnect_delay=1)
    MQTTConfig(reconnect_delay=100)

    # Invalid delay
    with pytest.raises(ValidationError, match="greater than or equal to 1"):
        MQTTConfig(reconnect_delay=0)


def test_mqtt_config_logging_defaults() -> None:
    """Test logging configuration defaults."""
    config = MQTTConfig()
    assert config.log_payloads is False
    assert config.max_payload_log_length == 100  # noqa: PLR2004


def test_mqtt_config_logging_custom() -> None:
    """Test logging configuration with custom values."""
    config = MQTTConfig(
        log_payloads=True,
        max_payload_log_length=500,
    )
    assert config.log_payloads is True
    assert config.max_payload_log_length == 500  # noqa: PLR2004


def test_mqtt_config_logging_validation() -> None:
    """Test max payload log length validation."""
    # Valid lengths
    MQTTConfig(max_payload_log_length=0)  # 0 means no limit
    MQTTConfig(max_payload_log_length=1000)

    # Invalid length
    with pytest.raises(ValidationError, match="greater than or equal to 0"):
        MQTTConfig(max_payload_log_length=-1)
