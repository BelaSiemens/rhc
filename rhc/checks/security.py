"""Security baseline checks."""

import re

from rhc.checks.base import BaseCheck, CheckInfo
from rhc.context import Context
from rhc.types import Category, Evidence, Finding, Severity

# Conservative secret patterns - prioritize low false positives
SECRET_PATTERNS = [
    # AWS
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    # Generic API keys with = or :
    (r"(?i)api[_-]?key\s*[=:]\s*['\"][a-zA-Z0-9_\-]{20,}['\"]", "API Key assignment"),
    # Private keys
    (r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----", "Private Key header"),
    # GitHub tokens
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
    (r"gho_[a-zA-Z0-9]{36}", "GitHub OAuth Token"),
    (r"ghs_[a-zA-Z0-9]{36}", "GitHub App Token"),
    # Slack tokens
    (r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*", "Slack Token"),
    # Stripe keys
    (r"sk_live_[a-zA-Z0-9]{24,}", "Stripe Secret Key"),
    # Generic secrets in env files (conservative)
    (r"(?i)(?:password|secret|token)\s*=\s*['\"][^'\"]{10,}['\"]", "Hardcoded credential"),
]

# Files to skip (binary, vendored, etc.)
SKIP_PATTERNS = [
    r"\.min\.js$",
    r"node_modules/",
    r"vendor/",
    r"\.lock$",
    r"\.sum$",
    r"package-lock\.json$",
    r"yarn\.lock$",
    r"\.woff",
    r"\.ttf",
    r"\.eot",
    r"\.ico$",
    r"\.png$",
    r"\.jpg$",
    r"\.gif$",
    r"\.svg$",
]


class SecretsSuspectedCheck(BaseCheck):
    """Check for suspected secrets in code."""

    info = CheckInfo(
        id="SEC.SECRETS_SUSPECTED",
        title="Secrets detection (suspected)",
        category=Category.SECURITY,
        description="""Scans for patterns that may indicate hardcoded secrets.

Looks for:
- AWS Access Key IDs (AKIA...)
- GitHub/Slack/Stripe tokens
- Private key headers
- Password/secret assignments

This uses conservative patterns to minimize false positives.
Only reports file paths, NEVER logs actual secret values.

Evidence: Lists files with suspected patterns (not the values).""",
        default_weight=-10,
    )

    def run(self, ctx: Context) -> list[Finding]:
        suspected_files: list[tuple[str, str]] = []  # (file, pattern_type)

        # Scan source files
        source_patterns = [
            "**/*.py",
            "**/*.js",
            "**/*.ts",
            "**/*.go",
            "**/*.java",
            "**/*.rb",
            "**/*.php",
            "**/*.sh",
            "**/*.bash",
            "**/*.yml",
            "**/*.yaml",
            "**/*.json",
            "**/*.env",
            "**/*.env.*",
            "**/config.*",
        ]

        scanned_files = 0
        max_files = 500  # Limit for performance

        for source_pattern in source_patterns:
            for file_path in ctx.fs.glob(source_pattern):
                if scanned_files >= max_files:
                    break

                # Skip files matching skip patterns
                file_str = str(file_path)
                if any(re.search(skip, file_str) for skip in SKIP_PATTERNS):
                    continue

                content = ctx.fs.read_text_safe(file_path, max_size=512 * 1024)  # 512KB limit
                if not content:
                    continue

                scanned_files += 1

                for pattern, pattern_name in SECRET_PATTERNS:
                    if re.search(pattern, content):
                        rel_path = str(file_path.relative_to(ctx.root_path))
                        suspected_files.append((rel_path, pattern_name))
                        break  # One finding per file is enough

        if suspected_files:
            # Group by pattern type
            unique_files = list(set(f[0] for f in suspected_files))
            pattern_types = list(set(f[1] for f in suspected_files))

            return [
                Finding(
                    id=self.info.id,
                    title=f"Suspected secrets in {len(unique_files)} file(s)",
                    severity=Severity.CRITICAL,
                    category=self.info.category,
                    score_impact=self.get_weight(ctx.config.checks.weights),
                    evidence=[
                        Evidence(
                            description=f"Patterns detected: {', '.join(pattern_types)}",
                            files=unique_files[:10],  # Limit to first 10
                            details={"total_suspect_files": len(unique_files)},
                        )
                    ],
                    recommendation="Review flagged files. Use environment variables or secret managers instead of hardcoding.",
                    refs=["https://git-secret.io/", "https://docs.github.com/en/actions/security-guides/encrypted-secrets"],
                )
            ]

        return []


class DependabotPresentCheck(BaseCheck):
    """Check for Dependabot configuration."""

    info = CheckInfo(
        id="SEC.DEPENDABOT_PRESENT",
        title="Dependabot configured",
        category=Category.SECURITY,
        description="""Checks if Dependabot or Renovate is configured.

Searches for:
- .github/dependabot.yml
- renovate.json, renovate.json5, .renovaterc

Automated dependency updates help:
- Patch security vulnerabilities quickly
- Keep dependencies current
- Reduce technical debt

Evidence: Notes configuration presence or absence.""",
        default_weight=-3,
    )

    def run(self, ctx: Context) -> list[Finding]:
        configs = [
            ".github/dependabot.yml",
            ".github/dependabot.yaml",
            "renovate.json",
            "renovate.json5",
            ".renovaterc",
            ".renovaterc.json",
        ]

        for config in configs:
            if ctx.fs.exists(config):
                return []

        return [
            Finding(
                id=self.info.id,
                title="No automated dependency updates configured",
                severity=Severity.LOW,
                category=self.info.category,
                score_impact=self.get_weight(ctx.config.checks.weights),
                evidence=[Evidence(description="No Dependabot or Renovate configuration found")],
                recommendation="Add .github/dependabot.yml for automated security updates.",
            )
        ]


class CodeownersPresentCheck(BaseCheck):
    """Check for CODEOWNERS file."""

    info = CheckInfo(
        id="SEC.CODEOWNERS_PRESENT",
        title="CODEOWNERS defined",
        category=Category.SECURITY,
        description="""Checks if a CODEOWNERS file exists.

Searches for:
- CODEOWNERS
- .github/CODEOWNERS
- docs/CODEOWNERS

CODEOWNERS ensures:
- Required reviewers for sensitive files
- Clear ownership of code areas
- Reduced bus factor

Evidence: Notes CODEOWNERS presence or absence.""",
        default_weight=-3,
    )

    def run(self, ctx: Context) -> list[Finding]:
        patterns = ["CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS"]

        for pattern in patterns:
            if ctx.fs.exists(pattern):
                return []

        return [
            Finding(
                id=self.info.id,
                title="No CODEOWNERS file",
                severity=Severity.LOW,
                category=self.info.category,
                score_impact=self.get_weight(ctx.config.checks.weights),
                evidence=[Evidence(description="No CODEOWNERS file found")],
                recommendation="Add a CODEOWNERS file to define code ownership and required reviewers.",
            )
        ]
