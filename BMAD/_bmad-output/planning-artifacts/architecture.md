---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments: [prd.md, ux-design-specification.md, product-brief-cloudlatency.md, product-brief-cloudlatency-distillate.md]
workflowType: 'architecture'
project_name: 'CloudLatency'
user_name: 'Rvunvulea'
date: '2026-03-28'
lastStep: 8
status: 'complete'
completedAt: '2026-03-28'
---

# Architecture Decision Document — CloudLatency

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements (29 total):**

- **Latency Measurement (FR1-FR7):** Async HTTPS probing of ~50+ cloud regions across 3 providers, concurrent within a 10s cycle. Core computational work — async I/O is the primary architectural concern.
- **Data Presentation — Table (FR8-FR11):** Sorted table with live updates via SSE. Pure frontend rendering, no server-side HTML.
- **Data Presentation — Summary (FR12-FR14):** Vendor averages and closest regions. UX design replaced charts with a summary banner — computed server-side and pushed via SSE.
- **Live Updates (FR15-FR17):** SSE push every 10s, auto-reconnect, connection status indicator.
- **REST API (FR18-FR22):** 5 endpoints (`/results`, `/results/{provider}`, `/summary`, `/health`, `/sse`). JSON-only, no auth, no rate limiting.
- **Application Lifecycle (FR23-FR26):** Single-command launch, 30s to first data, graceful shutdown.
- **Observability (FR27-FR29):** Structured logging, cycle success/failure counts, UI connection status.

**Non-Functional Requirements (21 total):**

- **Performance:** API < 200ms, probe cycle < 8s, UI render < 100ms, SSE delivery < 500ms, no memory leaks
- **Reliability:** Fault-isolated probes, auto-reconnect SSE, graceful shutdown < 3s
- **Compatibility:** Python 3.10+, cross-platform (Win/Mac/Linux), 4 browsers
- **Code Quality:** >90% coverage, CC ≤ 5, linter-enforced style, structured JSON logging
- **Accessibility:** Semantic HTML, WCAG AA contrast, keyboard-navigable table

**Scale & Complexity:**

- Complexity level: Low-medium
- Primary domain: Web App + API Backend Hybrid (Python)
- Estimated architectural components: ~5 (probe engine, data store, REST API, SSE broadcaster, static frontend)

### Technical Constraints & Dependencies

- **Python 3.10+** — language is fixed by PRD
- **Async I/O required** — 50+ concurrent HTTPS probes per cycle demands `asyncio` + `aiohttp`
- **No external databases** — in-memory state for MVP; SQLite deferred to Phase 2
- **No authentication** — local-only tool, no auth layer
- **No build tooling for frontend** — UX spec chose Tailwind CSS + vanilla JS; no React, no bundler
- **Single-process deployment** — `python -m cloudlatency` runs everything (web server + probe engine)
- **PyPI-distributable** — must be `pip install`-able

### Cross-Cutting Concerns Identified

1. **Async concurrency** — Probe engine runs on asyncio event loop; web server must share or coordinate with it
2. **Real-time data flow** — Probe results → in-memory store → SSE broadcast → browser render. This pipeline is the backbone.
3. **Error isolation** — One failed probe must not affect others; one disconnected SSE client must not affect the server
4. **Structured logging** — JSON-formatted logs across all components (NFR18)
5. **Testability** — >90% coverage requires clean component boundaries and dependency injection
6. **Cross-platform compatibility** — Must work on Windows, macOS, Linux without platform-specific code

## Starter Template Evaluation

### Primary Technology Domain

Python async web backend serving a static HTML/JS/CSS frontend. No frontend build tooling. No ORM. No auth. The framework choice determines the entire backend architecture.

### Starter Options Considered

| Framework | Version | SSE Support | Static Files | Async Native | Complexity |
| --------- | ------- | ----------- | ------------ | ------------ | ---------- |
| **aiohttp** | 3.13.3 | Built-in (`StreamResponse`) | Built-in | Yes (asyncio-native) | Low |
| **FastAPI** | 0.135.2 | Via `sse-starlette` | Via Starlette `StaticFiles` | Yes (ASGI) | Medium |
| **Starlette** | 0.46+ | Via `sse-starlette` | Built-in | Yes (ASGI) | Low-Medium |

### Selected Starter: aiohttp (manual project setup)

**Rationale:**

