"""Documentation checks."""

from rhc.checks.base import BaseCheck, CheckInfo
from rhc.context import Context
from rhc.types import Category, Evidence, Finding, Severity


class ReadmePresentCheck(BaseCheck):
    """Check for README file presence."""

    info = CheckInfo(
        id="DOC.README_PRESENT",
        title="README file present",
        category=Category.DOCS,
        description="""Checks if a README file exists in the repository root.

Searches for: README, README.md, README.rst, README.txt (case-insensitive).

A README is essential for any project as it provides:
- Project overview and purpose
- Installation instructions
- Basic usage examples
- Links to further documentation

Evidence: Lists the README file found or notes its absence.""",
        default_weight=-6,
    )

    def run(self, ctx: Context) -> list[Finding]:
        patterns = ["README", "README.md", "README.rst", "README.txt", "readme.md", "Readme.md"]

        for pattern in patterns:
            files = list(ctx.fs.glob(pattern))
            if files:
                return []  # README found, no issue

        return [
            Finding(
                id=self.info.id,
                title="Missing README",
                severity=Severity.HIGH,
                category=self.info.category,
                score_impact=self.get_weight(ctx.config.checks.weights),
                evidence=[Evidence(description="No README file found in repository root")],
                recommendation="Create a README.md with project overview, installation, and usage instructions.",
            )
        ]


class LicensePresentCheck(BaseCheck):
    """Check for LICENSE file presence."""

    info = CheckInfo(
        id="DOC.LICENSE_PRESENT",
        title="LICENSE file present",
        category=Category.DOCS,
        description="""Checks if a LICENSE file exists in the repository root.

Searches for: LICENSE, LICENSE.md, LICENSE.txt, LICENCE (case variations).

A license is legally required to grant usage rights and is essential for:
- Open source compliance
- Legal clarity for contributors and users
- Package registry requirements

Evidence: Lists the LICENSE file found or notes its absence.""",
        default_weight=-4,
    )

    def run(self, ctx: Context) -> list[Finding]:
        patterns = [
            "LICENSE",
            "LICENSE.md",
            "LICENSE.txt",
            "LICENCE",
            "LICENCE.md",
            "license",
            "license.md",
        ]

        for pattern in patterns:
            files = list(ctx.fs.glob(pattern))
            if files:
                return []

        return [
            Finding(
                id=self.info.id,
                title="Missing LICENSE",
                severity=Severity.MEDIUM,
                category=self.info.category,
                score_impact=self.get_weight(ctx.config.checks.weights),
                evidence=[Evidence(description="No LICENSE file found in repository root")],
                recommendation="Add a LICENSE file. Use https://choosealicense.com/ to select an appropriate license.",
            )
        ]


class ContributingPresentCheck(BaseCheck):
    """Check for CONTRIBUTING file presence."""

    info = CheckInfo(
        id="DOC.CONTRIBUTING_PRESENT",
        title="CONTRIBUTING guide present",
        category=Category.DOCS,
        description="""Checks if a CONTRIBUTING guide exists.

Searches for: CONTRIBUTING.md, CONTRIBUTING, .github/CONTRIBUTING.md

A contributing guide helps maintainers by:
- Setting expectations for PRs
- Documenting code style and process
- Reducing friction for new contributors

Evidence: Lists the file found or notes its absence.""",
        default_weight=-3,
    )

    def run(self, ctx: Context) -> list[Finding]:
        patterns = ["CONTRIBUTING", "CONTRIBUTING.md", ".github/CONTRIBUTING.md"]

        for pattern in patterns:
            files = list(ctx.fs.glob(pattern))
            if files:
                return []

        return [
            Finding(
                id=self.info.id,
                title="Missing CONTRIBUTING guide",
                severity=Severity.LOW,
                category=self.info.category,
                score_impact=self.get_weight(ctx.config.checks.weights),
                evidence=[Evidence(description="No CONTRIBUTING file found")],
                recommendation="Add a CONTRIBUTING.md describing how to contribute, code style, and PR process.",
            )
        ]


class SecurityPolicyPresentCheck(BaseCheck):
    """Check for SECURITY policy file presence."""

    info = CheckInfo(
        id="DOC.SECURITY_POLICY_PRESENT",
        title="Security policy present",
        category=Category.DOCS,
        description="""Checks if a security policy exists.

Searches for: SECURITY.md, .github/SECURITY.md

A security policy helps by:
- Providing clear vulnerability reporting instructions
- Setting expectations for response times
- Reducing risk of public vulnerability disclosure

Evidence: Lists the file found or notes its absence.""",
        default_weight=-3,
    )

    def run(self, ctx: Context) -> list[Finding]:
        patterns = ["SECURITY.md", ".github/SECURITY.md", "SECURITY"]

        for pattern in patterns:
            files = list(ctx.fs.glob(pattern))
            if files:
                return []

        return [
            Finding(
                id=self.info.id,
                title="Missing Security Policy",
                severity=Severity.LOW,
                category=self.info.category,
                score_impact=self.get_weight(ctx.config.checks.weights),
                evidence=[Evidence(description="No SECURITY.md file found")],
                recommendation="Add a SECURITY.md with vulnerability reporting instructions.",
            )
        ]
