# Quickstart: Cloud Latency Monitor

**Branch**: `001-cloud-latency-monitor` | **Date**: 2026-03-26

## Prerequisites

- Python 3.11+
- pip or uv package manager
- Internet connectivity (to reach cloud provider endpoints)

## Setup

```bash
# Clone the repository
git clone <repo-url>
cd cloudlatency

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

## Run the Application

```bash
# Start the server (latency engine + API + UI)
python -m cloudlatency.main
```

The application starts on `http://localhost:8000` by default.

## Access the UI

Open `http://localhost:8000` in your browser. You will see:

1. A **latency table** showing all cloud regions sorted by latency (lowest first)
2. A **bar chart** showing average latency per vendor (Azure, AWS, GCP)
3. A **bar chart** showing the closest region per vendor

All data auto-refreshes every 10 seconds via Server-Sent Events.

## Run Tests

```bash
# Run all tests with coverage
pytest --cov=cloudlatency --cov-report=term-missing

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

## Configuration

Environment variables (all optional):

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server port |
| `MEASUREMENT_INTERVAL` | `10` | Seconds between measurement cycles |
| `REQUEST_TIMEOUT` | `5` | Seconds before marking a region unreachable |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

## Project Structure

```text
cloudlatency/
├── engine/          # Latency measurement engine
│   ├── discovery.py # Region discovery via provider APIs
│   ├── prober.py    # HTTPS HEAD request probing
│   └── models.py    # Data models (CloudRegion, LatencyMeasurement, etc.)
├── api/             # REST API layer (FastAPI)
│   ├── routes.py    # API endpoints
│   ├── sse.py       # SSE streaming endpoint
│   └── schemas.py   # Pydantic response schemas
├── ui/              # Web UI (static HTML/JS/CSS)
│   └── static/
│       ├── index.html
│       ├── app.js
│       └── style.css
├── config.py        # Configuration management
└── main.py          # Application entry point

tests/
├── unit/            # Unit tests
├── integration/     # Integration tests
└── conftest.py      # Shared fixtures
```
