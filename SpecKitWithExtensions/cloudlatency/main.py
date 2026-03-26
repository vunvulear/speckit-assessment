"""Application entry point — starts uvicorn with engine initialization."""

import asyncio
import logging

import uvicorn

from cloudlatency.api.app import create_app
from cloudlatency.config import get_settings
from cloudlatency.logging_config import setup_logging

logger = logging.getLogger("cloudlatency.main")

# Will be set when engine module is implemented
_scheduler_task: asyncio.Task | None = None


async def start_engine() -> None:
    """Initialize and start the measurement engine."""
    global _scheduler_task
    try:
        from cloudlatency.engine.scheduler import run_scheduler

        _scheduler_task = asyncio.create_task(run_scheduler())
        logger.info("Measurement engine started")
    except ImportError:
        logger.warning("Scheduler not yet implemented — running API only")


async def stop_engine() -> None:
    """Gracefully stop the measurement engine."""
    global _scheduler_task
    if _scheduler_task and not _scheduler_task.done():
        _scheduler_task.cancel()
        try:
            await _scheduler_task
        except asyncio.CancelledError:
            pass
        logger.info("Measurement engine stopped")


def main() -> None:
    """Run the CloudLatency application."""
    settings = get_settings()
    setup_logging(settings.log_level)

    app = create_app()

    @app.on_event("startup")
    async def on_startup() -> None:
        await start_engine()

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        await stop_engine()

    logger.info("Starting CloudLatency on %s:%d", settings.host, settings.port)
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
