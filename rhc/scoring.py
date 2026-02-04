"""Scoring and grading logic."""

from rhc.types import Finding, Severity, Summary


def calculate_score(findings: list[Finding]) -> int:
    """Calculate the health score from findings.

    Starts at 100, subtracts score_impact from each finding.
    Result is clamped to 0-100.
    """
    score = 100

    for finding in findings:
        score += finding.score_impact  # score_impact is negative

    return max(0, min(100, score))


def calculate_grade(score: int) -> str:
    """Map score to letter grade.

    A: 90-100
    B: 80-89
    C: 70-79
    D: 55-69
    F: 0-54
    """
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 55:
        return "D"
    else:
        return "F"


def count_by_severity(findings: list[Finding]) -> dict[str, int]:
    """Count findings by severity level."""
    counts: dict[str, int] = {s.value: 0 for s in Severity}
    for finding in findings:
        counts[finding.severity.value] += 1
    return counts


def count_by_category(findings: list[Finding]) -> dict[str, int]:
    """Count findings by category."""
    counts: dict[str, int] = {}
    for finding in findings:
        cat = finding.category.value
        counts[cat] = counts.get(cat, 0) + 1
    return counts


def create_summary(findings: list[Finding]) -> Summary:
    """Create a summary from findings."""
    score = calculate_score(findings)
    return Summary(
        total_score=score,
        grade=calculate_grade(score),
        counts_by_severity=count_by_severity(findings),
        counts_by_category=count_by_category(findings),
    )


def check_policy_violation(
    findings: list[Finding],
    summary: Summary,
    min_score: int | None = None,
    fail_on: Severity | None = None,
) -> tuple[bool, str]:
    """Check if any policy is violated.

    Returns (violated, reason) tuple.
    """
    # Check min_score
    if min_score is not None and summary.total_score < min_score:
        return True, f"Score {summary.total_score} is below minimum {min_score}"

    # Check fail_on severity
    if fail_on is not None:
        for finding in findings:
            if finding.severity >= fail_on:
                return True, f"Found {finding.severity.value} severity issue: {finding.id}"

    return False, ""
