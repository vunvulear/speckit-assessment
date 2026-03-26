# Tasks: Fix Azure Region Discovery

**Input**: Design documents from `/specs/002-fix-azure-discovery/`
**Prerequisites**: plan.md (required), spec.md (required), research.md

## Phase 1: Update Tests (Test-First)

- [x] T001 Update Azure discovery tests in tests/unit/test_discovery.py to expect hardcoded regions returned without HTTP mocking
- [x] T002 Add test verifying at least 50 Azure regions are returned by discover_azure_regions()
- [x] T003 Add test verifying Azure regions have valid blob storage probe endpoints
- [x] T004 Add test verifying Azure regions have provider_id="azure"

## Phase 2: Replace Azure Discovery Implementation

- [x] T005 Create AZURE_REGIONS hardcoded registry in cloudlatency/engine/discovery.py with all GA Azure regions (region_code, display_name, probe_url)
- [x] T006 Replace discover_azure_regions() to return CloudRegion objects from the hardcoded AZURE_REGIONS registry instead of calling the Management API
- [x] T007 Remove the Azure Management API URL and HTTP client call from discover_azure_regions()

## Phase 3: Validation

- [x] T008 Run full test suite — all tests must pass with 90%+ coverage
- [x] T009 Run ruff lint and black formatting on changed files
- [x] T010 Update CHANGELOG.md with the Azure discovery fix
- [x] T011 Log drift in DRIFT-LOG.md (Azure discovery changed from dynamic API to hardcoded list)

## Phase 4: Verification

- [x] T012 Start the application and verify Azure regions appear in the latency table
- [x] T013 Verify Azure appears in both vendor charts with numeric data
- [x] T014 Run DocGuard score to confirm compliance maintained
