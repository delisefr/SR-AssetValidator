"""Base rule interface and severity levels."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pxr import Usd
    from .result import Issue


class Severity(Enum):
    ERROR = auto()
    WARNING = auto()
    INFO = auto()

    def __str__(self) -> str:
        return self.name


class BaseRule(ABC):
    """Abstract base for all validation rules.

    Each rule maps to a requirement code from simready-foundation
    (e.g., 'HI.004', 'VG.014', 'RB.COL.001').
    """

    requirement_code: str = ""  # e.g. "HI.004"
    category: str = "uncategorized"
    description: str = ""
    severity: Severity = Severity.ERROR
    dependencies: list[str] = []

    @abstractmethod
    def check(self, stage: Usd.Stage) -> list[Issue]:
        """Return a list of issues found on *stage*."""
        ...

    @classmethod
    def rule_name(cls) -> str:
        return cls.__name__
