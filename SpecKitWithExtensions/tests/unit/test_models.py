"""Unit tests for engine data models. @req FR-001"""

from datetime import datetime, timezone

import pytest

from cloudlatency.engine.models import (
    CloudProvider,
    CloudRegion,
    LatencyMeasurement,
    LatencySnapshot,
    VendorSummary,
)


class TestCloudProvider:
    """Test CloudProvider dataclass."""

    def test_create_provider(self) -> None:
        p = CloudProvider(id="aws", name="AWS")
        assert p.id == "aws"
        assert p.name == "AWS"

    def test_provider_is_frozen(self) -> None:
        p = CloudProvider(id="aws", name="AWS")
        with pytest.raises(AttributeError):
            p.id = "gcp"  # type: ignore[misc]

    def test_provider_equality(self) -> None:
        p1 = CloudProvider(id="aws", name="AWS")
        p2 = CloudProvider(id="aws", name="AWS")
        assert p1 == p2


class TestCloudRegion:
    """Test CloudRegion dataclass."""

    def test_create_region(self) -> None:
        r = CloudRegion(
            provider_id="aws",
            region_code="us-east-1",
            region_name="US East (N. Virginia)",
            endpoint_url="https://ec2.us-east-1.amazonaws.com",
        )
        assert r.provider_id == "aws"
        assert r.region_code == "us-east-1"
        assert r.region_name == "US East (N. Virginia)"
        assert r.endpoint_url == "https://ec2.us-east-1.amazonaws.com"

    def test_region_is_frozen(self) -> None:
        r = CloudRegion(
            provider_id="aws",
            region_code="us-east-1",
            region_name="US East",
            endpoint_url="https://example.com",
        )
        with pytest.raises(AttributeError):
            r.region_code = "eu-west-1"  # type: ignore[misc]


class TestLatencyMeasurement:
    """Test LatencyMeasurement dataclass."""

    def test_create_reachable_measurement(self) -> None:
        now = datetime(2026, 3, 26, 12, 0, 0, tzinfo=timezone.utc)
        m = LatencyMeasurement(
            provider_id="aws",
            region_code="us-east-1",
            latency_ms=25.3,
            is_reachable=True,
            measured_at=now,
        )
        assert m.latency_ms == 25.3
        assert m.is_reachable is True

    def test_create_unreachable_measurement(self) -> None:
        m = LatencyMeasurement(
            provider_id="gcp",
            region_code="us-central1",
            latency_ms=None,
            is_reachable=False,
        )
        assert m.latency_ms is None
        assert m.is_reachable is False

    def test_measurement_has_default_timestamp(self) -> None:
        m = LatencyMeasurement(
            provider_id="aws",
            region_code="us-east-1",
            latency_ms=10.0,
            is_reachable=True,
        )
        assert m.measured_at is not None
        assert m.measured_at.tzinfo is not None

    def test_measurement_default_region_name(self) -> None:
        m = LatencyMeasurement(
            provider_id="aws",
            region_code="us-east-1",
            latency_ms=10.0,
            is_reachable=True,
        )
        assert m.region_name == ""


class TestVendorSummary:
    """Test VendorSummary dataclass."""

    def test_create_summary_with_data(self) -> None:
        vs = VendorSummary(
            provider_id="aws",
            provider_name="AWS",
            average_latency_ms=73.0,
            closest_region_code="us-east-1",
            closest_region_name="US East (N. Virginia)",
            closest_latency_ms=25.3,
            total_regions=2,
            reachable_regions=2,
        )
        assert vs.average_latency_ms == 73.0
        assert vs.closest_region_code == "us-east-1"
        assert vs.total_regions == 2

    def test_create_summary_all_unreachable(self) -> None:
        vs = VendorSummary(
            provider_id="gcp",
            provider_name="GCP",
            average_latency_ms=None,
            closest_region_code=None,
            closest_region_name=None,
            closest_latency_ms=None,
            total_regions=1,
            reachable_regions=0,
        )
        assert vs.average_latency_ms is None
        assert vs.reachable_regions == 0


class TestLatencySnapshot:
    """Test LatencySnapshot dataclass."""

    def test_create_empty_snapshot(self) -> None:
        now = datetime(2026, 3, 26, 12, 0, 0, tzinfo=timezone.utc)
        snap = LatencySnapshot(measured_at=now)
        assert snap.measurements == []
        assert snap.vendor_summaries == []

    def test_create_snapshot_with_data(self, mock_snapshot: LatencySnapshot) -> None:
        assert len(mock_snapshot.measurements) == 4
        assert len(mock_snapshot.vendor_summaries) == 3

    def test_snapshot_measurements_sorted(self, mock_snapshot: LatencySnapshot) -> None:
        latencies = [
            m.latency_ms if m.latency_ms is not None else float("inf")
            for m in mock_snapshot.measurements
        ]
        assert latencies == sorted(latencies)
