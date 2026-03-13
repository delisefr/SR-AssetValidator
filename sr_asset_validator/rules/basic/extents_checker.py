"""VG.002: Boundable geometry must have valid extent values."""

from pxr import Usd, UsdGeom

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue


@RuleRegistry.register
class GeomExtentCheck(BaseRule):
    requirement_code = "VG.002"
    category = "geometry"
    description = "Boundable geometry primitives must have valid extent values."
    severity = Severity.WARNING

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        for prim in stage.Traverse():
            boundable = UsdGeom.Boundable(prim)
            if not boundable:
                continue
            extent_attr = boundable.GetExtentAttr()
            if not extent_attr or not extent_attr.HasValue():
                issues.append(Issue(
                    rule=self.rule_name(), severity=Severity.WARNING,
                    message="Boundable prim missing extent attribute.",
                    prim_path=str(prim.GetPath()),
                    requirement_code=self.requirement_code,
                ))
        return issues
