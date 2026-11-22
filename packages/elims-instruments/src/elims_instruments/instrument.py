"""Instrument domain models."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Instrument:
    """Small framework-independent instrument entity."""

    identifier: str
    name: str
