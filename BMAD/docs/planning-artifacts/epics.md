---
stepsCompleted: [1, 2, 3, 4]
status: complete
completedAt: '2026-03-28'
inputDocuments: [prd.md, architecture.md, ux-design-specification.md]
---

# CloudLatency - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for CloudLatency, decomposing the requirements from the PRD, UX Design, and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: System can discover all available Azure regions and their health-check endpoints
FR2: System can discover all available AWS regions and their health-check endpoints
FR3: System can discover all available GCP regions and their health-check endpoints
FR4: System can measure HTTPS response time to each discovered cloud region
FR5: System can probe all regions concurrently within a single measurement cycle
FR6: System can repeat measurement cycles automatically every 10 seconds
FR7: System can detect and report unreachable regions with an error status distinct from high latency
FR8: User can view a table of all cloud regions sorted by latency (lowest to highest)
FR9: User can see provider name, region name, latency (ms), and status for each row
FR10: User can distinguish between reachable regions (with latency) and unreachable regions (with error state)
FR11: Table auto-updates when new measurement data arrives without manual page refresh
FR12: User can view a chart showing average latency per cloud vendor
FR13: User can view a chart showing the closest (lowest-latency) region per cloud vendor
FR14: Charts auto-update when new measurement data arrives without manual page refresh
FR15: System can push new measurement data to connected browser clients via SSE
FR16: Browser client can automatically reconnect if the SSE connection drops
FR17: User can see a visual indicator of connection status (connected/reconnecting)
FR18: API consumer can retrieve all current latency measurements via GET request
FR19: API consumer can retrieve vendor averages and closest-region data via GET request
FR20: API consumer can check service health via GET request
FR21: API consumer can subscribe to an SSE stream for live measurement updates
FR22: API returns JSON responses with consistent error format for all endpoints
FR23: User can start the application with a single command
FR24: System can begin producing latency data within 30 seconds of launch
FR25: User can stop the application gracefully (Ctrl+C) without data corruption
FR26: System can log errors in a structured format sufficient to diagnose backend issues
FR27: System can log each measurement cycle's success/failure count
FR28: System can report probe errors without crashing the measurement loop
FR29: User can detect UI connection failures through visible status indication

### NonFunctional Requirements

NFR1: All API endpoints respond within 200ms (excluding SSE stream)
NFR2: A complete measurement cycle (all regions probed) completes within 8 seconds
NFR3: UI table re-render completes within 100ms after receiving new data
NFR4: First meaningful paint (table + charts visible) within 2 seconds of page load
NFR5: SSE event delivery latency < 500ms from measurement completion to browser receipt
NFR6: Memory usage remains stable over extended runtime (no leaks over 1-hour sessions)
NFR7: A single failed probe does not block or delay other probes in the same cycle
NFR8: The measurement loop continues operating if any individual region is unreachable
NFR9: SSE reconnection occurs automatically within 5 seconds of connection loss
NFR10: Application handles network interface changes (e.g., VPN connect/disconnect) without crashing
NFR11: Graceful shutdown completes within 3 seconds of receiving termination signal
NFR12: Application runs on Python 3.10+ across Windows, macOS, and Linux
NFR13: Web UI functions correctly in Chrome, Firefox, Edge, and Safari (latest 2 versions)
NFR14: REST API returns valid JSON consumable by standard HTTP clients
NFR15: Unit test line coverage > 90%, enforced in CI
NFR16: Cyclomatic complexity <= 5 per function, measured by radon
NFR17: All code follows a consistent style enforced by linter (ruff)
NFR18: Structured logging (JSON format) for all backend log output
NFR19: Semantic HTML used for all data display elements
NFR20: Sufficient color contrast (WCAG AA) for all text and data elements
NFR21: Latency table is navigable via keyboard

### Additional Requirements

