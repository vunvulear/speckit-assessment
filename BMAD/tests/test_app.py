"""Tests for application factory and lifecycle."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from aiohttp import web

from cloudlatency.app import DEFAULT_PORT, create_app, health_handler, on_shutdown, on_startup
from cloudlatency.store import LatencyStore


class TestCreateApp:
    """Tests for create_app()."""

    def test_returns_web_application(self):
        app = create_app()
        assert isinstance(app, web.Application)

    def test_stores_port(self):
        app = create_app(port=9999)
        assert app["_port"] == 9999

    def test_default_port(self):
        assert DEFAULT_PORT == 8080

    def test_has_health_route(self):
        app = create_app()
        routes = [r.resource.canonical for r in app.router.routes() if hasattr(r.resource, "canonical")]
        assert "/health" in routes

    def test_has_startup_hook(self):
        app = create_app()
        assert len(app.on_startup) > 0

    def test_has_shutdown_hook(self):
        app = create_app()
        assert len(app.on_shutdown) > 0


class TestOnStartup:
    """Tests for on_startup()."""

    @pytest.mark.asyncio
    async def test_creates_store(self):
        app = web.Application()
        with patch("cloudlatency.app.probe_loop", new_callable=lambda: lambda *a, **kw: asyncio.sleep(999)):
            await on_startup(app)

        assert isinstance(app["store"], LatencyStore)
        assert "data_event" in app
        assert "http_session" in app
        assert "probe_task" in app

        # cleanup
        app["probe_task"].cancel()
        try:
            await app["probe_task"]
        except (asyncio.CancelledError, Exception):
            pass
        await app["http_session"].close()


class TestOnShutdown:
    """Tests for on_shutdown()."""

    @pytest.mark.asyncio
    async def test_cancels_probe_task(self):
        app = web.Application()

        async def forever():
            await asyncio.sleep(999)

        task = asyncio.create_task(forever())
        app["probe_task"] = task
        session = AsyncMock()
        session.close = AsyncMock()
        app["http_session"] = session

        await on_shutdown(app)

        assert task.cancelled() or task.done()
        session.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_handles_missing_task(self):
        """Shutdown works even if probe_task is not set."""
        app = web.Application()
        await on_shutdown(app)

    @pytest.mark.asyncio
    async def test_handles_already_done_task(self):
        """Shutdown works if task already completed."""
        app = web.Application()

        async def instant():
            pass

        task = asyncio.create_task(instant())
        await task
        app["probe_task"] = task
        session = AsyncMock()
        session.close = AsyncMock()
        app["http_session"] = session

        await on_shutdown(app)
        session.close.assert_awaited_once()


class TestHealthHandler:
    """Tests for health endpoint."""

    @pytest.mark.asyncio
    async def test_health_returns_ok(self):
        request = AsyncMock()
        response = await health_handler(request)
        assert response.status == 200
