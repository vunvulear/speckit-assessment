"""FastAPI application factory."""

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from cloudlatency.api.routes import router
from cloudlatency.api.sse import sse_stream

logger = logging.getLogger("cloudlatency.api.app")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="CloudLatency",
        description="Real-time HTTPS latency monitoring for Azure, AWS, and GCP regions",
        version="0.1.0",
    )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled error on %s %s: %s", request.method, request.url.path, exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    app.include_router(router, prefix="/api/v1")
    app.add_api_route("/api/v1/stream", sse_stream, methods=["GET"])

    static_dir = Path(__file__).parent.parent / "ui" / "static"
    if static_dir.exists():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app
