"""VM.MDL.002: MDL Shaders must use standard OpenUSD shader source attributes.
VM.TEX.001: Texture dimensions limit."""

from pxr import Usd, UsdShade

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue


@RuleRegistry.register
class MdlSchemaCheck(BaseRule):
    requirement_code = "VM.MDL.002"
    category = "material"
    description = "MDL Shaders must use standard OpenUSD shader source attributes."
    severity = Severity.WARNING

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        for prim in stage.Traverse():
            shader = UsdShade.Shader(prim)
            if not shader:
                continue
            # Check if shader has info:mdl:sourceAsset but missing standard attrs
            mdl_attr = prim.GetAttribute("info:mdl:sourceAsset")
            if mdl_attr and mdl_attr.HasValue():
                impl = shader.GetImplementationSource()
                if impl != "sourceAsset":
                    issues.append(Issue(rule=self.rule_name(), severity=Severity.WARNING,
                        message="MDL shader does not use 'sourceAsset' implementation source.",
                        prim_path=str(prim.GetPath()), requirement_code=self.requirement_code))
        return issues
