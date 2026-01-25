"""Test ELIMS Common Package - MQTT Module - Return Codes and Flags."""

from typing import Any

import pytest
from elims_common.mqtt.constants import MQTTConnectionFlags, MQTTReturnCode, MQTTTLSVersion


@pytest.fixture
def return_code_messages() -> dict[MQTTReturnCode, str]:
    """Return expected messages for each return code."""
    return {
        MQTTReturnCode.SUCCESS: "Connection successful",
        MQTTReturnCode.PROTOCOL_ERROR: "incorrect protocol version",
        MQTTReturnCode.CLIENT_ID_REJECTED: "invalid client identifier",
        MQTTReturnCode.SERVER_UNAVAILABLE: "server unavailable",
        MQTTReturnCode.BAD_CREDENTIALS: "bad username or password",
        MQTTReturnCode.NOT_AUTHORIZED: "not authorized",
    }


@pytest.mark.parametrize(
    ("return_code", "expected_value"),
    [
        (MQTTReturnCode.SUCCESS, 0),
        (MQTTReturnCode.PROTOCOL_ERROR, 1),
        (MQTTReturnCode.CLIENT_ID_REJECTED, 2),
        (MQTTReturnCode.SERVER_UNAVAILABLE, 3),
        (MQTTReturnCode.BAD_CREDENTIALS, 4),
        (MQTTReturnCode.NOT_AUTHORIZED, 5),
    ],
)
def test_mqtt_return_code_values(return_code: MQTTReturnCode, expected_value: int) -> None:
    """Test MQTT return code enum values."""
    assert return_code.value == expected_value


@pytest.mark.parametrize(
    "return_code",
    [
        MQTTReturnCode.SUCCESS,
        MQTTReturnCode.PROTOCOL_ERROR,
        MQTTReturnCode.CLIENT_ID_REJECTED,
        MQTTReturnCode.SERVER_UNAVAILABLE,
        MQTTReturnCode.BAD_CREDENTIALS,
        MQTTReturnCode.NOT_AUTHORIZED,
    ],
)
def test_mqtt_return_code_get_message(
    return_code: MQTTReturnCode,
    return_code_messages: dict[MQTTReturnCode, str],
) -> None:
    """Test MQTT return code message retrieval."""
    message = return_code.get_message()
    expected_substring = return_code_messages[return_code]

    if return_code == MQTTReturnCode.SUCCESS:
        assert message == expected_substring
    else:
        assert expected_substring in message.lower()


@pytest.mark.parametrize(
    ("value", "expected_code"),
    [
        (0, MQTTReturnCode.SUCCESS),
        (1, MQTTReturnCode.PROTOCOL_ERROR),
        (2, MQTTReturnCode.CLIENT_ID_REJECTED),
        (3, MQTTReturnCode.SERVER_UNAVAILABLE),
        (4, MQTTReturnCode.BAD_CREDENTIALS),
        (5, MQTTReturnCode.NOT_AUTHORIZED),
    ],
)
def test_mqtt_return_code_from_int(value: int, expected_code: MQTTReturnCode) -> None:
    """Test creating return code from integer."""
    code = MQTTReturnCode(value)
    assert code == expected_code


def test_mqtt_return_code_comparison() -> None:
    """Test MQTT return code value comparisons."""
    # ===== MQTTConnectionFlags Tests =====""
    assert MQTTReturnCode.SUCCESS.value == 0
    assert MQTTReturnCode.BAD_CREDENTIALS.value == 4  # noqa: PLR2004
    assert MQTTReturnCode(0) == MQTTReturnCode.SUCCESS


# ===== MQTTConnectionFlags Tests =====


def test_mqtt_connection_flags_defaults() -> None:
    """Test connection flags with default values."""
    flags = MQTTConnectionFlags()
    assert flags.session_present is False


@pytest.mark.parametrize(
    "session_present",
    [True, False],
)
def test_mqtt_connection_flags_custom_values(session_present: bool) -> None:  # noqa: FBT001
    """Test connection flags with custom values."""
    flags = MQTTConnectionFlags(session_present=session_present)
    assert flags.session_present is session_present


@pytest.mark.parametrize(
    ("flags_dict", "expected_session_present"),
    [
        ({"session present": True}, True),
        ({"session present": False}, False),
        ({}, False),
        ({"session present": True, "other_key": "value"}, True),
        ({"session present": 1}, True),
        ({"session present": 0}, False),
    ],
)
def test_mqtt_connection_flags_from_dict(flags_dict: dict[str, Any], expected_session_present: bool) -> None:  # noqa: FBT001
    """Test creating connection flags from paho-mqtt callback dict."""
    flags = MQTTConnectionFlags.from_dict(flags_dict)
    assert flags.session_present is expected_session_present


@pytest.mark.parametrize(
    ("tls_version", "expected_value"),
    [
        (MQTTTLSVersion.V1_2, 2),
        (MQTTTLSVersion.V1_3, 3),
    ],
)
def test_tls_version_values(tls_version: MQTTTLSVersion, expected_value: int) -> None:
    """Test TLS version enum values."""
    assert tls_version.value == expected_value


@pytest.mark.parametrize(
    ("value", "expected_version"),
    [
        (2, MQTTTLSVersion.V1_2),
        (3, MQTTTLSVersion.V1_3),
    ],
)
def test_tls_version_from_int(value: int, expected_version: MQTTTLSVersion) -> None:
    """Test creating TLS version from integer."""
    version = MQTTTLSVersion(value)
    assert version == expected_version


def test_tls_version_comparison() -> None:
    """Test TLS version comparison."""
    assert MQTTTLSVersion.V1_2 != MQTTTLSVersion.V1_3
    assert MQTTTLSVersion.V1_3 > MQTTTLSVersion.V1_2
    assert MQTTTLSVersion.V1_3.value == 3  # noqa: PLR2004
