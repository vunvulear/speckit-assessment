"""Measurement scheduler — orchestrates discovery and periodic probing."""

import asyncio
import logging
from datetime import UTC, datetime

from cloudlatency.api.routes import set_engine_status, set_snapshot
from cloudlatency.config import get_settings
from cloudlatency.engine.discovery import discover_all_regions
from cloudlatency.engine.models import (
    CloudRegion,
    LatencyMeasurement,
    LatencySnapshot,
    VendorSummary,
)
from cloudlatency.engine.prober import probe_all_regions

logger = logging.getLogger("cloudlatency.engine.scheduler")

PROVIDER_NAMES = {"aws": "AWS", "azure": "Azure", "gcp": "GCP"}


def build_vendor_summaries(measurements: list[LatencyMeasurement]) -> list[VendorSummary]:
    """Compute vendor summaries from a list of measurements."""
    if not measurements:
        return []

    by_provider: dict[str, list[LatencyMeasurement]] = {}
    for m in measurements:
        by_provider.setdefault(m.provider_id, []).append(m)

    summaries: list[VendorSummary] = []
    for provider_id, provider_measurements in by_provider.items():
        reachable = [m for m in provider_measurements if m.is_reachable and m.latency_ms is not None]
        total = len(provider_measurements)
        reachable_count = len(reachable)

        if reachable:
            avg = sum(m.latency_ms for m in reachable) / len(reachable)  # type: ignore[misc]
            closest = min(reachable, key=lambda m: m.latency_ms)  # type: ignore[arg-type]
            summaries.append(
                VendorSummary(
                    provider_id=provider_id,
                    provider_name=PROVIDER_NAMES.get(provider_id, provider_id),
                    average_latency_ms=round(avg, 2),
                    closest_region_code=closest.region_code,
                    closest_region_name=closest.region_name,
                    closest_latency_ms=closest.latency_ms,
                    total_regions=total,
                    reachable_regions=reachable_count,
                )
            )
        else:
            summaries.append(
                VendorSummary(
                    provider_id=provider_id,
                    provider_name=PROVIDER_NAMES.get(provider_id, provider_id),
                    average_latency_ms=None,
                    closest_region_code=None,
                    closest_region_name=None,
                    closest_latency_ms=None,
                    total_regions=total,
                    reachable_regions=0,
                )
            )

    return summaries


def create_snapshot(measurements: list[LatencyMeasurement]) -> LatencySnapshot:
    """Create a complete snapshot from measurements, sorted by latency ascending."""
    sorted_measurements = sorted(
        measurements,
        key=lambda m: m.latency_ms if m.latency_ms is not None else float("inf"),
    )
    vendor_summaries = build_vendor_summaries(measurements)
    return LatencySnapshot(
        measured_at=datetime.now(UTC),
        measurements=sorted_measurements,
        vendor_summaries=vendor_summaries,
    )


async def run_measurement_cycle(regions: list[CloudRegion], timeout: int = 5) -> LatencySnapshot:
    """Execute one measurement cycle: probe all regions and build a snapshot."""
    if not regions:
        return LatencySnapshot(measured_at=datetime.now(UTC))

    try:
        measurements = await probe_all_regions(regions, timeout=timeout)
        return create_snapshot(measurements)
    except Exception as e:
        logger.error("Measurement cycle failed: %s", e)
        return LatencySnapshot(measured_at=datetime.now(UTC))


async def run_scheduler() -> None:
    """Main scheduler loop — discovers regions once, then probes every interval."""
    settings = get_settings()
    logger.info(
        "Starting scheduler with %ds interval, %ds timeout",
        settings.measurement_interval,
        settings.request_timeout,
    )

    regions = await discover_all_regions()
    set_engine_status(True, len(regions))
    logger.info("Discovery complete: %d regions", len(regions))

    while True:
        snapshot = await run_measurement_cycle(regions, timeout=settings.request_timeout)
        set_snapshot(snapshot)
        logger.info(
            "Cycle complete: %d measurements, %d reachable",
            len(snapshot.measurements),
            sum(1 for m in snapshot.measurements if m.is_reachable),
        )
        await asyncio.sleep(settings.measurement_interval)
