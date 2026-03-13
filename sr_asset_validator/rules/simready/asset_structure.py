"""RB.MB.001: Multi-body capability (at least two rigid bodies).
RB.COL.004: Collider non-uniform scale check.
HI.005: XformCommonAPI usage."""

from pxr import Usd, UsdGeom, UsdPhysics

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue


@RuleRegistry.register
class MultiBodyCapability(BaseRule):
    requirement_code = "RB.MB.001"
    category = "physics"
    description = "Assets must contain at least two rigid bodies."
    severity = Severity.INFO

    def check(self, stage: Usd.Stage) -> list[Issue]:
        count = sum(1 for p in stage.Traverse() if p.HasAPI(UsdPhysics.RigidBodyAPI))
        if count < 2:
            return [Issue(rule=self.rule_name(), severity=Severity.INFO,
                message=f"Found {count} rigid body(ies), multi-body requires >= 2.",
                requirement_code=self.requirement_code)]
        return []


@RuleRegistry.register
class ColliderNonUniformScale(BaseRule):
    requirement_code = "RB.COL.004"
    category = "physics"
    description = "Collision shape scale must be uniform for Sphere/Capsule/Cylinder/Cone."
    severity = Severity.ERROR

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        non_uniform_types = {"Sphere", "Capsule", "Cylinder", "Cone"}
        for prim in stage.Traverse():
            if not prim.HasAPI(UsdPhysics.CollisionAPI):
                continue
            if prim.GetTypeName() not in non_uniform_types:
                continue
            xformable = UsdGeom.Xformable(prim)
            if not xformable:
                continue
            for op in xformable.GetOrderedXformOps():
                if "scale" in op.GetOpName().lower():
                    val = op.Get()
                    if val and len(val) == 3:
                        if not (abs(val[0] - val[1]) < 1e-6 and abs(val[1] - val[2]) < 1e-6):
                            issues.append(Issue(rule=self.rule_name(), severity=Severity.ERROR,
                                message=f"Non-uniform scale {val} on {prim.GetTypeName()} collider.",
                                prim_path=str(prim.GetPath()), requirement_code=self.requirement_code))
        return issues


@RuleRegistry.register
class XformCommonApiUsage(BaseRule):
    requirement_code = "HI.005"
    category = "hierarchy"
    description = "Root prim transforms should conform to UsdGeomXformCommonAPI."
    severity = Severity.INFO

    def check(self, stage: Usd.Stage) -> list[Issue]:
        default_prim = stage.GetDefaultPrim()
        if not default_prim or not default_prim.IsValid():
            return []
        xformable = UsdGeom.Xformable(default_prim)
        if not xformable:
            return []
        common = UsdGeom.XformCommonAPI(default_prim)
        if not common:
            return [Issue(rule=self.rule_name(), severity=Severity.INFO,
                message="Root prim does not conform to XformCommonAPI.",
                prim_path=str(default_prim.GetPath()), requirement_code=self.requirement_code)]
        return []
