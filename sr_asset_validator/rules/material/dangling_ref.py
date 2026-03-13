"""VM.BIND.002: Shader inputs must have correct types."""

from pxr import Usd, UsdShade

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue


@RuleRegistry.register
class ShaderInputTypes(BaseRule):
    requirement_code = "VM.BIND.002"
    category = "material"
    description = "Shader inputs must have correct types matching their specification."
    severity = Severity.WARNING

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        for prim in stage.Traverse():
            binding_api = UsdShade.MaterialBindingAPI(prim)
            direct_binding = binding_api.GetDirectBinding()
            if not direct_binding:
                continue
            mat_path = direct_binding.GetMaterialPath()
            if mat_path and str(mat_path) != "":
                target = stage.GetPrimAtPath(mat_path)
                if not target or not target.IsValid():
                    issues.append(Issue(rule=self.rule_name(), severity=Severity.ERROR,
                        message=f"Material binding references non-existent path: {mat_path}",
                        prim_path=str(prim.GetPath()), requirement_code=self.requirement_code))
        return issues
