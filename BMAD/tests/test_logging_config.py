"""Tests for structured JSON logging configuration."""

import logging

from cloudlatency.logging_config import configure_logging


class TestConfigureLogging:
    """Tests for configure_logging()."""

    def test_configures_cloudlatency_logger(self):
        """CloudLatency logger gets a handler after configuration."""
        configure_logging()
        logger = logging.getLogger("cloudlatency")
        assert len(logger.handlers) > 0
        assert logger.level == logging.INFO
        assert logger.propagate is False

    def test_custom_level(self):
        """Custom log level is applied."""
        configure_logging(level=logging.DEBUG)
        logger = logging.getLogger("cloudlatency")
        assert logger.level == logging.DEBUG

    def test_handler_has_json_formatter(self):
        """Handler uses JSON formatter."""
        configure_logging()
        logger = logging.getLogger("cloudlatency")
        handler = logger.handlers[-1]
        assert "JsonFormatter" in type(handler.formatter).__name__

    def teardown_method(self):
        """Clean up handlers after each test."""
        logger = logging.getLogger("cloudlatency")
        logger.handlers.clear()
