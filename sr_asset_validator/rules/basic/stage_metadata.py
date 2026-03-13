"""UN.001: upAxis, UN.002: metersPerUnit, UN.007: metersPerUnit=1."""

from pxr import Usd, UsdGeom

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue

_TOLERANCE = 1e-6


@RuleRegistry.register
class UpAxisCheck(BaseRule):
    requirement_code = "UN.001"
    category = "units"
    description = "Stage must specify upAxis."
    severity = Severity.ERROR

    def check(self, stage: Usd.Stage) -> list[Issue]:
        up_axis = UsdGeom.GetStageUpAxis(stage)
        if not up_axis:
            return [Issue(
                rule=self.rule_name(), severity=Severity.ERROR,
                message="Stage upAxis is not set.",
                requirement_code=self.requirement_code,
            )]
        return []


@RuleRegistry.register
class MetersPerUnitCheck(BaseRule):
    requirement_code = "UN.002"
    category = "units"
    description = "Stage must specify metersPerUnit."
    severity = Severity.ERROR

    def check(self, stage: Usd.Stage) -> list[Issue]:
        mpu = UsdGeom.GetStageMetersPerUnit(stage)
        if mpu is None or mpu <= 0:
            return [Issue(
                rule=self.rule_name(), severity=Severity.ERROR,
                message="Stage metersPerUnit is not set or invalid.",
                requirement_code=self.requirement_code,
            )]
        return []


@RuleRegistry.register
class UpAxisZCheck(BaseRule):
    requirement_code = "UN.006"
    category = "units"
    description = "Stage must specify upAxis = 'Z'."
    severity = Severity.ERROR

    def check(self, stage: Usd.Stage) -> list[Issue]:
        up_axis = UsdGeom.GetStageUpAxis(stage)
        if up_axis != UsdGeom.Tokens.z:
            return [Issue(
                rule=self.rule_name(), severity=Severity.ERROR,
                message=f"Stage upAxis is '{up_axis}', expected 'Z'.",
                requirement_code=self.requirement_code,
            )]
        return []


@RuleRegistry.register
class MetersPerUnit1Check(BaseRule):
    requirement_code = "UN.007"
    category = "units"
    description = "Stage must specify metersPerUnit = 1.0."
    severity = Severity.ERROR

    def check(self, stage: Usd.Stage) -> list[Issue]:
        mpu = UsdGeom.GetStageMetersPerUnit(stage)
        if mpu is None or abs(mpu - 1.0) > _TOLERANCE:
            return [Issue(
                rule=self.rule_name(), severity=Severity.WARNING,
                message=f"metersPerUnit={mpu}, expected 1.0.",
                requirement_code=self.requirement_code,
            )]
        return []
