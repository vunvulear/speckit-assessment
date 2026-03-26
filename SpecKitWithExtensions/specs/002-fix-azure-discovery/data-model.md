# Data Model: Fix Azure Region Discovery

## Entity: Azure Region Registry

The Azure Region Registry is a static data structure containing all known Azure regions.

### Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| region_code | string | Azure region identifier (e.g., "eastus") |
| display_name | string | Human-readable name (e.g., "East US") |
| probe_url | string | HTTPS endpoint for latency probing |

### Constraints

- region_code MUST be unique across the registry
- probe_url MUST use HTTPS protocol
- probe_url MUST be publicly accessible without authentication
- All GA Azure regions MUST be included

### Relationship to Existing Models

The registry feeds into the existing `CloudRegion` dataclass:

- `provider_id` = "azure" (constant)
- `region_code` = registry.region_code
- `region_name` = registry.display_name
- `endpoint_url` = registry.probe_url

No changes to `CloudRegion`, `LatencyMeasurement`, `VendorSummary`, or `LatencySnapshot` dataclasses are required.