- Architecture specifies aiohttp 3.13.3 as single dependency for HTTP client + server (no starter template — manual project setup)
- Project uses `src/cloudlatency/` layout with pyproject.toml packaging
- Entry point via `python -m cloudlatency` (__main__.py)
- In-memory LatencyStore class (dict-backed) with protocol/ABC for Phase 2 swap
- SSE via aiohttp StreamResponse (no extra dependency)
- asyncio.Event signaling between probe engine and SSE broadcaster
- Dependency injection pattern: store passed via app["store"], ProbeEngine accepts constructor args
- CI pipeline: GitHub Actions with ruff + pytest-cov (>90%) + radon (CC <= 5)
- python-json-logger for structured JSON logging
- CLI args for port (default 8080), no config files
- Probe timeout: 5s per probe via aiohttp.ClientTimeout
- Graceful shutdown via aiohttp signal handlers + cancel probe task
- CORS enabled for localhost:* origins

### UX Design Requirements

UX-DR1: Implement dark-first color system with CSS custom properties (--bg-primary, --bg-surface, --bg-header, --bg-row-alt, provider colors, semantic colors) as specified in Visual Foundation
UX-DR2: Implement Header Bar component — app title (left), connection status dot + label + "Last updated Xs ago" timestamp (right), fixed position, 48px height
UX-DR3: Implement Summary Banner component — 3 equal columns (AWS | Azure | GCP), each showing provider color accent, average latency, closest region name + latency, 36px height
UX-DR4: Implement Latency Table component — semantic <table> with sticky header, 4 columns (Provider with color border, Region, Latency monospace right-aligned, Status badge), sorted ascending by latency, rows at 36px height
UX-DR5: Implement Connection Status Indicator — colored dot (8px) + text label, 3 states (Connected green, Reconnecting yellow pulsing, Disconnected red), role="status", aria-live="polite"
UX-DR6: Implement Status Badge component — pill-shaped badge with 3 variants: OK (green), Slow (amber), Unreachable (red), always includes text label (never color-only)
UX-DR7: Implement progressive data population — rows appear as probes return, fade in over 150ms, re-sort into position; summary banner recalculates with each new data point
UX-DR8: Implement empty/loading states — "Connecting..." on initial load, "Waiting for data..." placeholder in table, "—" placeholders in summary banner
UX-DR9: Implement timestamp freshness coloring — green (0-10s), amber (11-30s), red (30s+); relative time format "Updated Xs ago"
UX-DR10: Implement SSE disconnection behavior — data freezes in place (not cleared), timestamp turns red, connection status shows "Disconnected"
UX-DR11: Implement accessibility — semantic HTML (header role="banner", main, table with thead/tbody/th scope="col"), aria-sort on latency column, prefers-reduced-motion support, prefers-color-scheme support, focus ring on focusable elements
UX-DR12: Implement responsive layout — desktop-first (>=1024px full design), tablet (768-1023px reduced padding), mobile (<768px stacked header/banner, horizontal-scroll table, 44px min row height)
UX-DR13: Implement typography system — system font stack for UI, monospace stack (JetBrains Mono fallback chain) for latency values with tabular-nums, sizes as specified in Visual Foundation
UX-DR14: Implement data formatting patterns — latency as "32 ms" (integer + unit, right-aligned, monospace), provider as title case with color, region as lowercase provider convention, status as capitalized badge

### FR Coverage Map

FR1: Epic 1 - Azure region discovery
FR2: Epic 1 - AWS region discovery
FR3: Epic 1 - GCP region discovery
FR4: Epic 1 - HTTPS latency measurement
FR5: Epic 1 - Concurrent probing
FR6: Epic 1 - 10s auto-refresh cycle
FR7: Epic 1 - Unreachable region detection
FR8: Epic 2 - Sorted latency table
FR9: Epic 2 - Table columns (provider, region, latency, status)
FR10: Epic 2 - Reachable vs unreachable distinction
FR11: Epic 2 - Table auto-update via SSE
FR12: Epic 2 - Vendor average display
FR13: Epic 2 - Closest region display
FR14: Epic 2 - Summary auto-update via SSE
FR15: Epic 2 - SSE push to browser
FR16: Epic 2 - SSE auto-reconnect
FR17: Epic 2 - Connection status indicator
FR18: Epic 3 - GET all measurements
FR19: Epic 3 - GET vendor averages and closest regions
FR20: Epic 3 - GET health check
FR21: Epic 3 - SSE stream for API consumers
FR22: Epic 3 - Consistent JSON error format
FR23: Epic 1 - Single command launch
FR24: Epic 1 - Data within 30s of launch
FR25: Epic 1 - Graceful shutdown
FR26: Epic 1 - Structured error logging
FR27: Epic 1 - Cycle success/failure logging
FR28: Epic 1 - Error resilience (no crash on probe failure)
FR29: Epic 2 - UI connection failure indication

