"""Validation engine — orchestrates rule execution."""

from __future__ import annotations

from pathlib import Path

from .registry import RuleRegistry
from .result import ValidationReport, ValidationResult
from .spec import Specification, load_all_capabilities, load_all_features, Profile
from .stage_loader import load_stage, discover_usd_files


class ValidationEngine:
    """Run a Specification (resolved profile) against one or more USD files."""

    def validate_file(self, path: str, spec: Specification) -> ValidationReport:
        stage = load_stage(path)
        report = ValidationReport(file_path=path, spec_name=spec.name)

        rules_to_run = spec.rules
        if not rules_to_run:
            # Fallback: resolve rules from requirement codes
            RuleRegistry.discover()
            rules_to_run = RuleRegistry.rules_for_codes(spec.requirement_codes())

        for rule_cls in rules_to_run:
            rule = rule_cls()
            issues = rule.check(stage)
            errors = [i for i in issues if i.severity.name == "ERROR"]
            report.results.append(
                ValidationResult(
                    rule_name=rule_cls.rule_name(),
                    requirement_code=rule_cls.requirement_code,
                    passed=len(errors) == 0,
                    issues=issues,
                )
            )
        return report

    def validate_directory(
        self, directory: str, spec: Specification
    ) -> list[ValidationReport]:
        reports: list[ValidationReport] = []
        for usd_file in discover_usd_files(directory):
            try:
                reports.append(self.validate_file(str(usd_file), spec))
            except Exception as e:
                report = ValidationReport(
                    file_path=str(usd_file), spec_name=spec.name
                )
                report.results.append(
                    ValidationResult(
                        rule_name="StageLoad",
                        requirement_code="",
                        passed=False,
                        issues=[],
                    )
                )
                reports.append(report)
        return reports


def build_spec_from_profile(
    profile: Profile,
    capabilities: dict,
    features: dict,
) -> Specification:
    """Resolve a profile into a Specification with all requirement codes expanded."""
    all_codes: set[str] = set()
    from .spec import Requirement

    all_reqs: list[Requirement] = []
    req_lookup: dict[str, Requirement] = {}
    for cap in capabilities.values():
        for r in cap.requirements:
            req_lookup[r.code] = r

    def _expand_feature(feat_id: str, feat_ver: str, visited: set[tuple[str, str]]) -> None:
        key = (feat_id, feat_ver)
        if key in visited:
            return
        visited.add(key)
        feat = features.get(key)
        if not feat:
            return
        for dep_id, dep_ver in feat.dependencies:
            _expand_feature(dep_id, dep_ver, visited)
        all_codes.update(feat.requirement_codes)

    visited: set[tuple[str, str]] = set()
    for feat_id, feat_ver in profile.features:
        _expand_feature(feat_id, feat_ver, visited)

    reqs = [req_lookup[c] for c in sorted(all_codes) if c in req_lookup]

    RuleRegistry.discover()
    rules = RuleRegistry.rules_for_codes(all_codes)

    return Specification(
        name=f"{profile.name} v{profile.version}",
        description=f"Profile {profile.name} version {profile.version}",
        requirements=reqs,
        rules=rules,
    )