1. **Single dependency for both roles** — `aiohttp` is both the HTTP client (probing) and the HTTP server (API + static files + SSE). No other framework achieves this.
2. **Zero extra dependencies for SSE** — `StreamResponse` handles SSE natively
3. **Minimal abstraction** — For 5 endpoints, a full ASGI framework stack is overhead
4. **Aligned with PRD** — PRD mentions `aiohttp` for async probing; using it as the server too is the natural choice
5. **CC ≤ 5 friendly** — Simple routing, no decorators-within-decorators patterns

**Initialization Command:**

```bash
mkdir cloudlatency && cd cloudlatency
python -m venv .venv
pip install aiohttp>=3.13.0
```

**Architectural Decisions Provided by Starter:**

- **Language & Runtime:** Python 3.10+, asyncio event loop
- **HTTP Client:** `aiohttp.ClientSession` for probing
- **HTTP Server:** `aiohttp.web` for REST API + static files + SSE
- **No ASGI layer** — aiohttp runs its own server (`web.run_app`)
- **No auto-docs** — API documentation will be manual (5 endpoints don't warrant Swagger overhead)

**Technical Preferences Established:**

- **Testing:** pytest + pytest-asyncio + pytest-aiohttp (aiohttp's test client)
- **Linting:** ruff (fast Python linter, replaces flake8 + isort + black)
- **Complexity:** radon (CC measurement per PRD)
- **Coverage:** pytest-cov (>90% target)
- **Logging:** Python stdlib `logging` with JSON formatter
- **Frontend:** Tailwind CSS (CDN) + vanilla JS (no build step)

## Core Architectural Decisions

### Decision Priority Analysis

**Already Decided (by PRD + Starter):**

- Language: Python 3.10+
- Framework: aiohttp 3.13.3 (client + server)
- Frontend: Tailwind CSS CDN + vanilla JS
- Auth: None (local tool)
- Database: None (in-memory, MVP)

### Data Architecture

| Decision | Choice | Rationale |
| -------- | ------ | --------- |
| In-memory data store | Python dict behind a `LatencyStore` class | Simple, testable, no dependency. Stores latest measurement per region. |
| Data model | `LatencyResult` dataclass: `provider`, `region`, `latency_ms`, `status`, `timestamp` | Maps directly to PRD FR data schema. |
| Summary computation | Computed on read from store (not cached) | With ~50 regions, computing averages + min per vendor is O(n) where n≈50 — trivially fast. No caching needed. |
| Thread safety | Not needed — single asyncio event loop, no threads | aiohttp runs everything on one event loop. Store access is sequential within coroutines. |
| Phase 2 migration path | `LatencyStore` interface allows swap to SQLite-backed impl later | Abstract the store behind a protocol/ABC for future extensibility. |

### API & Communication

| Decision | Choice | Rationale |
| -------- | ------ | --------- |
| API style | REST, JSON-only | PRD requirement. 5 endpoints, no GraphQL complexity needed. |
| URL structure | `/api/v1/results`, `/api/v1/results/{provider}`, `/api/v1/summary`, `/api/v1/health`, `/api/v1/sse` | Directly from PRD endpoint spec. |
| Error format | `{"error": "message", "code": "ERROR_CODE"}` | PRD FR22 requires consistent JSON error format. |
| HTTP status codes | 200 (success), 404 (unknown provider), 500 (server error) | Standard REST. No 201/204 — all endpoints are GET-only. |
| SSE format | `data: {json}\n\n` with `event: measurement` | Standard SSE protocol. Single event type for MVP. |
| CORS | Allow `localhost:*` origins | PRD requirement for local development. |
| Content-Type | `application/json` for REST, `text/event-stream` for SSE, `text/html` for static | Standard MIME types. |

### Frontend Architecture

| Decision | Choice | Rationale |
| -------- | ------ | --------- |
| Rendering | Vanilla JS DOM manipulation | UX spec: no framework. Table rebuilt on each SSE event. |
| State management | None — SSE event IS the state | Each SSE event contains full measurement set. No client-side state accumulation. |
| Styling | Tailwind CSS via CDN (`<script src="...">`) | UX spec decision. No build step, no PostCSS, no purging. |
| JS modules | Single `<script>` tag, no ES modules | Simplicity. One file, ~200 lines of JS. No bundler. |
| SSE reconnect | `EventSource` built-in auto-reconnect | Browser-native. Add manual fallback with exponential backoff if `EventSource` fails. |

### Infrastructure & Deployment

| Decision | Choice | Rationale |
| -------- | ------ | --------- |
| Packaging | PyPI package via `pyproject.toml` + `setuptools` | PRD: `pip install cloudlatency`. |
| Entry point | `python -m cloudlatency` via `__main__.py` | PRD FR23: single-command launch. |
| Config | CLI args for port (default 8080), no config files | Zero-config per PRD. Port override is the only option. |
| Logging | Python `logging` module + `python-json-logger` for JSON output | NFR18: structured JSON logging. |
| CI/CD | GitHub Actions: lint (ruff) + test (pytest-cov) + complexity (radon) | NFR15-17: enforced quality gates. |
| Docker | Deferred to Phase 2 | PRD explicitly defers Docker to post-MVP. |

### Process Architecture

| Decision | Choice | Rationale |
| -------- | ------ | --------- |
| Probe scheduling | `asyncio.create_task` with 10s `asyncio.sleep` loop | Simple, reliable. Runs on same event loop as web server. |
| Probe execution | `asyncio.gather` with `return_exceptions=True` | All probes run concurrently. Failed probes return exception, not crash. (NFR7) |
| Probe timeout | 5s per probe (`aiohttp.ClientTimeout`) | Allows 8s cycle budget (NFR2) with margin. |
| SSE broadcast | Maintain `set` of `StreamResponse` objects; iterate and write on each cycle | Simple fan-out. Remove disconnected clients on write error. |
| Graceful shutdown | `aiohttp.web` signal handlers + cancel probe task | NFR11: shutdown < 3s. Cancel in-flight probes, close SSE connections. |

### Decision Impact Analysis

**Implementation Sequence:**

1. Project scaffolding (pyproject.toml, package structure)
2. Probe engine (regions config + aiohttp client + async gather)
3. In-memory store (LatencyStore class)
4. REST API endpoints (5 routes on aiohttp.web)
5. SSE broadcaster (StreamResponse fan-out)
6. Static frontend (HTML + JS + Tailwind)
7. CLI entry point (__main__.py)
8. Tests + CI

**Cross-Component Dependencies:**

- Probe engine → writes to → LatencyStore
- REST API → reads from → LatencyStore
- SSE broadcaster → triggered by → Probe engine completion
- Frontend → consumes → SSE + REST API

## Implementation Patterns & Consistency Rules

### Naming Patterns

**Python Code Naming:**

| Element | Convention | Example |
| ------- | ---------- | ------- |
| Modules | `snake_case.py` | `latency_store.py`, `probe_engine.py` |
| Classes | `PascalCase` | `LatencyStore`, `ProbeEngine`, `LatencyResult` |
| Functions | `snake_case` | `get_results`, `run_probe_cycle` |
| Variables | `snake_case` | `latency_ms`, `probe_timeout` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_PORT`, `PROBE_INTERVAL_SECONDS` |
| Dataclass fields | `snake_case` | `provider`, `region`, `latency_ms`, `status` |
| Private members | `_leading_underscore` | `_sse_clients`, `_probe_task` |

**API Naming:**

| Element | Convention | Example |
| ------- | ---------- | ------- |
| Endpoints | lowercase, plural nouns | `/api/v1/results`, `/api/v1/summary` |
| URL params | lowercase, singular | `/api/v1/results/{provider}` |
| JSON fields | `snake_case` | `latency_ms`, `provider`, `region` |
| Error codes | `UPPER_SNAKE_CASE` | `UNKNOWN_PROVIDER`, `INTERNAL_ERROR` |

**Frontend Naming:**

| Element | Convention | Example |
| ------- | ---------- | ------- |
| CSS classes | Tailwind utilities only (no custom classes) | `bg-surface`, `text-text-primary` |
| JS functions | `camelCase` | `renderTable`, `updateBanner`, `connectSSE` |
| JS variables | `camelCase` | `sseConnection`, `latencyData` |
| DOM IDs | `kebab-case` | `latency-table`, `summary-banner`, `connection-status` |
| CSS custom properties | `--kebab-case` | `--color-aws`, `--color-azure`, `--color-gcp` |

### Structure Patterns

**Module Organization:**

Each Python module has a single responsibility. No module exceeds ~200 lines.

| Module | Responsibility | Depends On |
| ------ | -------------- | ---------- |
| `regions.py` | Cloud region endpoint definitions | Nothing |
| `models.py` | `LatencyResult` dataclass + enums | Nothing |
| `store.py` | `LatencyStore` class (in-memory) | `models` |
| `probe.py` | Probe engine (async HTTP client) | `regions`, `models`, `store` |
| `api.py` | REST API route handlers | `store` |
| `sse.py` | SSE broadcaster | `store` |
| `app.py` | aiohttp app factory + startup/shutdown | All modules |
| `__main__.py` | CLI entry point | `app` |

**Test Organization:**

Tests in a parallel `tests/` directory, mirroring the module structure:

```text
tests/
├── conftest.py          # Shared fixtures (aiohttp test client, mock store)
├── test_models.py       # Dataclass tests
├── test_store.py        # LatencyStore tests
├── test_probe.py        # Probe engine tests (mocked HTTP)
├── test_api.py          # REST API endpoint tests
├── test_sse.py          # SSE broadcast tests
└── test_app.py          # Integration tests (app startup/shutdown)
```

### Format Patterns

**API Response Formats:**

Success response (all endpoints except SSE):

```json
{
  "results": [...],
  "timestamp": "2026-03-28T14:30:00Z"
}
```

Error response:

```json
{
  "error": "Provider 'foo' not found",
  "code": "UNKNOWN_PROVIDER"
}
```

SSE event format:

```text
event: measurement
data: {"results": [...], "summary": {...}, "timestamp": "..."}
```

**Date/Time Format:** ISO 8601 strings (`datetime.utcnow().isoformat() + "Z"`) everywhere — API, logs, SSE.

### Communication Patterns

**Data flow pattern (single direction):**

```text
ProbeEngine → LatencyStore → [REST API reads | SSE broadcast pushes]
```

- Probe engine writes to store after each cycle
- REST API reads from store on each request
- SSE broadcaster reads from store after probe engine signals completion
- Signal mechanism: `asyncio.Event` set by probe engine, awaited by SSE broadcaster

**Logging pattern:**

```python
logger.info("probe_cycle_complete", extra={"success": 48, "failed": 2, "duration_ms": 3200})
```

All log entries include: level, message, timestamp (auto), and structured `extra` fields. No `print()` statements anywhere.

### Process Patterns

**Error Handling:**

| Layer | Pattern |
| ----- | ------- |
| Probe (per-region) | `try/except` around each probe; failed probes return `LatencyResult(status="unreachable")` |
| Probe (cycle) | `asyncio.gather(return_exceptions=True)` — never crash the loop |
| API handler | `try/except` returning JSON error with appropriate HTTP status |
| SSE write | `try/except` on write; remove client from set on `ConnectionResetError` |
| App startup | Log and exit with clear message if port is in use |

**Dependency Injection (for testability):**

- `LatencyStore` is created in `app.py` and passed to all handlers via `app["store"]`
- `ProbeEngine` accepts store and aiohttp `ClientSession` as constructor args
- Tests inject mock store and mock HTTP responses

### Enforcement Guidelines

**All AI Agents MUST:**

1. Run `ruff check .` before committing — zero warnings allowed
2. Run `pytest --cov=cloudlatency --cov-fail-under=90` — must pass
3. Run `radon cc cloudlatency/ -a -nc` — no function above CC 5
4. Use `snake_case` for all Python identifiers (except classes)
5. Use `snake_case` for all JSON fields in API responses
6. Never use `print()` — always `logger.info/warning/error`
7. Never block the event loop — all I/O must be `async`

## Project Structure & Boundaries

### Complete Project Directory Structure

```text
cloudlatency/
├── README.md
├── LICENSE
├── pyproject.toml                # Package config, dependencies, entry points
├── .gitignore
├── .github/
│   └── workflows/
│       └── ci.yml                # ruff + pytest-cov + radon checks
├── src/
│   └── cloudlatency/
│       ├── __init__.py           # Package version
│       ├── __main__.py           # CLI entry point: python -m cloudlatency
│       ├── app.py                # aiohttp app factory, startup/shutdown hooks
│       ├── models.py             # LatencyResult dataclass, Status enum
│       ├── regions.py            # Cloud region endpoint definitions (Azure/AWS/GCP)
│       ├── store.py              # LatencyStore class (in-memory dict)
│       ├── probe.py              # ProbeEngine (async HTTP client, gather, scheduling)
│       ├── api.py                # REST API route handlers (/results, /summary, /health)
│       ├── sse.py                # SSE broadcaster (StreamResponse fan-out)
│       ├── logging_config.py     # JSON logging setup
│       └── static/
│           ├── index.html        # Single-page UI
│           ├── app.js            # Vanilla JS (SSE client, DOM rendering)
│           └── favicon.ico
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Shared fixtures (test client, mock store, mock HTTP)
│   ├── test_models.py
│   ├── test_store.py
│   ├── test_regions.py
│   ├── test_probe.py
│   ├── test_api.py
│   ├── test_sse.py
│   └── test_app.py              # Integration tests
└── docs/
    └── api.md                    # REST API documentation (5 endpoints)
```

### Architectural Boundaries

**API Boundaries:**

- All REST endpoints under `/api/v1/` — no other URL paths serve JSON
- Static files served from `/` (index.html) and `/static/` (JS, favicon)
- SSE stream at `/api/v1/sse` — same boundary as REST, different content-type
- No cross-origin requests except `localhost:*`

**Component Boundaries:**

| Component | Reads From | Writes To | Communicates Via |
| --------- | ---------- | --------- | ---------------- |
| `ProbeEngine` | `regions.py` | `LatencyStore` | Direct method call |
| `LatencyStore` | — | — | Read/write methods |
| `api.py` handlers | `LatencyStore` | HTTP response | `app["store"]` reference |
| `sse.py` broadcaster | `LatencyStore` | `StreamResponse` | `asyncio.Event` signal |
| `app.py` | All modules | — | aiohttp app lifecycle |
| `static/app.js` | SSE stream | DOM | `EventSource` API |

**Data Boundaries:**

- `LatencyStore` is the single source of truth — no other state exists
- Store is write-once-per-cycle (probe engine replaces all results atomically)
- API handlers are read-only — they never mutate the store
- Frontend has zero persistent state — each SSE event is the complete current state

### Requirements to Structure Mapping

**FR Category Mapping:**

| FR Category | Files |
| ----------- | ----- |
| Latency Measurement (FR1-FR7) | `regions.py`, `probe.py`, `models.py` |
| Data Presentation — Table (FR8-FR11) | `static/index.html`, `static/app.js` |
| Data Presentation — Summary (FR12-FR14) | `store.py` (computation), `static/app.js` (render) |
| Live Updates (FR15-FR17) | `sse.py`, `static/app.js` |
| REST API (FR18-FR22) | `api.py` |
| Application Lifecycle (FR23-FR26) | `__main__.py`, `app.py` |
| Observability (FR27-FR29) | `logging_config.py`, `probe.py`, `static/app.js` |

### Integration Points

**Internal Communication:**

```text
__main__.py → app.create_app() → aiohttp.web.run_app()
                ↓ on_startup
            ProbeEngine.start() → asyncio.create_task(probe_loop)
                ↓ every 10s
            probe_loop → gather(probe_region(...)) → store.update(results)
                ↓ asyncio.Event.set()
            sse_broadcaster → for client in clients: client.write(data)
```

**External Integrations:**

| External Service | Protocol | Timeout | Failure Mode |
| ---------------- | -------- | ------- | ------------ |
| Azure health endpoints | HTTPS GET | 5s | `status: "unreachable"` |
| AWS health endpoints | HTTPS GET | 5s | `status: "unreachable"` |
| GCP health endpoints | HTTPS GET | 5s | `status: "unreachable"` |
| Tailwind CSS CDN | HTTPS (browser) | Browser default | Unstyled but functional |

**Data Flow:**

```text
Cloud Endpoints → [HTTPS] → ProbeEngine → LatencyStore → REST API → [JSON] → API consumers
                                                       → SSE      → [SSE]  → Browser UI
```

### Development Workflow Integration

**Development Server:**

```bash
python -m cloudlatency --port 8080
```

No hot-reload — backend changes require restart, frontend changes require browser refresh.

**Build Process:**

```bash
python -m build                    # Build sdist + wheel
ruff check src/ tests/             # Lint
pytest --cov=cloudlatency --cov-fail-under=90  # Test + coverage
radon cc src/cloudlatency/ -a -nc  # Complexity check
```

**Deployment:** `pip install cloudlatency` from PyPI. No Docker, no cloud deploy for MVP.

## Architecture Validation

### Decision Compatibility Check

| Check | Status | Notes |
| ----- | ------ | ----- |
| aiohttp client + server on same event loop | Pass | Both use asyncio natively, no conflict |
| aiohttp StreamResponse for SSE | Pass | No extra dependency needed |
| Python 3.10+ compatibility | Pass | aiohttp 3.13.3 supports 3.10+ |
| Tailwind CDN + static file serving | Pass | aiohttp serves static dir, CDN loaded by browser |
| pytest-aiohttp test client | Pass | First-party integration, well-maintained |
| ruff + radon + pytest-cov | Pass | All Python-native, no version conflicts |
| pyproject.toml + setuptools | Pass | Standard Python packaging, `pip install` works |

### Functional Requirements Coverage

| FR | Covered By | Status |
| -- | ---------- | ------ |
| FR1-FR3 (Region discovery) | `regions.py` | Covered |
| FR4 (HTTPS measurement) | `probe.py` + `aiohttp.ClientSession` | Covered |
| FR5 (Concurrent probes) | `asyncio.gather` in `probe.py` | Covered |
| FR6 (10s auto-refresh) | `asyncio.sleep` loop in `probe.py` | Covered |
| FR7 (Unreachable detection) | `try/except` per probe, `status: "unreachable"` | Covered |
| FR8-FR10 (Sorted table) | `static/app.js` DOM rendering | Covered |
| FR11 (Auto-update table) | SSE event handler re-renders | Covered |
| FR12-FR13 (Summary data) | `store.py` computes averages + closest | Covered |
| FR14 (Auto-update summary) | SSE event includes summary payload | Covered |
| FR15 (SSE push) | `sse.py` StreamResponse broadcast | Covered |
| FR16 (SSE reconnect) | `EventSource` auto-reconnect + JS fallback | Covered |
| FR17 (Connection status) | `static/app.js` UI indicator | Covered |
| FR18-FR22 (REST API) | `api.py` route handlers | Covered |
| FR23 (Single command) | `__main__.py` | Covered |
| FR24 (30s to first data) | Probe cycle starts on `on_startup` | Covered |
| FR25 (Graceful shutdown) | aiohttp signal handlers | Covered |
| FR26-FR29 (Logging/observability) | `logging_config.py` + structured extras | Covered |

### Non-Functional Requirements Coverage

| NFR | Architecture Support | Status |
| --- | -------------------- | ------ |
| NFR1 (API < 200ms) | In-memory store, no DB query | Covered |
| NFR2 (Cycle < 8s) | 5s timeout + gather parallelism | Covered |
| NFR3 (UI render < 100ms) | Vanilla JS, ~50 rows, no framework overhead | Covered |
| NFR4 (FMP < 2s) | Static HTML, CDN CSS, minimal JS | Covered |
| NFR5 (SSE < 500ms) | Direct write to StreamResponse after store update | Covered |
| NFR6 (No memory leaks) | No accumulation, store overwrites, SSE clients cleaned | Covered |
| NFR7-NFR8 (Fault isolation) | `return_exceptions=True`, per-probe try/except | Covered |
| NFR9 (SSE reconnect < 5s) | EventSource default + manual fallback | Covered |
| NFR10 (Network change) | aiohttp handles socket errors gracefully | Covered |
| NFR11 (Shutdown < 3s) | Cancel probe task, close SSE connections | Covered |
| NFR12 (Python 3.10+ cross-platform) | No platform-specific code | Covered |
| NFR13 (4 browsers) | Standard HTML/JS/CSS, no exotic APIs | Covered |
| NFR14 (Valid JSON) | `aiohttp.web.json_response` | Covered |
| NFR15-NFR17 (Quality gates) | CI pipeline: ruff + pytest-cov + radon | Covered |
| NFR18 (Structured logging) | python-json-logger | Covered |
| NFR19-NFR21 (Accessibility) | Semantic HTML table, Tailwind contrast, keyboard nav | Covered |

### Gap Analysis

| Potential Gap | Assessment | Resolution |
| ------------- | ---------- | ---------- |
| No API versioning beyond URL path | Acceptable for v1 local tool | URL versioning sufficient |
| No rate limiting | PRD explicitly says none for v1 | N/A |
| No auth | PRD explicitly says none for v1 | N/A |
| No database migration path defined | Phase 2 concern | `LatencyStore` ABC enables swap |
| CDN dependency for Tailwind | Offline use would fail styling | Tool requires internet for probing anyway |

### Architecture Coherence Summary

**Strengths:**

- Single dependency (aiohttp) serves both client and server roles
- Clean unidirectional data flow: Probes → Store → [API | SSE] → Frontend
- Every FR and NFR has a clear owning module
- Testability built-in via dependency injection
- ~10 source files, each < 200 lines — entire codebase is comprehensible

**Risks Accepted:**

- No hot-reload for development (acceptable for tool of this size)
- No auto-generated API docs (5 endpoints, manual `docs/api.md` sufficient)
- Tailwind via CDN means no purging (larger CSS payload, but local tool)
