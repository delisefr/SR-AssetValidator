"""Test hierarchy and unit validation rules."""

import pytest
from sr_asset_validator.core.registry import RuleRegistry
RuleRegistry.discover()

from sr_asset_validator.rules.basic.default_prim import StageHasDefaultPrim
from sr_asset_validator.rules.basic.stage_metadata import UpAxisCheck, MetersPerUnitCheck
from sr_asset_validator.rules.basic.kind_checker import HierarchyHasRoot
from sr_asset_validator.core.stage_loader import load_stage


class TestStageHasDefaultPrim:
    def test_valid(self, simready_asset):
        stage = load_stage(simready_asset)
        issues = StageHasDefaultPrim().check(stage)
        assert all(i.severity.name != "ERROR" for i in issues)

    def test_missing(self, asset_no_default_prim):
        stage = load_stage(asset_no_default_prim)
        issues = StageHasDefaultPrim().check(stage)
        assert any(i.severity.name == "ERROR" for i in issues)


class TestUpAxisCheck:
    def test_valid(self, simready_asset):
        stage = load_stage(simready_asset)
        issues = UpAxisCheck().check(stage)
        assert len(issues) == 0


class TestMetersPerUnitCheck:
    def test_valid(self, simready_asset):
        stage = load_stage(simready_asset)
        issues = MetersPerUnitCheck().check(stage)
        assert len(issues) == 0
