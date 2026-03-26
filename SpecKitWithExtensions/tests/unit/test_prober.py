"""Unit tests for latency prober. @req FR-001 @req FR-008"""

import asyncio

import pytest
from aioresponses import aioresponses

from cloudlatency.engine.models import CloudRegion
from cloudlatency.engine.prober import probe_region, probe_all_regions


@pytest.fixture
def sample_regions() -> list[CloudRegion]:
    return [
        CloudRegion(
            provider_id="aws",
            region_code="us-east-1",
            region_name="US East (N. Virginia)",
            endpoint_url="https://ec2.us-east-1.amazonaws.com",
        ),
        CloudRegion(
            provider_id="azure",
            region_code="eastus",
            region_name="East US",
            endpoint_url="https://eastus.status.azure.com",
        ),
        CloudRegion(
            provider_id="gcp",
            region_code="us-central1",
            region_name="Iowa",
            endpoint_url="https://us-central1-run.googleapis.com",
        ),
    ]


class TestProbeRegion:
    """Test single region probing."""

    @pytest.mark.asyncio
    async def test_reachable_region_returns_measurement(self) -> None:
        region = CloudRegion(
            provider_id="aws",
            region_code="us-east-1",
            region_name="US East",
            endpoint_url="https://ec2.us-east-1.amazonaws.com",
        )
        with aioresponses() as mocked:
            mocked.head("https://ec2.us-east-1.amazonaws.com", status=200)
            measurement = await probe_region(region, timeout=5)
        assert measurement.is_reachable is True
        assert measurement.latency_ms is not None
        assert measurement.latency_ms >= 0
        assert measurement.provider_id == "aws"
        assert measurement.region_code == "us-east-1"

    @pytest.mark.asyncio
    async def test_unreachable_region_returns_null_latency(self) -> None:
        region = CloudRegion(
            provider_id="gcp",
            region_code="us-central1",
            region_name="Iowa",
            endpoint_url="https://us-central1-run.googleapis.com",
        )
        with aioresponses() as mocked:
            mocked.head("https://us-central1-run.googleapis.com", exception=asyncio.TimeoutError())
            measurement = await probe_region(region, timeout=5)
        assert measurement.is_reachable is False
        assert measurement.latency_ms is None

    @pytest.mark.asyncio
    async def test_server_error_still_measures_latency(self) -> None:
        region = CloudRegion(
            provider_id="aws",
            region_code="us-east-1",
            region_name="US East",
            endpoint_url="https://ec2.us-east-1.amazonaws.com",
        )
        with aioresponses() as mocked:
            mocked.head("https://ec2.us-east-1.amazonaws.com", status=403)
            measurement = await probe_region(region, timeout=5)
        # Even non-200 status means the server responded — it's reachable
        assert measurement.is_reachable is True
        assert measurement.latency_ms is not None

    @pytest.mark.asyncio
    async def test_connection_error_marks_unreachable(self) -> None:
        region = CloudRegion(
            provider_id="aws",
            region_code="us-east-1",
            region_name="US East",
            endpoint_url="https://ec2.us-east-1.amazonaws.com",
        )
        with aioresponses() as mocked:
            mocked.head("https://ec2.us-east-1.amazonaws.com", exception=ConnectionError("refused"))
            measurement = await probe_region(region, timeout=5)
        assert measurement.is_reachable is False
        assert measurement.latency_ms is None


class TestProbeAllRegions:
    """Test concurrent probing of multiple regions."""

    @pytest.mark.asyncio
    async def test_probes_all_regions_concurrently(self, sample_regions: list[CloudRegion]) -> None:
        with aioresponses() as mocked:
            for r in sample_regions:
                mocked.head(r.endpoint_url, status=200)
            measurements = await probe_all_regions(sample_regions, timeout=5)
        assert len(measurements) == 3
        providers = {m.provider_id for m in measurements}
        assert providers == {"aws", "azure", "gcp"}

    @pytest.mark.asyncio
    async def test_mixed_reachable_and_unreachable(self, sample_regions: list[CloudRegion]) -> None:
        with aioresponses() as mocked:
            mocked.head(sample_regions[0].endpoint_url, status=200)
            mocked.head(sample_regions[1].endpoint_url, exception=asyncio.TimeoutError())
            mocked.head(sample_regions[2].endpoint_url, status=200)
            measurements = await probe_all_regions(sample_regions, timeout=5)
        reachable = [m for m in measurements if m.is_reachable]
        unreachable = [m for m in measurements if not m.is_reachable]
        assert len(reachable) == 2
        assert len(unreachable) == 1

    @pytest.mark.asyncio
    async def test_empty_regions_returns_empty(self) -> None:
        measurements = await probe_all_regions([], timeout=5)
        assert measurements == []

    @pytest.mark.asyncio
    async def test_measurements_include_region_metadata(self, sample_regions: list[CloudRegion]) -> None:
        with aioresponses() as mocked:
            for r in sample_regions:
                mocked.head(r.endpoint_url, status=200)
            measurements = await probe_all_regions(sample_regions, timeout=5)
        for m in measurements:
            assert m.region_name != ""
            assert m.region_code != ""
