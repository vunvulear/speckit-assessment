"""CLI entry point for CloudLatency: python -m cloudlatency."""

from __future__ import annotations

import argparse
import logging
import sys

from aiohttp import web

from cloudlatency.app import DEFAULT_PORT, create_app
from cloudlatency.logging_config import configure_logging

logger = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        prog="cloudlatency",
        description="Real-time multi-cloud latency monitoring",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"HTTP server port (default: {DEFAULT_PORT})",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Start the CloudLatency application."""
    configure_logging()
    args = parse_args(argv)

    logger.info("cloudlatency_starting", extra={"version": "0.1.0", "port": args.port})

    app = create_app(port=args.port)
    try:
        web.run_app(app, host="0.0.0.0", port=args.port, print=None)
    except OSError as exc:
        logger.error("startup_failed", extra={"error": str(exc), "port": args.port})
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
