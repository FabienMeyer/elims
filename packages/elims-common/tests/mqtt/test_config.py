"""Test ELIMS Common Package - MQTT Module - Configuration."""

from pathlib import Path
from typing import Any

import pytest
from elims_common.mqtt.config import MQTTConfig
from elims_common.mqtt.constants import MQTTTLSVersion
from pydantic import SecretStr, ValidationError


@pytest.fixture
def mqtt_config_defaults() -> dict[str, Any]:
    """Return default MQTT configuration values."""
    return {
        "broker_host": "localhost",
        "broker_port": 8883,
        "qos": 1,
        "keepalive": 60,
        "clean_session": True,
        "reconnect_delay": 5,
        "max_reconnect_attempts": -1,
        "log_payloads": False,
        "max_payload_log_length": 100,
        "use_tls": False,
        "tls_insecure": False,
        "reconnect_on_failure": True,
    }


@pytest.fixture
def tls_certificate_files(tmp_path: Path) -> dict[str, Path]:
    """Create temporary TLS certificate files for testing."""
    ca_certificate_file = tmp_path / "ca.crt"
    certificate_file = tmp_path / "client.crt"
    key_file = tmp_path / "client.key"

    ca_certificate_file.write_text("fake ca cert")
    certificate_file.write_text("fake cert")
    key_file.write_text("fake key")

    return {"certificate_authority_file": ca_certificate_file, "certificate_file": certificate_file, "key_file": key_file}


def test_mqtt_config_defaults(mqtt_config_defaults: dict[str, Any]) -> None:
    """Test MQTT config with default values."""
    config = MQTTConfig()

    for key, expected_value in mqtt_config_defaults.items():
        assert getattr(config, key) == expected_value

    assert config.username is None
    assert config.password is None
    assert config.client_id is None
    assert config.certificate_authority_file is None
    assert config.certificate_file is None
    assert config.key_file is None
    assert config.tls_version is None


def test_mqtt_config_custom_values() -> None:
    """Test MQTT config with custom values."""
    config = MQTTConfig(
        broker_host="192.168.1.1",
        broker_port=8883,
        username="test_user",
        password="pass",  # noqa: S106
        client_id="test-client-123",
        qos=2,
    )
    assert config.broker_host == "192.168.1.1"
    assert config.broker_port == 8883  # noqa: PLR2004
    assert config.username == "test_user"
    assert config.client_id == "test-client-123"
    assert isinstance(config.password, SecretStr)
    assert config.password.get_secret_value() == "pass"
    assert config.qos == 2  # noqa: PLR2004


def test_mqtt_config_password_security() -> None:
    """Test that password is properly secured with SecretStr."""
    config = MQTTConfig(
        broker_host="127.0.0.1",
        username="test_user",
        password="secret_password",  # noqa: S106
    )

    assert isinstance(config.password, SecretStr)
    assert config.password.get_secret_value() == "secret_password"

    # Password should be masked in repr
    config_repr = repr(config)
    assert "secret_password" not in config_repr
    assert "**********" in config_repr


@pytest.mark.parametrize(
    ("field", "valid_values"),
    [
        ("broker_port", [1, 8883, 8883, 65535]),
        ("qos", [0, 1, 2]),
        ("keepalive", [1, 60, 300, 3600]),
        ("reconnect_delay", [1, 5, 30, 100]),
        ("max_payload_log_length", [0, 50, 100, 1000]),
    ],
)
def test_mqtt_config_integer_fields_valid_values(
    field: str,
    valid_values: list[int],
) -> None:
    """Test integer fields with valid values."""
    for value in valid_values:
        config = MQTTConfig(**{field: value, "broker_host": "127.0.0.1"})
        assert getattr(config, field) == value


@pytest.mark.parametrize(
    ("field", "invalid_value", "error_match"),
    [
        ("broker_port", 0, "greater than or equal to 1"),
        ("broker_port", 65536, "less than or equal to 65535"),
        ("broker_port", -1, "greater than or equal to 1"),
        ("qos", 3, "less than or equal to 2"),
        ("qos", -1, "greater than or equal to 0"),
        ("keepalive", 0, "greater than or equal to 1"),
        ("keepalive", 3601, "less than or equal to 3600"),
        ("keepalive", -1, "greater than or equal to 1"),
        ("reconnect_delay", 0, "greater than or equal to 1"),
        ("reconnect_delay", -1, "greater than or equal to 1"),
        ("max_payload_log_length", -1, "greater than or equal to 0"),
    ],
)
def test_mqtt_config_integer_fields_invalid_values(
    field: str,
    invalid_value: int,
    error_match: str,
) -> None:
    """Test integer fields with invalid values."""
    with pytest.raises(ValidationError, match=error_match):
        MQTTConfig(**{field: invalid_value, "broker_host": "127.0.0.1"})


@pytest.mark.parametrize(
    "broker_host",
    [
        # IPv4 addresses
        "127.0.0.1",
        "192.168.1.1",
        "10.0.0.1",
        "172.16.0.1",
        "255.255.255.255",
        "0.0.0.0",  # noqa: S104
        # IPv6 addresses
        "::1",
        "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
        "2001:db8::1",
        "fe80::1",
        # Hostnames
        "localhost",
        "mqtt.example.com",
        "broker",
        "my-mqtt-server",
        "test.broker_001",
    ],
)
def test_mqtt_config_broker_host_valid_values(broker_host: str) -> None:
    """Test broker_host with valid IP addresses and hostnames."""
    config = MQTTConfig(broker_host=broker_host)
    assert config.broker_host == broker_host


