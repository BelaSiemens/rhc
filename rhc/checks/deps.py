"""Dependency checks."""

import time

from rhc.checks.base import BaseCheck, CheckInfo
from rhc.context import Context
from rhc.types import Category, Evidence, Finding, Severity


class LockfilePresentCheck(BaseCheck):
    """Check for dependency lockfile presence."""

    info = CheckInfo(
        id="DEPS.LOCKFILE_PRESENT",
        title="Dependency lockfile present",
        category=Category.DEPS,
        description="""Checks if a dependency lockfile exists.

Searches for:
- npm: package-lock.json
- yarn: yarn.lock
- pnpm: pnpm-lock.yaml
- Python: poetry.lock, Pipfile.lock, uv.lock, requirements.txt (frozen)
- Go: go.sum
- Rust: Cargo.lock
- Ruby: Gemfile.lock
- PHP: composer.lock

Lockfiles ensure:
- Reproducible builds
- Consistent dependency versions
- Security audit capability

Evidence: Lists lockfiles found or notes absence.""",
        default_weight=-6,
    )

    def run(self, ctx: Context) -> list[Finding]:
        # Check if there are any package manifests first
        manifests = [
            "package.json",
            "pyproject.toml",
            "setup.py",
            "requirements.txt",
            "Pipfile",
            "go.mod",
            "Cargo.toml",
            "Gemfile",
            "composer.json",
        ]

        has_manifest = any(ctx.fs.exists(m) for m in manifests)
        if not has_manifest:
            # No package manager detected, skip this check
            return []

        lockfiles = [
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml",
            "poetry.lock",
            "Pipfile.lock",
            "uv.lock",
            "pdm.lock",
            "go.sum",
            "Cargo.lock",
            "Gemfile.lock",
            "composer.lock",
        ]

        for lockfile in lockfiles:
            if ctx.fs.exists(lockfile):
                return []

        return [
            Finding(
                id=self.info.id,
                title="No dependency lockfile found",
                severity=Severity.MEDIUM,
                category=self.info.category,
                score_impact=self.get_weight(ctx.config.checks.weights),
                evidence=[
                    Evidence(
                        description="Package manifest found but no lockfile",
                        details={"searched_lockfiles": lockfiles},
                    )
                ],
                recommendation="Generate a lockfile (npm install, poetry lock, cargo build) and commit it.",
            )
        ]


class OutdatedHintsCheck(BaseCheck):
    """Check for outdated dependency hints based on lockfile age."""

    info = CheckInfo(
        id="DEPS.OUTDATED_HINTS",
        title="Dependency freshness hints",
        category=Category.DEPS,
        description="""Checks lockfile age as a hint for outdated dependencies.

Uses file modification time as a heuristic:
- Lockfile > 6 months old: warning
- Lockfile > 12 months old: stronger warning

This is a heuristic only - for accurate data use npm audit, pip-audit, etc.

Evidence: Reports lockfile age if concerning.""",
        default_weight=-3,
    )

    def run(self, ctx: Context) -> list[Finding]:
        lockfiles = [
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml",
            "poetry.lock",
            "Pipfile.lock",
            "uv.lock",
            "go.sum",
            "Cargo.lock",
            "Gemfile.lock",
            "composer.lock",
        ]

        six_months_ago = time.time() - (180 * 24 * 60 * 60)
        one_year_ago = time.time() - (365 * 24 * 60 * 60)

        for lockfile_name in lockfiles:
            files = list(ctx.fs.glob(lockfile_name))
            if not files:
                continue

            stats = ctx.fs.file_stats(files[0])
            if not stats:
                continue

            if stats.mtime < one_year_ago:
                return [
                    Finding(
                        id=self.info.id,
                        title="Lockfile appears very outdated",
                        severity=Severity.MEDIUM,
                        category=self.info.category,
                        score_impact=self.get_weight(ctx.config.checks.weights),
                        evidence=[
                            Evidence(
                                description=f"{lockfile_name} was last modified over 12 months ago",
                                files=[str(files[0])],
                            )
                        ],
                        recommendation="Run `npm update`, `poetry update`, or equivalent to refresh dependencies.",
                    )
                ]
            elif stats.mtime < six_months_ago:
                return [
                    Finding(
                        id=self.info.id,
                        title="Lockfile may be outdated",
                        severity=Severity.LOW,
                        category=self.info.category,
                        score_impact=-1,  # Reduced impact for 6-month case
                        evidence=[
                            Evidence(
                                description=f"{lockfile_name} was last modified over 6 months ago",
                                files=[str(files[0])],
                            )
                        ],
                        recommendation="Consider updating dependencies periodically for security patches.",
                    )
                ]

        return []


class MultiplePackageManagersCheck(BaseCheck):
    """Check for conflicting package managers."""

    info = CheckInfo(
        id="DEPS.MULTIPLE_PACKAGE_MANAGERS",
        title="Multiple package managers detected",
        category=Category.DEPS,
        description="""Checks if multiple conflicting package managers are in use.

Detects conflicts like:
- npm + yarn + pnpm (pick one)
- pip + poetry + pipenv (pick one)

Multiple package managers cause:
- Inconsistent lockfiles
- Build confusion
- CI/CD complexity

Evidence: Lists conflicting package managers found.""",
        default_weight=-4,
    )

    def run(self, ctx: Context) -> list[Finding]:
        # JavaScript package manager conflicts
        js_managers = {
            "npm": "package-lock.json",
            "yarn": "yarn.lock",
            "pnpm": "pnpm-lock.yaml",
        }

        js_found = [name for name, lock in js_managers.items() if ctx.fs.exists(lock)]

        if len(js_found) > 1:
            return [
                Finding(
                    id=self.info.id,
                    title="Multiple JavaScript package managers detected",
                    severity=Severity.MEDIUM,
                    category=self.info.category,
                    score_impact=self.get_weight(ctx.config.checks.weights),
                    evidence=[
                        Evidence(
                            description=f"Found lockfiles for: {', '.join(js_found)}",
                            details={"package_managers": js_found},
                        )
                    ],
                    recommendation="Choose one package manager. Delete unused lockfiles and standardize on one.",
                )
            ]

        # Python package manager conflicts
        py_managers = {
            "poetry": "poetry.lock",
            "pipenv": "Pipfile.lock",
            "uv": "uv.lock",
            "pdm": "pdm.lock",
        }

        py_found = [name for name, lock in py_managers.items() if ctx.fs.exists(lock)]

        if len(py_found) > 1:
            return [
                Finding(
                    id=self.info.id,
                    title="Multiple Python package managers detected",
                    severity=Severity.MEDIUM,
                    category=self.info.category,
                    score_impact=self.get_weight(ctx.config.checks.weights),
                    evidence=[
                        Evidence(
                            description=f"Found lockfiles for: {', '.join(py_found)}",
                            details={"package_managers": py_found},
                        )
                    ],
                    recommendation="Choose one package manager. Delete unused lockfiles and standardize on one.",
                )
            ]

        return []
