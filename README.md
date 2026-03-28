# SpecKit vs SpecKit+Extensions vs BMAD — Quality Comparison Exercise

This repository contains **three implementations of the same application** (CloudLatency) built using three different AI-assisted development workflows, plus an automated quality comparison measuring 30+ metrics across 14 tools.

The goal: **compare the code quality outcomes of SpecKit (base), SpecKit+Extensions (DocGuard, Sync, Verify, Drift), and BMAD** when given the same prompt.

---

## Verdict

**Extensions wins 3 of 8 categories. BMAD wins 3. SpecKit wins 1. 1 is a 3-way tie.**

**Extensions** (9.00/10) leads overall thanks to documentation, project maturity, and architecture. **BMAD** (8.05/10) produces the most cognitively simple, well-tested, and compact code. **SpecKit** (7.19/10) produces the cleanest code under traditional linting but lacks both operational maturity and code simplicity.

The most impactful finding: **Halstead metrics revealed BMAD's hybrid architecture requires 59% less cognitive effort than SpecKit and 29% less than Extensions** — a dimension traditional linting tools don't capture.

---

## Key Results

### Scoring Summary (8 categories, 30+ metrics)

| Category | SpecKit | Extensions | BMAD | Winner |
|----------|---------|------------|------|--------|
| Code Quality (Pylint + Flake8 + CC) | 9.0 | 8.5 | 7.0 | SpecKit |
| Cognitive Complexity (Halstead) | 7.0 | 9.5 | 10.0 | **BMAD** |
| Test Quality | 7.5 | 9.0 | 9.5 | **BMAD** |
| Documentation | 5.0 | 9.5 | 6.5 | **Extensions** |
| Maintainability (MI + Lizard) | 8.5 | 8.5 | 9.0 | **BMAD** |
| Architecture (cohesion + coupling) | 7.5 | 8.0 | 7.5 | **Extensions** |
| Security (Bandit) | 9.0 | 9.0 | 9.0 | 3-way Tie |
| Project Maturity | 4.0 | 9.5 | 5.5 | **Extensions** |
| **Weighted Total** | **7.19** | **9.00** | **8.05** | **Extensions** |

### Headline Metrics

| Metric | SpecKit | Extensions | BMAD |
|--------|---------|------------|------|
| Pylint Score | **9.68**/10 | 9.32/10 | 8.50/10 |
| Halstead Effort | 2,664 | 1,526 | **1,090** (-59%) |
| Test Count | 65 | 102 | **107** |
| Test Coverage | 94.29% | 92.24% | **99.01%** |
| Documentation Artifacts | 9 | **22** | ~10 |
| Docstring Coverage | 90.8% | 92.7% | **96.1%** |
| Predicted Bugs (Halstead) | 0.204 | 0.174 | **0.128** (-37%) |

> **For the full 500+ line breakdown with per-tool analysis, hotspot identification, and methodology details, see [`comparison-report.md`](comparison-report.md).**

---

## Project Requirements (Original Request)

> Build a web app that measures latency across all Azure, AWS, and GCP regions worldwide. Every 10 seconds, the data is refreshed. Display a chart showing average latency per vendor and closest region latency per vendor. Table above sorted lowest to highest latency per cloud region. Page auto-updates on new data.

This single prompt was given identically to all three workflows (SpecKit, SpecKit+Extensions, and BMAD) to produce three independent implementations of the same application.

---

## What Is CloudLatency?

A real-time web application that measures HTTPS latency to all Azure, AWS, and GCP cloud regions worldwide. Features include:

- Sorted latency table refreshed every 10 seconds
- Average latency and closest region charts per vendor (Chart.js)
- SSE-based live updates with auto-reconnect
- Async region discovery and concurrent probing

---

## Repository Structure

```
├── SpecKit/                    # Built with base SpecKit workflow (8 workflows)
│   ├── src/cloudlatency/       # OOP architecture (classes)
│   ├── tests/                  # 65 tests, 94.29% coverage
│   ├── specs/                  # 1 feature spec (001-cloud-latency-monitor)
│   └── journey.md              # Full development narrative
│
├── SpecKitWithExtensions/      # Built with SpecKit + extensions (28 workflows)
│   ├── cloudlatency/           # Functional architecture (modules)
│   ├── tests/                  # 102 tests, 92.24% coverage
│   ├── specs/                  # 2 feature specs (001 + 002-fix-azure-discovery)
│   ├── docs-canonical/         # ARCHITECTURE, SECURITY, DATA-MODEL, etc.
│   └── journey.md              # Full development narrative
│
├── BMAD/                       # Built with BMAD methodology
│   ├── src/cloudlatency/       # Hybrid architecture (classes + functions)
│   ├── tests/                  # 107 tests, 99.01% coverage
│   ├── _bmad-output/           # Planning artifacts (PRD, architecture, epics, UX)
│   └── docs/api.md             # API documentation
│
├── comparison-report.md        # Full quality comparison (500+ lines, 30+ metrics)
└── README.md                   # This file
```

