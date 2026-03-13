"""Test geometry validation rules."""

import pytest
from pxr import Usd, UsdGeom, Gf

from sr_asset_validator.core.registry import RuleRegistry
RuleRegistry.discover()

from sr_asset_validator.rules.geometry.topology import MeshTopologyCheck
from sr_asset_validator.rules.geometry.primvar import AtLeastOneGeometry
from sr_asset_validator.core.stage_loader import load_stage


class TestMeshTopologyCheck:
    def test_valid_mesh(self, simready_asset):
        stage = load_stage(simready_asset)
        issues = MeshTopologyCheck().check(stage)
        assert all(i.severity.name != "ERROR" for i in issues)

    def test_bad_topology(self, tmp_path):
        path = str(tmp_path / "bad_topo.usda")
        stage = Usd.Stage.CreateNew(path)
        UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
        root = UsdGeom.Xform.Define(stage, "/Root")
        stage.SetDefaultPrim(root.GetPrim())
        mesh = UsdGeom.Mesh.Define(stage, "/Root/BadMesh")
        mesh.GetPointsAttr().Set([Gf.Vec3f(0, 0, 0), Gf.Vec3f(1, 0, 0)])
        mesh.GetFaceVertexCountsAttr().Set([3])
        mesh.GetFaceVertexIndicesAttr().Set([0, 1])
        stage.GetRootLayer().Save()
        stage2 = load_stage(path)
        issues = MeshTopologyCheck().check(stage2)
        assert any(i.severity.name == "ERROR" for i in issues)


class TestAtLeastOneGeometry:
    def test_has_geometry(self, simready_asset):
        stage = load_stage(simready_asset)
        issues = AtLeastOneGeometry().check(stage)
        assert len(issues) == 0
