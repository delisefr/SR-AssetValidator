"""HI.003: Root prim must be Xformable."""

from pxr import Usd, UsdGeom

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue


@RuleRegistry.register
class RootIsXformable(BaseRule):
    requirement_code = "HI.003"
    category = "hierarchy"
    description = "The root prim must inherit from UsdGeomXformable."
    severity = Severity.ERROR

    def check(self, stage: Usd.Stage) -> list[Issue]:
        default_prim = stage.GetDefaultPrim()
        if not default_prim or not default_prim.IsValid():
            return []  # HI.004 handles this
        if not default_prim.IsA(UsdGeom.Xformable):
            return [Issue(
                rule=self.rule_name(), severity=Severity.ERROR,
                message=f"Root prim {default_prim.GetPath()} is not Xformable (type: {default_prim.GetTypeName()}).",
                prim_path=str(default_prim.GetPath()),
                requirement_code=self.requirement_code,
            )]
        return []
