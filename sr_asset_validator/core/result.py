"""Validation result data structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .rule import Severity


@dataclass
class Issue:
    rule: str
    severity: Severity
    message: str
    prim_path: str = ""
    suggestion: str = ""
    requirement_code: str = ""

    def __str__(self) -> str:
        loc = f" @ {self.prim_path}" if self.prim_path else ""
        code = f" [{self.requirement_code}]" if self.requirement_code else ""
        return f"[{self.severity}]{code} {self.rule}{loc}: {self.message}"


@dataclass
class ValidationResult:
    """Result of running one rule against one stage."""

    rule_name: str
    requirement_code: str = ""
    passed: bool = True
    issues: list[Issue] = field(default_factory=list)


@dataclass
class ValidationReport:
    """Aggregate report for a single USD file against a specification."""

    file_path: str
    spec_name: str
    results: list[ValidationResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results)

    @property
    def error_count(self) -> int:
        return sum(
            1 for r in self.results for i in r.issues if i.severity == Severity.ERROR
        )

    @property
    def warning_count(self) -> int:
        return sum(
            1 for r in self.results for i in r.issues if i.severity == Severity.WARNING
        )

    def summary(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        name = Path(self.file_path).name
        parts = [f"[{status}] {name} ({self.spec_name})"]
        parts.append(
            f"  rules: {len(self.results)}  "
            f"errors: {self.error_count}  "
            f"warnings: {self.warning_count}"
        )
        return "\n".join(parts)
