"""VM.MAT.001: Each renderable GPrim must have a computed material bound.
VM.BIND.001: Material bindings must use appropriate scope."""

from pxr import Usd, UsdGeom, UsdShade

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue


@RuleRegistry.register
class MaterialAssignment(BaseRule):
    requirement_code = "VM.MAT.001"
    category = "material"
    description = "Each renderable GPrim must have a computed material bound."
    severity = Severity.WARNING

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        for prim in stage.Traverse():
            if not prim.IsA(UsdGeom.Gprim):
                continue
            purpose = UsdGeom.Imageable(prim).ComputePurpose()
            if purpose == UsdGeom.Tokens.guide:
                continue  # guide geometry doesn't need materials
            binding_api = UsdShade.MaterialBindingAPI(prim)
            mat_binding = binding_api.ComputeBoundMaterial()
            material = mat_binding[0] if mat_binding else None
            if not material or not material.GetPrim().IsValid():
                issues.append(Issue(rule=self.rule_name(), severity=Severity.WARNING,
                    message="Renderable GPrim has no material bound.",
                    prim_path=str(prim.GetPath()), requirement_code=self.requirement_code))
        return issues


@RuleRegistry.register
class MaterialBindScope(BaseRule):
    requirement_code = "VM.BIND.001"
    category = "material"
    description = "Material bindings must use appropriate scope."
    severity = Severity.WARNING

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        for prim in stage.Traverse():
            if not prim.IsA(UsdShade.Material):
                continue
            path_parts = str(prim.GetPath()).split("/")
            in_scope = any(p in ("Looks", "Materials", "materials") for p in path_parts)
            if not in_scope:
                issues.append(Issue(rule=self.rule_name(), severity=Severity.WARNING,
                    message="Material not under 'Looks' or 'Materials' scope.",
                    prim_path=str(prim.GetPath()), requirement_code=self.requirement_code))
        return issues
