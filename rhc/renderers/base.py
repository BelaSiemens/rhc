"""Base renderer interface."""

from abc import ABC, abstractmethod

from rhc.types import Report


class BaseRenderer(ABC):
    """Base class for all renderers."""

    @abstractmethod
    def render(self, report: Report) -> str:
        """Render report to string."""
        pass
