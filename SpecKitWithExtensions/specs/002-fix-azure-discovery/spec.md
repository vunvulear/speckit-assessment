# Feature Specification: Fix Azure Region Discovery

**Feature Branch**: `002-fix-azure-discovery`
**Created**: 2026-03-26
**Status**: Draft
**Input**: User description: "Fix Azure region discovery to use publicly accessible endpoints without authentication. Currently the Azure Management API returns 403 because it requires an auth token. Replace with a hardcoded list of known Azure regions using publicly accessible blob storage endpoints for latency probing."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Azure Regions Appear in Latency Table (Priority: P1)

A user opens the CloudLatency web application and sees Azure regions alongside AWS and GCP regions in the sorted latency table. Azure regions are probed using publicly accessible blob storage endpoints that do not require authentication. The table includes all major Azure regions with accurate latency measurements.

**Why this priority**: Without Azure regions, the application fails to deliver on its core promise of comparing all three major cloud vendors. This is a blocking defect.

**Independent Test**: Open the web UI and verify that Azure regions appear in the latency table with numeric latency values (not all "unreachable"). Confirm at least 40 Azure regions are listed.

**Acceptance Scenarios**:

1. **Given** the application starts and discovers regions, **When** the user views the latency table, **Then** Azure regions appear alongside AWS and GCP regions with measured latency values.
2. **Given** Azure regions are being probed, **When** the measurement cycle completes, **Then** at least 80% of Azure regions show numeric latency values (are reachable).
3. **Given** the Azure discovery mechanism uses a hardcoded region list, **When** a new Azure region is added by Microsoft, **Then** only a code update is required to add the new region (documented in maintenance notes).

---

### User Story 2 - Azure Data in Vendor Charts (Priority: P1)

The average latency chart and closest region chart both include Azure as a vendor with accurate data. Azure is no longer missing or shown as "N/A" in the vendor comparison charts.

**Why this priority**: Charts showing only AWS and GCP provide an incomplete and misleading comparison. Azure data is essential for the vendor comparison to be meaningful.

**Independent Test**: View both charts and confirm Azure has a colored bar with numeric latency data in both the average and closest-region charts.

**Acceptance Scenarios**:

1. **Given** Azure latency data has been collected, **When** the user views the average latency chart, **Then** Azure appears as a bar with a numeric average latency value.
2. **Given** Azure latency data has been collected, **When** the user views the closest region chart, **Then** Azure's closest region is displayed with its name and latency value.

---

### User Story 3 - Resilient Azure Probing (Priority: P2)

Azure blob storage endpoints may occasionally return non-200 status codes (e.g., 400 for missing headers). The system treats any HTTP response (regardless of status code) as "reachable" and measures the round-trip time. Only connection failures and timeouts are treated as "unreachable."

**Why this priority**: Blob storage endpoints respond to HEAD requests but may return 400 or 409. Treating these as unreachable would incorrectly mark working regions as down.

**Independent Test**: Mock an Azure endpoint returning HTTP 400 and verify the region is still marked as reachable with a valid latency measurement.

**Acceptance Scenarios**:

1. **Given** an Azure blob storage endpoint returns HTTP 400, **When** the prober measures it, **Then** the region is marked as reachable with a valid latency value.
2. **Given** an Azure blob storage endpoint times out, **When** the prober measures it, **Then** the region is marked as unreachable with null latency.
3. **Given** an Azure endpoint refuses the connection, **When** the prober measures it, **Then** the region is marked as unreachable.

---

### Edge Cases

- What happens if Azure adds new regions? The hardcoded list must be updated in code; the application will not discover new Azure regions automatically. This is a known trade-off documented in assumptions.
- What happens if Azure changes blob storage endpoint URLs? The endpoint pattern `https://<account>.blob.core.windows.net` is a stable Azure Storage URL format unlikely to change.
- How does the system handle Azure regions that have blob storage in preview or limited availability? These regions are excluded from the hardcoded list until generally available.

## Clarifications

### Session 2026-03-26

- Q: Why not use the Azure Management API? → A: It requires an OAuth2 bearer token (Azure AD authentication), which adds complexity and a dependency on Azure credentials. The application should work without any cloud provider credentials.
- Q: What Azure endpoint should be used for probing? → A: Azure Blob Storage endpoints (`https://<region-specific-account>.blob.core.windows.net`). These are publicly accessible and respond to unauthenticated HEAD requests.
- Q: How many Azure regions should be included? → A: All generally available Azure regions (approximately 60+ as of 2026).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST include a hardcoded list of all generally available Azure regions with their display names and probe endpoints.
- **FR-002**: Azure probe endpoints MUST be publicly accessible without any authentication credentials.
- **FR-003**: System MUST use Azure Blob Storage endpoints (`https://<account>.blob.core.windows.net`) for latency measurement via HTTPS HEAD requests.
- **FR-004**: System MUST treat any HTTP response (including 400, 403, 409) from an Azure endpoint as "reachable" and record the round-trip latency.
- **FR-005**: System MUST mark Azure regions as "unreachable" only on connection timeout, DNS failure, or connection refused errors.
- **FR-006**: Azure regions MUST appear in the latency table, average chart, and closest region chart alongside AWS and GCP data.
- **FR-007**: Existing unit tests for Azure discovery MUST be updated to use the new hardcoded approach instead of mocking the Management API.
- **FR-008**: The hardcoded Azure region list MUST be maintainable — stored as a clear data structure with region code, display name, and endpoint URL.

### Key Entities

- **Azure Region**: A geographic Azure datacenter region. Attributes: region code (e.g., "eastus"), display name (e.g., "East US"), probe endpoint URL.
- **Azure Region Registry**: The hardcoded data structure containing all known Azure regions and their probe endpoints.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least 50 Azure regions appear in the latency table when the application starts.
- **SC-002**: At least 80% of listed Azure regions show numeric latency values (are reachable).
- **SC-003**: Azure appears in both vendor charts (average and closest region) with numeric data.
- **SC-004**: All existing tests continue to pass after the change.
- **SC-005**: Test coverage remains above 90%.
- **SC-006**: No Azure credentials or authentication tokens are required to run the application.

## Assumptions

- Azure Blob Storage endpoints are publicly accessible and respond to unauthenticated HTTPS HEAD requests.
- The endpoint pattern `https://<account>.blob.core.windows.net` is stable and maintained by Microsoft.
- New Azure regions are added infrequently enough that manual updates to the hardcoded list are acceptable.
- The hardcoded list covers all generally available (GA) Azure regions as of March 2026.
- Preview or restricted regions are excluded from the list.
