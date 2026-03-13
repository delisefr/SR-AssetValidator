@echo off
echo === SR Asset Validator Setup ===

if not exist "simready-foundation" (
    echo Cloning SimReady Foundation...
    git clone https://github.com/nvidia/simready-foundation.git
)

echo Installing dependencies...
pip install usd-core pytest
if %errorlevel% neq 0 (
    pip3 install usd-core pytest
)

echo Pulling LFS assets...
cd simready-foundation
git lfs install
git lfs pull
cd ..

echo.
echo === Setup Complete ===
echo Run:  python -m sr_asset_validator.cli --list-rules
echo Test: python -m pytest tests/ -v
pause
