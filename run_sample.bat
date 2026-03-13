@echo off
call conda activate sr_validator
cd /d "%~dp0"

echo === Validating apple_a01 (simready_usd) ===
python -m sr_asset_validator.cli ^
  simready-foundation\sample_content\common_assets\props_general\apple_a01\simready_usd\sm_apple_a01_01.usd -v

echo.
echo === Validating apple_a01 (simready_physx_usd) ===
python -m sr_asset_validator.cli ^
  simready-foundation\sample_content\common_assets\props_general\apple_a01\simready_physx_usd\sm_apple_a01_01.usd -v

echo.
echo === Validating all props ===
python -m sr_asset_validator.cli ^
  simready-foundation\sample_content\common_assets\props_general\*\simready_usd\*.usd

pause
