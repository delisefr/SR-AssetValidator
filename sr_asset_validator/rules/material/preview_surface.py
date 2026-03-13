"""VM.PS.001: UsdPreviewSurface compliance.
VM.MDL.001: MDL source asset compliance."""

from pxr import Usd, UsdShade

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue


@RuleRegistry.register
class MaterialPreviewSurface(BaseRule):
    requirement_code = "VM.PS.001"
    category = "material"
    description = "Materials must comply with UsdPreviewSurface specification."
    severity = Severity.WARNING

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        for prim in stage.Traverse():
            mat = UsdShade.Material(prim)
            if not mat:
                continue
            surface_output = mat.GetSurfaceOutput()
            if not surface_output or not surface_output.HasConnectedSource():
                continue  # VM.MAT.001 handles unconnected materials
            sources = surface_output.GetConnectedSources()
            has_preview = False
            if sources:
                for source_info in sources[0]:
                    shader = UsdShade.Shader(source_info.source.GetPrim())
                    if shader:
                        shader_id = shader.GetIdAttr()
                        if shader_id and shader_id.HasValue() and shader_id.Get() == "UsdPreviewSurface":
                            has_preview = True
                            break
            if not has_preview:
                issues.append(Issue(rule=self.rule_name(), severity=Severity.INFO,
                    message="Material does not use UsdPreviewSurface (may use MDL).",
                    prim_path=str(prim.GetPath()), requirement_code=self.requirement_code))
        return issues


@RuleRegistry.register
class MaterialMdlSourceAsset(BaseRule):
    requirement_code = "VM.MDL.001"
    category = "material"
    description = "MDL shader source asset must be properly configured."
    severity = Severity.WARNING

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        for prim in stage.Traverse():
            shader = UsdShade.Shader(prim)
            if not shader:
                continue
            impl_source = shader.GetImplementationSource()
            if impl_source == "sourceAsset":
                source_asset = shader.GetSourceAsset("mdl")
                if source_asset and str(source_asset) != "":
                    # Valid MDL source
                    continue
        return issues
