"""Base check interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from rhc.context import Context
from rhc.types import Category, Finding


@dataclass
class CheckInfo:
    """Information about a check."""

    id: str
    title: str
    category: Category
    description: str
    default_enabled: bool = True
    default_weight: int = -5  # Default score impact


class BaseCheck(ABC):
    """Base class for all health checks."""

    info: CheckInfo

    @abstractmethod
    def run(self, ctx: Context) -> list[Finding]:
        """Run the check and return findings.

        Returns an empty list if no issues found.
        Returns a list of findings if issues are detected.
        """
        pass

    @property
    def id(self) -> str:
        return self.info.id

    @property
    def category(self) -> Category:
        return self.info.category

    @property
    def description(self) -> str:
        return self.info.description

    def get_weight(self, config_weights: dict[str, int]) -> int:
        """Get the score impact, considering config overrides."""
        return config_weights.get(self.info.id, self.info.default_weight)

    def explain(self) -> str:
        """Return a detailed explanation of the check."""
        return f"""Check: {self.info.id}
Title: {self.info.title}
Category: {self.info.category.value}
Default Impact: {self.info.default_weight}

{self.info.description}
"""
