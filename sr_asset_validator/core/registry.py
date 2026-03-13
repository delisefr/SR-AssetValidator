"""Rule discovery and registration, keyed by requirement codes."""

from __future__ import annotations

import importlib
import pkgutil
from typing import Type

from .rule import BaseRule


class RuleRegistry:
    """Registry mapping requirement codes (e.g. 'HI.004') to rule classes."""

    _rules: dict[str, Type[BaseRule]] = {}
    _by_name: dict[str, Type[BaseRule]] = {}

    @classmethod
    def register(cls, rule_cls: Type[BaseRule]) -> Type[BaseRule]:
        """Register a rule by its requirement code and class name."""
        if rule_cls.requirement_code:
            cls._rules[rule_cls.requirement_code] = rule_cls
        cls._by_name[rule_cls.rule_name()] = rule_cls
        return rule_cls

    @classmethod
    def get_by_code(cls, code: str) -> Type[BaseRule] | None:
        return cls._rules.get(code)

    @classmethod
    def get(cls, name: str) -> Type[BaseRule] | None:
        return cls._by_name.get(name)

    @classmethod
    def all_rules(cls) -> dict[str, Type[BaseRule]]:
        return dict(cls._by_name)

    @classmethod
    def all_by_code(cls) -> dict[str, Type[BaseRule]]:
        return dict(cls._rules)

    @classmethod
    def by_category(cls, category: str) -> list[Type[BaseRule]]:
        return [r for r in cls._by_name.values() if r.category == category]

    @classmethod
    def discover(cls, package_name: str = "sr_asset_validator.rules") -> None:
        """Import all sub-modules so decorated rules get registered."""
        package = importlib.import_module(package_name)
        for _importer, modname, ispkg in pkgutil.walk_packages(
            package.__path__, prefix=package.__name__ + "."
        ):
            importlib.import_module(modname)

    @classmethod
    def rules_for_codes(cls, codes: set[str]) -> list[Type[BaseRule]]:
        """Return rule classes for a set of requirement codes.
        Codes without implementations are silently skipped."""
        result = []
        for code in sorted(codes):
            rule_cls = cls._rules.get(code)
            if rule_cls:
                result.append(rule_cls)
        return result
