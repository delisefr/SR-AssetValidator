"""VG.019: Faces should have non-zero area."""

from pxr import Usd, UsdGeom, Gf

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue


@RuleRegistry.register
class ZeroAreaFaceCheck(BaseRule):
    requirement_code = "VG.019"
    category = "geometry"
    description = "Faces should have non-zero area."
    severity = Severity.WARNING

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        for prim in stage.Traverse():
            mesh = UsdGeom.Mesh(prim)
            if not mesh:
                continue
            pts_attr = mesh.GetPointsAttr()
            fvc_attr = mesh.GetFaceVertexCountsAttr()
            fvi_attr = mesh.GetFaceVertexIndicesAttr()
            if not all(a and a.HasValue() for a in (pts_attr, fvc_attr, fvi_attr)):
                continue
            points = pts_attr.Get()
            fvc = fvc_attr.Get()
            fvi = fvi_attr.Get()
            if points is None or fvc is None or fvi is None:
                continue
            degen = 0
            idx = 0
            for count in fvc:
                if count < 3:
                    degen += 1
                    idx += count
                    continue
                i0, i1, i2 = fvi[idx], fvi[idx + 1], fvi[idx + 2]
                if max(i0, i1, i2) < len(points):
                    p0 = Gf.Vec3d(points[i0])
                    cross = Gf.Cross(Gf.Vec3d(points[i1]) - p0, Gf.Vec3d(points[i2]) - p0)
                    if Gf.Vec3d(cross).GetLength() < 1e-10:
                        degen += 1
                idx += count
            if degen > 0:
                issues.append(Issue(rule=self.rule_name(), severity=Severity.WARNING,
                    message=f"Mesh has {degen} degenerate face(s).",
                    prim_path=str(prim.GetPath()), requirement_code=self.requirement_code))
        return issues
