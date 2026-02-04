# Contributing to RHC

Thanks for your interest in contributing!

## Development Setup

```bash
# Clone the repo
git clone https://github.com/<USER>/<REPO>.git
cd rhc

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Quick run
pytest -q

# With coverage
pytest --cov=rhc
```

## Linting

```bash
# Check for issues
ruff check rhc tests

# Auto-fix where possible
ruff check rhc tests --fix
```

## Adding a New Check

1. Create or edit the appropriate file in `rhc/checks/` (e.g., `docs.py`, `ci.py`)
2. Inherit from `BaseCheck` and define `info: CheckInfo`
3. Implement the `run(ctx) -> list[Finding]` method
4. Register the check in `rhc/checks/__init__.py`
5. Add tests in `tests/test_checks.py`

## Pull Request Process

1. Fork the repo and create a feature branch
2. Make your changes with tests
3. Run `ruff check` and `pytest` to ensure everything passes
4. Submit a PR with a clear description

## Code Style

- Python 3.10+ type hints
- Line length: 100 (configured in pyproject.toml)
- Follow existing patterns in the codebase
