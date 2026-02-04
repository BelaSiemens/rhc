"""Configuration loading and management."""

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from rhc.types import Severity

DEFAULT_CONFIG_FILENAME = ".rhc.yml"


@dataclass
class PolicyConfig:
    """Policy configuration for the scan."""

    min_score: int | None = None
    fail_on: Severity | None = None


@dataclass
class ChecksConfig:
    """Configuration for individual checks."""

    skip: list[str] = field(default_factory=list)
    only: list[str] = field(default_factory=list)
    weights: dict[str, int] = field(default_factory=dict)


@dataclass
class Config:
    """Complete configuration for RHC."""

    version: int = 1
    policy: PolicyConfig = field(default_factory=PolicyConfig)
    checks: ChecksConfig = field(default_factory=ChecksConfig)
    strict: bool = False
    offline: bool = True  # Default to offline
    debug: bool = False

    @classmethod
    def load(cls, config_path: Path | None = None, repo_path: Path | None = None) -> "Config":
        """Load configuration from file or use defaults."""
        config = cls()

        # Try to find config file
        search_paths: list[Path] = []
        if config_path:
            search_paths.append(config_path)
        if repo_path:
            search_paths.append(repo_path / DEFAULT_CONFIG_FILENAME)

        for path in search_paths:
            if path.exists():
                config = cls._load_from_file(path)
                break

        return config

    @classmethod
    def _load_from_file(cls, path: Path) -> "Config":
        """Load configuration from a YAML file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception:
            return cls()

        config = cls()
        config.version = data.get("version", 1)

        # Parse policy
        policy_data = data.get("policy", {})
        config.policy.min_score = policy_data.get("min_score")
        if "fail_on" in policy_data:
            try:
                config.policy.fail_on = Severity(policy_data["fail_on"])
            except ValueError:
                pass

        # Parse checks
        checks_data = data.get("checks", {})
        config.checks.skip = checks_data.get("skip", [])
        config.checks.only = checks_data.get("only", [])
        config.checks.weights = checks_data.get("weights", {})

        return config

    def merge_cli_args(
        self,
        fail_on: str | None = None,
        min_score: int | None = None,
        only: list[str] | None = None,
        skip: list[str] | None = None,
        strict: bool = False,
        offline: bool = True,
        debug: bool = False,
    ) -> "Config":
        """Merge CLI arguments into configuration (CLI takes precedence)."""
        if fail_on:
            try:
                self.policy.fail_on = Severity(fail_on)
            except ValueError:
                pass

        if min_score is not None:
            self.policy.min_score = min_score

        if only:
            self.checks.only = only

        if skip:
            self.checks.skip = list(set(self.checks.skip + skip))

        self.strict = strict
        self.offline = offline
        self.debug = debug

        return self


def generate_example_config() -> str:
    """Generate an example configuration file content."""
    return """# RHC Configuration File
# See: https://github.com/your/rhc for documentation

version: 1

# Policy settings - when to fail the check
policy:
  # Minimum acceptable score (0-100)
  # min_score: 75

  # Fail if findings of this severity or higher exist
  # Options: info, low, medium, high, critical
  # fail_on: high

# Check configuration
checks:
  # Skip specific checks
  # skip:
  #   - SEC.SECRETS_SUSPECTED

  # Only run specific checks (empty = run all)
  # only:
  #   - DOC.README_PRESENT
  #   - CI.CONFIG_PRESENT

  # Override default score impacts (must be negative)
  # weights:
  #   DOC.README_PRESENT: -8
  #   CI.CONFIG_PRESENT: -10
"""
