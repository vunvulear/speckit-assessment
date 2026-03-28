# CloudLatency REST API Documentation

## Base URL

```text
http://localhost:8080
```

The default port is `8080`. Override with `--port` CLI flag.

## Endpoints

### GET /api/v1/health

Service health check.

**Response (200):**

```json
{
  "status": "healthy",
  "uptime_seconds": 123.45,
  "last_cycle_at": "2026-01-01T00:00:00+00:00"
}
```

- `uptime_seconds` — seconds since the server started
- `last_cycle_at` — ISO 8601 timestamp of the most recent measurement, or `null` if no data yet

---

### GET /api/v1/results

All latency measurements sorted by latency ascending. Unreachable regions sort to the end.

**Response (200):**

```json
[
  {
    "provider": "aws",
    "region": "us-east-1",
    "latency_ms": 42.0,
    "status": "ok",
    "timestamp": "2026-01-01T00:00:00+00:00"
  },
  {
    "provider": "gcp",
    "region": "us-central1",
    "latency_ms": null,
    "status": "unreachable",
    "timestamp": "2026-01-01T00:00:00+00:00"
  }
]
```

Returns an empty array `[]` with status 200 if no measurements exist yet.

---

### GET /api/v1/results/{provider}

Filtered results for a single provider, sorted by latency ascending.

**Path Parameters:**

| Parameter  | Type   | Description                     |
|------------|--------|---------------------------------|
| `provider` | string | One of: `aws`, `azure`, `gcp`   |

**Response (200):**

```json
[
  {
    "provider": "aws",
    "region": "us-east-1",
    "latency_ms": 42.0,
    "status": "ok",
    "timestamp": "2026-01-01T00:00:00+00:00"
  }
]
```

**Error Response (404):**

```json
{
  "error": "Provider not found",
  "code": "PROVIDER_NOT_FOUND"
}
```

---

### GET /api/v1/summary

Vendor averages and closest region per provider.

**Response (200):**

```json
{
  "providers": {
    "aws": {
      "average_latency_ms": 81.0,
      "closest_region": "us-east-1",
      "closest_latency_ms": 42.0,
      "total_regions": 29,
      "reachable_regions": 28
    },
    "azure": {
      "average_latency_ms": 95.5,
      "closest_region": "westus",
      "closest_latency_ms": 30.0,
      "total_regions": 38,
      "reachable_regions": 38
    },
    "gcp": {
      "average_latency_ms": 110.2,
      "closest_region": "us-central1",
      "closest_latency_ms": 25.0,
      "total_regions": 39,
      "reachable_regions": 37
    }
  }
}
```

Returns `{"providers": {}}` if no measurements exist yet.

---

### GET /api/v1/sse

Server-Sent Events stream for live measurement updates.

**Headers:**

```text
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

**Event Format:**

Each event is sent after a probe cycle completes:

```text
data: {"results": [...], "summary": {"providers": {...}}}
```

The `data` payload is a JSON object containing:

- `results` — array of all latency results (same format as `/api/v1/results`)
- `summary` — vendor summary (same format as `/api/v1/summary`)

**Reconnection:** The browser `EventSource` API handles reconnection automatically. The server does not send `retry:` directives; default browser behavior applies (~3-5s).

---

## Error Responses

All errors return a consistent JSON format:

```json
{
  "error": "Human-readable description",
  "code": "MACHINE_READABLE_CODE"
}
```

| Status | Code                    | Description             |
|--------|-------------------------|-------------------------|
| 404    | `NOT_FOUND`             | Unknown route           |
| 404    | `PROVIDER_NOT_FOUND`    | Invalid provider name   |
| 500    | `INTERNAL_SERVER_ERROR` | Unexpected server error |

---

## CORS

CORS headers are included for requests with `Origin` containing `localhost` or `127.0.0.1`:

```text
Access-Control-Allow-Origin: <request origin>
Access-Control-Allow-Methods: GET, OPTIONS
Access-Control-Allow-Headers: Content-Type
```
