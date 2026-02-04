"""CLI entry point for RHC."""

import sys
from pathlib import Path

import click

from rhc import __version__
from rhc.checks import get_all_checks, get_check_by_id
from rhc.config import Config, generate_example_config
from rhc.renderers import get_renderer
from rhc.scanner import scan
from rhc.scoring import check_policy_violation
from rhc.types import Severity

# Exit codes
EXIT_OK = 0
EXIT_POLICY_VIOLATED = 1
EXIT_ANALYSIS_ERROR = 2
EXIT_INTERNAL_ERROR = 3


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(__version__, "--version", "-v")
def main(ctx: click.Context) -> None:
    """RHC - Repo Health Check CLI

    Analyze Git repositories for best practices, hygiene, and maintainability.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["text", "json", "md"], case_sensitive=False),
    default="text",
    help="Output format",
)
@click.option("--output", "-o", type=click.Path(), help="Write output to file")
@click.option(
    "--fail-on",
    type=click.Choice(["none", "info", "low", "medium", "high", "critical"], case_sensitive=False),
    default="none",
    help="Exit with error if findings of this severity or higher exist",
)
@click.option(
    "--min-score",
    type=click.IntRange(0, 100),
    help="Exit with error if score is below this threshold",
)
@click.option("--only", multiple=True, help="Only run specific checks (can be repeated)")
@click.option("--skip", multiple=True, help="Skip specific checks (can be repeated)")
@click.option("--strict", is_flag=True, help="Use stricter thresholds")
@click.option("--offline/--online", default=True, help="Disable/enable network checks")
@click.option("--plain", is_flag=True, help="Plain ASCII output (no unicode/colors, CI-friendly)")
@click.option("--debug", is_flag=True, help="Enable debug output")
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to config file")
def scan_cmd(
    path: str,
    format: str,
    output: str | None,
    fail_on: str,
    min_score: int | None,
    only: tuple[str, ...],
    skip: tuple[str, ...],
    strict: bool,
    offline: bool,
    plain: bool,
    debug: bool,
    config: str | None,
) -> None:
    """Scan a repository for health issues.

    PATH is the repository path (default: current directory)
    """
    try:
        repo_path = Path(path).resolve()

        # Load and merge config
        cfg = Config.load(
            config_path=Path(config) if config else None,
            repo_path=repo_path,
        )
        cfg.merge_cli_args(
            fail_on=fail_on if fail_on != "none" else None,
            min_score=min_score,
            only=list(only) if only else None,
            skip=list(skip) if skip else None,
            strict=strict,
            offline=offline,
            debug=debug,
        )

        if debug:
            click.echo(f"[DEBUG] Scanning: {repo_path}", err=True)
            click.echo(f"[DEBUG] Config: {cfg}", err=True)

        # Run scan
        report = scan(repo_path, cfg)

        # Render output
        renderer = get_renderer(format, plain=plain)
        result = renderer.render(report)

        # Write output
        if output:
            Path(output).write_text(result, encoding="utf-8")
            if format == "text":
                click.echo(f"Report written to {output}")
        else:
            click.echo(result)

        # Check policies
        fail_severity = Severity(fail_on) if fail_on != "none" else None
        violated, reason = check_policy_violation(
            report.findings,
            report.summary,
            min_score=min_score or cfg.policy.min_score,
            fail_on=fail_severity or cfg.policy.fail_on,
        )

        if violated:
            if debug or format == "text":
                marker = "[FAIL]" if plain else "❌"
                click.echo(f"\n{marker} Policy violation: {reason}", err=True)
            sys.exit(EXIT_POLICY_VIOLATED)

        sys.exit(EXIT_OK)

    except FileNotFoundError as e:
        click.echo(f"Error: Path not found - {e}", err=True)
        sys.exit(EXIT_ANALYSIS_ERROR)
    except Exception as e:
        if debug:
            import traceback
            traceback.print_exc()
        click.echo(f"Error: {e}", err=True)
        sys.exit(EXIT_INTERNAL_ERROR)


# Register scan as both 'scan' and default command
main.add_command(scan_cmd, name="scan")


@main.command("list-checks")
def list_checks() -> None:
    """List all available health checks."""
    checks = get_all_checks()

    click.echo("\nAvailable Checks:\n")
    click.echo(f"{'ID':<30} {'Category':<10} {'Impact':<8} Description")
    click.echo("-" * 80)

    for check in sorted(checks, key=lambda c: (c.info.category.value, c.info.id)):
        click.echo(
            f"{check.info.id:<30} {check.info.category.value:<10} {check.info.default_weight:<8} {check.info.title}"
        )

    click.echo(f"\nTotal: {len(checks)} checks")


@main.command()
@click.argument("check_id")
def explain(check_id: str) -> None:
    """Explain a specific check.

    CHECK_ID is the check identifier (e.g., DOC.README_PRESENT)
    """
    check = get_check_by_id(check_id)

    if not check:
        click.echo(f"Error: Check '{check_id}' not found.", err=True)
        click.echo("\nUse 'rhc list-checks' to see available checks.")
        sys.exit(EXIT_ANALYSIS_ERROR)

    click.echo(check.explain())


@main.command()
@click.option("--output", "-o", type=click.Path(), default=".rhc.yml", help="Output file path")
def init(output: str) -> None:
    """Create an example .rhc.yml configuration file."""
    output_path = Path(output)

    if output_path.exists():
        if not click.confirm(f"{output} already exists. Overwrite?"):
            click.echo("Aborted.")
            return

    content = generate_example_config()
    output_path.write_text(content, encoding="utf-8")
    click.echo(f"Created {output}")


if __name__ == "__main__":
    main()
