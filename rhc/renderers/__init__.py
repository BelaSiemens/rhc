"""Renderer exports."""

from rhc.renderers.json import JsonRenderer
from rhc.renderers.md import MarkdownRenderer
from rhc.renderers.text import TextRenderer

__all__ = ["JsonRenderer", "MarkdownRenderer", "TextRenderer"]


def get_renderer(format: str, plain: bool = False):
    """Get renderer by format name.

    Args:
        format: Output format (text, json, md, markdown)
        plain: If True, use ASCII-only output for text format
    """
    if format.lower() in ("text",):
        return TextRenderer(plain=plain)
    elif format.lower() in ("json",):
        return JsonRenderer()
    elif format.lower() in ("md", "markdown"):
        return MarkdownRenderer()
    return TextRenderer(plain=plain)
