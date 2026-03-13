"""HI.002: Every UsdGeomPrim must have a parent Xform."""

from pxr import Usd, UsdGeom

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue


@RuleRegistry.register
class ExclusiveXformParent(BaseRule):
    requirement_code = "HI.002"
    category = "hierarchy"
    description = "Every UsdGeomPrim must have a parent Xform."
    severity = Severity.WARNING

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        for prim in stage.Traverse():
            if not prim.IsA(UsdGeom.Gprim):
                continue
            parent = prim.GetParent()
            if parent and not parent.IsPseudoRoot() and not parent.IsA(UsdGeom.Xformable):
                issues.append(Issue(rule=self.rule_name(), severity=Severity.WARNING,
                    message=f"Gprim parent {parent.GetPath()} is not Xformable.",
                    prim_path=str(prim.GetPath()), requirement_code=self.requirement_code))
        return issues
