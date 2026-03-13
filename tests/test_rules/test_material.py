"""Test material validation rules."""

import pytest
from sr_asset_validator.core.registry import RuleRegistry
RuleRegistry.discover()

from sr_asset_validator.rules.material.binding import MaterialAssignment
from sr_asset_validator.rules.material.dangling_ref import ShaderInputTypes
from sr_asset_validator.core.stage_loader import load_stage


class TestMaterialAssignment:
    def test_bound(self, simready_asset):
        stage = load_stage(simready_asset)
        issues = MaterialAssignment().check(stage)
        assert len(issues) == 0

    def test_unbound(self, asset_no_material):
        stage = load_stage(asset_no_material)
        issues = MaterialAssignment().check(stage)
        assert len(issues) > 0


class TestShaderInputTypes:
    def test_no_dangling(self, simready_asset):
        stage = load_stage(simready_asset)
        issues = ShaderInputTypes().check(stage)
        assert len(issues) == 0
