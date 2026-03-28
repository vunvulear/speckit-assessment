"""Tests for LatencyStore."""

from datetime import datetime, timezone

from cloudlatency.models import LatencyResult, Status
from cloudlatency.store import LatencyStore


def _make_result(
    provider: str = "aws", region: str = "us-east-1", latency_ms: float | None = 42.0, status: Status = Status.OK,
) -> LatencyResult:
    """Helper to create a LatencyResult with defaults."""
    return LatencyResult(
        provider=provider,
        region=region,
        latency_ms=latency_ms,
        status=status,
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


class TestStoreBasics:
    """Basic store operations."""

    def test_new_store_is_empty(self):
        store = LatencyStore()
        assert store.is_empty()
        assert store.count() == 0

    def test_update_all_stores_results(self):
        store = LatencyStore()
        results = [_make_result(region="us-east-1"), _make_result(region="us-west-2")]
        store.update_all(results)
        assert store.count() == 2
        assert not store.is_empty()

    def test_update_all_replaces_previous(self):
        store = LatencyStore()
        store.update_all([_make_result(region="us-east-1")])
        assert store.count() == 1
        store.update_all([_make_result(region="eu-west-1"), _make_result(region="eu-west-2")])
        assert store.count() == 2

    def test_update_all_empty_clears_store(self):
        store = LatencyStore()
        store.update_all([_make_result()])
        store.update_all([])
        assert store.is_empty()


class TestGetAllSorted:
    """Tests for get_all_sorted()."""

    def test_sorted_by_latency_ascending(self):
        store = LatencyStore()
        store.update_all([
            _make_result(region="slow", latency_ms=200.0),
            _make_result(region="fast", latency_ms=10.0),
            _make_result(region="mid", latency_ms=100.0),
        ])
        results = store.get_all_sorted()
        assert [r.region for r in results] == ["fast", "mid", "slow"]

    def test_unreachable_sorts_last(self):
        store = LatencyStore()
        store.update_all([
            _make_result(region="unreachable", latency_ms=None, status=Status.UNREACHABLE),
            _make_result(region="fast", latency_ms=10.0),
        ])
        results = store.get_all_sorted()
        assert results[0].region == "fast"
        assert results[1].region == "unreachable"

    def test_empty_store_returns_empty(self):
        store = LatencyStore()
        assert store.get_all_sorted() == []

    def test_multiple_unreachable_sort_together(self):
        store = LatencyStore()
        store.update_all([
            _make_result(region="ok", latency_ms=50.0),
            _make_result(region="down1", latency_ms=None, status=Status.UNREACHABLE),
            _make_result(region="down2", latency_ms=None, status=Status.ERROR),
        ])
        results = store.get_all_sorted()
        assert results[0].region == "ok"
        assert results[0].latency_ms == 50.0


class TestGetByProvider:
    """Tests for get_by_provider()."""

    def test_filters_by_provider(self):
        store = LatencyStore()
        store.update_all([
            _make_result(provider="aws", region="us-east-1", latency_ms=50.0),
            _make_result(provider="azure", region="westus", latency_ms=60.0),
            _make_result(provider="aws", region="us-west-2", latency_ms=40.0),
        ])
        aws_results = store.get_by_provider("aws")
        assert len(aws_results) == 2
        assert all(r.provider == "aws" for r in aws_results)

    def test_sorted_within_provider(self):
        store = LatencyStore()
        store.update_all([
            _make_result(provider="aws", region="slow", latency_ms=200.0),
            _make_result(provider="aws", region="fast", latency_ms=10.0),
        ])
        results = store.get_by_provider("aws")
        assert results[0].region == "fast"

    def test_unknown_provider_returns_empty(self):
        store = LatencyStore()
        store.update_all([_make_result(provider="aws")])
        assert store.get_by_provider("unknown") == []

    def test_empty_store_returns_empty(self):
        store = LatencyStore()
        assert store.get_by_provider("aws") == []


class TestGetSummary:
    """Tests for get_summary()."""

    def test_summary_with_multiple_providers(self):
        store = LatencyStore()
        store.update_all([
            _make_result(provider="aws", region="us-east-1", latency_ms=50.0),
            _make_result(provider="aws", region="us-west-2", latency_ms=100.0),
            _make_result(provider="azure", region="westus", latency_ms=30.0),
        ])
        summary = store.get_summary()
        assert "providers" in summary
        assert "aws" in summary["providers"]
        assert "azure" in summary["providers"]

        aws = summary["providers"]["aws"]
        assert aws["average_latency_ms"] == 75.0
        assert aws["closest_region"] == "us-east-1"
        assert aws["closest_latency_ms"] == 50.0
        assert aws["total_regions"] == 2
        assert aws["reachable_regions"] == 2

        azure = summary["providers"]["azure"]
        assert azure["average_latency_ms"] == 30.0
        assert azure["closest_region"] == "westus"

    def test_summary_with_unreachable_excluded_from_avg(self):
        store = LatencyStore()
        store.update_all([
            _make_result(provider="aws", region="ok", latency_ms=50.0),
            _make_result(provider="aws", region="down", latency_ms=None, status=Status.UNREACHABLE),
        ])
        summary = store.get_summary()
        aws = summary["providers"]["aws"]
        assert aws["average_latency_ms"] == 50.0
        assert aws["total_regions"] == 2
        assert aws["reachable_regions"] == 1

    def test_summary_all_unreachable(self):
        store = LatencyStore()
        store.update_all([
            _make_result(provider="aws", region="down", latency_ms=None, status=Status.UNREACHABLE),
        ])
        summary = store.get_summary()
        aws = summary["providers"]["aws"]
        assert aws["average_latency_ms"] is None
        assert aws["closest_region"] is None
        assert aws["closest_latency_ms"] is None
        assert aws["reachable_regions"] == 0

    def test_summary_empty_store(self):
        store = LatencyStore()
        summary = store.get_summary()
        assert summary == {"providers": {}}

    def test_summary_single_provider(self):
        store = LatencyStore()
        store.update_all([_make_result(provider="gcp", region="us-central1", latency_ms=25.0)])
        summary = store.get_summary()
        assert len(summary["providers"]) == 1
        assert "gcp" in summary["providers"]
        gcp = summary["providers"]["gcp"]
        assert gcp["closest_region"] == "us-central1"
        assert gcp["closest_latency_ms"] == 25.0
