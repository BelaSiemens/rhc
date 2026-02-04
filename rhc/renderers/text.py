"""Text (terminal) renderer with rich formatting."""

import sys

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from rhc.renderers.base import BaseRenderer
from rhc.types import Report, Severity

# Severity to color mapping
SEVERITY_COLORS = {
    Severity.CRITICAL: "bold red",
    Severity.HIGH: "red",
    Severity.MEDIUM: "yellow",
    Severity.LOW: "blue",
    Severity.INFO: "dim",
}

# Severity to emoji (unicode)
SEVERITY_ICONS_UNICODE = {
    Severity.CRITICAL: "🔴",
    Severity.HIGH: "🟠",
    Severity.MEDIUM: "🟡",
    Severity.LOW: "🔵",
    Severity.INFO: "⚪",
}

# Severity to ASCII markers
SEVERITY_ICONS_ASCII = {
    Severity.CRITICAL: "[!!]",
    Severity.HIGH: "[!]",
    Severity.MEDIUM: "[~]",
    Severity.LOW: "[.]",
    Severity.INFO: "[-]",
}

# Grade to color
GRADE_COLORS = {
    "A": "bold green",
    "B": "green",
    "C": "yellow",
    "D": "red",
    "F": "bold red",
}


def _detect_unicode_support() -> bool:
    """Detect if terminal supports unicode."""
    encoding = getattr(sys.stdout, "encoding", None)
    if encoding and "UTF" in encoding.upper():
        return True
    return False


