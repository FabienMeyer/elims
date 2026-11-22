"""Ports implemented by communication adapters."""

from collections.abc import Awaitable, Callable
from typing import Protocol

from elims_com.models import Message

type MessageHandler = Callable[[Message], Awaitable[None]]


class Publisher(Protocol):
    """Publish messages through a concrete transport."""

    async def publish(self, message: Message) -> None:
        """Publish one message."""
        ...


class Subscriber(Protocol):
    """Register message handlers with a concrete transport."""

    async def subscribe(self, subject: str, handler: MessageHandler) -> None:
        """Subscribe a handler to a subject."""
        ...
