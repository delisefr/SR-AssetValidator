"""HI.001: All prims descend from a single root."""

from pxr import Usd

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue


@RuleRegistry.register
class HierarchyHasRoot(BaseRule):
    requirement_code = "HI.001"
    category = "hierarchy"
    description = "All prims must be descendants of a single root prim."
    severity = Severity.ERROR

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        pseudo_root = stage.GetPseudoRoot()
        root_children = [c for c in pseudo_root.GetChildren() if c.IsActive()]
        if len(root_children) > 1:
            names = [str(c.GetPath()) for c in root_children]
            issues.append(Issue(
                rule=self.rule_name(), severity=Severity.ERROR,
                message=f"Stage has {len(root_children)} root prims: {names}. Expected one.",
                requirement_code=self.requirement_code,
            ))
        elif len(root_children) == 0:
            issues.append(Issue(
                rule=self.rule_name(), severity=Severity.ERROR,
                message="Stage has no root prims.",
                requirement_code=self.requirement_code,
            ))
        return issues
