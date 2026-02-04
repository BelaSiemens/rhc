"""Hygiene and standards checks."""

import re

from rhc.checks.base import BaseCheck, CheckInfo
from rhc.context import Context
from rhc.types import Category, Evidence, Finding, Severity


class GitignorePresentCheck(BaseCheck):
    """Check for .gitignore file."""

    info = CheckInfo(
        id="HYG.GITIGNORE_PRESENT",
        title=".gitignore present",
        category=Category.HYGIENE,
        description="""Checks if a .gitignore file exists.

A .gitignore ensures:
- Build artifacts aren't committed
- IDE/editor files stay local
- Secrets in .env files are protected
- Cleaner repository history

Evidence: Notes .gitignore presence or absence.""",
        default_weight=-4,
    )

    def run(self, ctx: Context) -> list[Finding]:
        if ctx.fs.exists(".gitignore"):
            return []

        return [
            Finding(
                id=self.info.id,
                title="Missing .gitignore",
                severity=Severity.MEDIUM,
                category=self.info.category,
                score_impact=self.get_weight(ctx.config.checks.weights),
                evidence=[Evidence(description="No .gitignore file found")],
                recommendation="Add a .gitignore file. Use gitignore.io to generate one for your stack.",
            )
        ]


class EditorconfigPresentCheck(BaseCheck):
    """Check for .editorconfig file."""

    info = CheckInfo(
        id="HYG.EDITORCONFIG_PRESENT",
        title=".editorconfig present",
        category=Category.HYGIENE,
        description="""Checks if an .editorconfig file exists.

EditorConfig ensures:
- Consistent indentation across editors
- Consistent line endings
- Consistent charset
- Reduced whitespace diffs

Evidence: Notes .editorconfig presence or absence.""",
        default_weight=-2,
    )

    def run(self, ctx: Context) -> list[Finding]:
        if ctx.fs.exists(".editorconfig"):
            return []

        return [
            Finding(
                id=self.info.id,
                title="Missing .editorconfig",
                severity=Severity.INFO,
                category=self.info.category,
                score_impact=self.get_weight(ctx.config.checks.weights),
                evidence=[Evidence(description="No .editorconfig file found")],
                recommendation="Add an .editorconfig file for consistent formatting across editors.",
            )
        ]


class SemverTagsPresentCheck(BaseCheck):
    """Check for semantic versioning tags."""

    info = CheckInfo(
        id="REL.SEMVER_TAGS_PRESENT",
        title="Semantic version tags",
        category=Category.RELEASE,
        description="""Checks if the repository has semver-style version tags.

Searches for tags matching:
- v1.0.0, v0.1.0 (with v prefix)
- 1.0.0, 0.1.0 (without prefix)

Version tags help:
- Track release history
- Enable automatic changelog generation
- Support version pinning

Evidence: Lists version tags found or notes absence.""",
        default_weight=-3,
    )

    def run(self, ctx: Context) -> list[Finding]:
        if not ctx.git.is_repo:
            # Not a git repo, skip
            return []

        if not ctx.git.tags:
            return [
                Finding(
                    id=self.info.id,
                    title="No version tags found",
                    severity=Severity.LOW,
                    category=self.info.category,
                    score_impact=self.get_weight(ctx.config.checks.weights),
                    evidence=[Evidence(description="No git tags found")],
                    recommendation="Use semantic versioning tags (v1.0.0) for releases.",
                )
            ]

        # Check for semver pattern
        semver_pattern = r"^v?\d+\.\d+\.\d+"
        semver_tags = [t for t in ctx.git.tags if re.match(semver_pattern, t)]

        if not semver_tags:
            return [
                Finding(
                    id=self.info.id,
                    title="No semver tags found",
                    severity=Severity.LOW,
                    category=self.info.category,
                    score_impact=self.get_weight(ctx.config.checks.weights),
                    evidence=[
                        Evidence(
                            description=f"Found {len(ctx.git.tags)} tags but none follow semver",
                            details={"tags_found": ctx.git.tags[:5]},
                        )
                    ],
                    recommendation="Use semantic versioning tags (v1.0.0, v1.2.3).",
                )
            ]

        return []


class ChangelogPresentCheck(BaseCheck):
    """Check for CHANGELOG file."""

    info = CheckInfo(
        id="REL.CHANGELOG_PRESENT",
        title="CHANGELOG present",
        category=Category.RELEASE,
        description="""Checks if a changelog file exists.

Searches for:
- CHANGELOG.md, CHANGELOG
- HISTORY.md, HISTORY
- CHANGES.md, CHANGES
- NEWS.md

A changelog helps:
- Track breaking changes
- Document new features
- Communicate release notes

Evidence: Notes changelog presence or absence.""",
        default_weight=-3,
    )

    def run(self, ctx: Context) -> list[Finding]:
        changelog_patterns = [
            "CHANGELOG.md",
            "CHANGELOG",
            "CHANGELOG.txt",
            "HISTORY.md",
            "HISTORY",
            "CHANGES.md",
            "CHANGES",
            "NEWS.md",
            "NEWS",
            "changelog.md",
        ]

        for pattern in changelog_patterns:
            if ctx.fs.exists(pattern):
                return []

        return [
            Finding(
                id=self.info.id,
                title="Missing CHANGELOG",
                severity=Severity.LOW,
                category=self.info.category,
                score_impact=self.get_weight(ctx.config.checks.weights),
                evidence=[Evidence(description="No changelog file found")],
                recommendation="Add a CHANGELOG.md following https://keepachangelog.com/ format.",
            )
        ]
