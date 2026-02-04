"""Tests for health checks."""

from pathlib import Path

from rhc.checks.ci import BadgesPresentCheck, CIConfigPresentCheck
from rhc.checks.deps import LockfilePresentCheck, MultiplePackageManagersCheck
from rhc.checks.docs import (
    ContributingPresentCheck,
    LicensePresentCheck,
    ReadmePresentCheck,
    SecurityPolicyPresentCheck,
)
from rhc.checks.hygiene import (
    ChangelogPresentCheck,
    EditorconfigPresentCheck,
    GitignorePresentCheck,
)
from rhc.checks.security import CodeownersPresentCheck, DependabotPresentCheck
from rhc.checks.tests import LinterPresentCheck, TestsDetectedCheck
from rhc.config import Config
from rhc.context import Context


def test_readme_present_pass(minimal_repo: Path):
    """Test README check passes when README exists."""
    ctx = Context.build(minimal_repo, Config())
    check = ReadmePresentCheck()
    findings = check.run(ctx)
    assert len(findings) == 0


def test_readme_present_fail(bad_repo: Path):
    """Test README check fails when README is missing."""
    ctx = Context.build(bad_repo, Config())
    check = ReadmePresentCheck()
    findings = check.run(ctx)
    assert len(findings) == 1
    assert findings[0].id == "DOC.README_PRESENT"


def test_license_present_pass(minimal_repo: Path):
    """Test LICENSE check passes when LICENSE exists."""
    ctx = Context.build(minimal_repo, Config())
    check = LicensePresentCheck()
    findings = check.run(ctx)
    assert len(findings) == 0


def test_license_present_fail(bad_repo: Path):
    """Test LICENSE check fails when LICENSE is missing."""
    ctx = Context.build(bad_repo, Config())
    check = LicensePresentCheck()
    findings = check.run(ctx)
    assert len(findings) == 1
    assert findings[0].id == "DOC.LICENSE_PRESENT"


def test_gitignore_present_pass(minimal_repo: Path):
    """Test .gitignore check passes."""
    ctx = Context.build(minimal_repo, Config())
    check = GitignorePresentCheck()
    findings = check.run(ctx)
    assert len(findings) == 0


def test_gitignore_present_fail(bad_repo: Path):
    """Test .gitignore check fails."""
    ctx = Context.build(bad_repo, Config())
    check = GitignorePresentCheck()
    findings = check.run(ctx)
    assert len(findings) == 1


def test_tests_detected_pass(minimal_repo: Path):
    """Test detection when tests directory exists."""
    ctx = Context.build(minimal_repo, Config())
    check = TestsDetectedCheck()
    findings = check.run(ctx)
    assert len(findings) == 0


def test_tests_detected_fail(bad_repo: Path):
    """Test detection fails when no tests exist."""
    ctx = Context.build(bad_repo, Config())
    check = TestsDetectedCheck()
    findings = check.run(ctx)
    assert len(findings) == 1
    assert findings[0].id == "TESTS.DETECTED"


def test_ci_config_pass(good_repo: Path):
    """Test CI config check passes with valid CI."""
    ctx = Context.build(good_repo, Config())
    check = CIConfigPresentCheck()
    findings = check.run(ctx)
    assert len(findings) == 0


def test_ci_config_fail(bad_repo: Path):
    """Test CI config check fails without CI."""
    ctx = Context.build(bad_repo, Config())
    check = CIConfigPresentCheck()
    findings = check.run(ctx)
    assert len(findings) == 1


def test_badges_present_pass(good_repo: Path):
    """Test badges check passes when badges exist."""
    ctx = Context.build(good_repo, Config())
    check = BadgesPresentCheck()
    findings = check.run(ctx)
    assert len(findings) == 0


def test_linter_present_pass(good_repo: Path):
    """Test linter check passes with ruff config."""
    ctx = Context.build(good_repo, Config())
    check = LinterPresentCheck()
    findings = check.run(ctx)
    assert len(findings) == 0


def test_linter_present_fail(bad_repo: Path):
    """Test linter check fails without config."""
    ctx = Context.build(bad_repo, Config())
    check = LinterPresentCheck()
    findings = check.run(ctx)
    assert len(findings) == 1


def test_lockfile_skip_when_no_manifest(bad_repo: Path):
    """Test lockfile check skips when no package manifest."""
    ctx = Context.build(bad_repo, Config())
    check = LockfilePresentCheck()
    findings = check.run(ctx)
    # Should skip since there's no package manager
    assert len(findings) == 0


def test_lockfile_present_pass(good_repo: Path):
    """Test lockfile check passes with poetry.lock."""
    ctx = Context.build(good_repo, Config())
    check = LockfilePresentCheck()
    findings = check.run(ctx)
    assert len(findings) == 0


def test_dependabot_present_pass(good_repo: Path):
    """Test dependabot check passes with config."""
    ctx = Context.build(good_repo, Config())
    check = DependabotPresentCheck()
    findings = check.run(ctx)
    assert len(findings) == 0


def test_codeowners_present_pass(good_repo: Path):
    """Test CODEOWNERS check passes."""
    ctx = Context.build(good_repo, Config())
    check = CodeownersPresentCheck()
    findings = check.run(ctx)
    assert len(findings) == 0


def test_editorconfig_present_pass(good_repo: Path):
    """Test .editorconfig check passes."""
    ctx = Context.build(good_repo, Config())
    check = EditorconfigPresentCheck()
    findings = check.run(ctx)
    assert len(findings) == 0


def test_changelog_present_pass(good_repo: Path):
    """Test CHANGELOG check passes."""
    ctx = Context.build(good_repo, Config())
    check = ChangelogPresentCheck()
    findings = check.run(ctx)
    assert len(findings) == 0


def test_contributing_present_pass(good_repo: Path):
    """Test CONTRIBUTING check passes."""
    ctx = Context.build(good_repo, Config())
    check = ContributingPresentCheck()
    findings = check.run(ctx)
    assert len(findings) == 0


def test_security_policy_present_pass(good_repo: Path):
    """Test SECURITY.md check passes."""
    ctx = Context.build(good_repo, Config())
    check = SecurityPolicyPresentCheck()
    findings = check.run(ctx)
    assert len(findings) == 0


def test_multiple_package_managers_pass(good_repo: Path):
    """Test no conflict with single package manager."""
    ctx = Context.build(good_repo, Config())
    check = MultiplePackageManagersCheck()
    findings = check.run(ctx)
    assert len(findings) == 0


def test_multiple_package_managers_fail(temp_repo: Path):
    """Test conflict with multiple package managers."""
    # Create conflicting lockfiles
    (temp_repo / "package-lock.json").write_text("{}")
    (temp_repo / "yarn.lock").write_text("")

    ctx = Context.build(temp_repo, Config())
    check = MultiplePackageManagersCheck()
    findings = check.run(ctx)
    assert len(findings) == 1
    assert "npm" in str(findings[0].evidence[0].description)
    assert "yarn" in str(findings[0].evidence[0].description)
