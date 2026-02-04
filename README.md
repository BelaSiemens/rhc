# RHC — Repo Health Check CLI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
<!-- After you create the GitHub repo + Actions, replace <USER>/<REPO> below -->
<!-- [![CI](https://github.com/<USER>/<REPO>/actions/workflows/ci.yml/badge.svg)](https://github.com/<USER>/<REPO>/actions/workflows/ci.yml) -->

**RHC** is a fast, offline-first CLI that scans a repository and produces a **0–100 health score** plus **actionable findings** across:
docs, CI/CD, tests, dependencies, security basics, and repo hygiene.

- **Offline-first** (no required API calls)
- **Deterministic & explainable** (every score has evidence)
- **CI-friendly** (policy gates via exit codes)
- **Exports**: pretty terminal, JSON, Markdown

---

## TL;DR

```bash
# scan current repo
rhc scan

# fail CI if score is too low
rhc scan --min-score 80

# export a Markdown report for PRs
rhc scan --format md --output HEALTH.md

# export JSON for automation
rhc scan --format json --output report.json
```

---

## Installation

### Option A: pipx (recommended)
```bash
pipx install rhc
```

### Option B: pip
```bash
pip install rhc
```

### Option C: from source (dev)
```bash
git clone https://github.com/<USER>/<REPO>.git
cd rhc
pip install -e ".[dev]"
```

> **Note:** If you distribute binaries later (PyInstaller), add a “Download → Run” section here.

---

## What RHC checks (19 checks, 6 categories)

| Category | Examples |
|---|---|
| **Docs** | README, LICENSE, CONTRIBUTING, SECURITY.md |
| **CI/CD** | CI config (multiple providers), status badges |
| **Tests** | Test detection, CI runs tests, linter config |
| **Dependencies** | Lockfile present, outdated hints, multiple package managers |
| **Security** | Secret scanning (suspected), Dependabot, CODEOWNERS |
| **Hygiene** | .gitignore, .editorconfig, semver tags, changelog |

See the full list anytime:
```bash
rhc list-checks
```

And detailed rationale for a specific check:
```bash
rhc explain DOC.README_PRESENT
```

---

## Output formats

### 1) Terminal (default)
Fast overview: score + severity counts + top findings.

### 2) JSON
Machine-readable for pipelines:
```bash
rhc scan --format json --output report.json
```

### 3) Markdown
Great for PRs/Issues:
```bash
rhc scan --format md --output HEALTH.md
```

---

## CLI Reference

### `rhc scan [path]`
Scan a repository and generate a report.

**Common options:**
- `--format, -f` : `text` | `json` | `md` (default: `text`)
- `--output, -o` : write report to a file
- `--min-score <0-100>` : fail if final score is below threshold
- `--fail-on <severity>` : fail if findings at/above severity exist  
  (`none|info|low|medium|high|critical`)
- `--only <check_id>` : only run specific checks (repeatable)
- `--skip <check_id>` : skip specific checks (repeatable)
- `--strict` : stricter thresholds (where applicable)
- `--offline` : disable network checks (default behavior is offline-first)
- `--config, -c <path>` : use a specific config file
- `--debug` : verbose logs

### `rhc list-checks`
List all checks with category and default impact.

### `rhc explain <check_id>`
Explain what a check looks for and what evidence is gathered.

### `rhc init`
Generate an example `.rhc.yml` in the current directory.

---

## CI usage (policy gates)

### Example: fail if score < 80 or any high/critical finding exists
```bash
rhc scan --min-score 80 --fail-on high
```

### Exit codes
| Code | Meaning |
|---:|---|
| 0 | Success, no policy violations |
| 1 | Policy violated (min-score and/or fail-on) |
| 2 | Analysis error (e.g. path not found) |
| 3 | Internal error |

---

## Configuration (`.rhc.yml`)

Create `.rhc.yml` in your repo root:

```yaml
version: 1

policy:
  min_score: 75
  fail_on: high

checks:
  skip:
    - SEC.SECRETS_SUSPECTED
  weights:
    DOC.README_PRESENT: -8
    CI.CONFIG_PRESENT: -12
```

Generate a starter config:
```bash
rhc init
```

---

## Security note (secret scan)

The secret check is intentionally conservative:
- It reports **suspected** secrets based on common patterns.
- It should **not** print full secret values into logs/reports.
- Run with `--skip SEC.SECRETS_SUSPECTED` if your repo contains test tokens.

---

## Development

```bash
ruff check rhc tests
pytest -q
```

---

## Roadmap (small + high-impact)
- `--baseline` + diff reports
- SARIF export for GitHub Code Scanning
- Optional online mode (dependency freshness via API)

---

## License

MIT — see [LICENSE](LICENSE).
