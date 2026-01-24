"""Test ELIMS Common Package - MQTT Module - Return Codes and Flags."""

import pytest
from elims_common.mqtt.codes import MQTTConnectionFlags, MQTTReturnCode, TLSVersion


def test_mqtt_return_code_values() -> None:
    """Test MQTT return code enum values."""
    assert MQTTReturnCode.SUCCESS == 0
    assert MQTTReturnCode.PROTOCOL_ERROR == 1
    assert MQTTReturnCode.CLIENT_ID_REJECTED == 2  # noqa: PLR2004
    assert MQTTReturnCode.SERVER_UNAVAILABLE == 3  # noqa: PLR2004
    assert MQTTReturnCode.BAD_CREDENTIALS == 4  # noqa: PLR2004
    assert MQTTReturnCode.NOT_AUTHORIZED == 5  # noqa: PLR2004


def test_mqtt_return_code_get_message() -> None:
    """Test MQTT return code message retrieval."""
    assert MQTTReturnCode.SUCCESS.get_message() == "Connection successful"
    assert "incorrect protocol version" in MQTTReturnCode.PROTOCOL_ERROR.get_message()
    assert "invalid client identifier" in MQTTReturnCode.CLIENT_ID_REJECTED.get_message()
    assert "server unavailable" in MQTTReturnCode.SERVER_UNAVAILABLE.get_message()
    assert "bad username or password" in MQTTReturnCode.BAD_CREDENTIALS.get_message()
    assert "not authorized" in MQTTReturnCode.NOT_AUTHORIZED.get_message()


def test_mqtt_return_code_from_int() -> None:
    """Test creating return code from integer."""
    code = MQTTReturnCode(0)
    assert code == MQTTReturnCode.SUCCESS

    code = MQTTReturnCode(4)
    assert code == MQTTReturnCode.BAD_CREDENTIALS


def test_mqtt_return_code_comparison() -> None:
    """Test return code comparison with integers."""
    assert MQTTReturnCode.SUCCESS == 0
    assert MQTTReturnCode.BAD_CREDENTIALS == 4  # noqa: PLR2004
    assert MQTTReturnCode.SUCCESS == 0

    # Can use in conditions
    rc = 0
    if rc == MQTTReturnCode.SUCCESS:
        assert True
    else:
        pytest.fail("Comparison failed")


def test_mqtt_connection_flags_defaults() -> None:
    """Test connection flags with default values."""
    flags = MQTTConnectionFlags()
    assert flags.session_present is False


def test_mqtt_connection_flags_custom() -> None:
    """Test connection flags with custom values."""
    flags = MQTTConnectionFlags(session_present=True)
    assert flags.session_present is True


def test_mqtt_connection_flags_from_dict() -> None:
    """Test creating connection flags from paho-mqtt callback dict."""
    # With session present
    flags = MQTTConnectionFlags.from_dict({"session present": True})
    assert flags.session_present is True

    # Without session present
    flags = MQTTConnectionFlags.from_dict({"session present": False})
    assert flags.session_present is False

    # Empty dict (default to False)
    flags = MQTTConnectionFlags.from_dict({})
    assert flags.session_present is False

    # Dict with other keys (should ignore them)
    flags = MQTTConnectionFlags.from_dict({"session present": True, "other_key": "value"})
    assert flags.session_present is True


def test_tls_version_values() -> None:
    """Test TLS version enum values."""
    assert TLSVersion.TLSv1_2 == 2  # noqa: PLR2004
    assert TLSVersion.TLSv1_3 == 3  # noqa: PLR2004


def test_tls_version_from_int() -> None:
    """Test creating TLS version from integer."""
    version = TLSVersion(2)
    assert version == TLSVersion.TLSv1_2

    version = TLSVersion(3)
    assert version == TLSVersion.TLSv1_3


def test_tls_version_comparison() -> None:
    """Test TLS version comparison."""
    assert TLSVersion.TLSv1_2 < TLSVersion.TLSv1_3
    assert TLSVersion.TLSv1_3 > TLSVersion.TLSv1_2
    assert TLSVersion.TLSv1_3 == 3  # noqa: PLR2004
