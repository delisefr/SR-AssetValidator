#!/bin/bash
cd "$(dirname "$0")"

# Activate conda env if pxr not available in current env
python -c "from pxr import Usd" 2>/dev/null || {
    source "$HOME/miniforge3/bin/activate" sr_validator 2>/dev/null || {
        echo "Error: pxr (OpenUSD) not found. Run ./setup.sh first."
        exit 1
    }
}

echo "=== Validating apple_a01 (simready_usd) ==="
python -m sr_asset_validator.cli \
  simready-foundation/sample_content/common_assets/props_general/apple_a01/simready_usd/sm_apple_a01_01.usd -v

echo ""
echo "=== Validating apple_a01 (simready_physx_usd) ==="
python -m sr_asset_validator.cli \
  simready-foundation/sample_content/common_assets/props_general/apple_a01/simready_physx_usd/sm_apple_a01_01.usd -v

echo ""
echo "=== Validating all props ==="
python -m sr_asset_validator.cli \
  simready-foundation/sample_content/common_assets/props_general/*/simready_usd/*.usd
