"""Application configuration with environment variable overrides."""

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    """Application settings with sensible defaults and env var overrides."""

    host: str = field(default_factory=lambda: os.environ.get("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.environ.get("PORT", "8000")))
    measurement_interval: int = field(default_factory=lambda: int(os.environ.get("MEASUREMENT_INTERVAL", "10")))
    request_timeout: int = field(default_factory=lambda: int(os.environ.get("REQUEST_TIMEOUT", "5")))
    log_level: str = field(default_factory=lambda: os.environ.get("LOG_LEVEL", "INFO").upper())


def get_settings() -> Settings:
    """Create a Settings instance from current environment."""
    return Settings()
