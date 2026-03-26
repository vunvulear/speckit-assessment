# Requirements

<!-- docguard:version 1.0.0 -->
<!-- docguard:status approved -->

> Tracks functional requirements, non-functional requirements, and success criteria.
> Use requirement IDs (FR-001, NFR-001, SC-001) for traceability back to code and tests.
> Full detail in `specs/001-cloud-latency-monitor/spec.md`.

![CDD Canonical](https://img.shields.io/badge/CDD-Canonical-blue)

## Functional Requirements

| ID | Priority | Requirement | Status | Test Coverage |
|----|----------|-------------|--------|---------------|
| FR-001 | P1 | System MUST measure latency via HTTPS HEAD requests to all Azure, AWS, GCP regions | Approved | Planned: test_discovery.py, test_prober.py |
| FR-002 | P1 | System MUST refresh latency measurements every 10 seconds | Approved | Planned: test_scheduler.py |
| FR-003 | P1 | System MUST expose latency data via REST API (JSON) | Approved | Planned: test_routes.py |
| FR-004 | P1 | Web UI MUST display a sorted latency table (lowest to highest) | Approved | Planned: browser test |
| FR-005 | P2 | Web UI MUST display average latency bar chart per vendor | Approved | Planned: test_routes.py |
| FR-006 | P2 | Web UI MUST display closest region bar chart per vendor | Approved | Planned: test_routes.py |
| FR-007 | P1 | Web UI MUST auto-update via SSE every 10 seconds | Approved | Planned: test_sse.py |
| FR-008 | P1 | System MUST mark regions unreachable after 5s timeout | Approved | Planned: test_prober.py |
| FR-009 | P1 | System MUST preserve scroll position during updates | Approved | Planned: browser test |
| FR-010 | P2 | System MUST display last-updated timestamp | Approved | Planned: browser test |
| FR-011 | P1 | REST API MUST be sole interface between engine and UI | Approved | Architecture constraint |
| FR-012 | P2 | Each component MUST be independently deployable | Approved | Architecture constraint |

## Non-Functional Requirements

| ID | Category | Requirement | Metric |
|----|----------|-------------|--------|
| NFR-001 | Performance | Complete measurement cycle for 100+ regions within 10s | Measured via scheduler timing logs |
| NFR-002 | Performance | SSE delivery < 2s after measurement | Measured via event timestamps |
| NFR-003 | Reliability | Run continuously 24h without memory leaks or crashes | Manual soak test |
| NFR-004 | Compatibility | Render correctly on Chrome, Firefox, Safari, Edge (latest 2 versions) | Manual browser testing |
| NFR-005 | Quality | 90%+ test coverage across all components | pytest-cov report |

## Success Criteria

| ID | Criteria | Measurement | Target |
|----|----------|-------------|--------|
| SC-001 | Fully populated table within 15s of first load | Time from page open to full table | <= 15 seconds |
| SC-002 | Data refreshes with < 2s visible delay | Time from SSE event to DOM update | <= 2 seconds |
| SC-003 | Measures 90%+ of all publicly listed regions | Region count / total available | >= 90% |
| SC-004 | User can identify fastest region within 5s | Usability: table is sorted ascending | <= 5 seconds |
| SC-005 | 24h continuous run without degradation | Memory, uptime monitoring | No leaks/crashes |
| SC-006 | Test coverage above 90% | pytest-cov | >= 90% |
| SC-007 | Cross-browser rendering | Manual test on 4 browsers | All pass |

## User Scenarios

See `specs/001-cloud-latency-monitor/spec.md` for full Given/When/Then acceptance scenarios.

### User Story 1 - View Real-Time Latency Table (Priority: P1)

User opens the app and sees a sorted latency table for all cloud regions, auto-refreshing every 10 seconds.

### User Story 2 - View Average Latency Chart by Vendor (Priority: P2)

User sees a bar chart showing average latency per vendor (Azure, AWS, GCP).

### User Story 3 - View Closest Region Latency by Vendor (Priority: P2)

User sees a bar chart showing the closest (lowest-latency) region per vendor.

### User Story 4 - Automatic Page Updates (Priority: P1)

All data auto-updates via SSE without page reload, scroll loss, or flickering.

## Traceability Matrix

| Requirement | Source File | Test File | Status |
|-------------|------------|-----------|--------|
| FR-001 | `cloudlatency/engine/discovery.py` | `tests/unit/test_discovery.py` | Planned |
| FR-002 | `cloudlatency/engine/scheduler.py` | `tests/unit/test_scheduler.py` | Planned |
| FR-003 | `cloudlatency/api/routes.py` | `tests/unit/test_routes.py` | Planned |
| FR-004 | `cloudlatency/ui/static/app.js` | Browser test | Planned |
| FR-005 | `cloudlatency/ui/static/app.js` | `tests/unit/test_routes.py` | Planned |
| FR-006 | `cloudlatency/ui/static/app.js` | `tests/unit/test_routes.py` | Planned |
| FR-007 | `cloudlatency/api/sse.py` | `tests/unit/test_sse.py` | Planned |
| FR-008 | `cloudlatency/engine/prober.py` | `tests/unit/test_prober.py` | Planned |
| FR-009 | `cloudlatency/ui/static/app.js` | Browser test | Planned |
| FR-010 | `cloudlatency/ui/static/app.js` | Browser test | Planned |
| FR-011 | `cloudlatency/api/` (architecture) | Architecture validation | Planned |
| FR-012 | Component separation | Architecture validation | Planned |

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-03-26 | CloudLatency | Full requirements from spec.md |

---

*Generated by [DocGuard](https://github.com/raccioly/docguard) — aligned with [Spec Kit](https://github.com/github/spec-kit) standards.*
