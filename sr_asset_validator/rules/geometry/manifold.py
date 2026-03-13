"""VG.007: Mesh geometry must be manifold.
VG.025: Asset must be correctly positioned at origin."""

from pxr import Usd, UsdGeom, Gf

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue


@RuleRegistry.register
class MeshManifoldCheck(BaseRule):
    requirement_code = "VG.007"
    category = "geometry"
    description = "Mesh geometry must be manifold."
    severity = Severity.WARNING

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        for prim in stage.Traverse():
            mesh = UsdGeom.Mesh(prim)
            if not mesh:
                continue
            fvc_attr = mesh.GetFaceVertexCountsAttr()
            fvi_attr = mesh.GetFaceVertexIndicesAttr()
            if not fvc_attr or not fvi_attr:
                continue
            if not fvc_attr.HasValue() or not fvi_attr.HasValue():
                continue
            fvc = fvc_attr.Get()
            fvi = fvi_attr.Get()
            if fvc is None or fvi is None:
                continue
            edge_count: dict[tuple[int, int], int] = {}
            idx = 0
            for count in fvc:
                verts = [fvi[idx + i] for i in range(count)]
                for i in range(count):
                    a, b = verts[i], verts[(i + 1) % count]
                    edge = (min(a, b), max(a, b))
                    edge_count[edge] = edge_count.get(edge, 0) + 1
                idx += count
            non_manifold = sum(1 for c in edge_count.values() if c > 2)
            if non_manifold > 0:
                issues.append(Issue(rule=self.rule_name(), severity=Severity.WARNING,
                    message=f"Mesh has {non_manifold} non-manifold edge(s).",
                    prim_path=str(prim.GetPath()), requirement_code=self.requirement_code))
        return issues


@RuleRegistry.register
class AssetOriginPositioning(BaseRule):
    requirement_code = "VG.025"
    category = "geometry"
    description = "Asset must be positioned at origin (0,0,0)."
    severity = Severity.INFO

    def check(self, stage: Usd.Stage) -> list[Issue]:
        default_prim = stage.GetDefaultPrim()
        if not default_prim or not default_prim.IsValid():
            return []
        xformable = UsdGeom.Xformable(default_prim)
        if not xformable:
            return []
        xform_ops = xformable.GetOrderedXformOps()
        for op in xform_ops:
            if "translate" in op.GetOpName().lower():
                val = op.Get()
                if val and (abs(val[0]) > 1e-3 or abs(val[1]) > 1e-3 or abs(val[2]) > 1e-3):
                    return [Issue(rule=self.rule_name(), severity=Severity.INFO,
                        message=f"Root prim has non-zero translation: {val}.",
                        prim_path=str(default_prim.GetPath()),
                        requirement_code=self.requirement_code)]
        return []
