"""Tests for renderers."""

import json
from pathlib import Path

from rhc.config import Config
from rhc.renderers import JsonRenderer, MarkdownRenderer, TextRenderer, get_renderer
from rhc.scanner import scan


def test_get_renderer():
    """Test renderer factory."""
    assert isinstance(get_renderer("text"), TextRenderer)
    assert isinstance(get_renderer("json"), JsonRenderer)
    assert isinstance(get_renderer("md"), MarkdownRenderer)
    assert isinstance(get_renderer("markdown"), MarkdownRenderer)
    # Default to text
    assert isinstance(get_renderer("unknown"), TextRenderer)


def test_json_renderer(minimal_repo: Path):
    """Test JSON renderer produces valid JSON."""
    report = scan(minimal_repo, Config())
    renderer = JsonRenderer()
    output = renderer.render(report)

    # Should be valid JSON
    data = json.loads(output)
    assert "meta" in data
    assert "summary" in data
    assert "findings" in data


def test_json_renderer_structure(minimal_repo: Path):
    """Test JSON structure matches spec."""
    report = scan(minimal_repo, Config())
    renderer = JsonRenderer()
    data = json.loads(renderer.render(report))

    # Meta fields
    assert "tool_version" in data["meta"]
    assert "timestamp" in data["meta"]
    assert "duration_ms" in data["meta"]

    # Summary fields
    assert "total_score" in data["summary"]
    assert "grade" in data["summary"]
    assert "counts_by_severity" in data["summary"]
    assert "counts_by_category" in data["summary"]

    # Repo info
    assert "path" in data["repo"]
    assert "git" in data["repo"]


def test_text_renderer(minimal_repo: Path):
    """Test text renderer produces output."""
    report = scan(minimal_repo, Config())
    renderer = TextRenderer()
    output = renderer.render(report)

    assert "RHC Report" in output
    assert "Score:" in output or "score" in output.lower()


def test_markdown_renderer(minimal_repo: Path):
    """Test markdown renderer produces valid markdown."""
    report = scan(minimal_repo, Config())
    renderer = MarkdownRenderer()
    output = renderer.render(report)

    # Should have markdown elements
    assert "# Repo Health Check Report" in output
    assert "**Score:" in output
    assert "## Summary" in output


def test_markdown_renderer_with_findings(bad_repo: Path):
    """Test markdown renderer includes findings table."""
    report = scan(bad_repo, Config())
    renderer = MarkdownRenderer()
    output = renderer.render(report)

    # Should have findings table
    assert "## Findings" in output
    assert "| Severity |" in output
    assert "| Check |" in output


def test_markdown_renderer_recommendations(bad_repo: Path):
    """Test markdown renderer includes recommendations."""
    report = scan(bad_repo, Config())
    renderer = MarkdownRenderer()
    output = renderer.render(report)

    # Should have recommendations
    assert "## Recommendations" in output


def test_text_renderer_no_findings(good_repo: Path):
    """Test text renderer with minimal findings."""
    report = scan(good_repo, Config())
    renderer = TextRenderer()
    output = renderer.render(report)

    # Should indicate good health
    assert "RHC Report" in output
