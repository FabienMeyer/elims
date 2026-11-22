"""Tests for communication contracts."""

from datetime import UTC

from elims_com import JsonMessageCodec, Message


def test_message_defaults() -> None:
    """Messages receive an identifier, UTC timestamp, and empty payload."""
    message = Message(subject="system.ready")

    assert message.payload == {}
    assert message.created_at.tzinfo is UTC


def test_json_codec_round_trip() -> None:
    """JSON serialization preserves a validated message."""
    message = Message(subject="sample.created", payload={"sample_id": 42})

    assert JsonMessageCodec.decode(JsonMessageCodec.encode(message)) == message
