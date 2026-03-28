---
title: "Product Brief Distillate: CloudLatency"
type: llm-distillate
source: "product-brief-cloudlatency.md"
created: "2026-03-28"
purpose: "Token-efficient context for downstream PRD creation"
---

# Product Brief Distillate: CloudLatency

## Requirements Hints

- HTTPS-only probing — no ICMP, TCP, or custom probe methods in v1
- 10-second refresh cycle is a hard requirement, not configurable in v1
- REST API must be fully independent of UI — the UI is a consumer, not coupled
- SSE preferred for live updates (user mentioned "automatically updated whenever there are updates")
- Table must sort lowest-to-highest latency across all regions from all three providers
- Two charts required: (1) average latency per vendor, (2) closest region per vendor
- Table appears above charts in the layout
- Logging must be minimal but sufficient to detect backend and UI issues — structured logging implied
- Cross-browser: Chrome, Firefox, Edge, Safari

## Technical Constraints

- **Language**: Python (hard constraint)
- **Deployment**: Local execution, any environment — no Docker requirement, no cloud-specific dependencies
- **Architecture**: Multi-component split — measurement engine, REST API, web UI as separate concerns
- **Future-proofing**: REST API must support replacing the web UI entirely without backend changes
- **No API keys required** for measurement — must use publicly accessible cloud endpoints

## Quality & Engineering Standards

- **Test coverage**: > 90% line coverage (hard gate)
- **Complexity**: Minimal cyclomatic complexity — target CC ≤ 5 per function
- **Testing strategy**: Shift-left — tests written alongside or before implementation
- **Complexity metrics**: Must be actively monitored and kept minimal (user specifically called this out)

## User Context

- **Target users**: DevOps engineers and SREs evaluating/validating cloud region choices
- **Secondary users**: Platform engineers and architects for strategic multi-cloud decisions
- **Usage model**: Run locally on demand — not a persistent service in v1
- **Skill level**: Technical users comfortable with CLI — single-command launch expected

## Scope Signals

- **Firmly in**: Multi-cloud (Azure + AWS + GCP), sorted table, two chart types, auto-refresh, REST API, unit tests, local deployment
- **Firmly out**: Historical data, auth, SaaS, alerting, non-HTTPS probes, custom region filtering
- **Open for PRD**: Chart library choice, specific Python web framework, SSE vs WebSocket decision, endpoint discovery strategy (static list vs dynamic)

## Open Questions for PRD Phase

- How are cloud region endpoints discovered/maintained? Static registry or dynamic discovery?
- What Python web framework? (Flask, FastAPI, aiohttp — user did not specify)
- What chart library for the frontend? (Chart.js, D3, or Python-rendered?)
- Should unreachable regions show in the table with an error state, or be hidden?
- What happens if all regions for a provider are unreachable? How is this surfaced?
- Exact license: user said "free of use" — MIT is the likely choice but not confirmed

## Rejected Ideas / Not Discussed

- No mention of containerization (Docker) — keep deployment simple
- No mention of configuration files or settings UI
- No multi-user or team features
- No data export (CSV, JSON download) — could be a v2 feature via REST API
