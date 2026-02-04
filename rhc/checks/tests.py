"""Test and quality checks."""

import re

from rhc.checks.base import BaseCheck, CheckInfo
from rhc.context import Context
from rhc.types import Category, Evidence, Finding, Severity


class TestsDetectedCheck(BaseCheck):
    """Check if tests are present in the repository."""

    info = CheckInfo(
        id="TESTS.DETECTED",
        title="Tests detected",
        category=Category.TESTS,
        description="""Checks if test files or directories exist.

Searches for:
- test/tests/spec directories
- *_test.py, test_*.py files (Python)
- *.test.js, *.spec.js files (JavaScript)
- *_test.go files (Go)
- Test*.java files (Java)

Tests are essential for:
- Preventing regressions
- Documenting expected behavior
- Enabling confident refactoring

Evidence: Lists test directories/files found or notes absence.""",
        default_weight=-8,
    )

    def run(self, ctx: Context) -> list[Finding]:
        # Test directories
        test_dirs = ["tests", "test", "spec", "__tests__", "specs"]
        for dir_name in test_dirs:
            if ctx.fs.exists(dir_name):
                return []

        # Test file patterns
        test_patterns = [
            "**/*_test.py",
            "**/test_*.py",
            "**/*.test.js",
            "**/*.spec.js",
            "**/*.test.ts",
            "**/*.spec.ts",
            "**/*_test.go",
            "**/Test*.java",
            "**/*Test.java",
            "**/*_spec.rb",
        ]

        for pattern in test_patterns:
            files = list(ctx.fs.glob(pattern))
            if files:
                return []

        return [
            Finding(
                id=self.info.id,
                title="No tests detected",
                severity=Severity.HIGH,
                category=self.info.category,
                score_impact=self.get_weight(ctx.config.checks.weights),
                evidence=[
                    Evidence(
                        description="No test files or directories found",
                        details={"searched_dirs": test_dirs},
                    )
                ],
                recommendation="Add tests. Create a tests/ directory and write unit tests for core functionality.",
            )
        ]


class CIRunsTestsCheck(BaseCheck):
    """Check if CI configuration runs tests."""

    info = CheckInfo(
        id="TESTS.CI_RUNS_TESTS",
        title="CI runs tests",
        category=Category.TESTS,
        description="""Checks if CI workflow files contain test commands.

Searches CI configs for patterns like:
- pytest, npm test, go test
- test step keywords
- coverage commands

Running tests in CI ensures:
- Tests are not skipped locally
- All PRs are validated
- Consistent test environment

Evidence: Lists test commands found or notes absence.""",
        default_weight=-5,
    )

    def run(self, ctx: Context) -> list[Finding]:
        # Find CI files
        ci_files = list(ctx.fs.glob(".github/workflows/*.yml")) + list(
            ctx.fs.glob(".github/workflows/*.yaml")
        )
        ci_files.extend(list(ctx.fs.glob(".gitlab-ci.yml")))
        ci_files.extend(list(ctx.fs.glob(".circleci/config.yml")))
        ci_files.extend(list(ctx.fs.glob(".travis.yml")))

        if not ci_files:
            # No CI, skip (CI check will catch it)
            return []

        test_patterns = [
            r"\bpytest\b",
            r"\bnpm\s+test\b",
            r"\byarn\s+test\b",
            r"\bgo\s+test\b",
            r"\bcargo\s+test\b",
            r"\bmvn\s+test\b",
            r"\bgradle\s+test\b",
            r"\brspec\b",
            r"\bphpunit\b",
            r"run:\s*['\"]?test",
            r"script:\s*['\"]?test",
            r"\bcoverage\b",
            r"\bjest\b",
            r"\bmocha\b",
            r"\bvitest\b",
        ]

        for ci_file in ci_files:
            content = ctx.fs.read_text_safe(ci_file)
            if not content:
                continue

            for pattern in test_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return []

        return [
            Finding(
                id=self.info.id,
                title="CI does not appear to run tests",
                severity=Severity.MEDIUM,
                category=self.info.category,
                score_impact=self.get_weight(ctx.config.checks.weights),
                evidence=[
                    Evidence(
                        description="CI configuration files don't contain recognizable test commands",
                        files=[str(f) for f in ci_files[:5]],
                    )
                ],
                recommendation="Add test steps to your CI workflow (e.g., 'pytest' or 'npm test').",
            )
        ]


class LinterPresentCheck(BaseCheck):
    """Check if a linter is configured."""

    info = CheckInfo(
        id="QUALITY.LINTER_PRESENT",
        title="Linter configured",
        category=Category.TESTS,
        description="""Checks if a linter or formatter is configured.

Searches for:
- Python: ruff.toml, .flake8, .pylintrc, pyproject.toml [tool.ruff]
- JavaScript: .eslintrc*, .prettierrc*
- Go: .golangci.yml
- Rust: rustfmt.toml, clippy.toml

Linters ensure:
- Consistent code style
- Early bug detection
- Best practice enforcement

Evidence: Lists linter configs found or notes absence.""",
        default_weight=-4,
    )

    def run(self, ctx: Context) -> list[Finding]:
        linter_configs = [
            # Python
            "ruff.toml",
            ".ruff.toml",
            ".flake8",
            ".pylintrc",
            "pylintrc",
            ".mypy.ini",
            "mypy.ini",
            # JavaScript/TypeScript
            ".eslintrc",
            ".eslintrc.js",
            ".eslintrc.json",
            ".eslintrc.yml",
            ".prettierrc",
            ".prettierrc.js",
            ".prettierrc.json",
            "biome.json",
            # Go
            ".golangci.yml",
            ".golangci.yaml",
            # Rust
            "rustfmt.toml",
            ".rustfmt.toml",
            "clippy.toml",
            # Ruby
            ".rubocop.yml",
            # PHP
            ".php-cs-fixer.php",
            "phpcs.xml",
        ]

        for config in linter_configs:
            if ctx.fs.exists(config):
                return []

        # Check pyproject.toml for [tool.ruff] or similar
        pyproject = list(ctx.fs.glob("pyproject.toml"))
        if pyproject:
            content = ctx.fs.read_text_safe(pyproject[0])
            if content and "[tool.ruff]" in content:
                return []
            if content and "[tool.black]" in content:
                return []
            if content and "[tool.pylint]" in content:
                return []

        # Check package.json for eslint config
        package_json = list(ctx.fs.glob("package.json"))
        if package_json:
            content = ctx.fs.read_text_safe(package_json[0])
            if content and '"eslintConfig"' in content:
                return []

        return [
            Finding(
                id=self.info.id,
                title="No linter/formatter configured",
                severity=Severity.MEDIUM,
                category=self.info.category,
                score_impact=self.get_weight(ctx.config.checks.weights),
                evidence=[Evidence(description="No linter configuration files found")],
                recommendation="Configure a linter (ruff for Python, ESLint for JS/TS, golangci-lint for Go).",
            )
        ]
