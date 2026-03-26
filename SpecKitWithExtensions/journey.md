# CloudLatency — Development Journey

This document captures the full development journey of the CloudLatency project, from initial setup through implementation and the Azure discovery fix.

---

## Phase 0: DocGuard Setup & Canonical Docs

- Initialized DocGuard CDD compliance infrastructure
- Created canonical documentation: ARCHITECTURE.md, DATA-MODEL.md, SECURITY.md, TEST-SPEC.md, ENVIRONMENT.md
- Created AGENTS.md (AI agent instructions, standard-compliant)
- Initial DocGuard score: **4/100 (F)** → improved to **75/100 (B)** after docs
- ALCOA+ compliance: **9/9 attributes**

---

## Phase 1: Setup (T001–T007)

- Created project directory structure: `cloudlatency/`, `cloudlatency/engine/`, `cloudlatency/api/`, `cloudlatency/ui/static/`, `tests/`, `tests/unit/`, `tests/integration/`
- Created `pyproject.toml` with project metadata, pytest/ruff/black/coverage config
- Created `requirements.txt` (fastapi, uvicorn, aiohttp, sse-starlette, pydantic)
- Created `requirements-dev.txt` (pytest, pytest-asyncio, pytest-cov, aioresponses, httpx, ruff, black)
- Created all `__init__.py` files for packages
- Created LICENSE (MIT) and README.md

---

## Phase 2: Foundational (T008–T017)

- **config.py**: Application settings with environment variable overrides (HOST, PORT, MEASUREMENT_INTERVAL, REQUEST_TIMEOUT, LOG_LEVEL) using frozen dataclass
- **models.py**: Core engine data models — CloudProvider, CloudRegion, LatencyMeasurement, VendorSummary, LatencySnapshot (frozen dataclasses)
- **schemas.py**: Pydantic v2 response schemas — RegionResponse, VendorSummaryResponse, LatencyResponse, HealthResponse
- **logging_config.py**: Structured JSON logging with custom JSONFormatter
- **app.py**: FastAPI application factory with router inclusion and static file mounting
- **main.py**: Application entry point with uvicorn startup, engine init, and graceful shutdown
- **conftest.py**: Shared pytest fixtures for providers, regions, measurements, snapshots, FastAPI app, and async HTTP client
- **Tests**: Unit tests for config, models, and schemas — all passing

### Issue Encountered
- **aiohttp build failure on Windows ARM64**: Missing Microsoft C++ Build Tools
- **Fix**: Reinstalled aiohttp with `AIOHTTP_NO_EXTENSIONS=1` to force pure Python build

---

## Phase 3: User Story 1 — Latency Table (T018–T032)

### Tests Written First (Test-First Development)
- `test_discovery.py`: Region discovery for AWS, Azure, GCP (mock API responses, parse regions, handle failures)
- `test_prober.py`: Latency prober (mock HTTPS HEAD, measure latency, handle timeouts, concurrent probing)
- `test_scheduler.py`: Scheduler (cycle orchestration, snapshot creation, error handling)
- `test_routes.py`: API routes (GET /latency, /regions, /health, 503 when no data)
- `test_engine_api.py`: Integration test for engine-to-API data flow

### Implementation
- **discovery.py**: Region discovery for AWS (ip-ranges.amazonaws.com), Azure (Management API), GCP (gstatic.com cloud.json)
- **prober.py**: Async HTTPS HEAD latency prober with concurrent probing and timeout handling
- **scheduler.py**: Measurement scheduler — discovers regions once, probes every 10 seconds, builds VendorSummary aggregates
- **routes.py**: REST API routes — /api/v1/latency, /api/v1/regions, /api/v1/health with shared state management

### Web UI
- **index.html**: HTML structure with header, latency table, chart containers, status indicators
- **style.css**: Clean minimal design, responsive layout, provider color coding, alternating table rows
- **app.js**: Client-side rendering with SSE connection, Chart.js bar charts, table rendering, auto-reconnect

---

## Phase 4: User Story 2 — Average Latency Chart (T033–T038)

- Added Chart.js CDN link to index.html
- Implemented average latency bar chart in app.js (one bar per vendor, color-coded)
- Added canvas element and chart container to index.html
- Styled chart section in style.css (responsive width, proper sizing)

---

## Phase 5: User Story 3 — Closest Region Chart (T039–T042)

- Implemented closest-region bar chart in app.js (second Chart.js bar chart)
- Added canvas element for closest-region chart in index.html
- Styled second chart layout in style.css (consistent sizing with average chart)

---

## Phase 6: User Story 4 — SSE Updates (T043–T050)

- **sse.py**: SSE streaming endpoint with event generator, snapshot serialization, and FastAPI route
- Registered SSE route in app.py at `/api/v1/stream`
- Replaced polling with EventSource in app.js (connect to /api/v1/stream, parse events, update table + charts)
- Implemented last-updated timestamp display
- Implemented stale-data warning with auto-reconnect and tab refocus handling
- Added SSE connection logging (client connect/disconnect events)
- **test_sse.py**: Unit tests for snapshot serialization and event generator (emit, skip duplicate, skip null)

---

## Phase 7: Polish (T051–T056)

