# Environment & Configuration

<!-- docguard:version 1.0.0 -->
<!-- docguard:status approved -->
<!-- docguard:last-reviewed 2026-03-26 -->
<!-- docguard:owner @cloudlatency -->

> **Canonical document** — Design intent. This file documents everything needed to run this project.  
> Last updated: 2026-03-26

---

## Prerequisites

| Requirement | Version | Purpose |
|------------|---------|----------|
| Python | 3.11+ | Runtime |
| pip | latest | Package management |
| Internet access | — | Required to reach cloud provider APIs and region endpoints |

## Environment Variables

All variables are optional with sensible defaults. No secrets required.

| Variable | Required | Default | Description | Where to Get |
|----------|----------|---------|-------------|-------------|
| `HOST` | No | `0.0.0.0` | Server bind address | — |
| `PORT` | No | `8000` | Server port | — |
| `MEASUREMENT_INTERVAL` | No | `10` | Seconds between measurement cycles | — |
| `REQUEST_TIMEOUT` | No | `5` | Seconds before marking region unreachable | — |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) | — |

## Configuration Files

| File | Purpose | Template |
|------|---------|----------|
| `requirements.txt` | Pinned production dependencies | N/A |
| `requirements-dev.txt` | Test/lint/dev dependencies | N/A |
| `pyproject.toml` | Project metadata and tool config | N/A |

## Setup Steps

1. Clone the repository
2. Create and activate a virtual environment: `python -m venv .venv && .venv/Scripts/activate`
3. Install dependencies: `pip install -r requirements.txt -r requirements-dev.txt`
4. (Optional) Set environment variables or use defaults
5. Start the application: `python -m cloudlatency.main`
6. Open `http://localhost:8000` in your browser
