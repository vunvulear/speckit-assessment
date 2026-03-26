# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Project constitution with 6 core principles (`.specify/memory/constitution.md`)
- Feature specification for Cloud Latency Monitor (`specs/001-cloud-latency-monitor/spec.md`)
- 5 clarifications integrated into spec (measurement method, timeout, discovery, charts, SSE)
- Implementation plan with research, data model, and API contracts
- Requirements quality checklist (36 items across 8 dimensions)
- Task list with 56 tasks across 7 phases
- Cross-artifact consistency analysis (0 critical issues, 84% coverage)
- Canonical documentation: ARCHITECTURE.md, DATA-MODEL.md, SECURITY.md, TEST-SPEC.md, ENVIRONMENT.md
- DocGuard CDD compliance infrastructure (score: 75/100 B, ALCOA+ 9/9)
- Spec Kit extensions: DocGuard, Verify, Verify Tasks, Spec Sync
- Phase 1: Project structure, pyproject.toml, requirements.txt, requirements-dev.txt, LICENSE, README
- Phase 2: Configuration (config.py), data models (models.py), Pydantic schemas (schemas.py), logging (logging_config.py), FastAPI app factory (app.py), entry point (main.py), test fixtures (conftest.py)
- Phase 3: Region discovery for AWS/Azure/GCP (discovery.py), HTTPS HEAD prober (prober.py), measurement scheduler (scheduler.py), REST API routes (routes.py), web UI with HTML/CSS/JS
- Phase 4: Average latency bar chart per vendor (Chart.js in app.js)
- Phase 5: Closest region bar chart per vendor (Chart.js in app.js)
- Phase 6: SSE streaming endpoint (sse.py), EventSource client with auto-reconnect
- Phase 7: Global error handling middleware, ruff lint clean, black formatting
- 98 passing tests with 91%+ code coverage

### Fixed

- Azure region discovery now uses hardcoded region registry with Blob Storage probe endpoints instead of Management API (which requires OAuth2 auth)
- Azure regions (60+) now appear in latency table, average chart, and closest region chart
- 102 passing tests with 92%+ code coverage
