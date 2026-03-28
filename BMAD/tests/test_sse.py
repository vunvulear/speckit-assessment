"""Tests for SSE broadcaster."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from cloudlatency.models import LatencyResult, Status
from cloudlatency.sse import SSEBroadcaster
from cloudlatency.store import LatencyStore


@pytest.fixture
def store_with_data() -> LatencyStore:
    store = LatencyStore()
    store.update_all([
        LatencyResult("aws", "us-east-1", 42.0, Status.OK, datetime(2026, 1, 1, tzinfo=timezone.utc)),
        LatencyResult("azure", "westus", None, Status.UNREACHABLE, datetime(2026, 1, 1, tzinfo=timezone.utc)),
    ])
    return store


@pytest.fixture
def empty_store() -> LatencyStore:
    return LatencyStore()


@pytest.fixture
def data_event() -> asyncio.Event:
    return asyncio.Event()


class TestSSEBroadcasterBasics:
    """Tests for SSEBroadcaster initialization and client management."""

    def test_initial_client_count_is_zero(self, empty_store: LatencyStore, data_event: asyncio.Event):
        broadcaster = SSEBroadcaster(empty_store, data_event)
        assert broadcaster.client_count == 0

    @pytest.mark.asyncio
    async def test_add_client_increments_count(self, empty_store: LatencyStore, data_event: asyncio.Event):
        broadcaster = SSEBroadcaster(empty_store, data_event)
        mock_response = MagicMock()
        await broadcaster.add_client(mock_response)
        assert broadcaster.client_count == 1

    @pytest.mark.asyncio
    async def test_remove_client_decrements_count(self, empty_store: LatencyStore, data_event: asyncio.Event):
        broadcaster = SSEBroadcaster(empty_store, data_event)
        mock_response = MagicMock()
        await broadcaster.add_client(mock_response)
        await broadcaster.remove_client(mock_response)
        assert broadcaster.client_count == 0

    @pytest.mark.asyncio
    async def test_remove_unknown_client_is_safe(self, empty_store: LatencyStore, data_event: asyncio.Event):
        broadcaster = SSEBroadcaster(empty_store, data_event)
        mock_response = MagicMock()
        await broadcaster.remove_client(mock_response)
        assert broadcaster.client_count == 0


class TestSSEBroadcast:
    """Tests for broadcast behavior."""

    @pytest.mark.asyncio
    async def test_broadcast_sends_to_all_clients(self, store_with_data: LatencyStore, data_event: asyncio.Event):
        broadcaster = SSEBroadcaster(store_with_data, data_event)
        client1 = AsyncMock()
        client2 = AsyncMock()
        await broadcaster.add_client(client1)
        await broadcaster.add_client(client2)

        await broadcaster.broadcast()

        client1.write.assert_awaited_once()
        client2.write.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_broadcast_sends_valid_sse_format(self, store_with_data: LatencyStore, data_event: asyncio.Event):
        broadcaster = SSEBroadcaster(store_with_data, data_event)
        client = AsyncMock()
        await broadcaster.add_client(client)

        await broadcaster.broadcast()

        sent_bytes = client.write.call_args[0][0]
        sent_str = sent_bytes.decode("utf-8")
        assert sent_str.startswith("data: ")
        assert sent_str.endswith("\n\n")

        payload = json.loads(sent_str.removeprefix("data: ").strip())
        assert "results" in payload
        assert "summary" in payload

    @pytest.mark.asyncio
    async def test_broadcast_cleans_up_dead_clients(self, store_with_data: LatencyStore, data_event: asyncio.Event):
        broadcaster = SSEBroadcaster(store_with_data, data_event)

        alive_client = AsyncMock()
        dead_client = AsyncMock()
        dead_client.write = AsyncMock(side_effect=ConnectionResetError())

        await broadcaster.add_client(alive_client)
        await broadcaster.add_client(dead_client)
        assert broadcaster.client_count == 2

        await broadcaster.broadcast()

        assert broadcaster.client_count == 1
        alive_client.write.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_broadcast_empty_store(self, empty_store: LatencyStore, data_event: asyncio.Event):
        broadcaster = SSEBroadcaster(empty_store, data_event)
        client = AsyncMock()
        await broadcaster.add_client(client)

        await broadcaster.broadcast()

        sent_bytes = client.write.call_args[0][0]
        payload = json.loads(sent_bytes.decode("utf-8").removeprefix("data: ").strip())
        assert payload["results"] == []

    @pytest.mark.asyncio
    async def test_broadcast_no_clients_is_safe(self, store_with_data: LatencyStore, data_event: asyncio.Event):
        broadcaster = SSEBroadcaster(store_with_data, data_event)
        await broadcaster.broadcast()


class TestSSEBroadcasterRun:
    """Tests for the run() loop."""

    @pytest.mark.asyncio
    async def test_run_waits_for_event_and_broadcasts(self, store_with_data: LatencyStore, data_event: asyncio.Event):
        broadcaster = SSEBroadcaster(store_with_data, data_event)
        client = AsyncMock()
        await broadcaster.add_client(client)

        task = asyncio.create_task(broadcaster.run())
        data_event.set()
        await asyncio.sleep(0.05)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

        client.write.assert_awaited()


class TestSerializeResults:
    """Tests for result serialization."""

    def test_serialize_includes_all_fields(self, store_with_data: LatencyStore, data_event: asyncio.Event):
        broadcaster = SSEBroadcaster(store_with_data, data_event)
        json_str = broadcaster._serialize_results()
        data = json.loads(json_str)

        assert len(data["results"]) == 2
        result = data["results"][0]
        assert "provider" in result
        assert "region" in result
        assert "latency_ms" in result
        assert "status" in result
        assert "timestamp" in result


class TestSSEHandler:
    """Integration tests for sse_handler via aiohttp test client."""

    @pytest.mark.asyncio
    async def test_sse_endpoint_returns_event_stream(self, store_with_data: LatencyStore, data_event: asyncio.Event):
        """SSE endpoint returns correct content type."""
        from aiohttp import web
        from aiohttp.test_utils import TestClient, TestServer

        from cloudlatency.sse import sse_handler

        app = web.Application()
        broadcaster = SSEBroadcaster(store_with_data, data_event)
        app["sse_broadcaster"] = broadcaster
        app.router.add_get("/api/v1/sse", sse_handler)

        async with TestClient(TestServer(app)) as client:
            async with client.get("/api/v1/sse") as resp:
                assert resp.status == 200
                assert resp.headers["Content-Type"] == "text/event-stream"
                # Close immediately after checking headers
                resp.close()
