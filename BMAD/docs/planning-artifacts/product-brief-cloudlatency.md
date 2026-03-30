---
title: "Product Brief: CloudLatency"
status: "complete"
created: "2026-03-28"
updated: "2026-03-28"
inputs: [user-interview]
---

# Product Brief: CloudLatency

## Executive Summary

CloudLatency is an open-source, real-time latency monitoring tool that measures HTTPS response times to every Azure, AWS, and GCP region worldwide. It gives DevOps engineers and SREs an instant, auto-refreshing view of cloud network performance — sorted tables, vendor-average charts, and closest-region indicators — all updating every 10 seconds without manual intervention.

Today, teams choosing or validating cloud regions rely on sporadic manual tests, vendor-specific dashboards, or expensive third-party monitoring suites. CloudLatency replaces that friction with a single lightweight tool that runs locally, works across all three major providers simultaneously, and requires zero configuration. It is free to use, open source, and designed from the ground up for simplicity.

## The Problem

DevOps and SRE teams routinely need to answer: *"Which cloud region gives us the lowest latency from where we are right now?"* The answer changes depending on the provider, the time of day, and network conditions — yet the tools to answer it are fragmented:

- **Vendor dashboards** only show their own regions, forcing tab-switching across three consoles.
- **Manual curl/ping tests** are tedious, non-repeating, and produce raw numbers with no visualisation.
- **Commercial monitoring platforms** (Datadog, ThousandEyes) are overkill for region selection and carry significant licensing costs.
- **Stale data** — teams often pick a region based on a one-time test and never re-validate as conditions shift.

The result: suboptimal region choices, undetected latency regressions, and wasted engineering time cobbling together ad-hoc scripts.

> **Note:** CloudLatency measures latency *from the machine running it*. Results reflect your specific network path, not universal truth — which is exactly what teams need when deciding where to deploy from their infrastructure.

## The Solution

CloudLatency is a Python-based web application that runs locally and provides:

- **Sorted latency table** — every cloud region across Azure, AWS, and GCP ranked lowest-to-highest, refreshed every 10 seconds.
- **Vendor average chart** — at a glance, see which provider delivers the best average performance from your location.
- **Closest region chart** — the single best region per vendor, updated live.
- **Auto-updating UI** — the page reflects new measurements as they arrive, with no manual refresh.

The backend and frontend are separated into distinct components, exposing a REST API that can be consumed by custom dashboards, CLI tools, or automation pipelines independently of the web UI.

## What Makes This Different

- **Multi-cloud in one view** — Azure, AWS, and GCP side-by-side, not three separate tools.
- **Zero cost, zero setup** — runs locally with a single command, no API keys, no cloud accounts required for measurement.
- **Component separation** — the REST API is a first-class citizen, not an afterthought. The UI is one consumer; future consumers (CI pipelines, Slack bots, custom dashboards) plug in without changes.
- **Quality-first engineering** — >90% test coverage, minimal complexity metrics, shift-left testing strategy. The codebase is as clean as the UI.

## Technical Approach

CloudLatency is built in Python with a strict component separation:

- **Measurement Engine** — async HTTPS probes to known cloud region endpoints, running concurrently across all providers.
- **REST API** — exposes all latency data as JSON endpoints. This is the system's backbone — the UI is one consumer, but CLI tools, CI pipelines, or custom dashboards can replace it without any backend changes.
- **Web UI** — lightweight frontend consuming the REST API, using Server-Sent Events (SSE) for live push updates.

The architecture enforces a clean boundary: the API layer knows nothing about the UI, and the UI knows nothing about how measurements are taken.

## Who This Serves

**Primary: DevOps Engineers & SREs** — professionals evaluating cloud regions for new deployments, validating existing region choices, or troubleshooting latency issues. They need fast, reliable, multi-cloud data without procurement overhead.

**Secondary: Platform Engineers & Architects** — making strategic multi-cloud or region-expansion decisions. They benefit from the REST API for integrating latency data into capacity-planning workflows.

## Success Criteria

| Metric | Target |
| ------ | ------ |
| Test coverage | > 90% line coverage |
| Cyclomatic complexity | All functions CC ≤ 5 |
| Measurement refresh | Every 10 seconds |
| Cross-browser support | Chrome, Firefox, Edge, Safari |
| Time to first result | < 30 seconds after launch |
| REST API independence | UI can be fully replaced without backend changes |
| Probe success rate | > 95% of known regions reachable |
| Observability | Backend errors detectable via structured logs |

## Scope

**In (v1):**
- HTTPS latency probing to all Azure, AWS, and GCP regions
- Auto-refreshing sorted latency table
- Average-latency-per-vendor chart
- Closest-region-per-vendor chart
- Live page updates (SSE or WebSocket)
- REST API for all data
- Unit tests with >90% coverage
- Minimal, readable UI
- Local deployment (single command)
- MIT / free-to-use license

**Out (v1):**

- Historical data persistence or trending
- User authentication or multi-tenancy
- Hosted/SaaS deployment
- Custom region selection or filtering
- Alerting or notifications
- Non-HTTPS probing methods

**Known Risks:**

- Cloud providers may change or block health-check endpoints without notice — the endpoint registry must be maintainable.
- Firewall or proxy environments may skew or block measurements — the tool should report unreachable regions gracefully.
- 10-second refresh with many concurrent probes may stress constrained networks — backpressure handling is required.

## Vision

If CloudLatency succeeds as a local tool, it becomes the de facto open-source standard for multi-cloud latency benchmarking. Future iterations could add historical trending, region comparison over time, CI/CD integration (fail a pipeline if latency exceeds a threshold), and a community-contributed endpoint registry. The component-separated architecture ensures the core measurement engine can power use cases far beyond the initial web UI.
