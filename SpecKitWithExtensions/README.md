# CloudLatency

Real-time HTTPS latency monitoring for **Azure**, **AWS**, and **GCP** regions worldwide.

## Features

- Measures latency via HTTPS HEAD requests to all cloud regions
- Sorted latency table (lowest to highest)
- Average latency bar chart per vendor
- Closest region bar chart per vendor
- Auto-refreshes every 10 seconds via Server-Sent Events (SSE)

## Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd windsurf-project-6
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Run
python -m cloudlatency.main

# Open http://localhost:8000
```

## Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest --cov=cloudlatency

# Lint and format
ruff check cloudlatency/
black cloudlatency/
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| Framework | FastAPI + uvicorn |
| HTTP Client | aiohttp (async) |
| SSE | sse-starlette |
| Validation | Pydantic v2 |
| Charts | Chart.js |
| Testing | pytest, pytest-asyncio |

## Documentation

See `docs-canonical/` for architecture, data model, security, test spec, and environment docs.

See `specs/001-cloud-latency-monitor/` for the full feature specification and implementation plan.

## License

MIT
