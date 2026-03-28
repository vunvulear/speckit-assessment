"""Tests for REST API endpoints."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from cloudlatency.api import api_health, api_results, api_results_by_provider, api_summary
from cloudlatency.models import LatencyResult, Status
from cloudlatency.store import LatencyStore


def _make_app(store: LatencyStore) -> web.Application:
    """Create a minimal test app with API routes and a pre-populated store."""
    app = web.Application()
    app["store"] = store
    app.router.add_get("/api/v1/health", api_health)
    app.router.add_get("/api/v1/results", api_results)
    app.router.add_get("/api/v1/results/{provider}", api_results_by_provider)
    app.router.add_get("/api/v1/summary", api_summary)
    return app


def _populated_store() -> LatencyStore:
    store = LatencyStore()
    store.update_all([
        LatencyResult("aws", "us-east-1", 42.0, Status.OK, datetime(2026, 1, 1, tzinfo=timezone.utc)),
        LatencyResult("aws", "eu-west-1", 120.0, Status.OK, datetime(2026, 1, 1, tzinfo=timezone.utc)),
        LatencyResult("azure", "westus", 55.0, Status.OK, datetime(2026, 1, 1, tzinfo=timezone.utc)),
        LatencyResult("gcp", "us-central1", None, Status.UNREACHABLE, datetime(2026, 1, 1, tzinfo=timezone.utc)),
    ])
    return store


class TestApiHealth:
    """Tests for GET /api/v1/health."""

    @pytest.mark.asyncio
    async def test_health_returns_200(self):
        app = _make_app(_populated_store())
        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/api/v1/health")
            assert resp.status == 200
            data = await resp.json()
            assert data["status"] == "healthy"
            assert "uptime_seconds" in data
            assert data["last_cycle_at"] is not None

    @pytest.mark.asyncio
    async def test_health_empty_store(self):
        app = _make_app(LatencyStore())
        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/api/v1/health")
            assert resp.status == 200
            data = await resp.json()
            assert data["status"] == "healthy"
            assert data["last_cycle_at"] is None


class TestApiResults:
    """Tests for GET /api/v1/results."""

    @pytest.mark.asyncio
    async def test_results_returns_sorted_list(self):
        app = _make_app(_populated_store())
        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/api/v1/results")
            assert resp.status == 200
            data = await resp.json()
            assert isinstance(data, list)
            assert len(data) == 4
            # First result should have lowest latency
            assert data[0]["latency_ms"] == 42.0
            # Last result should be unreachable (None latency)
            assert data[-1]["latency_ms"] is None

    @pytest.mark.asyncio
    async def test_results_includes_all_fields(self):
        app = _make_app(_populated_store())
        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/api/v1/results")
            data = await resp.json()
            for result in data:
                assert "provider" in result
                assert "region" in result
                assert "latency_ms" in result
                assert "status" in result
                assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_results_empty_store(self):
        app = _make_app(LatencyStore())
        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/api/v1/results")
            assert resp.status == 200
            data = await resp.json()
            assert data == []


class TestApiResultsByProvider:
    """Tests for GET /api/v1/results/{provider}."""

    @pytest.mark.asyncio
    async def test_filter_aws(self):
        app = _make_app(_populated_store())
        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/api/v1/results/aws")
            assert resp.status == 200
            data = await resp.json()
            assert len(data) == 2
            assert all(r["provider"] == "aws" for r in data)

    @pytest.mark.asyncio
    async def test_filter_azure(self):
        app = _make_app(_populated_store())
        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/api/v1/results/azure")
            assert resp.status == 200
            data = await resp.json()
            assert len(data) == 1
            assert data[0]["provider"] == "azure"

    @pytest.mark.asyncio
    async def test_invalid_provider_returns_404(self):
        app = _make_app(_populated_store())
        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/api/v1/results/invalid")
            assert resp.status == 404
            data = await resp.json()
            assert data["code"] == "PROVIDER_NOT_FOUND"
            assert "error" in data


class TestApiSummary:
    """Tests for GET /api/v1/summary."""

    @pytest.mark.asyncio
    async def test_summary_returns_providers(self):
        app = _make_app(_populated_store())
        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/api/v1/summary")
            assert resp.status == 200
            data = await resp.json()
            assert "providers" in data
            assert "aws" in data["providers"]
            assert "azure" in data["providers"]
            assert "gcp" in data["providers"]

    @pytest.mark.asyncio
    async def test_summary_aws_values(self):
        app = _make_app(_populated_store())
        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/api/v1/summary")
            data = await resp.json()
            aws = data["providers"]["aws"]
            assert aws["average_latency_ms"] == 81.0
            assert aws["closest_region"] == "us-east-1"
            assert aws["closest_latency_ms"] == 42.0
            assert aws["total_regions"] == 2
            assert aws["reachable_regions"] == 2

    @pytest.mark.asyncio
    async def test_summary_empty_store(self):
        app = _make_app(LatencyStore())
        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/api/v1/summary")
            assert resp.status == 200
            data = await resp.json()
            assert data == {"providers": {}}


class TestCORS:
    """Tests for CORS middleware."""

    @pytest.mark.asyncio
    async def test_cors_headers_for_localhost(self):
        from cloudlatency.app import cors_middleware

        app = web.Application(middlewares=[cors_middleware])
        app["store"] = _populated_store()
        app.router.add_get("/api/v1/results", api_results)

        async with TestClient(TestServer(app)) as client:
            resp = await client.get(
                "/api/v1/results",
                headers={"Origin": "http://localhost:8080"},
            )
            assert resp.status == 200
            assert resp.headers["Access-Control-Allow-Origin"] == "http://localhost:8080"
            assert "GET" in resp.headers["Access-Control-Allow-Methods"]

    @pytest.mark.asyncio
    async def test_cors_headers_for_127(self):
        from cloudlatency.app import cors_middleware

        app = web.Application(middlewares=[cors_middleware])
        app["store"] = _populated_store()
        app.router.add_get("/api/v1/results", api_results)

        async with TestClient(TestServer(app)) as client:
            resp = await client.get(
                "/api/v1/results",
                headers={"Origin": "http://127.0.0.1:3000"},
            )
            assert resp.headers["Access-Control-Allow-Origin"] == "http://127.0.0.1:3000"

    @pytest.mark.asyncio
    async def test_no_cors_for_external_origin(self):
        from cloudlatency.app import cors_middleware

        app = web.Application(middlewares=[cors_middleware])
        app["store"] = _populated_store()
        app.router.add_get("/api/v1/results", api_results)

        async with TestClient(TestServer(app)) as client:
            resp = await client.get(
                "/api/v1/results",
                headers={"Origin": "https://evil.com"},
            )
            assert "Access-Control-Allow-Origin" not in resp.headers


class TestErrorFormat:
    """Tests for consistent JSON error responses."""

    @pytest.mark.asyncio
    async def test_404_returns_json_error(self):
        from cloudlatency.app import cors_middleware

        app = web.Application(middlewares=[cors_middleware])
        app["store"] = _populated_store()
        app.router.add_get("/api/v1/results", api_results)

        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/api/v1/nonexistent")
            assert resp.status == 404
            data = await resp.json()
            assert "error" in data
            assert "code" in data
