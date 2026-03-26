# Test Specification

<!-- docguard:version 1.0.0 -->
<!-- docguard:status approved -->
<!-- docguard:last-reviewed 2026-03-26 -->
<!-- docguard:owner @cloudlatency -->

> **Canonical document** — Design intent. This file declares what tests MUST exist.  
> Last updated: 2026-03-26

---

## Test Categories

| Category | Required | Applies To | Suggested Tools |
|----------|----------|-----------|-----------------|
| Unit | Yes | Engine models, discovery, prober, scheduler, API routes, schemas | pytest, pytest-asyncio |
| Integration | Yes | Engine-to-API data flow, API-to-SSE streaming | httpx (TestClient), pytest-asyncio |
| E2E | Optional | Full browser-based user journey (v2) | N/A for v1 |
| Load | Optional | Concurrent SSE connections, measurement throughput | k6 |

## Coverage Rules

| Source Pattern | Required Test Pattern | Category |
|---------------|----------------------|----------|
| `cloudlatency/engine/*.py` | `tests/unit/test_*.py` | Unit |
| `cloudlatency/api/*.py` | `tests/unit/test_*.py` | Unit |
| `cloudlatency/config.py` | `tests/unit/test_config.py` | Unit |
| `cloudlatency/api/routes.py` + `cloudlatency/engine/scheduler.py` | `tests/integration/test_engine_api.py` | Integration |
| `cloudlatency/api/sse.py` | `tests/integration/test_api_sse.py` | Integration |

**Coverage Gate**: 90%+ line coverage required (constitution principle II).

## Service-to-Test Map

| Source File | Unit Test | Integration Test | Status |
|------------|-----------|-----------------|--------|
| `cloudlatency/config.py` | `tests/unit/test_config.py` | — | Planned |
| `cloudlatency/engine/models.py` | `tests/unit/test_models.py` | — | Planned |
| `cloudlatency/engine/discovery.py` | `tests/unit/test_discovery.py` | `tests/integration/test_engine_api.py` | Planned |
| `cloudlatency/engine/prober.py` | `tests/unit/test_prober.py` | `tests/integration/test_engine_api.py` | Planned |
| `cloudlatency/engine/scheduler.py` | `tests/unit/test_scheduler.py` | `tests/integration/test_engine_api.py` | Planned |
| `cloudlatency/api/routes.py` | `tests/unit/test_routes.py` | `tests/integration/test_engine_api.py` | Planned |
| `cloudlatency/api/sse.py` | `tests/unit/test_sse.py` | `tests/integration/test_api_sse.py` | Planned |
| `cloudlatency/api/schemas.py` | `tests/unit/test_schemas.py` | — | Planned |

## Critical User Journeys (E2E Required)

| # | Journey Description | Test File | Status |
|---|-------------------|-----------|--------|
| 1 | Open UI, see sorted latency table, wait for auto-refresh | Browser manual test | Planned |
| 2 | View average latency chart per vendor | Browser manual test | Planned |
| 3 | View closest region chart per vendor | Browser manual test | Planned |
| 4 | SSE auto-update without page reload or scroll loss | Browser manual test | Planned |

## Canary Tests (Pre-Deploy Gates)

| Canary | What It Checks | File |
|--------|---------------|------|
| Health | `GET /api/v1/health` returns 200 with engine status | `tests/unit/test_routes.py` |
| Data Flow | Engine produces snapshot, API returns it | `tests/integration/test_engine_api.py` |

## Recommended Test Patterns

| Pattern | Description | Priority |
|---------|-------------|----------|
| Mock external APIs | Use `aioresponses` to mock cloud provider discovery endpoints | High |
| Mock HTTP HEAD | Use `aioresponses` to mock latency probe responses with controlled timing | High |
| Async test support | Use `pytest-asyncio` for all async engine and SSE tests | High |
| Edge cases | Unreachable regions (timeout), zero regions, all-unreachable vendor | Medium |
| Error paths | Discovery API failure, prober timeout, SSE disconnect | Medium |
