"""Renderer exports."""

from rhc.renderers.json import JsonRenderer
from rhc.renderers.md import MarkdownRenderer
from rhc.renderers.text import TextRenderer

__all__ = ["JsonRenderer", "MarkdownRenderer", "TextRenderer"]


def get_renderer(format: str):
    """Get renderer by format name."""
    renderers = {
        "text": TextRenderer,
        "json": JsonRenderer,
        "md": MarkdownRenderer,
        "markdown": MarkdownRenderer,
    }
    renderer_class = renderers.get(format.lower(), TextRenderer)
    return renderer_class()
