"""Semantic label rules — these codes (SL.*) are referenced in features but
defined outside the core config JSONs. We implement the check anyway."""

from pxr import Usd

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue


SEMANTIC_ATTR_PREFIXES = ("semantic:", "semantics:")


@RuleRegistry.register
class SemanticLabelExists(BaseRule):
    requirement_code = "SL.001"
    category = "simready"
    description = "Assets should have semantic labels."
    severity = Severity.WARNING

    def check(self, stage: Usd.Stage) -> list[Issue]:
        default_prim = stage.GetDefaultPrim()
        if not default_prim or not default_prim.IsValid():
            return []
        for prim in Usd.PrimRange(default_prim):
            for attr in prim.GetAttributes():
                if any(attr.GetName().startswith(p) for p in SEMANTIC_ATTR_PREFIXES):
                    return []
            for schema in prim.GetAppliedSchemas():
                if "Semantic" in schema or "semantic" in schema:
                    return []
        return [Issue(rule=self.rule_name(), severity=Severity.WARNING,
            message="No semantic labels found.",
            prim_path=str(default_prim.GetPath()), requirement_code=self.requirement_code)]
