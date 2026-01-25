"""ELIMS Common Package - MQTT Module - Return Codes."""

from enum import IntEnum

from pydantic import BaseModel


class MQTTTLSVersion(IntEnum):
    """TLS protocol versions for MQTT."""

    V1_2 = 2
    V1_3 = 3


class MQTTReturnCode(IntEnum):
    """MQTT connection return codes with error messages."""

    SUCCESS = 0
    PROTOCOL_ERROR = 1
    CLIENT_ID_REJECTED = 2
    SERVER_UNAVAILABLE = 3
    BAD_CREDENTIALS = 4
    NOT_AUTHORIZED = 5

    def get_message(self) -> str:
        """Get human-readable error message for the return code.

        Returns:
            Error message describing the return code

        """
        messages = {
            MQTTReturnCode.SUCCESS: "Connection successful",
            MQTTReturnCode.PROTOCOL_ERROR: "Connection refused - incorrect protocol version",
            MQTTReturnCode.CLIENT_ID_REJECTED: "Connection refused - invalid client identifier",
            MQTTReturnCode.SERVER_UNAVAILABLE: "Connection refused - server unavailable",
            MQTTReturnCode.BAD_CREDENTIALS: "Connection refused - bad username or password",
            MQTTReturnCode.NOT_AUTHORIZED: "Connection refused - not authorized",
        }
        return messages.get(self, f"Unknown error (code {self})")


class MQTTConnectionFlags(BaseModel):
    """MQTT connection response flags."""

    session_present: bool = False

    @classmethod
    def from_dict(cls, flags: dict[str, object]) -> "MQTTConnectionFlags":
        """Create MQTTConnectionFlags from paho-mqtt callback flags dictionary.

        Args:
            flags: Flags dictionary from on_connect callback

        Returns:
            MQTTConnectionFlags instance

        """
        return cls(session_present=bool(flags.get("session present", False)))
