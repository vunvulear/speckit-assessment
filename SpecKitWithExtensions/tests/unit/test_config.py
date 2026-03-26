"""Unit tests for configuration management. @req FR-001"""

import os
from unittest.mock import patch

import pytest

from cloudlatency.config import Settings, get_settings


class TestSettingsDefaults:
    """Test that Settings has correct defaults."""

    def test_default_host(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            s = Settings()
            assert s.host == "0.0.0.0"

    def test_default_port(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            s = Settings()
            assert s.port == 8000

    def test_default_measurement_interval(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            s = Settings()
            assert s.measurement_interval == 10

    def test_default_request_timeout(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            s = Settings()
            assert s.request_timeout == 5

    def test_default_log_level(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            s = Settings()
            assert s.log_level == "INFO"


class TestSettingsEnvOverrides:
    """Test that environment variables override defaults."""

    def test_host_override(self) -> None:
        with patch.dict(os.environ, {"HOST": "127.0.0.1"}):
            s = Settings()
            assert s.host == "127.0.0.1"

    def test_port_override(self) -> None:
        with patch.dict(os.environ, {"PORT": "9090"}):
            s = Settings()
            assert s.port == 9090

    def test_measurement_interval_override(self) -> None:
        with patch.dict(os.environ, {"MEASUREMENT_INTERVAL": "30"}):
            s = Settings()
            assert s.measurement_interval == 30

    def test_request_timeout_override(self) -> None:
        with patch.dict(os.environ, {"REQUEST_TIMEOUT": "10"}):
            s = Settings()
            assert s.request_timeout == 10

    def test_log_level_override(self) -> None:
        with patch.dict(os.environ, {"LOG_LEVEL": "debug"}):
            s = Settings()
            assert s.log_level == "DEBUG"


class TestSettingsValidation:
    """Test settings edge cases."""

    def test_settings_is_frozen(self) -> None:
        s = Settings()
        with pytest.raises(AttributeError):
            s.port = 9999  # type: ignore[misc]

    def test_get_settings_returns_settings(self) -> None:
        result = get_settings()
        assert isinstance(result, Settings)

    def test_invalid_port_raises(self) -> None:
        with patch.dict(os.environ, {"PORT": "not_a_number"}):
            with pytest.raises(ValueError):
                Settings()
