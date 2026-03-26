# Data Model: Cloud Latency Monitor

**Branch**: `001-cloud-latency-monitor` | **Date**: 2026-03-26

## Entities

### CloudProvider

Represents one of the three supported cloud vendors.

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique identifier: `aws`, `azure`, `gcp` |
| name | string | Display name: `AWS`, `Azure`, `GCP` |

**Constraints**:

- Fixed set of three providers.
- `id` is the canonical key used across all references.

### CloudRegion

Represents a geographic region within a cloud provider.

| Field | Type | Description |
|-------|------|-------------|
| provider_id | string | Reference to CloudProvider.id |
| region_code | string | Provider-specific region code (e.g., `us-east-1`, `westeurope`, `us-central1`) |
| region_name | string | Human-readable name (e.g., `US East (N. Virginia)`) |
| endpoint_url | string | HTTPS URL used for HEAD request latency probing |

**Constraints**:

- Composite uniqueness: (`provider_id`, `region_code`).
- `endpoint_url` MUST be a valid HTTPS URL.
- Discovered dynamically at startup via provider APIs.

### LatencyMeasurement

A single latency reading for a region at a point in time.

| Field | Type | Description |
|-------|------|-------------|
| provider_id | string | Reference to CloudProvider.id |
| region_code | string | Reference to CloudRegion.region_code |
| latency_ms | float or null | Round-trip time in milliseconds; null if unreachable |
| is_reachable | boolean | True if HEAD request completed within 5s timeout |
| measured_at | datetime (ISO 8601) | Timestamp when measurement was taken |

**Constraints**:

- `latency_ms` MUST be null when `is_reachable` is false.
- `latency_ms` MUST be >= 0 when `is_reachable` is true.
- `measured_at` MUST be in UTC.

### VendorSummary

Aggregated latency data per cloud provider, computed from the latest measurement cycle.

| Field | Type | Description |
|-------|------|-------------|
| provider_id | string | Reference to CloudProvider.id |
| provider_name | string | Display name of the provider |
| average_latency_ms | float or null | Mean latency across all reachable regions; null if all unreachable |
| closest_region_code | string or null | Region code with lowest latency; null if all unreachable |
| closest_region_name | string or null | Human-readable name of closest region |
| closest_latency_ms | float or null | Latency of the closest region; null if all unreachable |
| total_regions | int | Total number of regions for this provider |
| reachable_regions | int | Number of regions that responded within timeout |

**Constraints**:

- `average_latency_ms` computed only over reachable regions.
- `closest_region_code` is the region with the minimum `latency_ms` among reachable regions.

### LatencySnapshot

The complete result of one measurement cycle, sent to the UI via SSE.

| Field | Type | Description |
|-------|------|-------------|
| measured_at | datetime (ISO 8601) | Timestamp of this measurement cycle |
| measurements | list[LatencyMeasurement] | All individual region measurements, sorted by latency ascending |
| vendor_summaries | list[VendorSummary] | One summary per provider |

**Constraints**:

- `measurements` MUST be sorted by `latency_ms` ascending (unreachable regions at bottom).
- `vendor_summaries` MUST contain exactly 3 entries (one per provider).

## Relationships

```text
CloudProvider (1) ──── (many) CloudRegion
CloudRegion   (1) ──── (many) LatencyMeasurement
LatencySnapshot (1) ── (many) LatencyMeasurement
LatencySnapshot (1) ── (3)    VendorSummary
```

## State Transitions

The latency engine operates in a continuous loop:

```text
STARTING ──► DISCOVERING ──► MEASURING ──► PUBLISHING ──► WAITING ──► MEASURING
                  │                                           │
                  └── (on startup or re-discovery trigger) ◄──┘
```

- **STARTING**: Engine initializes configuration and HTTP client.
- **DISCOVERING**: Fetches region lists from provider APIs.
- **MEASURING**: Sends concurrent HTTPS HEAD requests to all regions (5s timeout).
- **PUBLISHING**: Computes VendorSummary aggregates, creates LatencySnapshot, pushes to API.
- **WAITING**: Sleeps until next 10-second cycle.
