"""Async probe engine for concurrent latency measurement."""

from __future__ import annotations

import asyncio
import logging
import time

import aiohttp

from cloudlatency.models import LatencyResult, Status
from cloudlatency.regions import Region
from cloudlatency.store import LatencyStore

logger = logging.getLogger(__name__)

PROBE_TIMEOUT_SECONDS = 5
PROBE_INTERVAL_SECONDS = 10


async def probe_region(session: aiohttp.ClientSession, region: Region) -> LatencyResult:
    """Measure HTTPS latency to a single cloud region.

    Returns LatencyResult with status OK and measured latency_ms on success,
    or status UNREACHABLE with latency_ms=None on failure.
    """
    try:
        start = time.monotonic()
        async with session.get(region.endpoint_url, timeout=aiohttp.ClientTimeout(total=PROBE_TIMEOUT_SECONDS)):
            elapsed_ms = (time.monotonic() - start) * 1000
            return LatencyResult(
                provider=region.provider,
                region=region.region_name,
                latency_ms=round(elapsed_ms, 2),
                status=Status.OK,
            )
    except Exception as exc:
        logger.warning(
            "probe_failed",
            extra={"provider": region.provider, "region": region.region_name, "error": str(exc)},
        )
        return LatencyResult(
            provider=region.provider,
            region=region.region_name,
            latency_ms=None,
            status=Status.UNREACHABLE,
        )


async def run_probe_cycle(
    session: aiohttp.ClientSession,
    regions: list[Region],
    store: LatencyStore,
    data_event: asyncio.Event | None = None,
) -> list[LatencyResult]:
    """Run a single measurement cycle probing all regions concurrently.

    Stores results in the LatencyStore and optionally signals data_event.
    Returns the list of results.
    """
    start = time.monotonic()
    tasks = [probe_region(session, region) for region in regions]
    results: list[LatencyResult] = await asyncio.gather(*tasks, return_exceptions=False)  # type: ignore[assignment]
    duration_ms = (time.monotonic() - start) * 1000

    store.update_all(results)

    success = sum(1 for r in results if r.status == Status.OK)
    failed = len(results) - success
    logger.info(
        "probe_cycle_complete",
        extra={"success": success, "failed": failed, "duration_ms": round(duration_ms, 2), "total": len(results)},
    )

    if data_event is not None:
        data_event.set()

    return results


async def probe_loop(
    session: aiohttp.ClientSession,
    regions: list[Region],
    store: LatencyStore,
    data_event: asyncio.Event | None = None,
    interval: float = PROBE_INTERVAL_SECONDS,
) -> None:
    """Run measurement cycles indefinitely with a sleep interval between them.

    Continues until the task is cancelled. Errors in individual cycles
    are logged but never crash the loop.
    """
    while True:
        try:
            await run_probe_cycle(session, regions, store, data_event)
        except asyncio.CancelledError:
            logger.info("probe_loop_cancelled")
            raise
        except Exception as exc:
            logger.error("probe_loop_cycle_error", extra={"error": str(exc)})
        await asyncio.sleep(interval)
