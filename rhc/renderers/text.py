"""Text (terminal) renderer with rich formatting."""

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

# Severity to emoji
SEVERITY_ICONS = {
    Severity.CRITICAL: "🔴",
    Severity.HIGH: "🟠",
    Severity.MEDIUM: "🟡",
    Severity.LOW: "🔵",
    Severity.INFO: "⚪",
}

# Grade to color
GRADE_COLORS = {
    "A": "bold green",
    "B": "green",
    "C": "yellow",
    "D": "red",
    "F": "bold red",
}


class TextRenderer(BaseRenderer):
    """Terminal-friendly text renderer using Rich."""

    def render(self, report: Report) -> str:
        """Render report to terminal-formatted string."""
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
            console.print("[green]✓ No issues found![/green]")
            return

        summary_text = Text("Issues: ")
        parts = []
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
            count = counts.get(severity.value, 0)
            if count > 0:
                parts.append(f"{SEVERITY_ICONS[severity]} {count} {severity.value}")

        summary_text.append("  ".join(parts))
        console.print()
        console.print(summary_text)

    def _render_findings(self, console: Console, report: Report) -> None:
        """Render findings table."""
        console.print()

        table = Table(title="Findings", show_header=True, header_style="bold")
        table.add_column("", width=3)
        table.add_column("ID", style="cyan", width=28)
        table.add_column("Title", width=35)
        table.add_column("Impact", justify="right", width=8)

        # Show top findings (max 10)
        for finding in report.findings[:10]:
            icon = SEVERITY_ICONS.get(finding.severity, "")
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
            parts.append(f"📁 {metrics.files_count} files")

        if metrics.languages_detected:
            langs = ", ".join(metrics.languages_detected[:3])
            parts.append(f"📝 {langs}")

        if metrics.ci_providers_found:
            ci = ", ".join(metrics.ci_providers_found[:2])
            parts.append(f"⚙️ {ci}")

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
