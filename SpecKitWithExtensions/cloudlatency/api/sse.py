"""Server-Sent Events endpoint for real-time latency updates."""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from datetime import datetime

from sse_starlette.sse import EventSourceResponse

from cloudlatency.api.routes import get_snapshot
from cloudlatency.api.schemas import LatencyResponse, RegionResponse, VendorSummaryResponse
from cloudlatency.engine.models import LatencySnapshot

logger = logging.getLogger("cloudlatency.api.sse")


def snapshot_to_dict(snapshot: LatencySnapshot) -> dict:
    """Convert a LatencySnapshot to a JSON-serializable dict."""
    response = LatencyResponse(
        measured_at=snapshot.measured_at,
        measurements=[
            RegionResponse(
                provider_id=m.provider_id,
                region_code=m.region_code,
                region_name=m.region_name,
                latency_ms=m.latency_ms,
                is_reachable=m.is_reachable,
            )
            for m in snapshot.measurements
        ],
        vendor_summaries=[
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
            for vs in snapshot.vendor_summaries
        ],
    )
    return json.loads(response.model_dump_json())


async def event_generator() -> AsyncGenerator[dict, None]:
    """Generate SSE events whenever a new snapshot is available."""
    last_measured_at: datetime | None = None

    while True:
        snapshot = get_snapshot()
        if snapshot is not None and snapshot.measured_at != last_measured_at:
            last_measured_at = snapshot.measured_at
            data = snapshot_to_dict(snapshot)
            yield {
                "event": "latency_update",
                "data": json.dumps(data),
            }
        await asyncio.sleep(1)


async def sse_stream() -> EventSourceResponse:
    """Create an SSE response for the latency stream."""
    return EventSourceResponse(event_generator())
