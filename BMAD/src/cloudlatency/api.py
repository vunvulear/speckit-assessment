"""REST API endpoints for CloudLatency."""

from __future__ import annotations

import time

from aiohttp import web

from cloudlatency.regions import PROVIDERS
from cloudlatency.store import LatencyStore

_start_time: float = time.monotonic()


def _get_store(request: web.Request) -> LatencyStore:
    """Retrieve the LatencyStore from the application."""
    return request.app["store"]


async def api_health(request: web.Request) -> web.Response:
    """GET /api/v1/health — service health check."""
    store = _get_store(request)
    uptime = round(time.monotonic() - _start_time, 2)
    results = store.get_all_sorted()
    last_cycle = results[0].timestamp.isoformat() if results else None
    return web.json_response({
        "status": "healthy",
        "uptime_seconds": uptime,
        "last_cycle_at": last_cycle,
    })


async def api_results(request: web.Request) -> web.Response:
    """GET /api/v1/results — all latency results sorted ascending."""
    store = _get_store(request)
    results = store.get_all_sorted()
    data = [
        {
            "provider": r.provider,
            "region": r.region,
            "latency_ms": r.latency_ms,
            "status": r.status.value,
            "timestamp": r.timestamp.isoformat(),
        }
        for r in results
    ]
    return web.json_response(data)


async def api_results_by_provider(request: web.Request) -> web.Response:
    """GET /api/v1/results/{provider} — filtered results for one provider."""
    provider = request.match_info["provider"]
    if provider not in PROVIDERS:
        return web.json_response(
            {"error": "Provider not found", "code": "PROVIDER_NOT_FOUND"},
            status=404,
        )
    store = _get_store(request)
    results = store.get_by_provider(provider)
    data = [
        {
            "provider": r.provider,
            "region": r.region,
            "latency_ms": r.latency_ms,
            "status": r.status.value,
            "timestamp": r.timestamp.isoformat(),
        }
        for r in results
    ]
    return web.json_response(data)


async def api_summary(request: web.Request) -> web.Response:
    """GET /api/v1/summary — vendor averages and closest regions."""
    store = _get_store(request)
    return web.json_response(store.get_summary())
