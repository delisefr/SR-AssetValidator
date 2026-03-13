"""Test the validation engine with SimReady Foundation specs."""

import pytest
from sr_asset_validator.core.engine import ValidationEngine
from sr_asset_validator.specs.simready_foundations import SimReadyFoundations


class TestEngineCompliant:
    def test_compliant_asset_passes(self, simready_asset):
        engine = ValidationEngine()
        report = engine.validate_file(simready_asset, SimReadyFoundations)
        errors = [r for r in report.results if not r.passed]
        for e in errors:
            print(f"  FAIL [{e.requirement_code}] {e.rule_name}: {[str(i) for i in e.issues]}")
        assert report.passed

    def test_report_summary(self, simready_asset):
        engine = ValidationEngine()
        report = engine.validate_file(simready_asset, SimReadyFoundations)
        summary = report.summary()
        assert "PASS" in summary or "FAIL" in summary

    def test_rule_count(self, simready_asset):
        engine = ValidationEngine()
        report = engine.validate_file(simready_asset, SimReadyFoundations)
        assert len(report.results) == len(SimReadyFoundations.rules)


class TestEngineDefects:
    def test_no_default_prim_fails(self, asset_no_default_prim):
        engine = ValidationEngine()
        report = engine.validate_file(asset_no_default_prim, SimReadyFoundations)
        dp_result = next(
            (r for r in report.results if r.requirement_code == "HI.004"), None
        )
        assert dp_result is not None
        assert not dp_result.passed

    def test_no_material_warns(self, asset_no_material):
        engine = ValidationEngine()
        report = engine.validate_file(asset_no_material, SimReadyFoundations)
        mat_result = next(
            (r for r in report.results if r.requirement_code == "VM.MAT.001"), None
        )
        assert mat_result is not None
        assert len(mat_result.issues) > 0
