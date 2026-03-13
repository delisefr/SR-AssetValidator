"""RB.003: Rigid bodies must be UsdGeomXformable prims.
RB.005: Rigid bodies cannot be part of a scene graph instance.
RB.006: Rigid bodies cannot be nested without resetXformStack."""

from pxr import Usd, UsdGeom, UsdPhysics

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue


@RuleRegistry.register
class RigidBodySchemaApplication(BaseRule):
    requirement_code = "RB.003"
    category = "physics"
    description = "Rigid bodies must be UsdGeomXformable prims."
    severity = Severity.ERROR

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        for prim in stage.Traverse():
            if prim.HasAPI(UsdPhysics.RigidBodyAPI):
                if not prim.IsA(UsdGeom.Xformable):
                    issues.append(Issue(rule=self.rule_name(), severity=Severity.ERROR,
                        message="RigidBodyAPI on non-Xformable prim.",
                        prim_path=str(prim.GetPath()), requirement_code=self.requirement_code))
        return issues


@RuleRegistry.register
class RigidBodyNoInstancing(BaseRule):
    requirement_code = "RB.005"
    category = "physics"
    description = "Rigid bodies cannot be part of a scene graph instance."
    severity = Severity.ERROR

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        for prim in stage.Traverse():
            if prim.HasAPI(UsdPhysics.RigidBodyAPI):
                if prim.IsInstance() or prim.IsInstanceProxy():
                    issues.append(Issue(rule=self.rule_name(), severity=Severity.ERROR,
                        message="RigidBodyAPI on instanced prim.",
                        prim_path=str(prim.GetPath()), requirement_code=self.requirement_code))
        return issues


@RuleRegistry.register
class RigidBodyNoNesting(BaseRule):
    requirement_code = "RB.006"
    category = "physics"
    description = "Rigid bodies cannot be nested unless resetXformStack is used."
    severity = Severity.ERROR

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        rb_paths: set[str] = set()
        for prim in stage.Traverse():
            if prim.HasAPI(UsdPhysics.RigidBodyAPI):
                path = str(prim.GetPath())
                for existing in rb_paths:
                    if path.startswith(existing + "/"):
                        xformable = UsdGeom.Xformable(prim)
                        if xformable and not xformable.GetResetXformStack():
                            issues.append(Issue(rule=self.rule_name(), severity=Severity.ERROR,
                                message=f"Nested rigid body under {existing}.",
                                prim_path=path, requirement_code=self.requirement_code))
                rb_paths.add(path)
        return issues
