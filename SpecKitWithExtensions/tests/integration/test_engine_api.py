"""Integration test for engine-to-API data flow. @req FR-003 @req FR-001"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from cloudlatency.api.app import create_app
from cloudlatency.api.routes import set_engine_status, set_snapshot
from cloudlatency.engine.models import (
    CloudRegion,
    LatencyMeasurement,
    LatencySnapshot,
)
from cloudlatency.engine.scheduler import create_snapshot as engine_create_snapshot


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
def sample_measurements() -> list[LatencyMeasurement]:
    now = datetime(2026, 3, 26, 12, 0, 0, tzinfo=timezone.utc)
    return [
        LatencyMeasurement(provider_id="aws", region_code="us-east-1", region_name="US East", latency_ms=25.0, is_reachable=True, measured_at=now),
        LatencyMeasurement(provider_id="aws", region_code="eu-west-1", region_name="EU West", latency_ms=120.0, is_reachable=True, measured_at=now),
        LatencyMeasurement(provider_id="azure", region_code="eastus", region_name="East US", latency_ms=30.0, is_reachable=True, measured_at=now),
        LatencyMeasurement(provider_id="gcp", region_code="us-central1", region_name="Iowa", latency_ms=None, is_reachable=False, measured_at=now),
    ]


class TestEngineToAPIFlow:
    """Test that engine-produced snapshots are correctly served by the API."""

    @pytest.mark.asyncio
    async def test_engine_snapshot_served_via_api(self, client: AsyncClient, sample_measurements: list[LatencyMeasurement]) -> None:
        """Engine creates a snapshot → set in routes → API serves it."""
        snapshot = engine_create_snapshot(sample_measurements)
        set_snapshot(snapshot)
        set_engine_status(True, 4)

        resp = await client.get("/api/v1/latency")
        assert resp.status_code == 200
        data = resp.json()

        # Measurements are sorted by latency (ascending, None last)
        latencies = [m["latency_ms"] for m in data["measurements"]]
        numeric = [l for l in latencies if l is not None]
        assert numeric == sorted(numeric)

        # Vendor summaries present
        assert len(data["vendor_summaries"]) == 3
        provider_ids = {vs["provider_id"] for vs in data["vendor_summaries"]}
        assert provider_ids == {"aws", "azure", "gcp"}

    @pytest.mark.asyncio
    async def test_health_reflects_engine_state(self, client: AsyncClient, sample_measurements: list[LatencyMeasurement]) -> None:
        """Health endpoint reflects engine running state."""
        # Before engine starts
        resp = await client.get("/api/v1/health")
        assert resp.json()["engine_running"] is False

        # After engine produces data
        snapshot = engine_create_snapshot(sample_measurements)
        set_snapshot(snapshot)
        set_engine_status(True, 4)

        resp = await client.get("/api/v1/health")
        data = resp.json()
        assert data["engine_running"] is True
        assert data["regions_discovered"] == 4
        assert data["last_measurement"] is not None

    @pytest.mark.asyncio
    async def test_regions_endpoint_groups_by_provider(self, client: AsyncClient, sample_measurements: list[LatencyMeasurement]) -> None:
        """Regions endpoint correctly groups measurements by provider."""
        snapshot = engine_create_snapshot(sample_measurements)
        set_snapshot(snapshot)

        resp = await client.get("/api/v1/regions")
        assert resp.status_code == 200
        regions = resp.json()["regions"]
        assert len(regions["aws"]) == 2
        assert len(regions["azure"]) == 1
        assert len(regions["gcp"]) == 1

    @pytest.mark.asyncio
    async def test_vendor_summary_accuracy(self, client: AsyncClient, sample_measurements: list[LatencyMeasurement]) -> None:
        """Vendor summaries have correct computed values."""
        snapshot = engine_create_snapshot(sample_measurements)
        set_snapshot(snapshot)

        resp = await client.get("/api/v1/latency")
        summaries = {vs["provider_id"]: vs for vs in resp.json()["vendor_summaries"]}

        # AWS: avg of 25+120=72.5, closest=us-east-1 at 25ms
        assert summaries["aws"]["average_latency_ms"] == pytest.approx(72.5)
        assert summaries["aws"]["closest_region_code"] == "us-east-1"
        assert summaries["aws"]["closest_latency_ms"] == 25.0
        assert summaries["aws"]["total_regions"] == 2
        assert summaries["aws"]["reachable_regions"] == 2

        # GCP: all unreachable
        assert summaries["gcp"]["average_latency_ms"] is None
        assert summaries["gcp"]["closest_region_code"] is None
        assert summaries["gcp"]["reachable_regions"] == 0
