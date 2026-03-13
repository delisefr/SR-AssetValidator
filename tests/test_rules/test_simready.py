"""Test SimReady-specific rules."""

import pytest
from sr_asset_validator.core.registry import RuleRegistry
RuleRegistry.discover()

from sr_asset_validator.rules.simready.semantic_labels import SemanticLabelExists
from sr_asset_validator.rules.simready.asset_structure import MultiBodyCapability
from sr_asset_validator.core.stage_loader import load_stage


class TestSemanticLabelExists:
    def test_has_labels(self, simready_asset):
        stage = load_stage(simready_asset)
        issues = SemanticLabelExists().check(stage)
        assert len(issues) == 0

    def test_no_labels(self, asset_no_semantic):
        stage = load_stage(asset_no_semantic)
        issues = SemanticLabelExists().check(stage)
        assert len(issues) > 0


class TestMultiBodyCapability:
    def test_single_body_is_info(self, simready_asset):
        stage = load_stage(simready_asset)
        issues = MultiBodyCapability().check(stage)
        assert all(i.severity.name == "INFO" for i in issues)
