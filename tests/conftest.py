"""Shared fixtures that build synthetic USD stages for testing."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from pxr import Usd, UsdGeom, UsdShade, UsdPhysics, Sdf, Gf, Kind


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


def _make_simready_stage(path: Path, *, skip: str | None = None) -> str:
    """Create a minimal SimReady-compliant USD file.

    *skip* can be one of: "collider", "mass", "material", "default_prim",
    "metadata", "semantic" to intentionally omit that part.
    """
    filepath = str(path)
    stage = Usd.Stage.CreateNew(filepath)

    # Stage metadata
    if skip != "metadata":
        UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
        UsdGeom.SetStageMetersPerUnit(stage, 1.0)

    # Root Xform
    root = UsdGeom.Xform.Define(stage, "/Root")
    root_prim = root.GetPrim()

    if skip != "default_prim":
        stage.SetDefaultPrim(root_prim)

    # Set kind
    Usd.ModelAPI(root_prim).SetKind(Kind.Tokens.component)

    # Add semantic label
    if skip != "semantic":
        root_prim.CreateAttribute(
            "semantic:Semantic:params:semanticType", Sdf.ValueTypeNames.String
        ).Set("class")
        root_prim.CreateAttribute(
            "semantic:Semantic:params:semanticData", Sdf.ValueTypeNames.String
        ).Set("prop")

    # Create geometry group and simple cube mesh
    UsdGeom.Xform.Define(stage, "/Root/Geometry")
    mesh = UsdGeom.Mesh.Define(stage, "/Root/Geometry/Cube")
    mesh.GetPointsAttr().Set(
        [
            Gf.Vec3f(-1, -1, -1), Gf.Vec3f(1, -1, -1),
            Gf.Vec3f(1, 1, -1), Gf.Vec3f(-1, 1, -1),
            Gf.Vec3f(-1, -1, 1), Gf.Vec3f(1, -1, 1),
            Gf.Vec3f(1, 1, 1), Gf.Vec3f(-1, 1, 1),
        ]
    )
    mesh.GetFaceVertexCountsAttr().Set([4, 4, 4, 4, 4, 4])
    mesh.GetFaceVertexIndicesAttr().Set(
        [
            0, 1, 2, 3,   # front
            4, 7, 6, 5,   # back
            0, 4, 5, 1,   # bottom
            2, 6, 7, 3,   # top
            0, 3, 7, 4,   # left
            1, 5, 6, 2,   # right
        ]
    )
    mesh.GetSubdivisionSchemeAttr().Set("none")
    mesh.GetNormalsAttr().Set(
        [Gf.Vec3f(0, 0, -1)] * 4
        + [Gf.Vec3f(0, 0, 1)] * 4
        + [Gf.Vec3f(0, -1, 0)] * 4
        + [Gf.Vec3f(0, 1, 0)] * 4
        + [Gf.Vec3f(-1, 0, 0)] * 4
        + [Gf.Vec3f(1, 0, 0)] * 4
    )
    mesh.GetNormalsInterpolation()

    # Extent
    mesh.GetExtentAttr().Set([Gf.Vec3f(-1, -1, -1), Gf.Vec3f(1, 1, 1)])

    # UV primvar
    pv_api = UsdGeom.PrimvarsAPI(mesh.GetPrim())
    st = pv_api.CreatePrimvar("st", Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.faceVarying)
    st.Set(
        [Gf.Vec2f(0, 0), Gf.Vec2f(1, 0), Gf.Vec2f(1, 1), Gf.Vec2f(0, 1)] * 6
    )

    # Physics: collider
    if skip != "collider":
        UsdPhysics.CollisionAPI.Apply(mesh.GetPrim())

    # Physics: mass
    if skip != "mass":
        mass_api = UsdPhysics.MassAPI.Apply(mesh.GetPrim())
        mass_api.GetMassAttr().Set(1.0)

    # Material
    if skip != "material":
        mat_scope = UsdGeom.Scope.Define(stage, "/Root/Looks")
        material = UsdShade.Material.Define(stage, "/Root/Looks/DefaultMat")
        shader = UsdShade.Shader.Define(stage, "/Root/Looks/DefaultMat/Shader")
        shader.CreateIdAttr("UsdPreviewSurface")
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(
            Gf.Vec3f(0.5, 0.5, 0.5)
        )
        material.CreateSurfaceOutput().ConnectToSource(
            shader.ConnectableAPI(), "surface"
        )

        # Bind material
        UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim())
        UsdShade.MaterialBindingAPI(mesh.GetPrim()).Bind(material)

    stage.GetRootLayer().Save()
    return filepath


@pytest.fixture
def simready_asset(tmp_path) -> str:
    """Return path to a fully compliant SimReady USD file."""
    return _make_simready_stage(tmp_path / "compliant.usda")


@pytest.fixture
def asset_no_collider(tmp_path) -> str:
    return _make_simready_stage(tmp_path / "no_collider.usda", skip="collider")


@pytest.fixture
def asset_no_mass(tmp_path) -> str:
    return _make_simready_stage(tmp_path / "no_mass.usda", skip="mass")


@pytest.fixture
def asset_no_material(tmp_path) -> str:
    return _make_simready_stage(tmp_path / "no_material.usda", skip="material")


@pytest.fixture
def asset_no_default_prim(tmp_path) -> str:
    return _make_simready_stage(tmp_path / "no_default.usda", skip="default_prim")


@pytest.fixture
def asset_no_metadata(tmp_path) -> str:
    return _make_simready_stage(tmp_path / "no_metadata.usda", skip="metadata")


@pytest.fixture
def asset_no_semantic(tmp_path) -> str:
    return _make_simready_stage(tmp_path / "no_semantic.usda", skip="semantic")
