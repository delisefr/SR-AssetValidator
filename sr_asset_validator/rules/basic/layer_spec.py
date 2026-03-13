"""HI.010: Assets must not contain undefined prims (overs)."""

from pxr import Usd, Sdf

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue


@RuleRegistry.register
class UndefinedPrimsCheck(BaseRule):
    requirement_code = "HI.010"
    category = "hierarchy"
    description = "Assets must not contain undefined prims (overs)."
    severity = Severity.WARNING

    def check(self, stage: Usd.Stage) -> list[Issue]:
        issues: list[Issue] = []
        root_layer = stage.GetRootLayer()

        def _check_specs(layer: Sdf.Layer, parent_path: str = "") -> None:
            for prim_path in layer.rootPrims:
                spec = layer.GetPrimAtPath(prim_path.path)
                if spec and spec.specifier == Sdf.SpecifierOver:
                    issues.append(Issue(
                        rule=self.rule_name(), severity=Severity.WARNING,
                        message="Root layer contains an 'over' prim (undefined).",
                        prim_path=str(spec.path),
                        requirement_code=self.requirement_code,
                    ))

        _check_specs(root_layer)
        return issues
