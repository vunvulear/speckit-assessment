# Tasks: Cloud Latency Monitor

**Input**: Design documents from `/specs/001-cloud-latency-monitor/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included — constitution mandates Test-First Development with 90%+ coverage.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure per plan.md: cloudlatency/, cloudlatency/engine/, cloudlatency/api/, cloudlatency/ui/static/, tests/, tests/unit/, tests/integration/
- [x] T002 Create pyproject.toml with project metadata, pytest/ruff/black/coverage configuration
- [x] T003 [P] Create requirements.txt with pinned production dependencies: fastapi, uvicorn, aiohttp, sse-starlette, pydantic
- [x] T004 [P] Create requirements-dev.txt with test/lint dependencies: pytest, pytest-asyncio, pytest-cov, aioresponses, httpx, ruff, black
- [x] T005 [P] Create all __init__.py files: cloudlatency/__init__.py, cloudlatency/engine/__init__.py, cloudlatency/api/__init__.py
- [x] T006 [P] Create LICENSE file (MIT license)
- [x] T007 [P] Create README.md with project overview and quickstart reference

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T008 Implement configuration management in cloudlatency/config.py (HOST, PORT, MEASUREMENT_INTERVAL, REQUEST_TIMEOUT, LOG_LEVEL with environment variable overrides and defaults)
- [x] T009 Implement data models in cloudlatency/engine/models.py (dataclasses: CloudProvider, CloudRegion, LatencyMeasurement, VendorSummary, LatencySnapshot)
- [x] T010 [P] Implement Pydantic response schemas in cloudlatency/api/schemas.py (LatencyResponse, RegionResponse, HealthResponse, VendorSummaryResponse)
- [x] T011 [P] Implement structured JSON logging setup in cloudlatency/config.py or cloudlatency/logging_config.py (severity levels: DEBUG, INFO, WARNING, ERROR)
- [x] T012 Create FastAPI app factory in cloudlatency/api/app.py (app creation, static file mounting for UI, CORS middleware)
- [x] T013 Create application entry point in cloudlatency/main.py (uvicorn startup, engine initialization, graceful shutdown)
- [x] T014 [P] Create shared test fixtures in tests/conftest.py (mock providers, mock regions, mock measurements, mock snapshots)

### Tests for Phase 2

- [x] T015 [P] Unit tests for config in tests/unit/test_config.py (defaults, env overrides, validation)
- [x] T016 [P] Unit tests for data models in tests/unit/test_models.py (creation, validation, serialization)
- [x] T017 [P] Unit tests for Pydantic schemas in tests/unit/test_schemas.py (serialization, validation)

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - View Real-Time Latency Table (Priority: P1) MVP

**Goal**: Display a table of all cloud regions sorted by latency (lowest to highest) that auto-refreshes every 10 seconds

**Independent Test**: Open the web UI and verify the table appears with latency data sorted ascending, refreshing automatically

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T018 [P] [US1] Unit test for region discovery in tests/unit/test_discovery.py (mock provider API responses, parse regions, handle failures)
- [x] T019 [P] [US1] Unit test for latency prober in tests/unit/test_prober.py (mock HTTPS HEAD responses, measure latency, handle timeouts, concurrent probing)
- [x] T020 [P] [US1] Unit test for scheduler in tests/unit/test_scheduler.py (10s cycle orchestration, snapshot creation, error handling)
- [x] T021 [P] [US1] Unit test for API routes in tests/unit/test_routes.py (GET /api/v1/latency, GET /api/v1/regions, GET /api/v1/health, 503 when no data)
- [x] T022 [P] [US1] Integration test for engine-to-API data flow in tests/integration/test_engine_api.py (engine produces snapshot, API serves it)

### Implementation for User Story 1

- [x] T023 [US1] Implement region discovery for AWS in cloudlatency/engine/discovery.py (fetch from ip-ranges.amazonaws.com, parse region list, build CloudRegion objects with ec2 endpoints)
- [x] T024 [US1] Implement region discovery for Azure in cloudlatency/engine/discovery.py (fetch from Azure public IP ranges or management API, parse region list, build CloudRegion objects)
- [x] T025 [US1] Implement region discovery for GCP in cloudlatency/engine/discovery.py (fetch from gstatic.com/ipranges/cloud.json, parse region list, build CloudRegion objects)
- [x] T026 [US1] Implement async HTTPS HEAD latency prober in cloudlatency/engine/prober.py (aiohttp session, concurrent probing, 5s timeout, latency measurement, unreachable handling)
- [x] T027 [US1] Implement measurement scheduler in cloudlatency/engine/scheduler.py (10s loop, call discovery on start, call prober each cycle, compute VendorSummary aggregates, build LatencySnapshot)
- [x] T028 [US1] Implement REST API routes in cloudlatency/api/routes.py (GET /api/v1/latency returns latest snapshot, GET /api/v1/regions returns discovered regions, GET /api/v1/health returns engine status)
- [x] T029 [US1] Create web UI HTML structure in cloudlatency/ui/static/index.html (page layout: header with title, last-updated timestamp, latency table placeholder, chart placeholders)
- [x] T030 [US1] Create web UI styling in cloudlatency/ui/static/style.css (clean minimal design, table styling with alternating rows, responsive layout for desktop/tablet)
- [x] T031 [US1] Implement table rendering in cloudlatency/ui/static/app.js (fetch /api/v1/latency on load, render sorted table with provider, region name, region code, latency columns, mark unreachable rows)
- [x] T032 [US1] Add logging to engine components in cloudlatency/engine/discovery.py, prober.py, scheduler.py (structured JSON, startup/cycle/error events)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently — table displays sorted latency data

---

## Phase 4: User Story 2 - View Average Latency Chart by Vendor (Priority: P2)

**Goal**: Display a bar chart showing the average latency for each cloud vendor (Azure, AWS, GCP)

**Independent Test**: Verify the average latency bar chart renders with three bars (one per vendor) and updates automatically

### Tests for User Story 2

- [x] T033 [P] [US2] Unit test for vendor summary computation in tests/unit/test_scheduler.py (average calculation, handle all-unreachable vendor, correct region counts)
- [x] T034 [P] [US2] Unit test for chart data endpoint validation in tests/unit/test_routes.py (vendor_summaries included in /api/v1/latency response)

### Implementation for User Story 2

- [x] T035 [US2] Add Chart.js library to cloudlatency/ui/static/index.html (CDN link or bundled file)
- [x] T036 [US2] Implement average latency bar chart in cloudlatency/ui/static/app.js (Chart.js bar chart, one bar per vendor, labeled axes, color-coded by vendor)
- [x] T037 [US2] Add chart container and layout to cloudlatency/ui/static/index.html (canvas element for average chart below table)
- [x] T038 [US2] Update cloudlatency/ui/static/style.css with chart section styling (proper sizing, spacing, responsive width)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently — table + average chart

---

## Phase 5: User Story 3 - View Closest Region Latency by Vendor (Priority: P2)

**Goal**: Display a bar chart showing the closest (lowest-latency) region for each vendor with region name label

**Independent Test**: Verify the closest-region bar chart shows minimum latency per vendor with region name annotations

### Tests for User Story 3

- [x] T039 [P] [US3] Unit test for closest region extraction in tests/unit/test_scheduler.py (minimum latency selection, handle ties, handle single-region vendor)

### Implementation for User Story 3

- [x] T040 [US3] Implement closest-region bar chart in cloudlatency/ui/static/app.js (second Chart.js bar chart, one bar per vendor, region name as label, latency as value)
- [x] T041 [US3] Add chart container for closest-region chart in cloudlatency/ui/static/index.html (canvas element below average chart)
- [x] T042 [US3] Update cloudlatency/ui/static/style.css with second chart layout (consistent sizing with average chart)

**Checkpoint**: All three data views operational — table + average chart + closest chart

---

## Phase 6: User Story 4 - Automatic Page Updates via SSE (Priority: P1)

**Goal**: Push latency data to the browser via SSE every 10 seconds without page reload or scroll position loss

**Independent Test**: Open the page, wait 30+ seconds, confirm at least 3 automatic data updates with no page reload and preserved scroll position

### Tests for User Story 4

- [x] T043 [P] [US4] Unit test for SSE endpoint in tests/unit/test_sse.py (stream produces events, correct event format, handles client disconnect)
- [x] T044 [P] [US4] Integration test for SSE data flow in tests/integration/test_api_sse.py (engine measurement → SSE event → client receives JSON)

### Implementation for User Story 4

- [x] T045 [US4] Implement SSE streaming endpoint in cloudlatency/api/sse.py (GET /api/v1/latency/stream, StreamingResponse with event: latency_update, retry: 5000, JSON data payload)
- [x] T046 [US4] Register SSE route in cloudlatency/api/app.py (mount SSE endpoint alongside REST routes)
- [x] T047 [US4] Replace polling with EventSource in cloudlatency/ui/static/app.js (connect to /api/v1/latency/stream, parse events, update table + both charts on each event, preserve scroll position)
- [x] T048 [US4] Implement last-updated timestamp display in cloudlatency/ui/static/app.js (update timestamp element on each SSE event)
- [x] T049 [US4] Implement stale-data warning in cloudlatency/ui/static/app.js (show warning banner when SSE disconnects, auto-reconnect via EventSource, fetch fresh data on tab refocus via visibilitychange event)
- [x] T050 [US4] Add SSE connection logging in cloudlatency/api/sse.py (client connect/disconnect events, structured JSON format)

**Checkpoint**: Full real-time experience — all data auto-updates via SSE without page reload

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T051 [P] Add error handling middleware in cloudlatency/api/app.py (global exception handler, structured error responses)
- [x] T052 [P] Add API documentation generation in cloudlatency/api/app.py (FastAPI auto-generated OpenAPI docs at /docs)
- [x] T053 Code cleanup: ensure all modules pass ruff linting and black formatting
- [x] T054 [P] Run full test suite with coverage report, ensure 90%+ line coverage across all components
- [x] T055 [P] Update README.md with final project documentation (setup, usage, architecture, API reference, contributing)
- [x] T056 Run quickstart.md validation: follow the quickstart steps end-to-end and verify they work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion — delivers MVP
- **User Story 2 (Phase 4)**: Depends on Foundational; can start after Phase 2 (independent of US1 for backend, but builds on US1's table UI)
- **User Story 3 (Phase 5)**: Depends on Foundational; can start after Phase 2 (independent of US2 for backend, but builds on US2's chart integration)
- **User Story 4 (Phase 6)**: Depends on Foundational + at least US1 (needs data to stream); enhances all previous stories
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational — No dependencies on other stories
- **User Story 2 (P2)**: Backend independent; UI extends US1's page layout
- **User Story 3 (P2)**: Backend independent; UI extends US2's chart setup
- **User Story 4 (P1)**: Requires US1's API routes; enhances all stories with live updates

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Backend before frontend
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- All test tasks marked [P] within a story can run in parallel
- US2 and US3 backend work can run in parallel after Foundational

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Table displays sorted latency data, refreshes
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → MVP (sorted table)
3. Add User Story 2 → Test independently → Average chart added
4. Add User Story 3 → Test independently → Closest region chart added
5. Add User Story 4 → Test independently → Full SSE real-time experience
6. Polish → Final quality pass

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
