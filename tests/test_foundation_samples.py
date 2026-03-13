"""Integration tests against simready-foundation sample_content.

Validates all prop assets from the official SimReady Foundation repo
against the Prop-Robotics-Neutral v1 profile.
"""

import pytest
from pathlib import Path

from sr_asset_validator.core.engine import ValidationEngine
from sr_asset_validator.specs.simready_foundations import SimReadyFoundations

SAMPLES_ROOT = Path(__file__).parent.parent / "simready-foundation" / "sample_content"
PROPS_DIR = SAMPLES_ROOT / "common_assets" / "props_general"

# All simready_usd prop assets from the foundation repo
PROP_SAMPLES = sorted(
    str(p)
    for p in PROPS_DIR.rglob("simready_usd/*.usd")
    if p.exists() and "payloads" not in str(p)
) if PROPS_DIR.exists() else []

# Also test physx variants
PHYSX_SAMPLES = sorted(
    str(p)
    for p in PROPS_DIR.rglob("simready_physx_usd/*.usd")
    if p.exists() and "payloads" not in str(p)
) if PROPS_DIR.exists() else []


def _is_lfs_pointer(path: str) -> bool:
    """Check if file is an unresolved LFS pointer."""
    try:
        with open(path, "rb") as f:
            header = f.read(50)
            return b"git-lfs" in header
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not PROP_SAMPLES,
    reason="SimReady Foundation sample content not available.",
)


class TestFoundationProps:
    """Every simready_usd prop must PASS the Prop-Robotics-Neutral profile."""

    engine = ValidationEngine()

    @pytest.mark.parametrize("sample", PROP_SAMPLES, ids=lambda p: Path(p).stem)
    def test_prop_simready_usd(self, sample: str):
        if _is_lfs_pointer(sample):
            pytest.skip("LFS pointer not resolved")
        report = self.engine.validate_file(sample, SimReadyFoundations)
        failing = [r for r in report.results if not r.passed]
        details = "\n".join(
            f"  [{r.requirement_code}] {r.rule_name}: {[str(i) for i in r.issues]}"
            for r in failing
        )
        assert report.passed, f"{Path(sample).name} failed:\n{details}"

    @pytest.mark.parametrize("sample", PHYSX_SAMPLES, ids=lambda p: Path(p).stem)
    def test_prop_simready_physx_usd(self, sample: str):
        if _is_lfs_pointer(sample):
            pytest.skip("LFS pointer not resolved")
        report = self.engine.validate_file(sample, SimReadyFoundations)
        failing = [r for r in report.results if not r.passed]
        details = "\n".join(
            f"  [{r.requirement_code}] {r.rule_name}: {[str(i) for i in r.issues]}"
            for r in failing
        )
        assert report.passed, f"{Path(sample).name} failed:\n{details}"

    def test_batch_all_props_pass(self):
        """All prop samples pass as a batch."""
        reports = []
        for sample in PROP_SAMPLES:
            if _is_lfs_pointer(sample):
                continue
            reports.append(self.engine.validate_file(sample, SimReadyFoundations))
        assert len(reports) > 0, "No samples available"
        failed = [r for r in reports if not r.passed]
        assert len(failed) == 0, f"{len(failed)}/{len(reports)} failed"
