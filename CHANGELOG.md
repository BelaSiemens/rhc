# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-02-04

### Added
- Initial release
- 19 health checks across 6 categories (docs, ci, tests, deps, security, hygiene)
- CLI commands: `scan`, `list-checks`, `explain`, `init`
- Output formats: text (terminal), JSON, Markdown
- Policy enforcement via `--min-score` and `--fail-on`
- Configuration via `.rhc.yml`
