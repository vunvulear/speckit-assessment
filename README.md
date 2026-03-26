# SpecKit vs SpecKit+Extensions — Quality Comparison Exercise

This repository contains **two implementations of the same application** (CloudLatency) built using two different AI-assisted development workflows, plus an automated quality comparison measuring 30+ metrics across 14 tools.

The goal: **determine whether SpecKit extensions (DocGuard, Sync, Verify, Drift) produce measurably better output** compared to base SpecKit alone.

---

## Verdict

**Extensions wins 5 of 8 categories, ties 2, loses 1.**

The extensions produce a more production-ready, cognitively simpler, and well-documented project. Base SpecKit produces slightly cleaner code under traditional linting but lacks operational maturity artifacts and has 43% higher cognitive complexity.

The most impactful finding: **Halstead metrics revealed the functional architecture (Extensions) requires 43% less cognitive effort to understand** — a dimension traditional linting tools don't capture.

---

## Key Results

### Scoring Summary (8 categories, 30+ metrics)

| Category | SpecKit | Extensions | Winner |
|----------|---------|------------|--------|
| Code Quality (Pylint + Flake8 + CC) | 9.0 | 8.5 | SpecKit |
| Cognitive Complexity (Halstead) | 7.0 | 9.5 | **Extensions** |
| Test Quality | 7.5 | 9.0 | **Extensions** |
| Documentation | 5.0 | 9.5 | **Extensions** |
| Maintainability (MI + Lizard) | 8.5 | 8.5 | Tie |
| Architecture (cohesion + coupling) | 7.5 | 8.0 | **Extensions** |
| Security (Bandit) | 9.0 | 9.0 | Tie |
| Project Maturity | 4.0 | 9.5 | **Extensions** |
| **Weighted Total** | **7.19** | **9.00** | **Extensions** |

### Headline Metrics

| Metric | SpecKit | Extensions |
|--------|---------|------------|
| Pylint Score | **9.68**/10 | 9.32/10 |
| Halstead Effort | 2,664 | **1,526** (-43%) |
| Test Count | 65 | **102** (+57%) |
| Test Coverage | **94.29%** | 92.24% |
| Documentation Artifacts | 9 | **22** (+144%) |
| DocGuard Score | N/A | **88/100 (A)** |
| Predicted Bugs (Halstead) | 0.204 | **0.174** (-15%) |

> **For the full 430-line breakdown with per-tool analysis, hotspot identification, and methodology details, see [`comparison-report.md`](comparison-report.md).**

---

## Project Requirements (Original Request)

> Build a web app that measures latency across all Azure, AWS, and GCP regions worldwide. Every 10 seconds, the data is refreshed. Display a chart showing average latency per vendor and closest region latency per vendor. Table above sorted lowest to highest latency per cloud region. Page auto-updates on new data.

This single prompt was given identically to both workflows (SpecKit and SpecKit+Extensions) to produce two independent implementations of the same application.

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
├── comparison-report.md        # Full quality comparison (430 lines, 30+ metrics)
└── README.md                   # This file
```

---

## Workflows Compared

### SpecKit (Base) — 8 workflows

| Workflow | Purpose |
|----------|---------|
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
```

### Run the quality measurements

```bash
# Install all measurement tools
pip install radon pylint flake8 interrogate bandit vulture lizard cohesion

# Example: run all metrics on one project
cd SpecKit  # or SpecKitWithExtensions

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

Where `<package>` is `src/cloudlatency` for SpecKit or `cloudlatency` for Extensions.

---

## Detailed Report

See [`comparison-report.md`](comparison-report.md) for the full 430-line report with per-tool breakdowns, analysis, and hotspot identification.

---

## License

Both CloudLatency implementations are MIT licensed.
