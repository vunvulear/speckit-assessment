<!--
Sync Impact Report
- Version change: 0.0.0 → 1.0.0
- Modified principles: N/A (initial creation)
- Added sections: Core Principles (6), Technology & Architecture Constraints, Development Workflow & Quality Gates, Governance
- Removed sections: N/A
- Templates requiring updates: ✅ spec-template.md (aligned), ✅ plan-template.md (aligned), ✅ tasks-template.md (aligned)
- Follow-up TODOs: None
-->

# CloudLatency Constitution

## Core Principles

### I. Cross-Browser Compatibility

CloudLatency MUST render and function correctly across all modern browsers (Chrome, Firefox, Safari, Edge).
The UI MUST NOT rely on browser-specific APIs or features without graceful fallback.
All interactive elements MUST be tested against at least the two latest major versions of each supported browser.

### II. Test-First Development (NON-NEGOTIABLE)

All business logic MUST be covered by unit tests following a shift-left testing strategy.
Tests MUST be written before or alongside implementation code — Red-Green-Refactor cycle enforced.
Test coverage MUST remain above 90% at all times; builds MUST fail if coverage drops below this threshold.
Integration tests MUST cover cross-component communication (backend API ↔ latency engine, UI ↔ API).

### III. Open Source & Transparency

CloudLatency is open source and MUST be distributed under a permissive license.
All dependencies MUST be compatible with the chosen open-source license.
Documentation MUST be sufficient for external contributors to onboard without private knowledge.

### IV. Simplicity & Readability

The UI MUST be simple, clean, and easy to read at a glance.
Data presentation MUST prioritize clarity: sorted tables, clearly labeled charts, and obvious refresh indicators.
Code MUST favor straightforward implementations over clever abstractions — YAGNI principle applies.
Cyclomatic complexity MUST be kept minimal; functions exceeding a complexity threshold MUST be refactored.

### V. Minimal & Actionable Logging

Log output MUST be minimal in volume but sufficient to diagnose any backend or UI issue.
Backend MUST use structured logging (JSON format) with severity levels (DEBUG, INFO, WARNING, ERROR).
Frontend MUST surface errors to the browser console with enough context for diagnosis.
Sensitive data (API keys, credentials) MUST NEVER appear in logs.

### VI. Component Separation

The solution MUST be split into independent components: a latency measurement engine, a REST API layer, and a web UI.
The REST API MUST be the sole interface between the latency engine and any consumer (UI, CLI, or third-party).
Each component MUST be independently deployable, testable, and replaceable.
This architecture MUST allow the web UI to be swapped for an alternative consumer without modifying the backend.

## Technology & Architecture Constraints

- **Language**: Python 3.11+ is the sole implementation language for all components.
- **Deployment**: The solution MUST be deployable in any environment (local, VM, container, cloud) without vendor lock-in.
- **Dependencies**: All third-party packages MUST be declared in a standard dependency file (`requirements.txt` or `pyproject.toml`) with pinned versions.
- **API Protocol**: The REST API MUST use JSON as the data interchange format.
- **Real-Time Updates**: The web UI MUST automatically refresh data every 10 seconds without manual user intervention; WebSocket or polling strategies are acceptable.
- **Cloud Providers**: The latency engine MUST measure latency across all publicly accessible Azure, AWS, and GCP regions worldwide.

## Development Workflow & Quality Gates

- **Shift-Left Testing**: Testing MUST occur as early as possible in the development cycle. Unit tests MUST be written before or alongside feature code.
- **Test Coverage Gate**: Minimum 90% line coverage enforced via CI; merges MUST be blocked if coverage drops below threshold.
- **Complexity Metrics**: Cyclomatic complexity MUST be measured and reported. Functions exceeding a configurable threshold MUST be flagged for refactoring before merge.
- **Linting & Formatting**: All Python code MUST pass linting (e.g., ruff or flake8) and formatting (e.g., black) checks before merge.
- **Commit Discipline**: Each commit SHOULD represent a single logical change. Commit messages MUST follow conventional format (`type: description`).

## Governance

This constitution supersedes all other development practices for the CloudLatency project.
Amendments require: (1) a written proposal describing the change and rationale, (2) an update to this document with version bump, and (3) propagation of changes to all dependent templates and documentation.

All code reviews and pull requests MUST verify compliance with the principles defined above.
Any deviation from a principle MUST be documented with justification in the relevant plan or task artifact.

Versioning follows semantic versioning:
- **MAJOR**: Principle removal or backward-incompatible governance change.
- **MINOR**: New principle added or existing principle materially expanded.
- **PATCH**: Clarifications, typo fixes, non-semantic refinements.

**Version**: 1.0.0 | **Ratified**: 2026-03-26 | **Last Amended**: 2026-03-26