## Epic List

### Epic 1: Instant Multi-Cloud Latency Measurement
Users can run a single command and immediately get real-time latency measurements for all Azure, AWS, and GCP regions, with structured logging for diagnostics.
**FRs covered:** FR1, FR2, FR3, FR4, FR5, FR6, FR7, FR23, FR24, FR25, FR26, FR27, FR28

### Epic 2: Live Monitoring Dashboard
Users can open a browser and see a real-time, auto-refreshing dashboard showing all cloud regions sorted by latency, vendor summaries, and connection status — with zero interaction required.
**FRs covered:** FR8, FR9, FR10, FR11, FR12, FR13, FR14, FR15, FR16, FR17, FR29
**UX-DRs covered:** UX-DR1 through UX-DR14

### Epic 3: REST API for External Consumers
API consumers (scripts, CI pipelines, custom tools) can retrieve latency data, vendor summaries, and health status via standard HTTP GET requests with consistent JSON responses.
**FRs covered:** FR18, FR19, FR20, FR21, FR22

## Epic 1: Instant Multi-Cloud Latency Measurement

Users can run a single command and immediately get real-time latency measurements for all Azure, AWS, and GCP regions, with structured logging for diagnostics.

### Story 1.1: Project Scaffolding & Package Setup

As a developer,
I want to set up the project structure with pyproject.toml and CI pipeline,
So that the codebase is ready for development with quality gates enforced.

**Acceptance Criteria:**

**Given** an empty repository
**When** the project scaffold is created
**Then** the `src/cloudlatency/` package structure exists with `__init__.py`, `__main__.py`
**And** `pyproject.toml` declares aiohttp>=3.13.0, python-json-logger as dependencies
**And** dev dependencies include pytest, pytest-asyncio, pytest-aiohttp, pytest-cov, ruff, radon
**And** `ruff check .` passes with zero warnings
**And** `.github/workflows/ci.yml` runs lint, test, and complexity checks
**And** `.gitignore` excludes standard Python artifacts

### Story 1.2: Cloud Region Endpoint Definitions

As a DevOps engineer,
I want the system to know all Azure, AWS, and GCP region health-check endpoints,
So that latency can be measured to every region across all three providers.

**Acceptance Criteria:**

**Given** the application is initialized
**When** region definitions are loaded from `regions.py`
**Then** Azure regions include all publicly available regions with valid HTTPS health-check URLs
**And** AWS regions include all publicly available regions with valid HTTPS health-check URLs
**And** GCP regions include all publicly available regions with valid HTTPS health-check URLs
**And** each region entry contains `provider`, `region_name`, and `endpoint_url`
**And** unit tests verify region data structure and non-empty lists per provider

### Story 1.3: Data Model & In-Memory Store

As a developer,
I want a data model and in-memory store for latency results,
So that probe measurements can be stored and retrieved consistently.

**Acceptance Criteria:**

**Given** a `LatencyResult` dataclass exists in `models.py`
**When** a measurement is recorded
**Then** it stores `provider`, `region`, `latency_ms`, `status` (ok/unreachable/error), and `timestamp`
**And** `LatencyStore` in `store.py` can update all results atomically for a measurement cycle
**And** `LatencyStore` can return all results sorted by latency ascending
**And** `LatencyStore` can return results filtered by provider
**And** `LatencyStore` can compute vendor averages and closest region per provider
**And** unit tests cover all store operations including edge cases (empty store, single provider)

