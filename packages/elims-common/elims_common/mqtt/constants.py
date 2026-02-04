"""ELIMS Common Package - MQTT Module - Return Codes."""

from enum import IntEnum

from pydantic import BaseModel

MQTT_MAX_TOPIC_LENGTH = 65535


class MQTTClientType:
    """Types of MQTT clients for logging purposes."""

    PUBLISHER = "Publisher"
    SUBSCRIBER = "Subscriber"


class MQTTReturnCode(IntEnum):
    """MQTT connection return codes with error messages."""

    SUCCESS = 0
    PROTOCOL_ERROR = 1
    CLIENT_ID_REJECTED = 2
    SERVER_UNAVAILABLE = 3
    BAD_CREDENTIALS = 4
    NOT_AUTHORIZED = 5

    @classmethod
    def get_message(cls, code: int) -> str:
        """Get human-readable error message for the return code.

        Args:
            code: MQTT return code

        Returns:
            Error message describing the return code

        """
        messages = {
            cls.SUCCESS: "Connection successful",
            cls.PROTOCOL_ERROR: "Connection refused - incorrect protocol version",
            cls.CLIENT_ID_REJECTED: "Connection refused - invalid client identifier",
            cls.SERVER_UNAVAILABLE: "Connection refused - server unavailable",
            cls.BAD_CREDENTIALS: "Connection refused - bad username or password",
            cls.NOT_AUTHORIZED: "Connection refused - not authorized",
        }
        try:
            return messages[cls(code)]
        except (ValueError, KeyError):
            return f"Unknown error (code {code})"


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
