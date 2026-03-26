# Research: Cloud Latency Monitor

**Branch**: `001-cloud-latency-monitor` | **Date**: 2026-03-26

## Cloud Provider Region Discovery

### Decision: Use provider-specific public JSON/API endpoints for dynamic region discovery

### Rationale
Each major cloud provider publishes machine-readable region metadata:
- **AWS**: `https://ip-ranges.amazonaws.com/ip-ranges.json` contains all regions. Additionally, EC2 endpoints follow a predictable pattern (`ec2.{region}.amazonaws.com`).
- **Azure**: `https://management.azure.com/providers/Microsoft.Network/locations?api-version=2023-09-01` or the published IP ranges JSON. Azure health endpoints follow patterns like `{region}.prod.warm.ingest.monitor.core.windows.net`.
- **GCP**: `https://www.gstatic.com/ipranges/cloud.json` lists all regions. Compute endpoints follow `compute.googleapis.com` with region metadata available via discovery API.

For latency probing, each provider has publicly accessible HTTPS endpoints per region that can be used for HEAD requests without authentication.

### Alternatives Considered
- **Static config file**: Simpler but requires manual updates when providers add regions. Rejected per user preference for dynamic discovery.
- **Cloud provider SDKs**: Would add heavy dependencies (boto3, azure-sdk, google-cloud). Rejected for simplicity — HTTP requests to public JSON endpoints suffice.

## HTTPS HEAD Latency Measurement

### Decision: Use `aiohttp` for concurrent async HTTPS HEAD requests

### Rationale
With 100+ regions to probe every 10 seconds, sequential measurement is infeasible. Python's `asyncio` with `aiohttp` enables concurrent HEAD requests with configurable timeouts. A 5-second timeout per request ensures the full measurement cycle completes well within 10 seconds.

### Alternatives Considered
- **`requests` with ThreadPoolExecutor**: Works but threads have higher overhead than async for I/O-bound tasks.
- **`httpx` async**: Viable alternative; `aiohttp` chosen for maturity and lower memory footprint at high concurrency.

## REST API Framework

### Decision: Use FastAPI

### Rationale
FastAPI is the leading Python web framework for building REST APIs. It provides:
- Native async support (critical for SSE streaming)
- Automatic OpenAPI documentation
- Pydantic data validation
- High performance on par with Node.js/Go frameworks
- SSE support via `sse-starlette` or native `StreamingResponse`

### Alternatives Considered
- **Flask**: Lacks native async support; would require additional libraries for SSE.
- **Django REST Framework**: Too heavyweight for this use case.

## Web UI Approach

### Decision: Server-rendered HTML with vanilla JavaScript and Chart.js

### Rationale
Aligns with the Simplicity principle. The UI is a single page with a table and two charts — no need for a heavy SPA framework. FastAPI can serve static HTML. Chart.js is lightweight, widely supported, and renders bar charts efficiently. EventSource API (native browser) handles SSE.

### Alternatives Considered
- **React/Vue SPA**: Overkill for a single-page dashboard. Adds build tooling complexity.
- **Plotly.js**: More powerful but heavier than needed for simple bar charts.
- **D3.js**: Maximum flexibility but higher development effort for simple charts.

## SSE Implementation

### Decision: FastAPI `StreamingResponse` with `sse-starlette` package

### Rationale
`sse-starlette` integrates cleanly with FastAPI's async architecture. The server pushes JSON payloads on each measurement cycle. The browser's native `EventSource` API handles reconnection automatically if the connection drops.

### Alternatives Considered
- **WebSocket**: Full-duplex unnecessary; data flows one direction only (server → client).
- **Client polling**: Simpler but wastes bandwidth and introduces variable delay.

## Testing Strategy

### Decision: pytest with pytest-asyncio, pytest-cov, and aioresponses for mocking

### Rationale
- `pytest` is the de facto Python testing framework.
- `pytest-asyncio` enables testing async code (latency engine, SSE endpoints).
- `pytest-cov` enforces the 90% coverage gate.
- `aioresponses` mocks HTTP responses for deterministic latency engine tests.
- `pytest-httpx` or `httpx` TestClient for FastAPI endpoint testing.

### Alternatives Considered
- **unittest**: More verbose; pytest is more ergonomic and widely adopted.