### Story 1.4: Async Probe Engine with Concurrent Measurement

As a DevOps engineer,
I want the system to measure HTTPS latency to all cloud regions concurrently,
So that I get results for all 50+ regions within seconds.

**Acceptance Criteria:**

**Given** the probe engine is started with a list of regions and a `LatencyStore`
**When** a measurement cycle runs
**Then** all regions are probed concurrently via `asyncio.gather`
**And** each probe measures HTTPS response time using `aiohttp.ClientSession` with 5s timeout
**And** successful probes store `LatencyResult(status="ok")` with measured `latency_ms`
**And** failed probes (timeout, connection error) store `LatencyResult(status="unreachable")` without crashing other probes
**And** the complete cycle finishes within 8 seconds (NFR2)
**And** an `asyncio.Event` is set after each cycle to signal new data availability
**And** unit tests verify concurrent execution, timeout handling, and error isolation using mocked HTTP

### Story 1.5: Auto-Refresh Probe Loop & Structured Logging

As a DevOps engineer,
I want measurements to repeat automatically every 10 seconds with structured logs,
So that I always have fresh data and can diagnose issues.

**Acceptance Criteria:**

**Given** the probe engine is running
**When** a measurement cycle completes
**Then** the next cycle starts after a 10-second sleep
**And** each cycle logs success count, failure count, and duration in structured JSON format
**And** probe errors are logged with region and error details without crashing the loop
**And** the loop continues indefinitely until cancelled
**And** `logging_config.py` configures `python-json-logger` for all log output
**And** unit tests verify loop timing, logging output, and error resilience

### Story 1.6: CLI Entry Point & Application Lifecycle

As a DevOps engineer,
I want to start CloudLatency with a single command and stop it gracefully,
So that I can use it without any setup and shut it down cleanly.

**Acceptance Criteria:**

**Given** the package is installed
**When** the user runs `python -m cloudlatency`
**Then** the aiohttp web server starts on port 8080 (default)
**And** the probe engine starts automatically via `on_startup` hook
**And** latency data begins appearing within 30 seconds (FR24)
**And** `--port` CLI argument allows overriding the default port
**And** Ctrl+C triggers graceful shutdown: cancels probe task, closes connections, exits within 3 seconds (NFR11)
**And** if the port is already in use, the application logs a clear error and exits
**And** integration tests verify startup, probe initiation, and graceful shutdown

## Epic 2: Live Monitoring Dashboard

Users can open a browser and see a real-time, auto-refreshing dashboard showing all cloud regions sorted by latency, vendor summaries, and connection status — with zero interaction required.

### Story 2.1: SSE Broadcaster & Static File Serving

As a developer,
I want the backend to push measurement data to browsers via SSE and serve the frontend files,
So that the dashboard can receive live updates without polling.

**Acceptance Criteria:**

**Given** the aiohttp server is running and ProbeEngine is producing data
**When** a browser connects to `/api/v1/sse`
**Then** a `StreamResponse` is opened with `Content-Type: text/event-stream`
**And** each time the probe `asyncio.Event` fires, the current store data is written as a JSON SSE event to all connected clients
**And** disconnected clients are cleaned up without affecting other clients
**And** static files are served from `/` (index.html) and `/static/` (JS, favicon)
**And** SSE delivery latency is < 500ms from store update to browser receipt (NFR5)
**And** unit tests verify fan-out to multiple clients, client cleanup, and event format

### Story 2.2: HTML Page Structure & Dark Theme Foundation

As a DevOps engineer,
I want a dark-themed monitoring page that loads instantly,
So that I can see the dashboard without configuration or visual noise.

**Acceptance Criteria:**

