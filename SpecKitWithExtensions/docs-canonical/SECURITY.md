# Security

<!-- docguard:version 1.0.0 -->
<!-- docguard:status approved -->
<!-- docguard:last-reviewed 2026-03-26 -->
<!-- docguard:owner @cloudlatency -->

> **Canonical document** — Design intent. This file defines the security model.  
> Last updated: 2026-03-26

---

## Authentication

No authentication is required. CloudLatency v1 is a publicly accessible, read-only dashboard with no user accounts or protected resources.

| Method | Implementation | Details |
|--------|---------------|---------|
| None | N/A | Public access — no auth for v1 |

## Authorization

No authorization model. All API endpoints are public and read-only.

| Role | Permissions | Scope |
|------|------------|-------|
| Anonymous | Read-only | All API endpoints, UI |

## Secrets Management

No application secrets are used. All configuration is via non-sensitive environment variables (host, port, intervals).

| Secret | Storage | Access Pattern |
|--------|---------|---------------|
| N/A | N/A | No secrets required |

## Security Rules

- All API routes are public (no authentication) — this is intentional for v1
- No secrets in code, logs, or error messages (constitution principle III)
- All user input from URL query params MUST be validated via Pydantic schemas
- No PII is collected or processed — the app only measures network latency
- Outbound HTTPS requests to cloud providers use TLS (no plaintext HTTP)
- No database credentials — all data is in-memory
- SSE endpoints MUST NOT leak internal stack traces on error
- CORS is configured to allow same-origin requests only (UI served from same server)
