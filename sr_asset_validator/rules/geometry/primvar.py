"""VG.001: Assets must contain at least one imageable geometry.
VG.MESH.001: All geometry shall be mesh primitives.
VG.029: Mesh winding order must be correct."""

from pxr import Usd, UsdGeom

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue


@RuleRegistry.register
class AtLeastOneGeometry(BaseRule):
    requirement_code = "VG.001"
    category = "geometry"
    description = "Assets must contain at least one imageable geometry."
    severity = Severity.ERROR

    def check(self, stage: Usd.Stage) -> list[Issue]:
        for prim in stage.Traverse():
            if prim.IsA(UsdGeom.Imageable) and prim.IsA(UsdGeom.Gprim):
                return []
        return [Issue(rule=self.rule_name(), severity=Severity.ERROR,
            message="No imageable geometry found in stage.",
            requirement_code=self.requirement_code)]


@RuleRegistry.register
class GeomShallBeMesh(BaseRule):
    requirement_code = "VG.MESH.001"
    category = "geometry"
    description = "All geometry shall be represented as mesh primitives."
    severity = Severity.WARNING

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        non_mesh_types = {"Curves", "Points", "BasisCurves", "NurbsCurves", "NurbsPatch"}
        for prim in stage.Traverse():
            if prim.GetTypeName() in non_mesh_types:
                issues.append(Issue(rule=self.rule_name(), severity=Severity.WARNING,
                    message=f"Non-mesh geometry type: {prim.GetTypeName()}.",
                    prim_path=str(prim.GetPath()), requirement_code=self.requirement_code))
        return issues


@RuleRegistry.register
class MeshWindingOrder(BaseRule):
    requirement_code = "VG.029"
    category = "geometry"
    description = "Winding order must correctly represent face orientation."
    severity = Severity.INFO

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        for prim in stage.Traverse():
            mesh = UsdGeom.Mesh(prim)
            if not mesh:
                continue
            orient_attr = mesh.GetOrientationAttr()
            if orient_attr and orient_attr.HasValue():
                orient = orient_attr.Get()
                if orient not in ("leftHanded", "rightHanded"):
                    issues.append(Issue(rule=self.rule_name(), severity=Severity.WARNING,
                        message=f"Unexpected orientation: {orient}.",
                        prim_path=str(prim.GetPath()), requirement_code=self.requirement_code))
        return issues