**Given** the user navigates to `localhost:8080`
**When** the page loads
**Then** `index.html` renders with semantic HTML: `<header role="banner">`, `<main>`, `<table>` with `<thead>`/`<tbody>`/`<th scope="col">`
**And** Tailwind CSS is loaded via CDN
**And** CSS custom properties define the dark color system (--bg-primary, --bg-surface, --bg-header, --bg-row-alt, provider colors, semantic colors) per UX-DR1
**And** typography uses system font stack for UI text and monospace stack for latency values with `tabular-nums` per UX-DR13
**And** first meaningful paint occurs within 2 seconds (NFR4)
**And** `<html lang="en">` and `<meta name="viewport">` are present per UX-DR11

### Story 2.3: Header Bar with Connection Status Indicator

As a DevOps engineer,
I want to see the app title, connection status, and data freshness at a glance,
So that I can trust the data is live and current.

**Acceptance Criteria:**

**Given** the page is loaded
**When** the SSE connection is established
**Then** the header bar (48px, fixed position) shows "CloudLatency" title (left) and connection status + timestamp (right) per UX-DR2
**And** connection status indicator shows: green dot + "Connected", yellow pulsing dot + "Reconnecting...", red dot + "Disconnected" per UX-DR5
**And** timestamp shows "Updated Xs ago" with freshness coloring: green (0-10s), amber (11-30s), red (30s+) per UX-DR9
**And** status indicator has `role="status"` and `aria-live="polite"` per UX-DR11
**And** on SSE disconnect, data freezes in place (not cleared), timestamp turns red per UX-DR10

### Story 2.4: Summary Banner with Vendor Averages

As a DevOps engineer,
I want to see average latency and closest region per cloud provider at a glance,
So that I can quickly compare vendors without scanning the full table.

**Acceptance Criteria:**

**Given** measurement data is available via SSE
**When** data arrives
**Then** the summary banner (36px) displays 3 equal columns (AWS | Azure | GCP) per UX-DR3
**And** each column shows provider color accent, average latency (integer + "ms"), and closest region name + latency
**And** banner recalculates with each SSE event per UX-DR7
**And** loading state shows "—" placeholders before first data per UX-DR8
**And** banner has `role="complementary"` and `aria-label="Provider summary"` per UX-DR11

### Story 2.5: Latency Table with Sorted Data & Status Badges

As a DevOps engineer,
I want a sorted table of all cloud regions with latency and status,
So that I can instantly see which region is fastest and which are unreachable.

**Acceptance Criteria:**

**Given** measurement data arrives via SSE
**When** the table renders
**Then** rows display Provider (with color left-border), Region, Latency (monospace, right-aligned, "32 ms" format), and Status badge per UX-DR4 and UX-DR14
**And** rows are sorted ascending by latency; unreachable regions sort to bottom
**And** status badges are pill-shaped: OK (green), Slow (amber), Unreachable (red) — always with text label per UX-DR6
**And** table header is sticky with `aria-sort="ascending"` on Latency column per UX-DR11
**And** table re-renders within 100ms of receiving new data (NFR3)
**And** empty state shows "Waiting for data..." centered placeholder per UX-DR8
**And** keyboard navigation via Tab through table rows per NFR21

### Story 2.6: SSE Client with Auto-Reconnect & Progressive Population

As a DevOps engineer,
I want the browser to automatically reconnect if the data stream drops and show data as it arrives,
So that I always have fresh data without manual intervention.

**Acceptance Criteria:**

**Given** the browser is connected to the SSE stream
**When** the connection drops
**Then** `EventSource` auto-reconnects within 5 seconds (NFR9)
**And** if auto-reconnect fails, a manual fallback retry fires after 5s
**And** connection status updates to "Reconnecting..." during retry, "Disconnected" after max retries per UX-DR5
**And** during initial load, rows appear progressively as probes return, fading in over 150ms per UX-DR7
**And** `prefers-reduced-motion` disables fade animations per UX-DR11
**And** on reconnect, full data replaces stale state

### Story 2.7: Responsive Layout & Accessibility Polish

As a DevOps engineer,
I want the dashboard to be readable on any screen size and accessible via keyboard/screen reader,
So that I can use it on different devices and with assistive technology.

