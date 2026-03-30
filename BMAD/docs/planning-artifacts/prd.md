---
stepsCompleted: [step-01-init, step-02-discovery, step-02b-vision, step-02c-executive-summary, step-03-success, step-04-journeys, step-05-domain, step-06-innovation, step-07-project-type, step-08-scoping, step-09-functional, step-10-nonfunctional, step-11-polish, step-12-complete]
status: complete
completedDate: '2026-03-28'
inputDocuments: [product-brief-cloudlatency.md, product-brief-cloudlatency-distillate.md]
workflowType: 'prd'
classification:
  projectType: web-app-api-hybrid
  domain: devops-infrastructure-tooling
  complexity: low-medium
  projectContext: greenfield
  notes: DevOps tooling UX conventions apply; async concurrency is a core concern
---

# Product Requirements Document - CloudLatency

**Author:** Rvunvulea
**Date:** 2026-03-28

## Executive Summary

CloudLatency is a real-time, multi-cloud latency monitoring tool that measures HTTPS response times to every Azure, AWS, and GCP region worldwide. It targets DevOps engineers and SREs who need to evaluate, compare, and validate cloud region choices from their actual network location — without switching between vendor-specific dashboards, running ad-hoc scripts, or paying for commercial monitoring suites.

The application runs locally with a single command, requires no API keys or cloud accounts, and auto-refreshes measurements every 10 seconds. It presents a sorted latency table across all providers, average latency per vendor, and closest-region indicators — all pushed live to the browser via Server-Sent Events.

### What Makes This Special

- **Multi-cloud in one view** — Azure, AWS, and GCP compared side-by-side in real time, eliminating the fragmented three-console workflow.
- **API-first architecture** — The REST API is the product's backbone. The web UI is one consumer; CLI tools, CI pipelines, and custom dashboards can replace it without any backend changes.
- **Zero friction** — No configuration, no API keys, no cost. One command, instant results.
- **Quality-engineered** — >90% test coverage, CC ≤ 5 per function, shift-left testing. The codebase is as clean as the UI.

## Project Classification

| Attribute | Value |
| --------- | ----- |
| Project Type | Web App + API Backend Hybrid |
| Domain | DevOps / Infrastructure Tooling |
| Complexity | Low-Medium (async concurrency, real-time push) |
| Project Context | Greenfield |
| UX Convention | Data-dense, minimal chrome, DevOps tooling patterns |

## Success Criteria

### User Success

- **Instant multi-cloud comparison** — Users see latency data for all Azure, AWS, and GCP regions within 30 seconds of launching the tool.
- **Effortless region validation** — Users identify the lowest-latency region per provider without any manual calculation or tab-switching.
- **Trust through freshness** — Data auto-refreshes every 10 seconds; users never wonder if results are stale.
- **Zero onboarding friction** — From install to first result in under 2 minutes, no configuration or credentials required.

### Business Success

- **Open-source adoption** — 100+ GitHub stars within 6 months (signals community validation for a DevOps utility).
- **Community contribution** — At least 1 external PR within 3 months (validates the component-separated architecture enables contribution).
- **API consumer diversity** — At least one non-UI consumer (CLI wrapper, CI integration, or community tool) built on the REST API within 6 months.

### Technical Success

- **Test coverage** — >90% line coverage, enforced in CI.
- **Complexity** — All functions CC ≤ 5, measured via radon.
- **Probe reliability** — >95% of known cloud regions return a valid HTTPS measurement per cycle.
- **Observability** — All backend errors detectable via structured logs; UI connection failures surfaced to the user.
- **Component isolation** — REST API fully functional and testable without the web UI running.

### Measurable Outcomes

| Metric | Target | Measurement |
| ------ | ------ | ----------- |
| Time to first result | < 30s | Stopwatch from `python -m cloudlatency` |
| Refresh cycle | 10s ± 1s | Measured in-browser |
| Test coverage | > 90% | pytest-cov |
| Cyclomatic complexity | CC ≤ 5 per function | radon cc |
| Probe success rate | > 95% | Logged per cycle |
| Cross-browser | Chrome, Firefox, Edge, Safari | Manual verification |

## User Journeys

### Journey 1: Kai — SRE Validating a Region Choice (Primary, Happy Path)

**Kai** is a Site Reliability Engineer at a mid-size SaaS company. The team just signed a deal with a client in Southeast Asia and the CTO wants to know: *"Should we spin up in AWS ap-southeast-1 or GCP asia-southeast1?"*

