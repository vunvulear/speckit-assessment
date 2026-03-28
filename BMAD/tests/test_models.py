"""Tests for data models."""

from datetime import datetime, timezone

from cloudlatency.models import LatencyResult, Status


class TestStatus:
    """Tests for Status enum."""

    def test_ok_value(self):
        assert Status.OK.value == "ok"

    def test_unreachable_value(self):
        assert Status.UNREACHABLE.value == "unreachable"

    def test_error_value(self):
        assert Status.ERROR.value == "error"


class TestLatencyResult:
    """Tests for LatencyResult dataclass."""

    def test_create_ok_result(self):
        r = LatencyResult(provider="aws", region="us-east-1", latency_ms=42.5, status=Status.OK)
        assert r.provider == "aws"
        assert r.region == "us-east-1"
        assert r.latency_ms == 42.5
        assert r.status == Status.OK
        assert isinstance(r.timestamp, datetime)

    def test_create_unreachable_result(self):
        r = LatencyResult(provider="azure", region="westus", latency_ms=None, status=Status.UNREACHABLE)
        assert r.latency_ms is None
        assert r.status == Status.UNREACHABLE

    def test_timestamp_defaults_to_utc(self):
        r = LatencyResult(provider="gcp", region="us-central1", latency_ms=10.0, status=Status.OK)
        assert r.timestamp.tzinfo is not None

    def test_custom_timestamp(self):
        ts = datetime(2026, 1, 1, tzinfo=timezone.utc)
        r = LatencyResult(provider="aws", region="us-east-1", latency_ms=50.0, status=Status.OK, timestamp=ts)
        assert r.timestamp == ts

    def test_frozen(self):
        r = LatencyResult(provider="aws", region="us-east-1", latency_ms=42.5, status=Status.OK)
        try:
            r.latency_ms = 100.0  # type: ignore[misc]
            assert False, "Should have raised"
        except AttributeError:
            pass
