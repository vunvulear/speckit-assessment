# Data Model

<!-- docguard:version 1.0.0 -->
<!-- docguard:status approved -->
<!-- docguard:last-reviewed 2026-03-26 -->
<!-- docguard:owner @cloudlatency -->

> **Canonical document** — Design intent. This file describes the data structures and their relationships.  
> ⚠️ Schema changes require this doc to be updated FIRST.

| Metadata | Value |
|----------|-------|
| **Status** | ![Status](https://img.shields.io/badge/status-approved-green) |
| **Version** | `1.0.0` |
| **Last Updated** | 2026-03-26 |
| **Owner** | @cloudlatency |

---

## Entities

| Entity | Storage | Primary Key | Description |
|--------|---------|-------------|-------------|
| CloudProvider | In-memory | `id` (string) | Cloud vendor: aws, azure, gcp |
| CloudRegion | In-memory | (`provider_id`, `region_code`) | Geographic region within a provider |
| LatencyMeasurement | In-memory | (`provider_id`, `region_code`, `measured_at`) | Single latency reading |
| VendorSummary | In-memory (computed) | `provider_id` | Aggregated vendor statistics |
| LatencySnapshot | In-memory | `measured_at` | Complete measurement cycle result |

## Schema Definitions

### CloudProvider

| Field | Type | Required | Default | Constraints | Description |
|-------|------|----------|---------|-------------|-------------|
| id | string | Yes | — | One of: `aws`, `azure`, `gcp` | Unique vendor identifier |
| name | string | Yes | — | Non-empty | Display name (AWS, Azure, GCP) |

### CloudRegion

| Field | Type | Required | Default | Constraints | Description |
|-------|------|----------|---------|-------------|-------------|
| provider_id | string | Yes | — | Valid CloudProvider.id | Parent provider |
| region_code | string | Yes | — | Non-empty, provider-specific | e.g., `us-east-1` |
| region_name | string | Yes | — | Non-empty | Human-readable name |
| endpoint_url | string | Yes | — | Valid HTTPS URL | URL for HEAD request probing |

### LatencyMeasurement

| Field | Type | Required | Default | Constraints | Description |
|-------|------|----------|---------|-------------|-------------|
| provider_id | string | Yes | — | Valid CloudProvider.id | Provider reference |
| region_code | string | Yes | — | Valid CloudRegion.region_code | Region reference |
| latency_ms | float or null | Yes | — | >= 0 when reachable, null otherwise | Round-trip time in ms |
| is_reachable | boolean | Yes | — | — | True if response within 5s timeout |
| measured_at | datetime | Yes | — | ISO 8601, UTC | Measurement timestamp |

### VendorSummary

| Field | Type | Required | Default | Constraints | Description |
|-------|------|----------|---------|-------------|-------------|
| provider_id | string | Yes | — | Valid CloudProvider.id | Provider reference |
| provider_name | string | Yes | — | Non-empty | Display name |
| average_latency_ms | float or null | Yes | — | Computed over reachable regions only | Arithmetic mean latency |
| closest_region_code | string or null | Yes | — | — | Region with minimum latency |
| closest_region_name | string or null | Yes | — | — | Human-readable closest region |
| closest_latency_ms | float or null | Yes | — | — | Latency of closest region |
| total_regions | int | Yes | — | >= 0 | Total regions for this provider |
| reachable_regions | int | Yes | — | >= 0, <= total_regions | Regions that responded |

### LatencySnapshot

| Field | Type | Required | Default | Constraints | Description |
|-------|------|----------|---------|-------------|-------------|
| measured_at | datetime | Yes | — | ISO 8601, UTC | Cycle timestamp |
| measurements | list | Yes | — | Sorted by latency_ms ascending | All region measurements |
| vendor_summaries | list | Yes | — | Exactly 3 entries | One summary per provider |

## Relationships

| From | To | Type | FK/Reference | Cascade |
|------|-----|------|-------------|---------|
| CloudRegion | CloudProvider | many:1 | `provider_id` → `CloudProvider.id` | N/A (in-memory) |
| LatencyMeasurement | CloudRegion | many:1 | (`provider_id`, `region_code`) | N/A |
| LatencySnapshot | LatencyMeasurement | 1:many | Contains list | N/A |
| LatencySnapshot | VendorSummary | 1:3 | Contains list | N/A |

## Indexes

N/A — All data is stored in-memory with no persistent database. Lookups use Python dict/list operations.

## Migration Strategy

N/A — No persistent storage in v1. All data is ephemeral and reconstructed on each application restart.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-03-26 | CloudLatency | Initial data model from spec entities |
