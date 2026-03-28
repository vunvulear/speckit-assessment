"""Structured JSON logging configuration for CloudLatency."""

from __future__ import annotations

import logging
import sys

from pythonjsonlogger.json import JsonFormatter


def configure_logging(level: int = logging.INFO) -> None:
    """Configure structured JSON logging for all CloudLatency loggers."""
    handler = logging.StreamHandler(sys.stdout)
    formatter = JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        rename_fields={"asctime": "timestamp", "levelname": "level"},
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger("cloudlatency")
    root_logger.setLevel(level)
    root_logger.addHandler(handler)
    root_logger.propagate = False
