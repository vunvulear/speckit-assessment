"""Tests for package initialization and CLI argument parsing."""

from unittest.mock import MagicMock, patch

import pytest

from cloudlatency import __version__
from cloudlatency.__main__ import main, parse_args
from cloudlatency.app import DEFAULT_PORT


def test_version_exists():
    """Package exposes a version string."""
    assert isinstance(__version__, str)
    assert __version__ == "0.1.0"


def test_package_importable():
    """Package is importable without errors."""
    import cloudlatency

    assert hasattr(cloudlatency, "__version__")


def test_parse_args_default_port():
    """Default port is 8080."""
    args = parse_args([])
    assert args.port == DEFAULT_PORT


def test_parse_args_custom_port():
    """--port flag overrides default."""
    args = parse_args(["--port", "9090"])
    assert args.port == 9090


@patch("cloudlatency.__main__.web.run_app")
@patch("cloudlatency.__main__.create_app")
def test_main_starts_server(mock_create_app: MagicMock, mock_run_app: MagicMock):
    """main() creates app and calls run_app."""
    mock_app = MagicMock()
    mock_create_app.return_value = mock_app

    main(["--port", "9999"])

    mock_create_app.assert_called_once_with(port=9999)
    mock_run_app.assert_called_once_with(mock_app, host="0.0.0.0", port=9999, print=None)


@patch("cloudlatency.__main__.web.run_app", side_effect=OSError("Address already in use"))
@patch("cloudlatency.__main__.create_app")
def test_main_exits_on_port_conflict(mock_create_app: MagicMock, mock_run_app: MagicMock):
    """main() exits with code 1 if port is in use."""
    mock_create_app.return_value = MagicMock()

    with pytest.raises(SystemExit) as exc_info:
        main(["--port", "8080"])

    assert exc_info.value.code == 1
