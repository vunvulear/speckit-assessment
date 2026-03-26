"""Unit tests for SSE streaming. @req FR-007"""

import asyncio
from datetime import datetime, timezone

import pytest

from cloudlatency.api.routes import set_engine_status, set_snapshot
from cloudlatency.api.sse import event_generator, snapshot_to_dict
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
def sample_snapshot() -> LatencySnapshot:
    now = datetime(2026, 3, 26, 12, 0, 0, tzinfo=timezone.utc)
    return LatencySnapshot(
        measured_at=now,
        measurements=[
            LatencyMeasurement(provider_id="aws", region_code="us-east-1", region_name="US East", latency_ms=25.0, is_reachable=True, measured_at=now),
            LatencyMeasurement(provider_id="gcp", region_code="us-central1", region_name="Iowa", latency_ms=None, is_reachable=False, measured_at=now),
        ],
        vendor_summaries=[
            VendorSummary(provider_id="aws", provider_name="AWS", average_latency_ms=25.0, closest_region_code="us-east-1", closest_region_name="US East", closest_latency_ms=25.0, total_regions=1, reachable_regions=1),
            VendorSummary(provider_id="gcp", provider_name="GCP", average_latency_ms=None, closest_region_code=None, closest_region_name=None, closest_latency_ms=None, total_regions=1, reachable_regions=0),
        ],
    )


class TestSnapshotToDict:
    """Test snapshot serialization for SSE."""

    def test_converts_snapshot_to_dict(self, sample_snapshot: LatencySnapshot) -> None:
        data = snapshot_to_dict(sample_snapshot)
        assert "measured_at" in data
        assert "measurements" in data
        assert "vendor_summaries" in data

    def test_measurements_serialized(self, sample_snapshot: LatencySnapshot) -> None:
        data = snapshot_to_dict(sample_snapshot)
        assert len(data["measurements"]) == 2
        m = data["measurements"][0]
        assert m["provider_id"] == "aws"
        assert m["latency_ms"] == 25.0
        assert m["is_reachable"] is True

    def test_unreachable_measurement(self, sample_snapshot: LatencySnapshot) -> None:
        data = snapshot_to_dict(sample_snapshot)
        gcp = next(m for m in data["measurements"] if m["provider_id"] == "gcp")
        assert gcp["latency_ms"] is None
        assert gcp["is_reachable"] is False

    def test_vendor_summaries_serialized(self, sample_snapshot: LatencySnapshot) -> None:
        data = snapshot_to_dict(sample_snapshot)
        assert len(data["vendor_summaries"]) == 2
        aws = next(vs for vs in data["vendor_summaries"] if vs["provider_id"] == "aws")
        assert aws["average_latency_ms"] == 25.0
        assert aws["closest_region_code"] == "us-east-1"

    def test_all_values_json_serializable(self, sample_snapshot: LatencySnapshot) -> None:
        """Ensure the dict can be JSON-serialized without errors."""
        import json
        data = snapshot_to_dict(sample_snapshot)
        result = json.dumps(data)
        assert isinstance(result, str)


class TestEventGenerator:
    """Test SSE event generator."""

    @pytest.mark.asyncio
    async def test_emits_event_when_snapshot_set(self, sample_snapshot: LatencySnapshot) -> None:
        set_snapshot(sample_snapshot)
        gen = event_generator()
        event = await asyncio.wait_for(gen.__anext__(), timeout=3)
        assert event["event"] == "latency_update"
        assert "data" in event
        import json
        data = json.loads(event["data"])
        assert "measurements" in data
        assert "vendor_summaries" in data
        await gen.aclose()

    @pytest.mark.asyncio
    async def test_skips_when_no_snapshot(self) -> None:
        """Generator should not emit when snapshot is None."""
        gen = event_generator()
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(gen.__anext__(), timeout=1.5)
        await gen.aclose()

    @pytest.mark.asyncio
    async def test_skips_duplicate_timestamp(self, sample_snapshot: LatencySnapshot) -> None:
        """Generator should not re-emit the same snapshot."""
        set_snapshot(sample_snapshot)
        gen = event_generator()
        # First event
        event1 = await asyncio.wait_for(gen.__anext__(), timeout=3)
        assert event1["event"] == "latency_update"
        # Second call should not emit (same timestamp)
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(gen.__anext__(), timeout=1.5)
        await gen.aclose()
