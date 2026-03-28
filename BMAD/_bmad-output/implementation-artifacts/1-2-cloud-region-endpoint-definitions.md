# Story 1.2: Cloud Region Endpoint Definitions

Status: done

## Story

As a DevOps engineer,
I want the system to know all Azure, AWS, and GCP region health-check endpoints,
so that latency can be measured to every region across all three providers.

## Acceptance Criteria

1. **Given** the application is initialized **When** region definitions are loaded from `regions.py` **Then** Azure regions include all publicly available regions with valid HTTPS health-check URLs
2. **And** AWS regions include all publicly available regions with valid HTTPS health-check URLs
3. **And** GCP regions include all publicly available regions with valid HTTPS health-check URLs
4. **And** each region entry contains `provider`, `region_name`, and `endpoint_url`
5. **And** unit tests verify region data structure and non-empty lists per provider

## Tasks / Subtasks

- [x] Task 1: Create `src/cloudlatency/regions.py` with region data structures (AC: #4)
  - [x] Define a `Region` NamedTuple with fields: `provider`, `region_name`, `endpoint_url`
  - [x] Define provider constants: `PROVIDER_AWS = "aws"`, `PROVIDER_AZURE = "azure"`, `PROVIDER_GCP = "gcp"`
  - [x] Define `PROVIDERS` list for iteration
- [x] Task 2: Add Azure region endpoints (AC: #1)
  - [x] 38 Azure regions with Azure Monitor warm ingest endpoints
- [x] Task 3: Add AWS region endpoints (AC: #2)
  - [x] 29 AWS regions with DynamoDB regional endpoints
- [x] Task 4: Add GCP region endpoints (AC: #3)
  - [x] 39 GCP regions with Cloud Run regional endpoints
- [x] Task 5: Create helper functions
  - [x] `get_all_regions() -> list[Region]` returning flat list of all regions
  - [x] `get_regions_by_provider(provider: str) -> list[Region]` for filtering
- [x] Task 6: Create `tests/test_regions.py` (AC: #5)
  - [x] Test that each provider has at least 5 regions
  - [x] Test that all regions have non-empty `provider`, `region_name`, `endpoint_url`
  - [x] Test that all endpoint URLs start with `https://`
  - [x] Test `get_all_regions()` returns combined list
  - [x] Test `get_regions_by_provider()` filters correctly
  - [x] Test invalid provider returns empty list

## Dev Notes

### Architecture Compliance

- **File:** `src/cloudlatency/regions.py` — cloud region endpoint definitions
- **Depends on:** Nothing (leaf module)
- **Module responsibility:** Single responsibility — region data only, no HTTP logic
- **Naming:** Module `regions.py`, constants `UPPER_SNAKE_CASE`, functions `snake_case`
- **Data structure:** Use a dataclass or NamedTuple for `Region` with `provider`, `region_name`, `endpoint_url` fields
- **No imports from other cloudlatency modules** — this is a leaf dependency

### Endpoint Strategy

- Endpoints must be publicly accessible HTTPS URLs that respond to GET requests without authentication
- Use well-known health-check or status endpoints per provider
- Azure: Use `https://<region>.prod.warm.ingest.monitor.core.windows.net/` or similar Azure Front Door endpoints
- AWS: Use `https://ec2.<region>.amazonaws.com/ping` or S3 endpoints
- GCP: Use `https://<region>-run.googleapis.com/` or similar
- Endpoints stored as static data in config-like structure (not hardcoded in probe logic)
- Architecture says: "Store endpoints in a config file (not hardcoded)" — regions.py serves as the config

### Previous Story (1.1) Learnings

- Build backend must be `setuptools.build_meta` (not `_legacy`)
- Ruff lint config goes in `[tool.ruff.lint]` section
- `pragma: no cover` for `if __name__` guards
- 100% coverage achieved — maintain this standard

### References

- [Source: architecture.md#Module Organization] — regions.py depends on nothing
- [Source: architecture.md#FR Category Mapping] — FR1-FR7 map to regions.py, probe.py, models.py
- [Source: epics.md#Story 1.2] — Acceptance criteria
- [Source: prd.md#Functional Requirements] — FR1, FR2, FR3

## Change Log

- 2026-03-28: Story 1.2 implemented — 106 regions across 3 providers, 19 tests

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4 (Cascade)

### Debug Log References

No issues encountered.

### Completion Notes List

- 22 total tests passing (3 from 1.1 + 19 new), 100% coverage
- AWS: 29 regions (DynamoDB endpoints), Azure: 38 regions (Monitor endpoints), GCP: 39 regions (Cloud Run endpoints)
- Total: 106 regions across all providers

### File List

- `src/cloudlatency/regions.py` (new)
- `tests/test_regions.py` (new)
