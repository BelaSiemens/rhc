"""CI/CD checks."""

import re

from rhc.checks.base import BaseCheck, CheckInfo
from rhc.context import Context
from rhc.types import Category, Evidence, Finding, Severity


class CIConfigPresentCheck(BaseCheck):
    """Check for CI/CD configuration presence."""

    info = CheckInfo(
        id="CI.CONFIG_PRESENT",
        title="CI/CD configuration present",
        category=Category.CI,
        description="""Checks if any CI/CD configuration exists.

Searches for:
- GitHub Actions: .github/workflows/*.yml
- GitLab CI: .gitlab-ci.yml
- CircleCI: .circleci/config.yml
- Travis CI: .travis.yml
- Azure Pipelines: azure-pipelines.yml
- Jenkins: Jenkinsfile

Continuous Integration ensures:
- Code is tested on every change
- Consistent build environment
- Early bug detection

Evidence: Lists CI providers found or notes absence.""",
        default_weight=-10,
    )

    def run(self, ctx: Context) -> list[Finding]:
        ci_configs = {
            "GitHub Actions": [".github/workflows/*.yml", ".github/workflows/*.yaml"],
            "GitLab CI": [".gitlab-ci.yml"],
            "CircleCI": [".circleci/config.yml"],
            "Travis CI": [".travis.yml"],
            "Azure Pipelines": ["azure-pipelines.yml"],
            "Jenkins": ["Jenkinsfile"],
        }

        found_providers = []
        for provider, patterns in ci_configs.items():
            for pattern in patterns:
                if ctx.fs.exists(pattern):
                    found_providers.append(provider)
                    break

        if found_providers:
            return []

        return [
            Finding(
                id=self.info.id,
                title="No CI/CD configuration found",
                severity=Severity.HIGH,
                category=self.info.category,
                score_impact=self.get_weight(ctx.config.checks.weights),
                evidence=[
                    Evidence(
                        description="No CI/CD configuration files detected",
                        details={"searched_providers": list(ci_configs.keys())},
                    )
                ],
                recommendation="Set up CI/CD. For GitHub, create .github/workflows/ci.yml",
            )
        ]


class BadgesPresentCheck(BaseCheck):
    """Check for status badges in README."""

    info = CheckInfo(
        id="CI.BADGES_PRESENT",
        title="Status badges in README",
        category=Category.CI,
        description="""Checks if the README contains status badges.

Searches for common badge patterns:
- shields.io badges
- GitHub Actions status badges
- codecov/coveralls badges
- npm/pypi version badges

Badges provide at-a-glance project health info:
- Build status
- Test coverage
- Version information

Evidence: Lists badge patterns found or notes absence.""",
        default_weight=-2,
    )

    def run(self, ctx: Context) -> list[Finding]:
        readme_patterns = ["README.md", "README.rst", "README", "readme.md"]

        readme_content = None
        for pattern in readme_patterns:
            files = list(ctx.fs.glob(pattern))
            if files:
                readme_content = ctx.fs.read_text_safe(files[0])
                break

        if not readme_content:
            # No README, skip this check (README check will catch it)
            return []

        # Common badge patterns
        badge_patterns = [
            r"!\[.*\]\(https?://.*shields\.io",
            r"!\[.*\]\(https?://.*badge",
            r"!\[.*\]\(https?://github\.com/.*/(workflows|actions)",
            r"!\[.*\]\(https?://codecov\.io",
            r"!\[.*\]\(https?://coveralls\.io",
            r"!\[.*\]\(https?://img\.shields\.io",
        ]

        for pattern in badge_patterns:
            if re.search(pattern, readme_content, re.IGNORECASE):
                return []

        return [
            Finding(
                id=self.info.id,
                title="No status badges in README",
                severity=Severity.INFO,
                category=self.info.category,
                score_impact=self.get_weight(ctx.config.checks.weights),
                evidence=[Evidence(description="README does not contain recognizable status badges")],
                recommendation="Add status badges (build, coverage, version) to README for quick health visibility.",
            )
        ]
