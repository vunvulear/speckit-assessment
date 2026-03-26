"""Unit tests for logging configuration."""

import json
import logging

from cloudlatency.logging_config import JSONFormatter, setup_logging


class TestJSONFormatter:
    """Test JSON log formatter."""

    def test_formats_as_json(self) -> None:
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="hello world",
            args=(),
            exc_info=None,
        )
        output = formatter.format(record)
        data = json.loads(output)
        assert data["level"] == "INFO"
        assert data["message"] == "hello world"
        assert data["logger"] == "test"
        assert "timestamp" in data

    def test_includes_exception(self) -> None:
        formatter = JSONFormatter()
        try:
            raise ValueError("test error")
        except ValueError:
            import sys
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=1,
                msg="failure",
                args=(),
                exc_info=sys.exc_info(),
            )
        output = formatter.format(record)
        data = json.loads(output)
        assert "exception" in data
        assert "ValueError" in data["exception"]


class TestSetupLogging:
    """Test logging setup."""

    def test_creates_handler(self) -> None:
        logger = logging.getLogger("cloudlatency")
        logger.handlers.clear()
        setup_logging("DEBUG")
        assert len(logger.handlers) == 1
        assert logger.level == logging.DEBUG

    def test_does_not_duplicate_handlers(self) -> None:
        logger = logging.getLogger("cloudlatency")
        logger.handlers.clear()
        setup_logging("INFO")
        setup_logging("INFO")
        assert len(logger.handlers) == 1

    def test_invalid_level_defaults_to_info(self) -> None:
        logger = logging.getLogger("cloudlatency")
        logger.handlers.clear()
        setup_logging("INVALID")
        assert logger.level == logging.INFO
