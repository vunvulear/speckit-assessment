"""Shared test fixtures for CloudLatency tests."""

from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient

from cloudlatency.api.app import create_app
from cloudlatency.engine.models import (
    CloudProvider,
    CloudRegion,
    LatencyMeasurement,
    LatencySnapshot,
    VendorSummary,
)


@pytest.fixture
def mock_providers() -> list[CloudProvider]:
    """Sample cloud providers."""
    return [
        CloudProvider(id="aws", name="AWS"),
        CloudProvider(id="azure", name="Azure"),
        CloudProvider(id="gcp", name="GCP"),
    ]


@pytest.fixture
def mock_regions() -> list[CloudRegion]:
    """Sample cloud regions."""
    return [
        CloudRegion(
            provider_id="aws",
            region_code="us-east-1",
            region_name="US East (N. Virginia)",
            endpoint_url="https://ec2.us-east-1.amazonaws.com",
        ),
        CloudRegion(
            provider_id="aws",
            region_code="eu-west-1",
            region_name="EU (Ireland)",
            endpoint_url="https://ec2.eu-west-1.amazonaws.com",
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


@pytest.fixture
def mock_measurements() -> list[LatencyMeasurement]:
    """Sample latency measurements."""
    now = datetime(2026, 3, 26, 12, 0, 0, tzinfo=timezone.utc)
    return [
        LatencyMeasurement(
            provider_id="aws",
            region_code="us-east-1",
            region_name="US East (N. Virginia)",
            latency_ms=25.3,
            is_reachable=True,
            measured_at=now,
        ),
        LatencyMeasurement(
            provider_id="aws",
            region_code="eu-west-1",
            region_name="EU (Ireland)",
            latency_ms=120.7,
            is_reachable=True,
            measured_at=now,
        ),
        LatencyMeasurement(
            provider_id="azure",
            region_code="eastus",
            region_name="East US",
            latency_ms=30.1,
            is_reachable=True,
            measured_at=now,
        ),
        LatencyMeasurement(
            provider_id="gcp",
            region_code="us-central1",
            region_name="Iowa",
            latency_ms=None,
            is_reachable=False,
            measured_at=now,
        ),
    ]


@pytest.fixture
def mock_vendor_summaries() -> list[VendorSummary]:
    """Sample vendor summaries."""
    return [
        VendorSummary(
            provider_id="aws",
            provider_name="AWS",
            average_latency_ms=73.0,
            closest_region_code="us-east-1",
            closest_region_name="US East (N. Virginia)",
            closest_latency_ms=25.3,
            total_regions=2,
            reachable_regions=2,
        ),
        VendorSummary(
            provider_id="azure",
            provider_name="Azure",
            average_latency_ms=30.1,
            closest_region_code="eastus",
            closest_region_name="East US",
            closest_latency_ms=30.1,
            total_regions=1,
            reachable_regions=1,
        ),
        VendorSummary(
            provider_id="gcp",
            provider_name="GCP",
            average_latency_ms=None,
            closest_region_code=None,
            closest_region_name=None,
            closest_latency_ms=None,
            total_regions=1,
            reachable_regions=0,
        ),
    ]


@pytest.fixture
def mock_snapshot(
    mock_measurements: list[LatencyMeasurement],
    mock_vendor_summaries: list[VendorSummary],
) -> LatencySnapshot:
    """Sample complete latency snapshot."""
    return LatencySnapshot(
        measured_at=datetime(2026, 3, 26, 12, 0, 0, tzinfo=timezone.utc),
        measurements=sorted(
            mock_measurements,
            key=lambda m: m.latency_ms if m.latency_ms is not None else float("inf"),
        ),
        vendor_summaries=mock_vendor_summaries,
    )


@pytest.fixture
def app():
    """Create a test FastAPI app instance."""
    return create_app()


@pytest.fixture
async def client(app):
    """Async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
