"""Tests for scanner and scoring."""

from pathlib import Path

from rhc.config import Config
from rhc.scanner import scan
from rhc.scoring import calculate_grade, calculate_score
from rhc.types import Category, Finding, Severity


def test_calculate_score_no_findings():
    """Test score is 100 with no findings."""
    score = calculate_score([])
    assert score == 100


def test_calculate_score_with_findings():
    """Test score decreases with findings."""
    findings = [
        Finding(
            id="TEST.1",
            title="Test",
            severity=Severity.HIGH,
            category=Category.DOCS,
            score_impact=-10,
        ),
        Finding(
            id="TEST.2",
            title="Test 2",
            severity=Severity.LOW,
            category=Category.DOCS,
            score_impact=-5,
        ),
    ]
    score = calculate_score(findings)
    assert score == 85


def test_calculate_score_clamps_to_zero():
    """Test score doesn't go below 0."""
    findings = [
        Finding(
            id="TEST.BIG",
            title="Test",
            severity=Severity.CRITICAL,
            category=Category.DOCS,
            score_impact=-200,
        )
    ]
    score = calculate_score(findings)
    assert score == 0


def test_grades():
    """Test grade mapping."""
    assert calculate_grade(100) == "A"
    assert calculate_grade(95) == "A"
    assert calculate_grade(90) == "A"
    assert calculate_grade(89) == "B"
    assert calculate_grade(80) == "B"
    assert calculate_grade(79) == "C"
    assert calculate_grade(70) == "C"
    assert calculate_grade(69) == "D"
    assert calculate_grade(55) == "D"
    assert calculate_grade(54) == "F"
    assert calculate_grade(0) == "F"


def test_scan_minimal_repo(minimal_repo: Path):
    """Test scanning a minimal repo produces a report."""
    report = scan(minimal_repo, Config())

    assert report.summary.total_score > 0
    assert report.summary.grade in ["A", "B", "C", "D", "F"]
    assert report.meta.tool_version == "0.1.0"
    assert report.meta.duration_ms >= 0
    assert isinstance(report.findings, list)


def test_scan_good_repo(good_repo: Path):
    """Test a good repo scores high."""
    report = scan(good_repo, Config())

    # Good repo should have very few findings
    assert report.summary.total_score >= 80, f"Score {report.summary.total_score} too low"
    assert report.summary.grade in ["A", "B"]


def test_scan_bad_repo(bad_repo: Path):
    """Test a bad repo has many findings."""
    report = scan(bad_repo, Config())

    # Bad repo should have many issues
    assert len(report.findings) >= 5
    assert report.summary.total_score < 70


def test_scan_with_skip_config(minimal_repo: Path):
    """Test skipping checks via config."""
    config = Config()
    config.checks.skip = ["DOC.LICENSE_PRESENT", "DOC.CONTRIBUTING_PRESENT"]

    report = scan(minimal_repo, config)

    finding_ids = [f.id for f in report.findings]
    assert "DOC.LICENSE_PRESENT" not in finding_ids
    assert "DOC.CONTRIBUTING_PRESENT" not in finding_ids


def test_scan_with_only_config(minimal_repo: Path):
    """Test running only specific checks."""
    config = Config()
    config.checks.only = ["DOC.README_PRESENT"]

    report = scan(minimal_repo, config)

    # Should only have findings from that check (or none if it passes)
    for finding in report.findings:
        assert finding.id == "DOC.README_PRESENT"


def test_report_to_dict(minimal_repo: Path):
    """Test report serialization."""
    report = scan(minimal_repo, Config())
    data = report.to_dict()

    assert "meta" in data
    assert "repo" in data
    assert "summary" in data
    assert "findings" in data
    assert "metrics" in data
    assert data["meta"]["tool_version"] == "0.1.0"
