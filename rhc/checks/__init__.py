"""Check registry and discovery."""

from rhc.checks.base import BaseCheck
from rhc.checks.ci import BadgesPresentCheck, CIConfigPresentCheck
from rhc.checks.deps import (
    LockfilePresentCheck,
    MultiplePackageManagersCheck,
    OutdatedHintsCheck,
)
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
    SemverTagsPresentCheck,
)
from rhc.checks.security import (
    CodeownersPresentCheck,
    DependabotPresentCheck,
    SecretsSuspectedCheck,
)
from rhc.checks.tests import (
    CIRunsTestsCheck,
    LinterPresentCheck,
    TestsDetectedCheck,
)

# All available checks
ALL_CHECKS: list[type[BaseCheck]] = [
    # Docs
    ReadmePresentCheck,
    LicensePresentCheck,
    ContributingPresentCheck,
    SecurityPolicyPresentCheck,
    # CI
    CIConfigPresentCheck,
    BadgesPresentCheck,
    # Tests
    TestsDetectedCheck,
    CIRunsTestsCheck,
    LinterPresentCheck,
    # Deps
    LockfilePresentCheck,
    OutdatedHintsCheck,
    MultiplePackageManagersCheck,
    # Security
    SecretsSuspectedCheck,
    DependabotPresentCheck,
    CodeownersPresentCheck,
    # Hygiene
    GitignorePresentCheck,
    EditorconfigPresentCheck,
    SemverTagsPresentCheck,
    ChangelogPresentCheck,
]


def get_all_checks() -> list[BaseCheck]:
    """Get instances of all registered checks."""
    return [check_class() for check_class in ALL_CHECKS]


def get_check_by_id(check_id: str) -> BaseCheck | None:
    """Get a check instance by its ID."""
    for check_class in ALL_CHECKS:
        check = check_class()
        if check.id == check_id:
            return check
    return None


def filter_checks(
    checks: list[BaseCheck],
    skip: list[str] | None = None,
    only: list[str] | None = None,
) -> list[BaseCheck]:
    """Filter checks based on skip and only lists."""
    skip = skip or []
    only = only or []

    filtered = []
    for check in checks:
        if skip and check.id in skip:
            continue
        if only and check.id not in only:
            continue
        filtered.append(check)

    return filtered