**Opening Scene:** Kai has been manually curling health endpoints for 20 minutes, juggling three terminal tabs, and copying numbers into a spreadsheet. The results are inconsistent because each test is a single point-in-time snapshot.

**Rising Action:** Kai discovers CloudLatency, runs `pip install cloudlatency && python -m cloudlatency`, and opens the browser. Within 15 seconds, a sorted table appears showing all regions across all three providers. The table auto-refreshes — no need to re-run anything.

**Climax:** After watching two minutes of live data, Kai sees that AWS ap-southeast-1 consistently beats GCP asia-southeast1 by 30ms from their office. The vendor-average chart confirms AWS has lower average latency to Asia-Pacific from their location. The answer is clear and backed by continuous data, not a single test.

**Resolution:** Kai screenshots the dashboard, drops it in the architecture decision record, and moves on. Total time: 5 minutes instead of an hour. The tool stays running in a background tab for the rest of the week as a sanity check.

### Journey 2: Kai — Network Anomaly (Primary, Edge Case)

**Opening Scene:** Same Kai, three weeks later. Alerts fire — users in Europe report slow response times. Kai opens CloudLatency to see if it's a provider issue.

**Rising Action:** The sorted table shows Azure westeurope at 180ms — normally it's 40ms. Other Azure EU regions are similarly degraded. AWS and GCP EU regions are normal. This points to an Azure networking issue, not Kai's application.

**Climax:** Some Azure regions show "Unreachable" in the table. The UI clearly indicates which regions failed instead of silently dropping them. Kai can distinguish between "slow" and "down."

**Resolution:** Kai reports to the team with confidence: "Azure EU networking is degraded — it's not us." When Azure resolves the issue 20 minutes later, CloudLatency's live table confirms recovery in real time.

### Journey 3: Morgan — Platform Architect Evaluating Multi-Cloud Strategy (Secondary)

**Morgan** is a Platform Architect preparing a multi-cloud strategy proposal for the VP of Engineering.

**Opening Scene:** Morgan needs data to justify recommending a primary and secondary cloud provider. Vendor-published latency numbers are marketing material, not real measurements from their corporate network.

**Rising Action:** Morgan runs CloudLatency from three different office locations (NYC, London, Singapore) over a week, collecting the vendor-average charts from each. The REST API makes it easy to script data collection: `curl localhost:8080/api/v1/results | jq`.

**Climax:** The data tells a clear story — AWS wins in North America, GCP wins in Asia, and Azure is competitive in Europe. Morgan has real, repeatable numbers instead of vendor claims.

**Resolution:** Morgan's architecture proposal includes CloudLatency screenshots and API-sourced data tables. The VP approves the multi-cloud strategy with confidence. Morgan recommends the team keep CloudLatency as a periodic validation tool.

### Journey 4: Dev — Building a CI Latency Gate (API Consumer)

**Dev** is a DevOps engineer who wants to fail CI builds if the team's primary region latency exceeds a threshold.

**Opening Scene:** The team deploys to AWS eu-west-1. Occasionally, network changes cause latency spikes that go unnoticed until users complain.

**Rising Action:** Dev discovers CloudLatency's REST API docs. They write a 20-line Python script that hits `/api/v1/results`, filters for `aws/eu-west-1`, and asserts latency < 100ms. The script runs as a CI step.

**Climax:** A network change causes eu-west-1 latency to spike to 150ms. The CI pipeline fails with a clear message: "Region latency 150ms exceeds threshold 100ms." The team catches the issue before deploying.

**Resolution:** Dev shares the script with the team Slack channel. Two other teams adopt it. The REST API proves its value as a standalone data source beyond the web UI.

### Journey Requirements Summary

| Journey | Capabilities Revealed |
| ------- | --------------------- |
| Kai — Happy Path | Sorted table, vendor charts, auto-refresh, single-command launch |
| Kai — Edge Case | Unreachable region handling, clear error states, live recovery detection |
| Morgan — Architect | REST API data access, vendor-average comparison, repeatable measurements |
| Dev — CI Gate | REST API endpoints, JSON response format, filterable by provider/region |

## Web App + API Hybrid Requirements

### Project-Type Overview

