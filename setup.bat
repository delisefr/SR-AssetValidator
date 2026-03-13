@echo off
echo === SR Asset Validator Setup ===

where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: conda not found. Install Miniforge from:
    echo https://github.com/conda-forge/miniforge/releases/latest
    echo Then re-run this script.
    pause
    exit /b 1
)

echo Creating conda environment 'sr_validator'...
call conda create -n sr_validator python=3.12 openusd pytest git-lfs -c conda-forge -y

echo.
echo === Cloning SimReady Foundation ===
if not exist "simready-foundation" (
    git clone https://github.com/nvidia/simready-foundation.git
)

echo Pulling LFS assets...
call conda activate sr_validator
cd simready-foundation
git lfs install
git lfs pull
cd ..

echo.
echo === Setup Complete ===
echo To run:
echo   conda activate sr_validator
echo   run_sample.bat
echo   python -m pytest tests/ -v
pause
