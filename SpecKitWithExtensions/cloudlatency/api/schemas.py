"""Pydantic response schemas for the REST API."""

from datetime import datetime

from pydantic import BaseModel, Field


class RegionResponse(BaseModel):
    """Single region in the latency response."""

    provider_id: str
    provider_name: str = ""
    region_code: str
    region_name: str
    latency_ms: float | None = None
    is_reachable: bool = True


class VendorSummaryResponse(BaseModel):
    """Aggregated vendor statistics."""

    provider_id: str
    provider_name: str
    average_latency_ms: float | None = None
    closest_region_code: str | None = None
    closest_region_name: str | None = None
    closest_latency_ms: float | None = None
    total_regions: int = 0
    reachable_regions: int = 0


class LatencyResponse(BaseModel):
    """Full latency snapshot response."""

    measured_at: datetime
    measurements: list[RegionResponse] = Field(default_factory=list)
    vendor_summaries: list[VendorSummaryResponse] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    engine_running: bool = False
    last_measurement: datetime | None = None
    regions_discovered: int = 0