**Acceptance Criteria:**

**Given** the dashboard is rendered
**When** viewed on desktop (>=1024px)
**Then** full layout renders as designed (header + banner + full table) per UX-DR12
**And** on tablet (768-1023px), padding reduces slightly; all columns remain visible
**And** on mobile (<768px), header and banner stack vertically, table scrolls horizontally, rows are 44px min height
**And** all text/background pairings meet WCAG AA contrast (4.5:1) per NFR20
**And** `prefers-color-scheme` is respected (dark default, light via system preference) per UX-DR11
**And** focus rings visible on all focusable elements via Tailwind `focus:ring-2`
**And** Lighthouse accessibility audit scores 90+

## Epic 3: REST API for External Consumers

API consumers (scripts, CI pipelines, custom tools) can retrieve latency data, vendor summaries, and health status via standard HTTP GET requests with consistent JSON responses.

### Story 3.1: Health Check & Results Endpoints

As an API consumer,
I want to check service health and retrieve all current latency measurements via HTTP GET,
So that I can verify the service is running and access raw measurement data.

**Acceptance Criteria:**

**Given** the CloudLatency server is running and has measurement data
**When** a client sends GET `/api/v1/health`
**Then** a 200 response returns `{ "status": "healthy", "uptime_seconds": N, "last_cycle_at": "ISO8601" }`
**And** when a client sends GET `/api/v1/results`
**Then** a 200 response returns a JSON array of all latency results sorted by latency ascending
**And** each result includes `provider`, `region`, `latency_ms`, `status`, and `timestamp`
**And** response time is < 200ms (NFR1)
**And** if the store is empty (no measurements yet), results returns an empty array with 200
**And** unit tests verify response format, status codes, and empty-store edge case

### Story 3.2: Filtered Results & Summary Endpoints

As an API consumer,
I want to filter results by provider and retrieve vendor summaries,
So that I can build scripts that focus on specific providers or compare averages.

**Acceptance Criteria:**

**Given** measurement data exists in the store
**When** a client sends GET `/api/v1/results/{provider}` (e.g., `/api/v1/results/aws`)
**Then** a 200 response returns only results for that provider, sorted by latency
**And** if the provider is invalid, a 404 response returns `{ "error": "Provider not found", "code": "PROVIDER_NOT_FOUND" }`
**And** when a client sends GET `/api/v1/summary`
**Then** a 200 response returns vendor averages and closest region per provider
**And** response format: `{ "providers": { "aws": { "avg_ms": N, "closest": { "region": "...", "latency_ms": N } }, ... } }`
**And** response time is < 200ms (NFR1)
**And** unit tests verify filtering, summary computation, and error responses

### Story 3.3: SSE Stream for API Consumers & Error Format

As an API consumer,
I want to subscribe to live measurement updates via SSE and receive consistent error responses,
So that I can build real-time integrations and handle errors programmatically.

**Acceptance Criteria:**

**Given** the server is running
**When** a client connects to GET `/api/v1/sse`
**Then** the server sends SSE events with `data:` containing the full measurement payload as JSON
**And** events are sent after each probe cycle completes
**And** all API error responses use consistent format: `{ "error": "message", "code": "ERROR_CODE" }`
**And** 404 for unknown routes, 500 for internal errors, 503 if service is starting up
**And** CORS headers allow `localhost:*` origins for all API endpoints
**And** unit tests verify SSE event format, error responses, and CORS headers

### Story 3.4: API Documentation

As an API consumer,
I want clear documentation of all REST endpoints,
So that I can integrate with CloudLatency without reading the source code.

**Acceptance Criteria:**

**Given** the `docs/api.md` file exists
**When** a developer reads the documentation
**Then** all 5 endpoints are documented: `/health`, `/results`, `/results/{provider}`, `/summary`, `/sse`
**And** each endpoint documents: HTTP method, URL, request parameters, response format with example JSON, error responses, and status codes
**And** SSE event format is documented with example payload
**And** documentation matches the actual API behavior (verified by comparing with tests)
