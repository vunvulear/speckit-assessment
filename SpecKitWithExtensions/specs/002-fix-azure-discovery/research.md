# Research: Fix Azure Region Discovery

## Decision 1: Azure Region Discovery Method

**Decision**: Use a hardcoded list of Azure regions with Azure Blob Storage probe endpoints.

**Rationale**: The Azure Management API (`management.azure.com`) requires an OAuth2 bearer token for authentication. This creates a dependency on Azure AD credentials and adds complexity. A hardcoded list avoids all authentication requirements while providing reliable region data.

**Alternatives Considered**:

| Alternative | Pros | Cons |
|-------------|------|------|
| Azure Management API | Dynamic discovery | Requires auth token, Azure AD setup |
| Azure Resource Graph | Real-time data | Requires auth, SDK dependency |
| Scraping Azure status page | No auth needed | Fragile, TOS violation risk |
| **Hardcoded region list** | **No auth, reliable, fast** | **Manual updates for new regions** |

## Decision 2: Azure Probe Endpoint Pattern

**Decision**: Use Azure Blob Storage endpoints: `https://<regioncode>.blob.core.windows.net`

**Rationale**: Azure Blob Storage has a well-known endpoint per region. These endpoints are publicly resolvable and respond to HTTPS HEAD requests without authentication. The response may be a 400 (missing headers) but the TCP/TLS round-trip measures latency accurately.

**Alternatives Considered**:

| Alternative | Pros | Cons |
|-------------|------|------|
| `<region>.status.azure.com` | Status page | Not all regions, may not respond to HEAD |
| Azure CDN endpoints | Fast | Not region-specific |
| `<region>.cloudapp.azure.com` | Region-specific | DNS-only, no HTTP response |
| **`<region>.blob.core.windows.net`** | **Public, reliable, per-region** | **Returns 400 on HEAD (still measures latency)** |

Note: The Azure Blob Storage endpoint format uses the region code directly in the subdomain. Some regions use a storage account naming pattern. For probing, we use `https://<regioncode>.blob.core.windows.net` which resolves to the region's storage infrastructure.

## Decision 3: Handling Non-200 Responses

**Decision**: Treat ANY HTTP response (including 400, 403, 409) as "reachable." Only connection failures and timeouts indicate unreachable.

**Rationale**: The prober already implements this correctly — any HTTP response means the server is reachable and the round-trip time is valid. Azure Blob Storage returns 400 for unauthenticated HEAD requests, but the latency measurement is still accurate.

## Azure Region List Source

As of March 2026, Microsoft lists 60+ generally available Azure regions. The full list is available at:
- https://azure.microsoft.com/en-us/explore/global-infrastructure/geographies/
- Azure CLI: `az account list-locations`

The hardcoded list will include all GA regions with their standard names and codes.