---

## Workflows Compared

### SpecKit (Base) — 8 workflows

| Workflow | Purpose |
|----------|---------- |
| `speckit.constitution` | Establish project principles |
| `speckit.specify` | Create feature specification |
| `speckit.clarify` | Resolve spec ambiguities |
| `speckit.plan` | Generate implementation plan |
| `speckit.tasks` | Generate task list |
| `speckit.analyze` | Cross-artifact consistency check |
| `speckit.implement` | Execute tasks |
| `speckit.taskstoissues` | Convert tasks to GitHub issues |

### SpecKit + Extensions — 28 workflows (adds 20)

All base workflows plus:

- **DocGuard** (6 workflows) — Documentation quality gate, CDD compliance scoring, canonical doc generation
- **Sync** (5 workflows) — Drift detection, conflict resolution, spec backfill
- **Verify** (2 workflows) — Post-implementation verification against specs
- **Verify-Tasks** (2 workflows) — Phantom completion detection
- **Additional** — `speckit.drift`, `speckit.checklist`, enhanced `speckit.verify`

### BMAD — Agent-based methodology

BMAD (BMad Agentic Development) uses a multi-agent approach with specialized roles (analyst, architect, developer, PM) and structured planning artifacts:

- **Planning phase** — Product brief → PRD → Architecture → Epics → UX Design Spec → Implementation readiness report
- **Implementation phase** — Sprint-based task execution with YAML status tracking
- **Quality tools** — Ruff linting, pytest with coverage enforcement (≥90%)

---

## Measurement Tools Used

All tools are pip-installable (no Docker or external services required):

```bash
pip install radon pylint flake8 interrogate bandit vulture lizard cohesion
```

| Tool | What It Measures |
|------|-----------------|
| **Radon** (CC, MI, Halstead, Raw) | Cyclomatic complexity, maintainability index, cognitive effort, LOC |
| **Pylint** | Overall code quality score (0–10) |
| **Flake8** | PEP 8 style violations |
| **Interrogate** | Docstring coverage % |
| **Bandit** | Security vulnerabilities (SAST) |
| **Vulture** | Dead/unused code |
| **Lizard** | Per-function NLOC, CCN, token count, parameter count |
| **Cohesion** | Class method-attribute cohesion % |
| **pytest-cov** | Test line coverage % |
| **Custom AST analysis** | Import coupling and dependency density |

---

## How to Reproduce

### Run each project

```bash
# SpecKit
cd SpecKit
pip install -r requirements.txt
python -m cloudlatency

# SpecKit + Extensions
cd SpecKitWithExtensions
pip install -r requirements.txt
python -m cloudlatency.main

# BMAD
cd BMAD
pip install -e .
python -m cloudlatency
```

### Run the quality measurements

```bash
# Install all measurement tools
pip install radon pylint flake8 interrogate bandit vulture lizard cohesion

# Example: run all metrics on one project
cd SpecKit  # or SpecKitWithExtensions or BMAD

radon cc <package> -a -s          # Cyclomatic complexity
radon mi <package> -s             # Maintainability index
radon hal <package>               # Halstead complexity
radon raw <package> -s            # LOC metrics
pylint <package> --score=y        # Code quality score
flake8 <package> --statistics     # PEP 8 violations
interrogate <package> -v          # Docstring coverage
bandit -r <package> -f json       # Security analysis
vulture <package>                 # Dead code
lizard <package> -l python        # Function-level metrics
cohesion -d <package>             # Class cohesion
pytest --cov=<package>            # Test coverage
```

Where `<package>` is `src/cloudlatency` for SpecKit and BMAD, or `cloudlatency` for Extensions.

---

## Detailed Report

See [`comparison-report.md`](comparison-report.md) for the full 500+ line report with per-tool breakdowns, analysis, and hotspot identification.

---

## License

The SpecKit and SpecKit+Extensions CloudLatency implementations are MIT licensed. BMAD's implementation uses MIT license per `pyproject.toml`.
