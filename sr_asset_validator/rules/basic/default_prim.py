"""HI.004: Stage must specify a default prim."""

from pxr import Usd, UsdGeom

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue


@RuleRegistry.register
class StageHasDefaultPrim(BaseRule):
    requirement_code = "HI.004"
    category = "hierarchy"
    description = "Stage must specify a default prim to define the root entry point."
    severity = Severity.ERROR

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        default_prim = stage.GetDefaultPrim()
        if not default_prim or not default_prim.IsValid():
            issues.append(Issue(
                rule=self.rule_name(), severity=Severity.ERROR,
                message="Stage has no defaultPrim set.",
                requirement_code=self.requirement_code,
            ))
        elif not default_prim.IsActive():
            issues.append(Issue(
                rule=self.rule_name(), severity=Severity.ERROR,
                message=f"Default prim {default_prim.GetPath()} is not active.",
                prim_path=str(default_prim.GetPath()),
                requirement_code=self.requirement_code,
            ))
        return issues
