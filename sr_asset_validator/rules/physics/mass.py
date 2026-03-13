"""RB.007: Rigid bodies or descendants should have mass specification.
RB.001: Assets must contain at least one rigid body."""

from pxr import Usd, UsdPhysics

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue


@RuleRegistry.register
class RigidBodyCapability(BaseRule):
    requirement_code = "RB.001"
    category = "physics"
    description = "Assets must contain at least one rigid body."
    severity = Severity.INFO

    def check(self, stage: Usd.Stage) -> list[Issue]:
        for prim in stage.Traverse():
            if prim.HasAPI(UsdPhysics.RigidBodyAPI):
                return []
        return [Issue(rule=self.rule_name(), severity=Severity.INFO,
            message="No rigid body found (may be added at simulation time).",
            requirement_code=self.requirement_code)]


@RuleRegistry.register
class RigidBodyMass(BaseRule):
    requirement_code = "RB.007"
    category = "physics"
    description = "Rigid bodies or descendants should have mass specification."
    severity = Severity.WARNING

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        for prim in stage.Traverse():
            if not prim.HasAPI(UsdPhysics.RigidBodyAPI):
                continue
            has_mass = False
            for desc in Usd.PrimRange(prim):
                if desc.HasAPI(UsdPhysics.MassAPI):
                    has_mass = True
                    break
            if not has_mass:
                issues.append(Issue(rule=self.rule_name(), severity=Severity.WARNING,
                    message="Rigid body has no mass specification in subtree.",
                    prim_path=str(prim.GetPath()), requirement_code=self.requirement_code))
        return issues
