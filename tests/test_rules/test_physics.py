"""Test physics validation rules."""

import pytest
from sr_asset_validator.core.registry import RuleRegistry
RuleRegistry.discover()

from sr_asset_validator.rules.physics.collider import ColliderCapability, MeshCollisionApiCheck
from sr_asset_validator.rules.physics.mass import RigidBodyCapability, RigidBodyMass
from sr_asset_validator.rules.physics.rigid_body import RigidBodySchemaApplication
from sr_asset_validator.core.stage_loader import load_stage


class TestColliderCapability:
    def test_has_collider(self, simready_asset):
        stage = load_stage(simready_asset)
        issues = ColliderCapability().check(stage)
        assert all(i.severity.name != "ERROR" for i in issues)


class TestRigidBodyCapability:
    def test_no_rigid_body_is_info(self, simready_asset):
        stage = load_stage(simready_asset)
        issues = RigidBodyCapability().check(stage)
        assert all(i.severity.name in ("INFO", "WARNING") for i in issues)


class TestMeshCollisionApiCheck:
    def test_valid(self, simready_asset):
        stage = load_stage(simready_asset)
        issues = MeshCollisionApiCheck().check(stage)
        assert len(issues) == 0
