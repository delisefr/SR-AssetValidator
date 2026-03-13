"""Test hierarchy/layout validation rules."""

import pytest
from sr_asset_validator.core.registry import RuleRegistry
RuleRegistry.discover()

from sr_asset_validator.rules.layout.prim_encapsulation import ExclusiveXformParent
from sr_asset_validator.rules.layout.orphaned_prim import PlaceableAreXformable
from sr_asset_validator.core.stage_loader import load_stage


class TestExclusiveXformParent:
    def test_valid(self, simready_asset):
        stage = load_stage(simready_asset)
        issues = ExclusiveXformParent().check(stage)
        assert len(issues) == 0


class TestPlaceableAreXformable:
    def test_valid(self, simready_asset):
        stage = load_stage(simready_asset)
        issues = PlaceableAreXformable().check(stage)
        assert len(issues) == 0
