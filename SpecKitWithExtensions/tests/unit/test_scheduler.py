"""Unit tests for measurement scheduler. @req FR-002"""

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

from cloudlatency.engine.models import (
    CloudRegion,
    LatencyMeasurement,
    LatencySnapshot,
    VendorSummary,
)
from cloudlatency.engine.scheduler import build_vendor_summaries, create_snapshot, run_measurement_cycle


@pytest.fixture
def sample_regions() -> list[CloudRegion]:
    return [
        CloudRegion(provider_id="aws", region_code="us-east-1", region_name="US East", endpoint_url="https://ec2.us-east-1.amazonaws.com"),
        CloudRegion(provider_id="aws", region_code="eu-west-1", region_name="EU West", endpoint_url="https://ec2.eu-west-1.amazonaws.com"),
        CloudRegion(provider_id="azure", region_code="eastus", region_name="East US", endpoint_url="https://eastus.status.azure.com"),
        CloudRegion(provider_id="gcp", region_code="us-central1", region_name="Iowa", endpoint_url="https://us-central1-run.googleapis.com"),
    ]


@pytest.fixture
def sample_measurements() -> list[LatencyMeasurement]:
    now = datetime(2026, 3, 26, 12, 0, 0, tzinfo=timezone.utc)
    return [
        LatencyMeasurement(provider_id="aws", region_code="us-east-1", region_name="US East", latency_ms=25.0, is_reachable=True, measured_at=now),
        LatencyMeasurement(provider_id="aws", region_code="eu-west-1", region_name="EU West", latency_ms=120.0, is_reachable=True, measured_at=now),
        LatencyMeasurement(provider_id="azure", region_code="eastus", region_name="East US", latency_ms=30.0, is_reachable=True, measured_at=now),
        LatencyMeasurement(provider_id="gcp", region_code="us-central1", region_name="Iowa", latency_ms=None, is_reachable=False, measured_at=now),
    ]


class TestBuildVendorSummaries:
    """Test vendor summary aggregation."""

    def test_computes_average_latency(self, sample_measurements: list[LatencyMeasurement]) -> None:
        summaries = build_vendor_summaries(sample_measurements)
        aws_summary = next(s for s in summaries if s.provider_id == "aws")
        assert aws_summary.average_latency_ms == pytest.approx(72.5)

    def test_finds_closest_region(self, sample_measurements: list[LatencyMeasurement]) -> None:
        summaries = build_vendor_summaries(sample_measurements)
        aws_summary = next(s for s in summaries if s.provider_id == "aws")
        assert aws_summary.closest_region_code == "us-east-1"
        assert aws_summary.closest_latency_ms == 25.0

    def test_counts_regions(self, sample_measurements: list[LatencyMeasurement]) -> None:
        summaries = build_vendor_summaries(sample_measurements)
        aws_summary = next(s for s in summaries if s.provider_id == "aws")
        assert aws_summary.total_regions == 2
        assert aws_summary.reachable_regions == 2

    def test_all_unreachable_vendor(self, sample_measurements: list[LatencyMeasurement]) -> None:
        summaries = build_vendor_summaries(sample_measurements)
        gcp_summary = next(s for s in summaries if s.provider_id == "gcp")
        assert gcp_summary.average_latency_ms is None
        assert gcp_summary.closest_region_code is None
        assert gcp_summary.reachable_regions == 0

    def test_empty_measurements(self) -> None:
        summaries = build_vendor_summaries([])
        assert summaries == []

    def test_includes_provider_name(self, sample_measurements: list[LatencyMeasurement]) -> None:
        summaries = build_vendor_summaries(sample_measurements)
        names = {s.provider_name for s in summaries}
        assert "AWS" in names
        assert "Azure" in names
        assert "GCP" in names


class TestCreateSnapshot:
    """Test snapshot creation."""

    def test_creates_snapshot_with_sorted_measurements(self, sample_measurements: list[LatencyMeasurement]) -> None:
        snapshot = create_snapshot(sample_measurements)
        assert isinstance(snapshot, LatencySnapshot)
        latencies = [
            m.latency_ms if m.latency_ms is not None else float("inf")
            for m in snapshot.measurements
        ]
        assert latencies == sorted(latencies)

    def test_snapshot_has_vendor_summaries(self, sample_measurements: list[LatencyMeasurement]) -> None:
        snapshot = create_snapshot(sample_measurements)
        assert len(snapshot.vendor_summaries) == 3

    def test_snapshot_has_timestamp(self, sample_measurements: list[LatencyMeasurement]) -> None:
        snapshot = create_snapshot(sample_measurements)
        assert snapshot.measured_at is not None
        assert snapshot.measured_at.tzinfo is not None

    def test_empty_measurements_snapshot(self) -> None:
        snapshot = create_snapshot([])
        assert snapshot.measurements == []
        assert snapshot.vendor_summaries == []


class TestRunMeasurementCycle:
    """Test a single measurement cycle."""

    @pytest.mark.asyncio
    async def test_cycle_produces_snapshot(self, sample_regions: list[CloudRegion], sample_measurements: list[LatencyMeasurement]) -> None:
        with patch("cloudlatency.engine.scheduler.probe_all_regions", new_callable=AsyncMock, return_value=sample_measurements):
            snapshot = await run_measurement_cycle(sample_regions, timeout=5)
        assert isinstance(snapshot, LatencySnapshot)
        assert len(snapshot.measurements) == 4

    @pytest.mark.asyncio
    async def test_cycle_handles_empty_regions(self) -> None:
        snapshot = await run_measurement_cycle([], timeout=5)
        assert snapshot.measurements == []

    @pytest.mark.asyncio
    async def test_cycle_error_returns_empty_snapshot(self, sample_regions: list[CloudRegion]) -> None:
        with patch("cloudlatency.engine.scheduler.probe_all_regions", new_callable=AsyncMock, side_effect=Exception("network error")):
            snapshot = await run_measurement_cycle(sample_regions, timeout=5)
        assert snapshot.measurements == []