CloudLatency is a single-page application (SPA) with a decoupled REST API backend. The web UI is one consumer of the API; the API is designed to be independently consumable by CLI tools, scripts, and CI pipelines. No authentication, rate limiting, or SEO concerns apply in v1 (local-only tool).

### Web Application Requirements

| Requirement | Decision |
| ----------- | -------- |
| Architecture | SPA — single page, no routing needed |
| Browser support | Chrome, Firefox, Edge, Safari (latest 2 versions) |
| Responsive design | Desktop-first; basic mobile readability acceptable |
| SEO | Not required (local tool, not publicly hosted) |
| Real-time updates | SSE (Server-Sent Events), 10-second push cycle |
| Accessibility | Basic level — semantic HTML, sufficient contrast, keyboard-navigable table |
| Performance target | First meaningful paint < 2s; table render < 100ms per update |

### REST API Requirements

| Requirement | Decision |
| ----------- | -------- |
| Versioning | URL-path: `/api/v1/...` |
| Data format | JSON only |
| Authentication | None (v1, local deployment) |
| Rate limiting | None (v1, single user) |
| CORS | Enabled for localhost origins |

### API Endpoint Specification

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/api/v1/results` | All current latency measurements |
| GET | `/api/v1/results/{provider}` | Measurements filtered by provider (aws/azure/gcp) |
| GET | `/api/v1/summary` | Vendor averages and closest regions |
| GET | `/api/v1/health` | Service health check |
| GET | `/api/v1/sse` | SSE stream for live updates |

### Implementation Considerations

- **Error codes**: API returns standard HTTP status codes (200, 404, 500) with JSON error bodies.
- **Data schema**: Each measurement includes `provider`, `region`, `latency_ms`, `status` (ok/unreachable/error), and `timestamp`.

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach:** Problem-solving MVP — deliver the smallest thing that makes multi-cloud latency comparison effortless. If a user can launch the tool and answer "which region is fastest?" within 30 seconds, the MVP succeeds.

**Resource Requirements:** Solo developer, Python proficiency, basic frontend skills. No infrastructure or cloud accounts needed.

### MVP Feature Set (Phase 1)

**Core User Journeys Supported:**

- Kai — SRE validating a region choice (happy path)
- Kai — Network anomaly detection (edge case)

**Must-Have Capabilities:**

| Capability | Justification |
| ---------- | ------------- |
| HTTPS probing to all Azure/AWS/GCP regions | Core value — without this, the product doesn't exist |
| Sorted latency table | Primary UI element; answers "which is fastest?" |
| Vendor-average chart | Answers "which provider is best overall?" |
| Closest-region chart | Answers "where should I deploy?" |
| 10s auto-refresh via SSE | Trust through freshness — stale data kills value |
| REST API (`/results`, `/summary`, `/health`, `/sse`) | Component separation — architectural requirement |
| Unreachable region handling | Edge case journey — "slow" vs "down" distinction |
| Unit tests >90% coverage | Hard quality gate |
| Single-command launch | Zero-friction onboarding |

**Explicitly deferred from MVP:**

- Provider-filtered API endpoints (`/results/{provider}`) — nice-to-have, trivial to add in Phase 2
- Historical data — requires persistence layer, not needed for core value

### Post-MVP Features

**Phase 2 (Growth):**

- Provider-filtered API endpoints
- Historical latency trending + SQLite persistence
- Region filtering in UI
- CSV/JSON export from API
- CLI consumer tool
- Docker container packaging

**Phase 3 (Expansion):**

- CI/CD integration (pipeline latency gate)
- Community endpoint registry
- Multi-location distributed probes
- Alerting and threshold notifications
- Plugin architecture for additional providers

### Risk Mitigation Strategy

**Technical Risks:**

- *Endpoint instability* — Cloud providers may change health-check URLs. **Mitigation:** Store endpoints in a config file (not hardcoded), document how to update.
- *Concurrent probe load* — 50+ simultaneous HTTPS requests every 10s. **Mitigation:** Use async I/O (aiohttp), implement backpressure and timeout handling.
- *Firewall/proxy blocking* — Corporate networks may block probes. **Mitigation:** Graceful "unreachable" status per region, not silent failure.

**Market Risks:**

- *Low adoption* — DevOps tools compete for attention. **Mitigation:** Zero-friction install (`pip install`), instant value, no config needed.
- *Alternatives emerge* — Cloud providers add built-in comparison. **Mitigation:** Open source + API-first means community value outlasts any single provider's tool.

**Resource Risks:**

- *Solo developer bandwidth* — **Mitigation:** Lean MVP scope. The must-have list is intentionally small (~10 capabilities). Achievable in 2-3 sprints.

## Functional Requirements

### Latency Measurement

- **FR1:** System can discover all available Azure regions and their health-check endpoints
- **FR2:** System can discover all available AWS regions and their health-check endpoints
- **FR3:** System can discover all available GCP regions and their health-check endpoints
- **FR4:** System can measure HTTPS response time to each discovered cloud region
- **FR5:** System can probe all regions concurrently within a single measurement cycle
- **FR6:** System can repeat measurement cycles automatically every 10 seconds
- **FR7:** System can detect and report unreachable regions with an error status distinct from high latency

### Data Presentation — Table

- **FR8:** User can view a table of all cloud regions sorted by latency (lowest to highest)
- **FR9:** User can see provider name, region name, latency (ms), and status for each row
- **FR10:** User can distinguish between reachable regions (with latency) and unreachable regions (with error state)
- **FR11:** Table auto-updates when new measurement data arrives without manual page refresh

### Data Presentation — Charts

- **FR12:** User can view a chart showing average latency per cloud vendor
- **FR13:** User can view a chart showing the closest (lowest-latency) region per cloud vendor
- **FR14:** Charts auto-update when new measurement data arrives without manual page refresh

### Live Updates

- **FR15:** System can push new measurement data to connected browser clients via SSE
- **FR16:** Browser client can automatically reconnect if the SSE connection drops
- **FR17:** User can see a visual indicator of connection status (connected/reconnecting)

### REST API

- **FR18:** API consumer can retrieve all current latency measurements via GET request
- **FR19:** API consumer can retrieve vendor averages and closest-region data via GET request
- **FR20:** API consumer can check service health via GET request
- **FR21:** API consumer can subscribe to an SSE stream for live measurement updates
- **FR22:** API returns JSON responses with consistent error format for all endpoints

### Application Lifecycle

- **FR23:** User can start the application with a single command
- **FR24:** System can begin producing latency data within 30 seconds of launch
- **FR25:** User can stop the application gracefully (Ctrl+C) without data corruption
- **FR26:** System can log errors in a structured format sufficient to diagnose backend issues

### Observability

- **FR27:** System can log each measurement cycle's success/failure count
- **FR28:** System can report probe errors without crashing the measurement loop
- **FR29:** User can detect UI connection failures through visible status indication

## Non-Functional Requirements

### Performance

- **NFR1:** All API endpoints respond within 200ms (excluding SSE stream)
- **NFR2:** A complete measurement cycle (all regions probed) completes within 8 seconds to allow 2s buffer before the next 10s cycle
- **NFR3:** UI table re-render completes within 100ms after receiving new data
- **NFR4:** First meaningful paint (table + charts visible) within 2 seconds of page load
- **NFR5:** SSE event delivery latency < 500ms from measurement completion to browser receipt
- **NFR6:** Memory usage remains stable over extended runtime (no leaks over 1-hour sessions)

### Reliability

- **NFR7:** A single failed probe does not block or delay other probes in the same cycle
- **NFR8:** The measurement loop continues operating if any individual region is unreachable
- **NFR9:** SSE reconnection occurs automatically within 5 seconds of connection loss
- **NFR10:** Application handles network interface changes (e.g., VPN connect/disconnect) without crashing
- **NFR11:** Graceful shutdown completes within 3 seconds of receiving termination signal

### Compatibility

- **NFR12:** Application runs on Python 3.10+ across Windows, macOS, and Linux
- **NFR13:** Web UI functions correctly in Chrome, Firefox, Edge, and Safari (latest 2 versions)
- **NFR14:** REST API returns valid JSON consumable by standard HTTP clients (curl, requests, fetch)

### Code Quality

- **NFR15:** Unit test line coverage > 90%, enforced in CI
- **NFR16:** Cyclomatic complexity ≤ 5 per function, measured by radon
- **NFR17:** All code follows a consistent style enforced by linter (ruff or flake8)
- **NFR18:** Structured logging (JSON format) for all backend log output

### Accessibility (Basic)

- **NFR19:** Semantic HTML used for all data display elements (tables use `<table>`, not `<div>`)
- **NFR20:** Sufficient color contrast (WCAG AA) for all text and data elements
- **NFR21:** Latency table is navigable via keyboard
