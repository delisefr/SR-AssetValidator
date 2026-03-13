"""VG.010: Use subdivision only when needed for smooth surfaces."""

from pxr import Usd, UsdGeom

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue


@RuleRegistry.register
class SubdivisionCheck(BaseRule):
    requirement_code = "VG.010"
    category = "geometry"
    description = "Use subdivision only when needed for smooth surfaces or displacement."
    severity = Severity.WARNING

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        for prim in stage.Traverse():
            mesh = UsdGeom.Mesh(prim)
            if not mesh:
                continue
            subdiv_attr = mesh.GetSubdivisionSchemeAttr()
            if subdiv_attr and subdiv_attr.HasValue():
                scheme = subdiv_attr.Get()
                if scheme and scheme != "none":
                    issues.append(Issue(rule=self.rule_name(), severity=Severity.WARNING,
                        message=f"Mesh uses subdivision '{scheme}' — verify it's needed.",
                        prim_path=str(prim.GetPath()), requirement_code=self.requirement_code))
        return issues
