"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_repo():
    """Create a temporary directory for test repos."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def minimal_repo(temp_repo: Path):
    """Create a minimal valid repo structure."""
    # README
    (temp_repo / "README.md").write_text("# Test Project\n\nA test project.")

    # LICENSE
    (temp_repo / "LICENSE").write_text("MIT License")

    # .gitignore
    (temp_repo / ".gitignore").write_text("*.pyc\n__pycache__/\n.env\n")

    # Basic Python structure
    (temp_repo / "src").mkdir()
    (temp_repo / "src" / "__init__.py").write_text("")
    (temp_repo / "src" / "main.py").write_text("def main():\n    print('Hello')\n")

    # Tests
    (temp_repo / "tests").mkdir()
    (temp_repo / "tests" / "__init__.py").write_text("")
    (temp_repo / "tests" / "test_main.py").write_text("def test_example():\n    assert True\n")

    # pyproject.toml
    (temp_repo / "pyproject.toml").write_text("""[project]
name = "test-project"
version = "0.1.0"
""")

    return temp_repo


@pytest.fixture
def bad_repo(temp_repo: Path):
    """Create a repo with many issues."""
    # Only a single Python file, nothing else
    (temp_repo / "main.py").write_text("print('hello')\n")
    return temp_repo


@pytest.fixture
def good_repo(temp_repo: Path):
    """Create a repo with best practices."""
    # README
    (temp_repo / "README.md").write_text("""# Great Project

![Build](https://github.com/example/project/actions/workflows/ci.yml/badge.svg)

A well-maintained project.
""")

    # LICENSE
    (temp_repo / "LICENSE").write_text("MIT License")

    # CONTRIBUTING
    (temp_repo / "CONTRIBUTING.md").write_text("# Contributing\n\nPlease read our guidelines.")

    # SECURITY
    (temp_repo / "SECURITY.md").write_text("# Security\n\nReport vulnerabilities to security@example.com")

    # CHANGELOG
    (temp_repo / "CHANGELOG.md").write_text("# Changelog\n\n## 1.0.0\n- Initial release")

    # .gitignore
    (temp_repo / ".gitignore").write_text("*.pyc\n__pycache__/\n.env\n")

    # .editorconfig
    (temp_repo / ".editorconfig").write_text("[*]\nindent_style = space\n")

    # CI
    (temp_repo / ".github").mkdir()
    (temp_repo / ".github" / "workflows").mkdir()
    (temp_repo / ".github" / "workflows" / "ci.yml").write_text("""name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest
""")

    # Dependabot
    (temp_repo / ".github" / "dependabot.yml").write_text("version: 2\nupdates: []\n")

    # CODEOWNERS
    (temp_repo / ".github" / "CODEOWNERS").write_text("* @maintainer\n")

    # Tests
    (temp_repo / "tests").mkdir()
    (temp_repo / "tests" / "test_main.py").write_text("def test_example():\n    assert True\n")

    # pyproject.toml with linter config
    (temp_repo / "pyproject.toml").write_text("""[project]
name = "great-project"
version = "1.0.0"

[tool.ruff]
line-length = 100
""")

    # Lockfile
    (temp_repo / "poetry.lock").write_text("# lockfile content\n")

    return temp_repo
