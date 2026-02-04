"""JSON renderer."""

import json

from rhc.renderers.base import BaseRenderer
from rhc.types import Report


class JsonRenderer(BaseRenderer):
    """Machine-readable JSON renderer."""

    def render(self, report: Report) -> str:
        """Render report as JSON."""
        return json.dumps(report.to_dict(), indent=2, ensure_ascii=False)
