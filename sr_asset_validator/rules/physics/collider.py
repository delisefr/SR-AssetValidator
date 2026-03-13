"""RB.COL.001: Colliding Gprims must apply CollisionAPI.
RB.COL.002: MeshCollisionAPI requires CollisionAPI on same prim.
RB.COL.003: MeshCollisionAPI may only be applied to UsdGeom.Mesh."""

from pxr import Usd, UsdGeom, UsdPhysics

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue


@RuleRegistry.register
class ColliderCapability(BaseRule):
    requirement_code = "RB.COL.001"
    category = "physics"
    description = "Colliding Gprims must apply the Collision API."
    severity = Severity.INFO

    def check(self, stage: Usd.Stage) -> list[Issue]:
        has_collider = any(
            prim.HasAPI(UsdPhysics.CollisionAPI) for prim in stage.Traverse()
        )
        if not has_collider:
            return [Issue(rule=self.rule_name(), severity=Severity.INFO,
                message="No prims with CollisionAPI found (physics may be in companion file).",
                requirement_code=self.requirement_code)]
        return []


@RuleRegistry.register
class MeshCollisionApiCheck(BaseRule):
    requirement_code = "RB.COL.002"
    category = "physics"
    description = "MeshCollisionAPI requires CollisionAPI on the same prim."
    severity = Severity.ERROR

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        for prim in stage.Traverse():
            if prim.HasAPI(UsdPhysics.MeshCollisionAPI):
                if not prim.HasAPI(UsdPhysics.CollisionAPI):
                    issues.append(Issue(rule=self.rule_name(), severity=Severity.ERROR,
                        message="MeshCollisionAPI without CollisionAPI.",
                        prim_path=str(prim.GetPath()), requirement_code=self.requirement_code))
        return issues


@RuleRegistry.register
class ColliderMeshOnly(BaseRule):
    requirement_code = "RB.COL.003"
    category = "physics"
    description = "MeshCollisionAPI may only be applied to Mesh prims."
    severity = Severity.ERROR

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        for prim in stage.Traverse():
            if prim.HasAPI(UsdPhysics.MeshCollisionAPI):
                if not prim.IsA(UsdGeom.Mesh):
                    issues.append(Issue(rule=self.rule_name(), severity=Severity.ERROR,
                        message=f"MeshCollisionAPI on non-Mesh prim ({prim.GetTypeName()}).",
                        prim_path=str(prim.GetPath()), requirement_code=self.requirement_code))
        return issues
