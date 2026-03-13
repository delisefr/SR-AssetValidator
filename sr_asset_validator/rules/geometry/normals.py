"""VG.027: Non-subdivided meshes must have normals.
VG.028: Mesh normals values must be valid."""

from pxr import Usd, UsdGeom, Gf

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue


@RuleRegistry.register
class MeshNormalsExist(BaseRule):
    requirement_code = "VG.027"
    category = "geometry"
    description = "All non-subdivided meshes must have normals."
    severity = Severity.WARNING

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        for prim in stage.Traverse():
            mesh = UsdGeom.Mesh(prim)
            if not mesh:
                continue
            subdiv = mesh.GetSubdivisionSchemeAttr()
            if subdiv and subdiv.HasValue() and subdiv.Get() != "none":
                continue  # subdivided mesh — normals computed
            normals = mesh.GetNormalsAttr()
            if not normals or not normals.HasValue():
                issues.append(Issue(rule=self.rule_name(), severity=Severity.WARNING,
                    message="Non-subdivided mesh has no normals.",
                    prim_path=str(prim.GetPath()), requirement_code=self.requirement_code))
        return issues


@RuleRegistry.register
class MeshNormalsValid(BaseRule):
    requirement_code = "VG.028"
    category = "geometry"
    description = "Mesh normals values must be valid."
    severity = Severity.WARNING

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        for prim in stage.Traverse():
            mesh = UsdGeom.Mesh(prim)
            if not mesh:
                continue
            normals_attr = mesh.GetNormalsAttr()
            if not normals_attr or not normals_attr.HasValue():
                continue
            normals = normals_attr.Get()
            if normals is not None and len(normals) == 0:
                issues.append(Issue(rule=self.rule_name(), severity=Severity.WARNING,
                    message="Mesh has empty normals array.",
                    prim_path=str(prim.GetPath()), requirement_code=self.requirement_code))
        return issues
