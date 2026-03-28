"""Application factory and lifecycle management for CloudLatency."""

from __future__ import annotations

import asyncio
import logging
import pathlib

import aiohttp
from aiohttp import web

from cloudlatency.api import api_health, api_results, api_results_by_provider, api_summary
from cloudlatency.probe import probe_loop
from cloudlatency.regions import get_all_regions
from cloudlatency.sse import SSEBroadcaster, sse_handler
from cloudlatency.store import LatencyStore

STATIC_DIR = pathlib.Path(__file__).parent / "static"

logger = logging.getLogger(__name__)

DEFAULT_PORT = 8080


async def on_startup(app: web.Application) -> None:
    """Start the probe engine when the server starts."""
    store = LatencyStore()
    data_event = asyncio.Event()
    regions = get_all_regions()

    app["store"] = store
    app["data_event"] = data_event

    session = aiohttp.ClientSession()
    app["http_session"] = session

    task = asyncio.create_task(probe_loop(session, regions, store, data_event))
    app["probe_task"] = task

    broadcaster = SSEBroadcaster(store, data_event)
    app["sse_broadcaster"] = broadcaster
    sse_task = asyncio.create_task(broadcaster.run())
    app["sse_task"] = sse_task

    logger.info(
        "app_started",
        extra={"port": app.get("_port", DEFAULT_PORT), "region_count": len(regions)},
    )


async def on_shutdown(app: web.Application) -> None:
    """Gracefully shut down: cancel probe task and close HTTP session."""
    for key in ("probe_task", "sse_task"):
        task = app.get(key)
        if task is not None and not task.done():
            task.cancel()
            try:
                await asyncio.wait_for(task, timeout=3.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass

    session = app.get("http_session")
    if session is not None:
        await session.close()

    logger.info("app_shutdown_complete")


async def health_handler(request: web.Request) -> web.Response:
    """Simple health check endpoint."""
    return web.json_response({"status": "ok"})


@web.middleware
async def cors_middleware(request: web.Request, handler):
    """Add CORS headers for localhost origins to all API responses."""
    try:
        response = await handler(request)
    except web.HTTPException as exc:
        response = web.json_response(
            {"error": exc.reason, "code": exc.reason.upper().replace(" ", "_")},
            status=exc.status,
        )
    origin = request.headers.get("Origin", "")
    if "localhost" in origin or "127.0.0.1" in origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


def create_app(port: int = DEFAULT_PORT) -> web.Application:
    """Create and configure the aiohttp application."""
    app = web.Application(middlewares=[cors_middleware])
    app["_port"] = port

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    app.router.add_get("/health", health_handler)
    app.router.add_get("/api/v1/health", api_health)
    app.router.add_get("/api/v1/results", api_results)
    app.router.add_get("/api/v1/results/{provider}", api_results_by_provider)
    app.router.add_get("/api/v1/summary", api_summary)
    app.router.add_get("/api/v1/sse", sse_handler)

    if STATIC_DIR.is_dir():
        app.router.add_get("/", _index_handler)
        app.router.add_static("/static", STATIC_DIR, name="static")

    return app


async def _index_handler(request: web.Request) -> web.FileResponse:
    """Serve index.html from static directory."""
    return web.FileResponse(STATIC_DIR / "index.html")
