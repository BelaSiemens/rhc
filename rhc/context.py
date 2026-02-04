"""Context providers for repository analysis."""

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

from rhc.config import Config


@dataclass
class FileStats:
    """Statistics for a file."""

    size: int
    mtime: float
    is_symlink: bool = False


class FileIndex:
    """File system index for efficient file operations."""

    def __init__(self, root_path: Path, follow_symlinks: bool = False):
        self.root = root_path.resolve()
        self.follow_symlinks = follow_symlinks
        self._cache: dict[str, bool] = {}

    def exists(self, *patterns: str) -> bool:
        """Check if any file matching the patterns exists."""
        for pattern in patterns:
            if self._glob_exists(pattern):
                return True
        return False

    def _glob_exists(self, pattern: str) -> bool:
        """Check if any file matching the glob pattern exists."""
        cache_key = f"exists:{pattern}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        result = any(self.root.glob(pattern))
        self._cache[cache_key] = result
        return result

    def glob(self, pattern: str) -> Iterator[Path]:
        """Glob for files matching pattern."""
        for path in self.root.glob(pattern):
            if not self.follow_symlinks and path.is_symlink():
                continue
            yield path

    def find_files(self, *patterns: str) -> list[Path]:
        """Find all files matching any of the patterns."""
        files: list[Path] = []
        for pattern in patterns:
            files.extend(self.glob(pattern))
        return files

    def read_text_safe(self, path: Path, max_size: int = 1024 * 1024) -> str | None:
        """Safely read text from a file with size limit."""
        try:
            if path.stat().st_size > max_size:
                return None
            return path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return None

    def file_stats(self, path: Path) -> FileStats | None:
        """Get file statistics."""
        try:
            stat = path.stat()
            return FileStats(
                size=stat.st_size,
                mtime=stat.st_mtime,
                is_symlink=path.is_symlink(),
            )
        except Exception:
            return None

    def count_files(self, pattern: str = "**/*") -> int:
        """Count files matching pattern."""
        count = 0
        for path in self.glob(pattern):
            if path.is_file():
                count += 1
        return count


@dataclass
class GitInfo:
    """Git repository information."""

    is_repo: bool = False
    branch: str | None = None
    head_sha: str | None = None
    tags: list[str] = field(default_factory=list)
    tracked_files: set[str] = field(default_factory=set)

    @classmethod
    def from_repo(cls, root_path: Path) -> "GitInfo":
        """Extract git information from repository."""
        info = cls()

        # Check if it's a git repo
        git_dir = root_path / ".git"
        if not git_dir.exists():
            return info

        info.is_repo = True

        try:
            # Get current branch
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=root_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                info.branch = result.stdout.strip()

            # Get HEAD SHA
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=root_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                info.head_sha = result.stdout.strip()[:12]

            # Get tags
            result = subprocess.run(
                ["git", "tag", "--list"],
                cwd=root_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                info.tags = [t for t in result.stdout.strip().split("\n") if t]

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return info


@dataclass
class StackInfo:
    """Detected technology stack information."""

    languages: list[str] = field(default_factory=list)
    package_managers: list[str] = field(default_factory=list)
    ci_providers: list[str] = field(default_factory=list)

    @classmethod
    def detect(cls, fs: FileIndex) -> "StackInfo":
        """Detect technology stack from file system."""
        info = cls()

        # Detect languages
        lang_indicators: dict[str, list[str]] = {
            "Python": ["*.py", "pyproject.toml", "setup.py", "requirements.txt"],
            "JavaScript": ["*.js", "*.jsx", "package.json"],
            "TypeScript": ["*.ts", "*.tsx", "tsconfig.json"],
            "Go": ["*.go", "go.mod"],
            "Rust": ["*.rs", "Cargo.toml"],
            "Java": ["*.java", "pom.xml", "build.gradle"],
            "Ruby": ["*.rb", "Gemfile"],
            "PHP": ["*.php", "composer.json"],
            "C#": ["*.cs", "*.csproj"],
        }

        for lang, patterns in lang_indicators.items():
            for pattern in patterns:
                if fs.exists(pattern):
                    if lang not in info.languages:
                        info.languages.append(lang)
                    break

        # Detect package managers
        pm_indicators: dict[str, list[str]] = {
            "npm": ["package-lock.json"],
            "yarn": ["yarn.lock"],
            "pnpm": ["pnpm-lock.yaml"],
            "pip": ["requirements.txt"],
            "poetry": ["poetry.lock"],
            "uv": ["uv.lock"],
            "pipenv": ["Pipfile.lock"],
            "cargo": ["Cargo.lock"],
            "go modules": ["go.sum"],
            "maven": ["pom.xml"],
            "gradle": ["build.gradle", "build.gradle.kts"],
            "composer": ["composer.lock"],
            "bundler": ["Gemfile.lock"],
        }

        for pm, patterns in pm_indicators.items():
            for pattern in patterns:
                if fs.exists(pattern):
                    if pm not in info.package_managers:
                        info.package_managers.append(pm)
                    break

        # Detect CI providers
        ci_indicators: dict[str, list[str]] = {
            "GitHub Actions": [".github/workflows/*.yml", ".github/workflows/*.yaml"],
            "GitLab CI": [".gitlab-ci.yml"],
            "CircleCI": [".circleci/config.yml"],
            "Travis CI": [".travis.yml"],
            "Azure Pipelines": ["azure-pipelines.yml"],
            "Jenkins": ["Jenkinsfile"],
        }

        for ci, patterns in ci_indicators.items():
            for pattern in patterns:
                if fs.exists(pattern):
                    if ci not in info.ci_providers:
                        info.ci_providers.append(ci)
                    break

        return info


@dataclass
class Context:
    """Complete context for running checks."""

    root_path: Path
    fs: FileIndex
    git: GitInfo
    stack: StackInfo
    config: Config

    @classmethod
    def build(cls, path: Path, config: Config) -> "Context":
        """Build context from a repository path."""
        root_path = path.resolve()

        fs = FileIndex(root_path)
        git = GitInfo.from_repo(root_path)
        stack = StackInfo.detect(fs)

        return cls(
            root_path=root_path,
            fs=fs,
            git=git,
            stack=stack,
            config=config,
        )
