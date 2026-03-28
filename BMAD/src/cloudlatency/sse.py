"""SSE broadcaster for pushing measurement data to connected clients."""

from __future__ import annotations

import asyncio
import json
import logging

from aiohttp import web

from cloudlatency.store import LatencyStore

logger = logging.getLogger(__name__)


class SSEBroadcaster:
    """Manages SSE client connections and broadcasts store data on events."""

    def __init__(self, store: LatencyStore, data_event: asyncio.Event) -> None:
        self._store = store
        self._data_event = data_event
        self._clients: set[web.StreamResponse] = set()

    @property
    def client_count(self) -> int:
        """Number of currently connected SSE clients."""
        return len(self._clients)

    def _serialize_results(self) -> str:
        """Serialize current store data as a JSON string for SSE."""
        results = self._store.get_all_sorted()
        data = [
            {
                "provider": r.provider,
                "region": r.region,
                "latency_ms": r.latency_ms,
                "status": r.status.value,
                "timestamp": r.timestamp.isoformat(),
            }
            for r in results
        ]
        return json.dumps({"results": data, "summary": self._store.get_summary()})

    async def add_client(self, response: web.StreamResponse) -> None:
        """Register a new SSE client connection."""
        self._clients.add(response)
        logger.info("sse_client_connected", extra={"client_count": self.client_count})

    async def remove_client(self, response: web.StreamResponse) -> None:
        """Unregister an SSE client connection."""
        self._clients.discard(response)
        logger.info("sse_client_disconnected", extra={"client_count": self.client_count})

    async def broadcast(self) -> None:
        """Send current store data to all connected clients."""
        payload = self._serialize_results()
        message = f"data: {payload}\n\n"
        dead_clients: list[web.StreamResponse] = []

        for client in self._clients:
            try:
                await client.write(message.encode("utf-8"))
            except (ConnectionResetError, ConnectionAbortedError, Exception):
                dead_clients.append(client)

        for client in dead_clients:
            await self.remove_client(client)

    async def run(self) -> None:
        """Wait for data events and broadcast to all clients indefinitely."""
        while True:
            await self._data_event.wait()
            self._data_event.clear()
            await self.broadcast()


async def sse_handler(request: web.Request) -> web.StreamResponse:
    """Handle an SSE connection from a browser client."""
    response = web.StreamResponse(
        status=200,
        reason="OK",
        headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
    await response.prepare(request)

    broadcaster: SSEBroadcaster = request.app["sse_broadcaster"]
    await broadcaster.add_client(response)

    try:
        while True:
            await asyncio.sleep(1)
            if response.task is None or response.task.done():
                break
    except (asyncio.CancelledError, ConnectionResetError):
        pass
    finally:
        await broadcaster.remove_client(response)

    return response
