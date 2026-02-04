"""Data models for RHC."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    """Severity levels for findings."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    def __lt__(self, other: "Severity") -> bool:
        order = [Severity.INFO, Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
        return order.index(self) < order.index(other)


class Category(str, Enum):
    """Categories for checks and findings."""

    DOCS = "docs"
    CI = "ci"
    TESTS = "tests"
    DEPS = "deps"
    SECURITY = "security"
    HYGIENE = "hygiene"
    RELEASE = "release"


# Default weights per category (for reference)
CATEGORY_WEIGHTS = {
    Category.DOCS: 15,
    Category.CI: 20,
    Category.TESTS: 20,
    Category.DEPS: 20,
    Category.SECURITY: 15,
    Category.HYGIENE: 10,
}


@dataclass
class Evidence:
    """Evidence supporting a finding."""

    description: str
    files: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class Finding:
    """A single finding from a check."""

    id: str
    title: str
    severity: Severity
    category: Category
    score_impact: int  # Negative value, e.g., -6
    evidence: list[Evidence] = field(default_factory=list)
    recommendation: str = ""
    refs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "severity": self.severity.value,
            "category": self.category.value,
            "score_impact": self.score_impact,
            "evidence": [
                {"description": e.description, "files": e.files, "details": e.details}
                for e in self.evidence
            ],
            "recommendation": self.recommendation,
            "refs": self.refs,
        }


@dataclass
class ReportMeta:
    """Metadata about the report generation."""

    tool_version: str
    timestamp: str
    duration_ms: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_version": self.tool_version,
            "timestamp": self.timestamp,
            "duration_ms": self.duration_ms,
        }


@dataclass
class RepoInfo:
    """Information about the scanned repository."""

    path: str
    is_git_repo: bool = False
    branch: str | None = None
    head_sha: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"path": self.path}
        if self.is_git_repo:
            result["git"] = {
                "is_repo": True,
                "branch": self.branch,
                "head_sha": self.head_sha,
            }
        else:
            result["git"] = {"is_repo": False}
        return result


@dataclass
class Summary:
    """Summary of the scan results."""

    total_score: int
    grade: str
    counts_by_severity: dict[str, int]
    counts_by_category: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_score": self.total_score,
            "grade": self.grade,
            "counts_by_severity": self.counts_by_severity,
            "counts_by_category": self.counts_by_category,
        }


@dataclass
class Metrics:
    """Additional metrics about the repository."""

    files_count: int = 0
    languages_detected: list[str] = field(default_factory=list)
    ci_providers_found: list[str] = field(default_factory=list)
    package_managers_found: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "files_count": self.files_count,
            "languages_detected": self.languages_detected,
            "ci_providers_found": self.ci_providers_found,
            "package_managers_found": self.package_managers_found,
        }


@dataclass
class Report:
    """Complete health check report."""

    meta: ReportMeta
    repo: RepoInfo
    summary: Summary
    findings: list[Finding]
    metrics: Metrics

    def to_dict(self) -> dict[str, Any]:
        return {
            "meta": self.meta.to_dict(),
            "repo": self.repo.to_dict(),
            "summary": self.summary.to_dict(),
            "findings": [f.to_dict() for f in self.findings],
            "metrics": self.metrics.to_dict(),
        }
