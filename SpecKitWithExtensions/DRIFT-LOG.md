# Drift Log

> Documents conscious deviations from canonical specifications.  
> Every `// DRIFT:` comment in code MUST have a matching entry here.

---

## Active Drift

| ID | File | Line | Canonical Doc | Deviation | Reason | Date |
|----|------|------|--------------|-----------|--------|------|
| D-001 | cloudlatency/engine/discovery.py | 83 | spec.md FR-001 (dynamic discovery) | Azure uses hardcoded region list instead of dynamic API discovery | Azure Management API requires OAuth2 auth token; no public unauthenticated endpoint available | 2026-03-26 |

## Resolved Drift

| ID | Resolution | Date |
|----|-----------|------|
| <!-- D-000 --> | <!-- How it was resolved --> | <!-- 2026-03-26 --> |
