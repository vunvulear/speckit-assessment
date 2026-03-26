"""Async HTTPS HEAD latency prober for cloud regions."""

import asyncio
import logging
import time
from datetime import UTC, datetime

import aiohttp

from cloudlatency.engine.models import CloudRegion, LatencyMeasurement

logger = logging.getLogger("cloudlatency.engine.prober")


async def probe_region(region: CloudRegion, timeout: int = 5) -> LatencyMeasurement:
    """Probe a single region with an HTTPS HEAD request and measure round-trip time."""
    now = datetime.now(UTC)
    try:
        async with aiohttp.ClientSession() as session:
            start = time.monotonic()
            async with session.head(
                region.endpoint_url,
                timeout=aiohttp.ClientTimeout(total=timeout),
                allow_redirects=True,
                ssl=False,
            ) as _resp:
                elapsed_ms = (time.monotonic() - start) * 1000
                return LatencyMeasurement(
                    provider_id=region.provider_id,
                    region_code=region.region_code,
                    region_name=region.region_name,
                    endpoint_url=region.endpoint_url,
                    latency_ms=round(elapsed_ms, 2),
                    is_reachable=True,
                    measured_at=now,
                )
    except (TimeoutError, aiohttp.ClientError, ConnectionError, OSError) as e:
        logger.debug("Region %s/%s unreachable: %s", region.provider_id, region.region_code, e)
        return LatencyMeasurement(
            provider_id=region.provider_id,
            region_code=region.region_code,
            region_name=region.region_name,
            endpoint_url=region.endpoint_url,
            latency_ms=None,
            is_reachable=False,
            measured_at=now,
        )
    except Exception as e:
        logger.error("Unexpected error probing %s/%s: %s", region.provider_id, region.region_code, e)
        return LatencyMeasurement(
            provider_id=region.provider_id,
            region_code=region.region_code,
            region_name=region.region_name,
            endpoint_url=region.endpoint_url,
            latency_ms=None,
            is_reachable=False,
            measured_at=now,
        )


async def probe_all_regions(regions: list[CloudRegion], timeout: int = 5) -> list[LatencyMeasurement]:
    """Probe all regions concurrently and return measurements."""
    if not regions:
        return []

    tasks = [probe_region(region, timeout=timeout) for region in regions]
    measurements = await asyncio.gather(*tasks)
    logger.info("Probed %d regions: %d reachable", len(measurements), sum(1 for m in measurements if m.is_reachable))
    return list(measurements)
