"""VG.014: Mesh topology must be valid."""

from pxr import Usd, UsdGeom

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue


@RuleRegistry.register
class MeshTopologyCheck(BaseRule):
    requirement_code = "VG.014"
    category = "geometry"
    description = "Mesh topology must be valid."
    severity = Severity.ERROR

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        for prim in stage.Traverse():
            mesh = UsdGeom.Mesh(prim)
            if not mesh:
                continue
            fvc_attr = mesh.GetFaceVertexCountsAttr()
            fvi_attr = mesh.GetFaceVertexIndicesAttr()
            pts_attr = mesh.GetPointsAttr()
            if not fvc_attr or not fvc_attr.HasValue():
                issues.append(Issue(rule=self.rule_name(), severity=Severity.ERROR,
                    message="Mesh missing faceVertexCounts.", prim_path=str(prim.GetPath()),
                    requirement_code=self.requirement_code))
                continue
            if not fvi_attr or not fvi_attr.HasValue():
                issues.append(Issue(rule=self.rule_name(), severity=Severity.ERROR,
                    message="Mesh missing faceVertexIndices.", prim_path=str(prim.GetPath()),
                    requirement_code=self.requirement_code))
                continue
            fvc = fvc_attr.Get()
            fvi = fvi_attr.Get()
            if fvc is None or fvi is None:
                continue
            expected = sum(fvc)
            if expected != len(fvi):
                issues.append(Issue(rule=self.rule_name(), severity=Severity.ERROR,
                    message=f"faceVertexCounts sum ({expected}) != faceVertexIndices length ({len(fvi)}).",
                    prim_path=str(prim.GetPath()), requirement_code=self.requirement_code))
            if pts_attr and pts_attr.HasValue():
                points = pts_attr.Get()
                if points is not None and len(fvi) > 0:
                    max_idx = max(fvi)
                    if max_idx >= len(points):
                        issues.append(Issue(rule=self.rule_name(), severity=Severity.ERROR,
                            message=f"faceVertexIndex {max_idx} out of range (points: {len(points)}).",
                            prim_path=str(prim.GetPath()), requirement_code=self.requirement_code))
        return issues
