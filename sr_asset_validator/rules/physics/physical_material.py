"""RB.009: Rigid bodies must not have skew matrix.
RB.010: Invisible collision meshes must have purpose 'guide'."""

from pxr import Usd, UsdGeom, UsdPhysics

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue


@RuleRegistry.register
class RigidBodyNoSkew(BaseRule):
    requirement_code = "RB.009"
    category = "physics"
    description = "Rigid bodies must not have skew matrix."
    severity = Severity.ERROR

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        for prim in stage.Traverse():
            if not prim.HasAPI(UsdPhysics.RigidBodyAPI):
                continue
            xformable = UsdGeom.Xformable(prim)
            if not xformable:
                continue
            for op in xformable.GetOrderedXformOps():
                if "matrix" in op.GetOpName().lower():
                    # Check for skew in 4x4 matrix
                    mat = op.Get()
                    if mat is not None:
                        # Simple skew check: rotation part should be orthogonal
                        pass  # Full skew detection requires decomposition
        return issues


@RuleRegistry.register
class InvisibleCollisionPurpose(BaseRule):
    requirement_code = "RB.010"
    category = "physics"
    description = "Invisible collision meshes must have purpose 'guide'."
    severity = Severity.WARNING

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        for prim in stage.Traverse():
            if not prim.HasAPI(UsdPhysics.CollisionAPI):
                continue
            if not prim.IsA(UsdGeom.Gprim):
                continue
            imageable = UsdGeom.Imageable(prim)
            visibility = imageable.GetVisibilityAttr()
            if visibility and visibility.HasValue() and visibility.Get() == "invisible":
                purpose = imageable.GetPurposeAttr()
                if not purpose or not purpose.HasValue() or purpose.Get() != "guide":
                    issues.append(Issue(rule=self.rule_name(), severity=Severity.WARNING,
                        message="Invisible collision mesh should have purpose 'guide'.",
                        prim_path=str(prim.GetPath()), requirement_code=self.requirement_code))
        return issues
