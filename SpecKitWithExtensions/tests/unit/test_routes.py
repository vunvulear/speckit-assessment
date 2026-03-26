"""Unit tests for REST API routes. @req FR-003 @req FR-001"""

from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient

from cloudlatency.api.app import create_app
from cloudlatency.api.routes import set_engine_status, set_snapshot
from cloudlatency.engine.models import (
    LatencyMeasurement,
    LatencySnapshot,
    VendorSummary,
)


@pytest.fixture(autouse=True)
def reset_state():
    """Reset shared route state before each test."""
    set_snapshot(None)  # type: ignore[arg-type]
    set_engine_status(False, 0)
    yield
    set_snapshot(None)  # type: ignore[arg-type]
    set_engine_status(False, 0)


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_snapshot() -> LatencySnapshot:
    now = datetime(2026, 3, 26, 12, 0, 0, tzinfo=timezone.utc)
    return LatencySnapshot(
        measured_at=now,
        measurements=[
            LatencyMeasurement(provider_id="aws", region_code="us-east-1", region_name="US East", latency_ms=25.0, is_reachable=True, measured_at=now),
            LatencyMeasurement(provider_id="azure", region_code="eastus", region_name="East US", latency_ms=30.0, is_reachable=True, measured_at=now),
            LatencyMeasurement(provider_id="gcp", region_code="us-central1", region_name="Iowa", latency_ms=None, is_reachable=False, measured_at=now),
        ],
        vendor_summaries=[
            VendorSummary(provider_id="aws", provider_name="AWS", average_latency_ms=25.0, closest_region_code="us-east-1", closest_region_name="US East", closest_latency_ms=25.0, total_regions=1, reachable_regions=1),
            VendorSummary(provider_id="azure", provider_name="Azure", average_latency_ms=30.0, closest_region_code="eastus", closest_region_name="East US", closest_latency_ms=30.0, total_regions=1, reachable_regions=1),
            VendorSummary(provider_id="gcp", provider_name="GCP", average_latency_ms=None, closest_region_code=None, closest_region_name=None, closest_latency_ms=None, total_regions=1, reachable_regions=0),
        ],
    )


class TestGetLatency:
    """Test GET /api/v1/latency."""

    @pytest.mark.asyncio
    async def test_returns_503_when_no_data(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/latency")
        assert resp.status_code == 503

    @pytest.mark.asyncio
    async def test_returns_snapshot_data(self, client: AsyncClient, sample_snapshot: LatencySnapshot) -> None:
        set_snapshot(sample_snapshot)
        resp = await client.get("/api/v1/latency")
        assert resp.status_code == 200
        data = resp.json()
        assert "measured_at" in data
        assert len(data["measurements"]) == 3
        assert len(data["vendor_summaries"]) == 3

    @pytest.mark.asyncio
    async def test_measurements_contain_required_fields(self, client: AsyncClient, sample_snapshot: LatencySnapshot) -> None:
        set_snapshot(sample_snapshot)
        resp = await client.get("/api/v1/latency")
        m = resp.json()["measurements"][0]
        assert "provider_id" in m
        assert "region_code" in m
        assert "region_name" in m
        assert "latency_ms" in m
        assert "is_reachable" in m

    @pytest.mark.asyncio
    async def test_vendor_summaries_contain_required_fields(self, client: AsyncClient, sample_snapshot: LatencySnapshot) -> None:
        set_snapshot(sample_snapshot)
        resp = await client.get("/api/v1/latency")
        vs = resp.json()["vendor_summaries"][0]
        assert "provider_id" in vs
        assert "provider_name" in vs
        assert "average_latency_ms" in vs
        assert "closest_region_code" in vs
        assert "total_regions" in vs


class TestGetRegions:
    """Test GET /api/v1/regions."""

    @pytest.mark.asyncio
    async def test_returns_503_when_no_data(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/regions")
        assert resp.status_code == 503

    @pytest.mark.asyncio
    async def test_returns_grouped_regions(self, client: AsyncClient, sample_snapshot: LatencySnapshot) -> None:
        set_snapshot(sample_snapshot)
        resp = await client.get("/api/v1/regions")
        assert resp.status_code == 200
        data = resp.json()
        assert "regions" in data
        assert "aws" in data["regions"]
        assert "azure" in data["regions"]
        assert "gcp" in data["regions"]


class TestHealthCheck:
    """Test GET /api/v1/health."""

    @pytest.mark.asyncio
    async def test_health_returns_200(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_health_starting_status(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/health")
        data = resp.json()
        assert data["status"] == "starting"
        assert data["engine_running"] is False

    @pytest.mark.asyncio
    async def test_health_running_status(self, client: AsyncClient, sample_snapshot: LatencySnapshot) -> None:
        set_engine_status(True, 150)
        set_snapshot(sample_snapshot)
        resp = await client.get("/api/v1/health")
        data = resp.json()
        assert data["status"] == "ok"
        assert data["engine_running"] is True
        assert data["regions_discovered"] == 150
        assert data["last_measurement"] is not None
