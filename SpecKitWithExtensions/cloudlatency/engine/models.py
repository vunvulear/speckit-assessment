"""Core data models for the latency measurement engine."""

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class CloudProvider:
    """Cloud vendor: aws, azure, gcp."""

    id: str
    name: str


@dataclass(frozen=True)
class CloudRegion:
    """Geographic region within a cloud provider."""

    provider_id: str
    region_code: str
    region_name: str
    endpoint_url: str


@dataclass(frozen=True)
class LatencyMeasurement:
    """Single latency reading for a cloud region."""

    provider_id: str
    region_code: str
    latency_ms: float | None
    is_reachable: bool
    measured_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    region_name: str = ""
    endpoint_url: str = ""


@dataclass(frozen=True)
class VendorSummary:
    """Aggregated vendor statistics computed from measurements."""

    provider_id: str
    provider_name: str
    average_latency_ms: float | None
    closest_region_code: str | None
    closest_region_name: str | None
    closest_latency_ms: float | None
    total_regions: int
    reachable_regions: int


@dataclass(frozen=True)
class LatencySnapshot:
    """Complete measurement cycle result."""

    measured_at: datetime
    measurements: list[LatencyMeasurement] = field(default_factory=list)
    vendor_summaries: list[VendorSummary] = field(default_factory=list)
