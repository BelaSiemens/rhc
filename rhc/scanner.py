"""Scanner orchestration."""

import time
from datetime import datetime, timezone
from pathlib import Path

from rhc import __version__
from rhc.checks import filter_checks, get_all_checks
from rhc.config import Config
from rhc.context import Context
from rhc.scoring import create_summary
from rhc.types import Finding, Metrics, RepoInfo, Report, ReportMeta


def scan(path: Path, config: Config) -> Report:
    """Run a full health scan on a repository.

    Args:
        path: Path to the repository root
        config: Configuration for the scan

    Returns:
        Complete health check report
    """
    start_time = time.time()

    # Build context
    ctx = Context.build(path, config)

    # Get and filter checks
    all_checks = get_all_checks()
    checks = filter_checks(
        all_checks,
        skip=config.checks.skip,
        only=config.checks.only if config.checks.only else None,
    )

    # Run all checks
    findings: list[Finding] = []
    for check in checks:
        try:
            check_findings = check.run(ctx)
            findings.extend(check_findings)
        except Exception as e:
            if config.debug:
                print(f"[DEBUG] Check {check.id} failed: {e}")
            # Continue with other checks

    # Sort findings by severity (highest first) then by impact
    findings.sort(key=lambda f: (-list(f.severity.__class__).index(f.severity), f.score_impact))

    # Calculate timing
    duration_ms = int((time.time() - start_time) * 1000)

    # Build report
    report = Report(
        meta=ReportMeta(
            tool_version=__version__,
            timestamp=datetime.now(timezone.utc).isoformat(),
            duration_ms=duration_ms,
        ),
        repo=RepoInfo(
            path=str(path.resolve()),
            is_git_repo=ctx.git.is_repo,
            branch=ctx.git.branch,
            head_sha=ctx.git.head_sha,
        ),
        summary=create_summary(findings),
        findings=findings,
        metrics=Metrics(
            files_count=ctx.fs.count_files(),
            languages_detected=ctx.stack.languages,
            ci_providers_found=ctx.stack.ci_providers,
            package_managers_found=ctx.stack.package_managers,
        ),
    )

    return report