- **T051**: Added global error handling middleware in app.py (exception handler, structured error JSON response, logging)
- **T052**: FastAPI auto-generates OpenAPI docs at /docs (built-in)
- **T053**: Ran ruff lint (fixed F841 unused vars, E501 long lines) and black formatting (4 files reformatted)
- **T054**: Final test suite — **98 tests passing, 91.42% coverage** (threshold: 90%)
- **T055**: Updated CHANGELOG.md with all implementation phases
- **T056**: Created `.env.example` for environment documentation

### DocGuard Score Progression
| Checkpoint | Score | Grade |
|-----------|-------|-------|
| Initial (no docs) | 4/100 | F |
| After canonical docs | 75/100 | B |
| After implementation | 84/100 | A |
| After .env.example | **88/100** | **A** |

---

## Feature 002: Fix Azure Region Discovery

### Problem
Azure regions were missing from the latency table. The Azure Management API (`management.azure.com`) requires an OAuth2 bearer token — without it, requests return HTTP 403.

### Spec Kit Workflow

Full Spec Kit workflow was followed for this fix:

1. **Specify**: Created `specs/002-fix-azure-discovery/spec.md` with 3 user stories, 8 functional requirements, 6 success criteria
2. **Research**: Created `research.md` analyzing 4 alternatives — chose hardcoded region list with Blob Storage endpoints
3. **Plan**: Created `plan.md` with root cause analysis, solution design, and risk assessment
4. **Data Model**: Created `data-model.md` defining the Azure Region Registry entity
5. **Tasks**: Created `tasks.md` with 14 tasks across 4 phases
6. **Checklist**: Created `checklists/requirements.md` — all items passing

### Solution
- Replaced `discover_azure_regions()` body with a hardcoded `AZURE_REGIONS` list of 59 GA Azure regions
- Probe endpoints use Azure Blob Storage: `https://<regioncode>.blob.core.windows.net`
- These are publicly accessible, respond to HTTPS HEAD (HTTP 400 without auth, but round-trip time is still valid)
- Logged drift in DRIFT-LOG.md (D-001)

### Test-First Approach
- Updated Azure discovery tests to validate hardcoded list (no HTTP mocking needed)
- Added tests for: ≥50 regions, correct provider_id, blob storage endpoints, known regions present, no duplicates
- Updated `discover_all_regions` tests since Azure is always available (hardcoded)

### Results After Fix

| Metric | Before Fix | After Fix |
|--------|-----------|-----------|
| Azure regions | 0 | **59** |
| Total regions | 89 | **148** |
| Reachable | 83 | **112** |
| Tests | 98 | **102** |
| Coverage | 91.42% | **92.24%** |
| DocGuard | 88/100 (A) | **88/100 (A)** |

---

## Final Project State

### Architecture
- **Engine Layer**: Region discovery (AWS API + Azure hardcoded + GCP API), async HTTPS HEAD prober, 10s measurement scheduler
- **API Layer**: FastAPI with REST endpoints (`/latency`, `/regions`, `/health`), SSE streaming (`/stream`), global error middleware, OpenAPI docs at `/docs`
- **Web UI**: Sorted latency table, average latency bar chart, closest region bar chart, SSE auto-refresh with reconnect — vanilla HTML/CSS/JS + Chart.js

### Key Files
| File | Purpose |
|------|---------|
| `cloudlatency/config.py` | Settings with env var overrides |
| `cloudlatency/logging_config.py` | JSON structured logging |
| `cloudlatency/main.py` | uvicorn entry point with engine lifecycle |
| `cloudlatency/engine/discovery.py` | AWS/Azure/GCP region discovery |
| `cloudlatency/engine/prober.py` | Async HTTPS HEAD latency prober |
| `cloudlatency/engine/scheduler.py` | 10s measurement loop, vendor summaries |
| `cloudlatency/api/app.py` | FastAPI factory with error middleware |
| `cloudlatency/api/routes.py` | REST endpoints |
| `cloudlatency/api/schemas.py` | Pydantic v2 response models |
| `cloudlatency/api/sse.py` | SSE streaming endpoint |
| `cloudlatency/ui/static/index.html` | Web UI structure |
| `cloudlatency/ui/static/style.css` | Web UI styling |
| `cloudlatency/ui/static/app.js` | Client-side JS (charts, SSE, table) |

### Test Files
| File | Coverage Area |
|------|--------------|
| `tests/unit/test_config.py` | Configuration management |
| `tests/unit/test_models.py` | Engine data models |
| `tests/unit/test_schemas.py` | Pydantic API schemas |
| `tests/unit/test_logging.py` | JSON logging config |
| `tests/unit/test_discovery.py` | Region discovery (AWS/Azure/GCP) |
| `tests/unit/test_prober.py` | Latency prober |
| `tests/unit/test_scheduler.py` | Measurement scheduler |
| `tests/unit/test_routes.py` | REST API routes |
| `tests/unit/test_sse.py` | SSE streaming |
| `tests/integration/test_engine_api.py` | Engine-to-API data flow |

### Final Metrics
- **102 tests passing**
- **92.24% code coverage** (threshold: 90%)
- **DocGuard score: 88/100 (A)**
- **ALCOA+ compliance: 9/9**
- **148 regions discovered** (AWS ~42 + Azure 59 + GCP ~47)
- **112 regions reachable**
- **Ruff lint: clean**
- **Black format: clean**

### How to Run
```bash
pip install -r requirements.txt
python -m cloudlatency.main
# Open http://localhost:8000
```
