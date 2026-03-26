# REST API Contract: Cloud Latency Monitor

**Branch**: `001-cloud-latency-monitor` | **Date**: 2026-03-26

## Base URL

```
http://{host}:{port}/api/v1
```

## Endpoints

### GET /api/v1/latency

Returns the latest latency snapshot with all region measurements and vendor summaries.

**Response**: `200 OK`

```json
{
  "measured_at": "2026-03-26T17:00:10Z",
  "measurements": [
    {
      "provider_id": "aws",
      "region_code": "us-east-1",
      "region_name": "US East (N. Virginia)",
      "latency_ms": 12.4,
      "is_reachable": true,
      "measured_at": "2026-03-26T17:00:10Z"
    },
    {
      "provider_id": "azure",
      "region_code": "westeurope",
      "region_name": "West Europe",
      "latency_ms": 25.7,
      "is_reachable": true,
      "measured_at": "2026-03-26T17:00:10Z"
    },
    {
      "provider_id": "gcp",
      "region_code": "asia-east1",
      "region_name": "Taiwan",
      "latency_ms": null,
      "is_reachable": false,
      "measured_at": "2026-03-26T17:00:10Z"
    }
  ],
  "vendor_summaries": [
    {
      "provider_id": "aws",
      "provider_name": "AWS",
      "average_latency_ms": 45.2,
      "closest_region_code": "us-east-1",
      "closest_region_name": "US East (N. Virginia)",
      "closest_latency_ms": 12.4,
      "total_regions": 30,
      "reachable_regions": 29
    },
    {
      "provider_id": "azure",
      "provider_name": "Azure",
      "average_latency_ms": 52.1,
      "closest_region_code": "westeurope",
      "closest_region_name": "West Europe",
      "closest_latency_ms": 25.7,
      "total_regions": 60,
      "reachable_regions": 58
    },
    {
      "provider_id": "gcp",
      "provider_name": "GCP",
      "average_latency_ms": 61.8,
      "closest_region_code": "europe-west1",
      "closest_region_name": "Belgium",
      "closest_latency_ms": 28.3,
      "total_regions": 35,
      "reachable_regions": 34
    }
  ]
}
```

**Error Response**: `503 Service Unavailable` (no measurements collected yet)

```json
{
  "error": "no_data",
  "message": "No latency measurements available yet. Engine is starting up."
}
```

---

### GET /api/v1/latency/stream

Server-Sent Events (SSE) endpoint. Pushes a new `LatencySnapshot` JSON payload every 10 seconds.

**Response**: `200 OK` with `Content-Type: text/event-stream`

```
event: latency_update
data: {"measured_at":"2026-03-26T17:00:10Z","measurements":[...],"vendor_summaries":[...]}

event: latency_update
data: {"measured_at":"2026-03-26T17:00:20Z","measurements":[...],"vendor_summaries":[...]}
```

**Reconnection**: The server sets `retry: 5000` (5 seconds) to instruct the browser's EventSource to reconnect if disconnected.

---

### GET /api/v1/regions

Returns the list of all discovered cloud regions (without latency data).

**Response**: `200 OK`

```json
{
  "regions": [
    {
      "provider_id": "aws",
      "region_code": "us-east-1",
      "region_name": "US East (N. Virginia)",
      "endpoint_url": "https://ec2.us-east-1.amazonaws.com"
    }
  ],
  "total_count": 125,
  "discovered_at": "2026-03-26T16:59:00Z"
}
```

---

### GET /api/v1/health

Health check endpoint for monitoring and deployment probes.

**Response**: `200 OK`

```json
{
  "status": "healthy",
  "engine_running": true,
  "last_measurement_at": "2026-03-26T17:00:10Z",
  "regions_discovered": 125
}
```

---

### GET /

Serves the web UI (static HTML page with embedded JavaScript for SSE and Chart.js).

**Response**: `200 OK` with `Content-Type: text/html`

## Common Headers

All JSON endpoints return:

- `Content-Type: application/json`
- `Cache-Control: no-cache` (data is always fresh)

SSE endpoint returns:

- `Content-Type: text/event-stream`
- `Cache-Control: no-cache`
- `Connection: keep-alive`
