# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in RHC, please report it by emailing **[your-email@example.com]** (replace with your actual contact).

**Do not** open a public GitHub issue for security vulnerabilities.

### What to include
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fixes (optional)

### Response time
We aim to respond within **48 hours** and will work with you to understand and resolve the issue promptly.

## Scope

This policy applies to the RHC CLI tool itself. Issues in dependencies should be reported to those projects directly.

## Secret Detection Disclaimer

RHC includes a `SEC.SECRETS_SUSPECTED` check that scans for common secret patterns. This check:
- Uses conservative patterns to minimize false positives
- Never logs or outputs actual secret values
- Only reports file paths and pattern types

If you find cases where secrets are inadvertently exposed in reports, please report this as a security issue.
