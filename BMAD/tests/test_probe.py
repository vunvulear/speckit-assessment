"""Tests for async probe engine."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cloudlatency.models import Status
from cloudlatency.probe import PROBE_INTERVAL_SECONDS, PROBE_TIMEOUT_SECONDS, probe_loop, probe_region, run_probe_cycle
from cloudlatency.regions import Region
from cloudlatency.store import LatencyStore


@pytest.fixture
def sample_region() -> Region:
    return Region(provider="aws", region_name="us-east-1", endpoint_url="https://example.com/")


@pytest.fixture
def sample_regions() -> list[Region]:
    return [
        Region(provider="aws", region_name="us-east-1", endpoint_url="https://example.com/1"),
        Region(provider="azure", region_name="westus", endpoint_url="https://example.com/2"),
        Region(provider="gcp", region_name="us-central1", endpoint_url="https://example.com/3"),
    ]


@pytest.fixture
def store() -> LatencyStore:
    return LatencyStore()


class TestProbeRegion:
    """Tests for probe_region()."""

    @pytest.mark.asyncio
    async def test_successful_probe_returns_ok(self, sample_region: Region):
        """A successful HTTP response returns status OK with latency."""
        mock_response = AsyncMock()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = AsyncMock(spec_set=["get"])
        mock_session.get = MagicMock(return_value=mock_response)

        result = await probe_region(mock_session, sample_region)

        assert result.status == Status.OK
        assert result.provider == "aws"
        assert result.region == "us-east-1"
        assert result.latency_ms is not None
        assert result.latency_ms >= 0

    @pytest.mark.asyncio
    async def test_timeout_returns_unreachable(self, sample_region: Region):
        """A timeout returns status UNREACHABLE with None latency."""
        mock_session = AsyncMock(spec_set=["get"])
        mock_session.get = MagicMock(side_effect=asyncio.TimeoutError())

        result = await probe_region(mock_session, sample_region)

        assert result.status == Status.UNREACHABLE
        assert result.latency_ms is None
        assert result.provider == "aws"
        assert result.region == "us-east-1"

    @pytest.mark.asyncio
    async def test_connection_error_returns_unreachable(self, sample_region: Region):
        """A connection error returns status UNREACHABLE."""
        mock_session = AsyncMock(spec_set=["get"])
        mock_session.get = MagicMock(side_effect=ConnectionError("refused"))

        result = await probe_region(mock_session, sample_region)

        assert result.status == Status.UNREACHABLE
        assert result.latency_ms is None

    @pytest.mark.asyncio
    async def test_generic_exception_returns_unreachable(self, sample_region: Region):
        """Any exception returns UNREACHABLE, never crashes."""
        mock_session = AsyncMock(spec_set=["get"])
        mock_session.get = MagicMock(side_effect=RuntimeError("unexpected"))

        result = await probe_region(mock_session, sample_region)

        assert result.status == Status.UNREACHABLE
        assert result.latency_ms is None


class TestProbeTimeout:
    """Tests for timeout configuration."""

    def test_timeout_constant_is_5_seconds(self):
        assert PROBE_TIMEOUT_SECONDS == 5


class TestRunProbeCycle:
    """Tests for run_probe_cycle()."""

    @pytest.mark.asyncio
    async def test_probes_all_regions(self, sample_regions: list[Region], store: LatencyStore):
        """All regions are probed and results stored."""
        mock_response = AsyncMock()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = AsyncMock(spec_set=["get"])
        mock_session.get = MagicMock(return_value=mock_response)

        results = await run_probe_cycle(mock_session, sample_regions, store)

        assert len(results) == 3
        assert store.count() == 3

    @pytest.mark.asyncio
    async def test_stores_results_in_store(self, sample_regions: list[Region], store: LatencyStore):
        """Results are stored in the LatencyStore."""
        mock_response = AsyncMock()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = AsyncMock(spec_set=["get"])
        mock_session.get = MagicMock(return_value=mock_response)

        await run_probe_cycle(mock_session, sample_regions, store)

        assert not store.is_empty()
        all_results = store.get_all_sorted()
        providers = {r.provider for r in all_results}
        assert providers == {"aws", "azure", "gcp"}

    @pytest.mark.asyncio
    async def test_sets_data_event(self, sample_regions: list[Region], store: LatencyStore):
        """data_event is set after cycle completes."""
        mock_response = AsyncMock()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = AsyncMock(spec_set=["get"])
        mock_session.get = MagicMock(return_value=mock_response)

        event = asyncio.Event()
        assert not event.is_set()

        await run_probe_cycle(mock_session, sample_regions, store, data_event=event)

        assert event.is_set()

    @pytest.mark.asyncio
    async def test_no_event_is_ok(self, sample_regions: list[Region], store: LatencyStore):
        """Passing None for data_event works without error."""
        mock_response = AsyncMock()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = AsyncMock(spec_set=["get"])
        mock_session.get = MagicMock(return_value=mock_response)

        results = await run_probe_cycle(mock_session, sample_regions, store, data_event=None)
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_mixed_success_and_failure(self, store: LatencyStore):
        """Some probes succeed, some fail — all results stored."""
        regions = [
            Region(provider="aws", region_name="ok", endpoint_url="https://ok.com/"),
            Region(provider="aws", region_name="fail", endpoint_url="https://fail.com/"),
        ]

        call_count = 0

        def mock_get(url, **kwargs):
            nonlocal call_count
            call_count += 1
            if "fail" in url:
                raise asyncio.TimeoutError()
            mock_resp = AsyncMock()
            mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
            mock_resp.__aexit__ = AsyncMock(return_value=False)
            return mock_resp

        mock_session = AsyncMock(spec_set=["get"])
        mock_session.get = MagicMock(side_effect=mock_get)

        results = await run_probe_cycle(mock_session, regions, store)

        assert len(results) == 2
        assert store.count() == 2
        statuses = {r.region: r.status for r in results}
        assert statuses["ok"] == Status.OK
        assert statuses["fail"] == Status.UNREACHABLE

    @pytest.mark.asyncio
    async def test_empty_regions_list(self, store: LatencyStore):
        """Empty region list completes without error."""
        mock_session = AsyncMock(spec_set=["get"])

        results = await run_probe_cycle(mock_session, [], store)

        assert results == []
        assert store.is_empty()

    @pytest.mark.asyncio
    async def test_returns_results_list(self, sample_regions: list[Region], store: LatencyStore):
        """run_probe_cycle returns the list of LatencyResult objects."""
        mock_response = AsyncMock()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = AsyncMock(spec_set=["get"])
        mock_session.get = MagicMock(return_value=mock_response)

        results = await run_probe_cycle(mock_session, sample_regions, store)

        assert all(hasattr(r, "provider") for r in results)
        assert all(hasattr(r, "latency_ms") for r in results)


class TestProbeInterval:
    """Tests for interval constant."""

    def test_interval_is_10_seconds(self):
        assert PROBE_INTERVAL_SECONDS == 10


class TestProbeLoop:
    """Tests for probe_loop()."""

    @pytest.mark.asyncio
    async def test_loop_runs_and_can_be_cancelled(self, sample_regions: list[Region], store: LatencyStore):
        """Loop runs at least one cycle then cancels cleanly."""
        mock_response = AsyncMock()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = AsyncMock(spec_set=["get"])
        mock_session.get = MagicMock(return_value=mock_response)

        task = asyncio.create_task(probe_loop(mock_session, sample_regions, store, interval=0.01))
        await asyncio.sleep(0.05)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

        assert not store.is_empty()

    @pytest.mark.asyncio
    async def test_loop_continues_after_cycle_error(self, store: LatencyStore):
        """Loop continues running even if a cycle raises an unexpected error."""
        call_count = 0

        async def mock_cycle(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("test error")

        with patch("cloudlatency.probe.run_probe_cycle", side_effect=mock_cycle):
            task = asyncio.create_task(probe_loop(AsyncMock(), [], store, interval=0.01))
            await asyncio.sleep(0.05)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task

        assert call_count >= 2

    @pytest.mark.asyncio
    async def test_loop_sets_data_event(self, sample_regions: list[Region], store: LatencyStore):
        """Loop signals data_event after each cycle."""
        mock_response = AsyncMock()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = AsyncMock(spec_set=["get"])
        mock_session.get = MagicMock(return_value=mock_response)

        event = asyncio.Event()
        task = asyncio.create_task(probe_loop(mock_session, sample_regions, store, data_event=event, interval=0.01))
        await asyncio.sleep(0.05)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

        assert event.is_set()
