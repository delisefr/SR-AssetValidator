#!/bin/bash
set -e

echo "=== SR Asset Validator Setup ==="

ARCH=$(uname -m)

# Clone simready-foundation if not present
if [ ! -d "simready-foundation" ]; then
    echo "Cloning SimReady Foundation..."
    git clone https://github.com/nvidia/simready-foundation.git
fi

# Try pip first (works on x86_64)
if pip install usd-core pytest 2>/dev/null; then
    echo "Installed via pip."
elif pip3 install usd-core pytest 2>/dev/null; then
    echo "Installed via pip3."
else
    # Fallback to conda for aarch64 / ARM64
    echo "pip install failed (likely $ARCH — no usd-core wheel)."
    echo "Falling back to conda..."

    if ! command -v conda &> /dev/null; then
        if [ ! -f "$HOME/miniforge3/bin/conda" ]; then
            OS=$(uname -s)
            echo "Installing Miniforge for $OS-$ARCH..."
            wget -q "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-${OS}-${ARCH}.sh" -O /tmp/miniforge.sh
            bash /tmp/miniforge.sh -b -p "$HOME/miniforge3"
            rm /tmp/miniforge.sh
        fi
        export PATH="$HOME/miniforge3/bin:$PATH"
    fi

    conda create -n sr_validator python=3.12 openusd pytest git-lfs -c conda-forge -y
    echo ""
    echo "Activate with: source \$(conda info --base)/bin/activate sr_validator"
fi

# Pull LFS files for sample content
echo "Pulling LFS assets..."
cd simready-foundation
git lfs install 2>/dev/null || true
git lfs pull 2>/dev/null || echo "git-lfs not available — sample USD files will be LFS pointers"
cd ..

echo ""
echo "=== Setup Complete ==="
echo "Run:  python -m sr_asset_validator.cli --list-rules"
echo "Test: python -m pytest tests/ -v"
