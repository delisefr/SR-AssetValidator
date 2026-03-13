"""HI.006: Placeable/posable prims must be Xformable.
HI.008: Geometry should be logically grouped."""

from pxr import Usd, UsdGeom

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue


@RuleRegistry.register
class PlaceableAreXformable(BaseRule):
    requirement_code = "HI.006"
    category = "hierarchy"
    description = "Placeable/posable prims must inherit from UsdGeomXformable."
    severity = Severity.WARNING

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        for prim in stage.Traverse():
            # Prims with children that represent distinct objects
            children = prim.GetChildren()
            has_geom_children = any(c.IsA(UsdGeom.Gprim) for c in children)
            if has_geom_children and not prim.IsA(UsdGeom.Xformable):
                issues.append(Issue(rule=self.rule_name(), severity=Severity.WARNING,
                    message="Prim with geometry children is not Xformable.",
                    prim_path=str(prim.GetPath()), requirement_code=self.requirement_code))
        return issues
