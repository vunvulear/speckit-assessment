# Implementation Plan: Fix Azure Region Discovery

**Feature**: 002-fix-azure-discovery
**Branch**: `002-fix-azure-discovery`
**Created**: 2026-03-26

## Technical Context

- **Language**: Python 3.11+
- **Framework**: FastAPI + aiohttp
- **Affected file**: `cloudlatency/engine/discovery.py`
- **Test files**: `tests/unit/test_discovery.py`
- **Dependencies**: No new dependencies required

## Constitution Check

- **II. Test-First Development**: Tests will be updated before implementation changes.
- **VI. Component Separation**: Change is isolated to the engine discovery module.
- **IV. Simplicity**: Hardcoded list is simpler than an authenticated API call.

## Root Cause Analysis

The current `discover_azure_regions()` function calls the Azure Management API at:
`https://management.azure.com/subscriptions/.../locations?api-version=2022-12-01`

This endpoint requires an OAuth2 bearer token. Without authentication, it returns HTTP 403, resulting in zero Azure regions being discovered.

## Solution Design

### Approach

Replace the Azure Management API call with a hardcoded registry of all GA Azure regions. Each region entry includes:

- Region code (e.g., `eastus`)
- Display name (e.g., `East US`)
- Probe endpoint URL: `https://<regioncode>.blob.core.windows.net`

### Changes Required

1. **`cloudlatency/engine/discovery.py`**: Replace `discover_azure_regions()` body with hardcoded region list. Remove the aiohttp API call. Return `CloudRegion` objects from the static list.

2. **`tests/unit/test_discovery.py`**: Update Azure discovery tests to verify the hardcoded list returns regions without any HTTP mocking. Remove the `aioresponses` mock for the Azure Management API.

3. **No changes needed** to: models, schemas, routes, prober, scheduler, SSE, UI.

### Probe Endpoint Validation

Azure Blob Storage endpoints (`https://<region>.blob.core.windows.net`) are:

- Publicly resolvable DNS names
- Respond to HTTPS HEAD requests (HTTP 400 without auth headers)
- The prober already treats any HTTP response as "reachable"
- Round-trip time accurately measures latency to the region

## Risk Assessment

| Risk | Mitigation |
| ---- | ---------- |
| New Azure regions not auto-discovered | Document in DRIFT-LOG; update list manually |
| Blob endpoint URL pattern changes | Stable since 2014; very low risk |
| Some regions may not have blob endpoints | Include only confirmed GA regions |

## Phase Summary

| Phase | Description | Files |
| ----- | ----------- | ----- |
| 1 | Update tests (test-first) | tests/unit/test_discovery.py |
| 2 | Replace Azure discovery implementation | cloudlatency/engine/discovery.py |
| 3 | Run full test suite + lint | All |
| 4 | Verify in browser | Manual |
