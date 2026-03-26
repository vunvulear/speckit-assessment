"""REST API routes for latency data."""

import logging

from fastapi import APIRouter, HTTPException

from cloudlatency.api.schemas import HealthResponse, LatencyResponse, RegionResponse, VendorSummaryResponse
from cloudlatency.engine.models import LatencySnapshot

logger = logging.getLogger("cloudlatency.api.routes")

router = APIRouter()

# Shared state — set by the scheduler, read by routes
_latest_snapshot: LatencySnapshot | None = None
_engine_running: bool = False
_regions_discovered: int = 0


def set_snapshot(snapshot: LatencySnapshot) -> None:
    """Update the latest snapshot (called by the scheduler)."""
    global _latest_snapshot
    _latest_snapshot = snapshot


def set_engine_status(running: bool, regions: int = 0) -> None:
    """Update engine status flags."""
    global _engine_running, _regions_discovered
    _engine_running = running
    _regions_discovered = regions


def get_snapshot() -> LatencySnapshot | None:
    """Get the current snapshot (for SSE and testing)."""
    return _latest_snapshot


@router.get("/latency", response_model=LatencyResponse)
async def get_latency() -> LatencyResponse:
    """Return the latest latency snapshot."""
    if _latest_snapshot is None:
        raise HTTPException(status_code=503, detail="No measurement data available yet")

    measurements = [
        RegionResponse(
            provider_id=m.provider_id,
            region_code=m.region_code,
            region_name=m.region_name,
            latency_ms=m.latency_ms,
            is_reachable=m.is_reachable,
        )
        for m in _latest_snapshot.measurements
    ]

    vendor_summaries = [
        VendorSummaryResponse(
            provider_id=vs.provider_id,
            provider_name=vs.provider_name,
            average_latency_ms=vs.average_latency_ms,
            closest_region_code=vs.closest_region_code,
            closest_region_name=vs.closest_region_name,
            closest_latency_ms=vs.closest_latency_ms,
            total_regions=vs.total_regions,
            reachable_regions=vs.reachable_regions,
        )
        for vs in _latest_snapshot.vendor_summaries
    ]

    return LatencyResponse(
        measured_at=_latest_snapshot.measured_at,
        measurements=measurements,
        vendor_summaries=vendor_summaries,
    )


@router.get("/regions")
async def get_regions() -> dict:
    """Return discovered regions grouped by provider."""
    if _latest_snapshot is None:
        raise HTTPException(status_code=503, detail="No measurement data available yet")

    regions: dict[str, list[dict]] = {}
    for m in _latest_snapshot.measurements:
        if m.provider_id not in regions:
            regions[m.provider_id] = []
        regions[m.provider_id].append(
            {
                "region_code": m.region_code,
                "region_name": m.region_name,
            }
        )
    return {"regions": regions}


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return engine health status."""
    return HealthResponse(
        status="ok" if _engine_running else "starting",
        engine_running=_engine_running,
        last_measurement=_latest_snapshot.measured_at if _latest_snapshot else None,
        regions_discovered=_regions_discovered,
    )