class TextRenderer(BaseRenderer):
    """Terminal-friendly text renderer using Rich."""

    def __init__(self, plain: bool = False):
        """Initialize renderer.

        Args:
            plain: If True, use ASCII-only output without colors/unicode.
        """
        self.plain = plain
        self.use_unicode = not plain and _detect_unicode_support()

    def render(self, report: Report) -> str:
        """Render report to terminal-formatted string."""
        if self.plain:
            return self._render_plain(report)

        console = Console(record=True, force_terminal=True, width=100)

        # Header with score
        self._render_header(console, report)

        # Summary panel
        self._render_summary(console, report)

        # Top findings
        if report.findings:
            self._render_findings(console, report)

        # Metrics
        self._render_metrics(console, report)

        # Footer
        self._render_footer(console, report)

        return console.export_text()

    def _get_severity_icon(self, severity: Severity) -> str:
        """Get severity icon based on unicode support."""
        if self.use_unicode:
            return SEVERITY_ICONS_UNICODE.get(severity, "")
        return SEVERITY_ICONS_ASCII.get(severity, "")

    def _render_header(self, console: Console, report: Report) -> None:
        """Render the header with score and grade."""
        grade = report.summary.grade
        score = report.summary.total_score
        grade_color = GRADE_COLORS.get(grade, "white")

        # Grade display
        grade_text = Text()
        grade_text.append("Repo Health Score: ", style="bold")
        grade_text.append(f"{score}/100 ", style=grade_color)
        grade_text.append(f"(Grade: {grade})", style=grade_color)

        console.print()
        console.print(Panel(grade_text, title="[bold]RHC Report[/bold]", border_style=grade_color))

    def _render_summary(self, console: Console, report: Report) -> None:
        """Render severity summary."""
        counts = report.summary.counts_by_severity
        has_findings = any(v > 0 for v in counts.values())

        if not has_findings:
            console.print()
            icon = "✓" if self.use_unicode else "[OK]"
            console.print(f"[green]{icon} No issues found![/green]")
            return

        summary_text = Text("Issues: ")
        parts = []
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
            count = counts.get(severity.value, 0)
            if count > 0:
                icon = self._get_severity_icon(severity)
                parts.append(f"{icon} {count} {severity.value}")

        summary_text.append("  ".join(parts))
        console.print()
        console.print(summary_text)

    def _render_findings(self, console: Console, report: Report) -> None:
        """Render findings table."""
        console.print()

        table = Table(title="Findings", show_header=True, header_style="bold")
        table.add_column("", width=4)
        table.add_column("ID", style="cyan", width=28)
        table.add_column("Title", width=35)
        table.add_column("Impact", justify="right", width=8)

        # Show top findings (max 10)
        for finding in report.findings[:10]:
            icon = self._get_severity_icon(finding.severity)
            color = SEVERITY_COLORS.get(finding.severity, "")
            table.add_row(
                icon,
                finding.id,
                Text(finding.title, style=color),
                str(finding.score_impact),
            )

        if len(report.findings) > 10:
            table.add_row("", f"... and {len(report.findings) - 10} more", "", "")

        console.print(table)

    def _render_metrics(self, console: Console, report: Report) -> None:
        """Render repository metrics."""
        console.print()

        metrics = report.metrics
        parts = []

        if metrics.files_count:
            icon = "📁" if self.use_unicode else "Files:"
            parts.append(f"{icon} {metrics.files_count} files" if self.use_unicode else f"{icon} {metrics.files_count}")

        if metrics.languages_detected:
            langs = ", ".join(metrics.languages_detected[:3])
            icon = "📝" if self.use_unicode else "Lang:"
            parts.append(f"{icon} {langs}")

        if metrics.ci_providers_found:
            ci = ", ".join(metrics.ci_providers_found[:2])
            icon = "⚙️" if self.use_unicode else "CI:"
            parts.append(f"{icon} {ci}")

        if parts:
            console.print("  ".join(parts), style="dim")

    def _render_footer(self, console: Console, report: Report) -> None:
        """Render footer with timing info."""
        console.print()
        git_info = ""
        if report.repo.is_git_repo and report.repo.branch:
            git_info = f" | {report.repo.branch}"
            if report.repo.head_sha:
                git_info += f"@{report.repo.head_sha}"

        console.print(
            f"[dim]rhc v{report.meta.tool_version} | {report.meta.duration_ms}ms{git_info}[/dim]"
        )
        console.print()

    def _render_plain(self, report: Report) -> str:
        """Render report as plain ASCII text without colors or unicode."""
        lines: list[str] = []

        # Header
        grade = report.summary.grade
        score = report.summary.total_score
        lines.append("=" * 60)
        lines.append("RHC Report")
        lines.append("=" * 60)
        lines.append(f"Score: {score}/100 (Grade: {grade})")
        lines.append("")

        # Summary
        counts = report.summary.counts_by_severity
        has_findings = any(v > 0 for v in counts.values())

        if not has_findings:
            lines.append("[OK] No issues found!")
        else:
            parts = []
            for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
                count = counts.get(severity.value, 0)
                if count > 0:
                    parts.append(f"{count} {severity.value}")
            lines.append(f"Issues: {', '.join(parts)}")

        lines.append("")

        # Findings
        if report.findings:
            lines.append("-" * 60)
            lines.append(f"{'ID':<30} {'Title':<20} {'Impact':>8}")
            lines.append("-" * 60)

            for finding in report.findings[:10]:
                icon = SEVERITY_ICONS_ASCII.get(finding.severity, "")
                title = finding.title[:18] + ".." if len(finding.title) > 20 else finding.title
                lines.append(f"{icon} {finding.id:<26} {title:<20} {finding.score_impact:>6}")

            if len(report.findings) > 10:
                lines.append(f"    ... and {len(report.findings) - 10} more")

            lines.append("")

        # Metrics
        metrics = report.metrics
        metric_parts = []
        if metrics.files_count:
            metric_parts.append(f"{metrics.files_count} files")
        if metrics.languages_detected:
            metric_parts.append(", ".join(metrics.languages_detected[:3]))
        if metrics.ci_providers_found:
            metric_parts.append(", ".join(metrics.ci_providers_found[:2]))

        if metric_parts:
            lines.append(" | ".join(metric_parts))

        # Footer
        git_info = ""
        if report.repo.is_git_repo and report.repo.branch:
            git_info = f" | {report.repo.branch}"
            if report.repo.head_sha:
                git_info += f"@{report.repo.head_sha}"

        lines.append(f"rhc v{report.meta.tool_version} | {report.meta.duration_ms}ms{git_info}")
        lines.append("")

        return "\n".join(lines)
