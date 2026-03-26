"""Unit tests for Pydantic API response schemas. @req FR-003"""

from datetime import datetime, timezone

import pytest

from cloudlatency.api.schemas import (
    HealthResponse,
    LatencyResponse,
    RegionResponse,
    VendorSummaryResponse,
)


class TestRegionResponse:
    """Test RegionResponse schema."""

    def test_create_reachable_region(self) -> None:
        r = RegionResponse(
            provider_id="aws",
            region_code="us-east-1",
            region_name="US East (N. Virginia)",
            latency_ms=25.3,
            is_reachable=True,
        )
        assert r.provider_id == "aws"
        assert r.latency_ms == 25.3

    def test_create_unreachable_region(self) -> None:
        r = RegionResponse(
            provider_id="gcp",
            region_code="us-central1",
            region_name="Iowa",
            latency_ms=None,
            is_reachable=False,
        )
        assert r.latency_ms is None
        assert r.is_reachable is False

    def test_serialization(self) -> None:
        r = RegionResponse(
            provider_id="aws",
            region_code="us-east-1",
            region_name="US East",
            latency_ms=25.3,
            is_reachable=True,
        )
        data = r.model_dump()
        assert data["provider_id"] == "aws"
        assert data["latency_ms"] == 25.3

    def test_defaults(self) -> None:
        r = RegionResponse(
            provider_id="aws",
            region_code="us-east-1",
            region_name="US East",
        )
        assert r.latency_ms is None
        assert r.is_reachable is True
        assert r.provider_name == ""


class TestVendorSummaryResponse:
    """Test VendorSummaryResponse schema."""

    def test_create_summary(self) -> None:
        vs = VendorSummaryResponse(
            provider_id="aws",
            provider_name="AWS",
            average_latency_ms=73.0,
            closest_region_code="us-east-1",
            closest_region_name="US East",
            closest_latency_ms=25.3,
            total_regions=2,
            reachable_regions=2,
        )
        assert vs.average_latency_ms == 73.0

    def test_defaults(self) -> None:
        vs = VendorSummaryResponse(
            provider_id="aws",
            provider_name="AWS",
        )
        assert vs.average_latency_ms is None
        assert vs.total_regions == 0
        assert vs.reachable_regions == 0

    def test_serialization(self) -> None:
        vs = VendorSummaryResponse(
            provider_id="aws",
            provider_name="AWS",
            average_latency_ms=50.0,
            total_regions=3,
            reachable_regions=2,
        )
        data = vs.model_dump()
        assert data["average_latency_ms"] == 50.0
        assert data["total_regions"] == 3


class TestLatencyResponse:
    """Test LatencyResponse schema."""

    def test_create_response(self) -> None:
        now = datetime(2026, 3, 26, 12, 0, 0, tzinfo=timezone.utc)
        lr = LatencyResponse(
            measured_at=now,
            measurements=[
                RegionResponse(
                    provider_id="aws",
                    region_code="us-east-1",
                    region_name="US East",
                    latency_ms=25.0,
                    is_reachable=True,
                )
            ],
            vendor_summaries=[
                VendorSummaryResponse(
                    provider_id="aws",
                    provider_name="AWS",
                    average_latency_ms=25.0,
                    total_regions=1,
                    reachable_regions=1,
                )
            ],
        )
        assert len(lr.measurements) == 1
        assert len(lr.vendor_summaries) == 1

    def test_empty_defaults(self) -> None:
        now = datetime(2026, 3, 26, 12, 0, 0, tzinfo=timezone.utc)
        lr = LatencyResponse(measured_at=now)
        assert lr.measurements == []
        assert lr.vendor_summaries == []

    def test_serialization_roundtrip(self) -> None:
        now = datetime(2026, 3, 26, 12, 0, 0, tzinfo=timezone.utc)
        lr = LatencyResponse(measured_at=now)
        data = lr.model_dump()
        lr2 = LatencyResponse(**data)
        assert lr2.measured_at == now


class TestHealthResponse:
    """Test HealthResponse schema."""

    def test_defaults(self) -> None:
        h = HealthResponse()
        assert h.status == "ok"
        assert h.engine_running is False
        assert h.last_measurement is None
        assert h.regions_discovered == 0

    def test_running_engine(self) -> None:
        now = datetime(2026, 3, 26, 12, 0, 0, tzinfo=timezone.utc)
        h = HealthResponse(
            status="ok",
            engine_running=True,
            last_measurement=now,
            regions_discovered=150,
        )
        assert h.engine_running is True
        assert h.regions_discovered == 150

    def test_serialization(self) -> None:
        h = HealthResponse(status="starting", engine_running=False)
        data = h.model_dump()
        assert data["status"] == "starting"
