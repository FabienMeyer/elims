"""Message serialization."""

from elims_com.models import Message


class JsonMessageCodec:
    """Encode and decode messages as UTF-8 JSON."""

    @staticmethod
    def encode(message: Message) -> bytes:
        """Serialize a message."""
        return message.model_dump_json().encode()

    @staticmethod
    def decode(data: bytes) -> Message:
        """Deserialize and validate a message."""
        return Message.model_validate_json(data)
