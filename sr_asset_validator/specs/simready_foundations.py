"""Build specifications from the simready-foundation repository configs."""

from __future__ import annotations

from pathlib import Path

from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.spec import (
    Specification,
    Profile,
    load_all_capabilities,
    load_all_features,
)
from sr_asset_validator.core.engine import build_spec_from_profile

# Ensure all rules are discovered
RuleRegistry.discover()

# Default path to simready-foundation repo (relative to project root)
_PROJECT_ROOT = Path(__file__).parent.parent.parent
_SR_FOUNDATION = _PROJECT_ROOT / "simready-foundation"
_CONFIG_DIR = _SR_FOUNDATION / "nv_core" / "sr_specs" / "config"
_FEATURES_DIR = _SR_FOUNDATION / "nv_core" / "sr_specs" / "docs" / "features"


def _load_specs() -> dict[str, dict]:
    """Load capabilities and features from simready-foundation."""
    caps = load_all_capabilities(_CONFIG_DIR) if _CONFIG_DIR.exists() else {}
    feats = load_all_features(_FEATURES_DIR) if _FEATURES_DIR.exists() else {}
    return {"capabilities": caps, "features": feats}


def get_profile_spec(
    profile_name: str,
    profile_version: str,
    features_list: list[tuple[str, str]],
) -> Specification:
    """Build a resolved Specification for a given profile."""
    data = _load_specs()
    profile = Profile(
        name=profile_name,
        version=profile_version,
        features=features_list,
    )
    return build_spec_from_profile(
        profile, data["capabilities"], data["features"]
    )


# Pre-built profiles matching simready-foundation/nv_core/sr_specs/docs/profiles/profiles.toml

PropRoboticsNeutral = get_profile_spec(
    "Prop-Robotics-Neutral", "1.0.0",
    [
        ("FET000_CORE", "0.1.0"),
        ("FET001_BASE_NEUTRAL", "0.1.0"),
        ("FET003_BASE_NEUTRAL", "0.1.0"),
        ("FET004_BASE_NEUTRAL", "0.1.0"),
        ("FET005_BASE_NEUTRAL", "0.1.0"),
        ("FET006_BASE_MDL", "0.1.0"),
    ],
)

PropRoboticsPhysx = get_profile_spec(
    "Prop-Robotics-Physx", "1.0.0",
    [
        ("FET000_CORE", "0.1.0"),
        ("FET001_BASE_NEUTRAL", "0.1.0"),
        ("FET003_BASE_PHYSX", "0.1.0"),
        ("FET004_BASE_PHYSX", "0.1.0"),
        ("FET005_BASE_NEUTRAL", "0.1.0"),
        ("FET006_BASE_MDL", "0.1.0"),
    ],
)

PropRoboticsNeutralV2 = get_profile_spec(
    "Prop-Robotics-Neutral", "2.0.0",
    [
        ("FET000_CORE", "0.1.0"),
        ("FET001_BASE_NEUTRAL", "1.0.0"),
        ("FET003_BASE_NEUTRAL", "0.1.0"),
        ("FET004_BASE_NEUTRAL", "0.1.0"),
        ("FET005_BASE_NEUTRAL", "0.1.0"),
        ("FET006_BASE_MDL", "0.1.0"),
    ],
)

# All available profiles
PROFILES = {
    "Prop-Robotics-Neutral-v1": PropRoboticsNeutral,
    "Prop-Robotics-Neutral-v2": PropRoboticsNeutralV2,
    "Prop-Robotics-Physx-v1": PropRoboticsPhysx,
}

# Default: use Neutral v1 which covers the broadest set of sample content
SimReadyFoundations = PropRoboticsNeutral
