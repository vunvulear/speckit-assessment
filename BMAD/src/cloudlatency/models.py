"""Data models for CloudLatency measurements."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class Status(Enum):
    """Measurement status for a probe result."""

    OK = "ok"
    UNREACHABLE = "unreachable"
    ERROR = "error"


@dataclass(frozen=True)
class LatencyResult:
    """A single latency measurement for one cloud region."""

    provider: str
    region: str
    latency_ms: float | None
    status: Status
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