@pytest.mark.parametrize(
    "broker_host",
    [
        # Empty or invalid hostnames
        "",
        "   ",
        "broker with spaces",
        "invalid@hostname",
        "host#name",
        "bad$host",
    ],
)
def test_mqtt_config_broker_host_invalid_values(broker_host: str) -> None:
    """Test broker_host with invalid values (invalid hostnames and empty strings)."""
    with pytest.raises(ValidationError, match="broker_host"):
        MQTTConfig(broker_host=broker_host)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("username", "valid_user"),
        ("username", "user123"),
        ("username", "user-name"),
        ("username", "user_name"),
        ("username", "User_Name-123"),
        ("username", "ABC"),
        ("client_id", "valid-client"),
        ("client_id", "client123"),
        ("client_id", "Client_ID-001"),
        ("client_id", "c"),
        ("client_id", "my-mqtt-client_2024"),
    ],
)
def test_mqtt_config_string_fields_valid_values(field: str, value: str) -> None:
    """Test username and client_id with valid values."""
    config = MQTTConfig(**{field: value, "broker_host": "127.0.0.1"})
    assert getattr(config, field) == value


@pytest.mark.parametrize(
    ("field", "value", "error_match"),
    [
        ("username", "us", "String should have at least 3 characters"),
        ("username", "u", "String should have at least 3 characters"),
        ("username", "user@domain", "String should match pattern"),
        ("username", "user name", "String should match pattern"),
        ("username", "user.name", "String should match pattern"),
        ("username", "user#123", "String should match pattern"),
        ("client_id", "", "String should have at least 1 character"),
        ("client_id", "client@id", "String should match pattern"),
        ("client_id", "client id", "String should match pattern"),
        ("client_id", "client.id", "String should match pattern"),
        ("client_id", "client#id", "String should match pattern"),
    ],
)
def test_mqtt_config_string_fields_invalid_values(field: str, value: str, error_match: str) -> None:
    """Test username and client_id with invalid values."""
    with pytest.raises(ValidationError, match=error_match):
        MQTTConfig(**{field: value, "broker_host": "127.0.0.1"})


def test_mqtt_config_tls_enabled() -> None:
    """Test TLS configuration when enabled."""
    config = MQTTConfig(
        broker_host="127.0.0.1",
        use_tls=True,
        tls_version=MQTTTLSVersion.V1_3,
        tls_insecure=False,
    )
    assert config.use_tls is True
    assert config.tls_version == MQTTTLSVersion.V1_3
    assert config.tls_insecure is False


@pytest.mark.parametrize(
    ("tls_version", "expected_value"),
    [
        (MQTTTLSVersion.V1_2, 2),
        (MQTTTLSVersion.V1_3, 3),
    ],
)
def test_mqtt_config_tls_version_values(tls_version: MQTTTLSVersion, expected_value: int) -> None:
    """Test TLS version enum values."""
    assert tls_version.value == expected_value

    config = MQTTConfig(broker_host="127.0.0.1", tls_version=tls_version)
    assert config.tls_version == expected_value


def test_mqtt_config_tls_with_certificates(tls_certificate_files: dict[str, Path]) -> None:
    """Test TLS configuration with certificate files."""
    config = MQTTConfig(
        broker_host="127.0.0.1",
        use_tls=True,
        **tls_certificate_files,
    )
    assert config.certificate_authority_file == tls_certificate_files["certificate_authority_file"]
    assert config.certificate_file == tls_certificate_files["certificate_file"]
    assert config.key_file == tls_certificate_files["key_file"]


@pytest.mark.parametrize(
    "certificate_field",
    ["certificate_authority_file", "certificate_file", "key_file"],
)
def test_mqtt_config_certificate_file_validation(certificate_field: str) -> None:
    """Test that non-existent certificate files raise validation error."""
    with pytest.raises(ValidationError, match="Certificate file not found"):
        MQTTConfig(
            broker_host="127.0.0.1",
            **{certificate_field: Path("/nonexistent/cert.pem")},
        )


@pytest.mark.parametrize(
    ("reconnect_on_failure", "reconnect_delay", "max_reconnect_attempts"),
    [
        (True, 5, -1),  # Defaults
        (False, 10, 0),
        (True, 1, 1),
        (True, 30, 10),
        (False, 5, -1),  # Infinite attempts with reconnect disabled
    ],
)
def test_mqtt_config_reconnection_settings(
    reconnect_on_failure: bool,  # noqa: FBT001
    reconnect_delay: int,
    max_reconnect_attempts: int,
) -> None:
    """Test reconnection configuration with various combinations."""
    config = MQTTConfig(
        broker_host="127.0.0.1",
        reconnect_on_failure=reconnect_on_failure,
        reconnect_delay=reconnect_delay,
        max_reconnect_attempts=max_reconnect_attempts,
    )
    assert config.reconnect_on_failure is reconnect_on_failure
    assert config.reconnect_delay == reconnect_delay
    assert config.max_reconnect_attempts == max_reconnect_attempts


@pytest.mark.parametrize(
    ("log_payloads", "max_payload_log_length"),
    [
        (False, 100),  # Default
        (True, 0),  # No limit
        (True, 50),
        (True, 500),
        (False, 1000),
    ],
)
def test_mqtt_config_logging_settings(log_payloads: bool, max_payload_log_length: int) -> None:  # noqa: FBT001
    """Test logging configuration with various combinations."""
    config = MQTTConfig(
        broker_host="127.0.0.1",
        log_payloads=log_payloads,
        max_payload_log_length=max_payload_log_length,
    )
    assert config.log_payloads is log_payloads
    assert config.max_payload_log_length == max_payload_log_length
