#!/bin/bash
set -e

echo "=== SR Asset Validator Setup ==="

# Install miniforge if conda not found
if ! command -v conda &> /dev/null; then
    if [ ! -f "$HOME/miniforge3/bin/conda" ]; then
        echo "Installing Miniforge..."
        ARCH=$(uname -m)
        OS=$(uname -s)
        wget -q "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-${OS}-${ARCH}.sh" -O /tmp/miniforge.sh
        bash /tmp/miniforge.sh -b -p "$HOME/miniforge3"
        rm /tmp/miniforge.sh
    fi
    export PATH="$HOME/miniforge3/bin:$PATH"
fi

# Create conda environment
echo "Creating conda environment 'sr_validator'..."
conda create -n sr_validator python=3.12 openusd pytest git-lfs -c conda-forge -y

echo ""
echo "=== Cloning SimReady Foundation ==="
if [ ! -d "simready-foundation" ]; then
    git clone https://github.com/nvidia/simready-foundation.git
fi

# Pull LFS files for sample content
echo "Pulling LFS assets..."
source "$(conda info --base)/bin/activate" sr_validator
cd simready-foundation
git lfs install
git lfs pull
cd ..

echo ""
echo "=== Setup Complete ==="
echo "To run:"
echo "  source \$(conda info --base)/bin/activate sr_validator"
echo "  ./run_sample.sh"
echo "  python -m pytest tests/ -v"
