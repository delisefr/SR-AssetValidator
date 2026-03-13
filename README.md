# SR Asset Validator

Lightweight USD asset validator for [NVIDIA SimReady Foundation](https://github.com/nvidia/simready-foundation) specifications. No Kit or Carbonite required.

## What It Does

Validates OpenUSD assets against official SimReady Foundation profiles by loading specs, capabilities, features, and requirement codes directly from the `nvidia/simready-foundation` repository configs.

- **30 rule implementations** mapped to official requirement codes (HI.\*, UN.\*, VG.\*, VM.\*, RB.\*)
- **3 profiles**: Prop-Robotics-Neutral v1/v2, Prop-Robotics-Physx v1
- **Only dependency**: `usd-core` (pip) — falls back to `openusd` (conda-forge) on aarch64

## Prerequisites

- Python 3.10+
- [Git LFS](https://git-lfs.com/) (for pulling sample USD assets)

## Setup

### Windows

```cmd
git clone https://github.com/delisefr/SR-AssetValidator.git
cd SR-AssetValidator
setup.bat
```

This will:
1. Clone `nvidia/simready-foundation` for specs and sample assets
2. Install `usd-core` and `pytest` via pip
3. Pull LFS assets

### Linux / macOS

```bash
git clone https://github.com/delisefr/SR-AssetValidator.git
cd SR-AssetValidator
./setup.sh
```

This will:
1. Clone `nvidia/simready-foundation` for specs and sample assets
2. Install `usd-core` and `pytest` via pip
3. If pip fails (aarch64/ARM64 — no wheels available), falls back to conda via [Miniforge](https://github.com/conda-forge/miniforge)
4. Pull LFS assets

> **Note (aarch64 only):** If the setup falls back to conda, activate the environment before running:
> ```bash
> source $(conda info --base)/bin/activate sr_validator
> ```

### Manual Setup

```bash
pip install usd-core pytest
git clone https://github.com/nvidia/simready-foundation.git
cd simready-foundation && git lfs pull && cd ..
```

## Usage

### Windows

```cmd
:: Validate a single asset
python -m sr_asset_validator.cli path\to\asset.usd -v

:: Run the sample script
run_sample.bat

:: Run tests
python -m pytest tests\ -v
```

### Linux / macOS

```bash
# Validate a single asset
python -m sr_asset_validator.cli path/to/asset.usd -v

# Run the sample script
./run_sample.sh

# Run tests
python -m pytest tests/ -v
```

## CLI Reference

```
python -m sr_asset_validator.cli [options] <paths...>

Arguments:
  paths                 USD file(s) or directories to validate

Options:
  --profile NAME        Profile to validate against (default: Prop-Robotics-Neutral-v1)
  --format FORMAT       Output format: console or json
  -v, --verbose         Show all rules including passing ones
  --list-rules          List all implemented rules with requirement codes
  --list-profiles       List available profiles
```

### Examples

```bash
# Verbose output showing all rules
python -m sr_asset_validator.cli asset.usd -v

# Validate against the PhysX profile
python -m sr_asset_validator.cli asset.usd --profile Prop-Robotics-Physx-v1

# JSON output (for CI pipelines)
python -m sr_asset_validator.cli asset.usd --format json

# Validate an entire directory
python -m sr_asset_validator.cli ./my_assets/

# List all rules
python -m sr_asset_validator.cli --list-rules
```

## Profiles

| Profile | Requirements | Description |
|---------|-------------|-------------|
| Prop-Robotics-Neutral-v1 | 31 | Base props with neutral physics + MDL materials |
| Prop-Robotics-Neutral-v2 | 38 | Stricter geometry/hierarchy checks (Z-up, mesh-only, normals) |
| Prop-Robotics-Physx-v1 | 31 | Props with PhysX-specific physics |

## Implemented Rules

| Code | Rule | Category |
|------|------|----------|
| HI.001 | HierarchyHasRoot | hierarchy |
| HI.002 | ExclusiveXformParent | hierarchy |
| HI.003 | RootIsXformable | hierarchy |
| HI.004 | StageHasDefaultPrim | hierarchy |
| HI.005 | XformCommonApiUsage | hierarchy |
| HI.006 | PlaceableAreXformable | hierarchy |
| HI.010 | UndefinedPrimsCheck | hierarchy |
| UN.001 | UpAxisCheck | units |
| UN.002 | MetersPerUnitCheck | units |
| UN.006 | UpAxisZCheck | units |
| UN.007 | MetersPerUnit1Check | units |
| VG.001 | AtLeastOneGeometry | geometry |
| VG.002 | GeomExtentCheck | geometry |
| VG.007 | MeshManifoldCheck | geometry |
| VG.010 | SubdivisionCheck | geometry |
| VG.014 | MeshTopologyCheck | geometry |
| VG.019 | ZeroAreaFaceCheck | geometry |
| VG.025 | AssetOriginPositioning | geometry |
| VG.027 | MeshNormalsExist | geometry |
| VG.028 | MeshNormalsValid | geometry |
| VG.029 | MeshWindingOrder | geometry |
| VG.MESH.001 | GeomShallBeMesh | geometry |
| VM.MAT.001 | MaterialAssignment | material |
| VM.BIND.001 | MaterialBindScope | material |
| VM.BIND.002 | ShaderInputTypes | material |
| VM.PS.001 | MaterialPreviewSurface | material |
| VM.MDL.001 | MaterialMdlSourceAsset | material |
| VM.MDL.002 | MdlSchemaCheck | material |
| RB.001 | RigidBodyCapability | physics |
| RB.003 | RigidBodySchemaApplication | physics |
| RB.005 | RigidBodyNoInstancing | physics |
| RB.006 | RigidBodyNoNesting | physics |
| RB.007 | RigidBodyMass | physics |
| RB.009 | RigidBodyNoSkew | physics |
| RB.010 | InvisibleCollisionPurpose | physics |
| RB.COL.001 | ColliderCapability | physics |
| RB.COL.002 | MeshCollisionApiCheck | physics |
| RB.COL.003 | ColliderMeshOnly | physics |
| RB.COL.004 | ColliderNonUniformScale | physics |
| RB.MB.001 | MultiBodyCapability | physics |
| SL.001 | SemanticLabelExists | simready |

## Architecture

```
                          ┌─────────────────────────────────────────┐
                          │         nvidia/simready-foundation      │
                          │                                         │
                          │  config/*.json     docs/features/*.json │
                          │  (Capabilities)      (Features)         │
                          │  HI, UN, VG, VM,     FET000..FET100     │
                          │  RB, JT, DJ, BA      requirement lists  │
                          │                                         │
                          │  docs/profiles/profiles.toml            │
                          │  (Profiles)                             │
                          │  Prop-Robotics-Neutral v1/v2            │
                          │  Prop-Robotics-Physx v1                 │
                          └──────────────┬──────────────────────────┘
                                         │ loads at runtime
                                         ▼
┌──────────────┐    ┌─────────────────────────────────────────────────────┐
│              │    │              SR Asset Validator                     │
│  USD Asset   │    │                                                     │
│  (.usd/.usda │───▶│  ┌───────────┐    ┌──────────┐    ┌─────────────┐  │
│   /.usdc)    │    │  │ Stage     │    │ Spec     │    │ Rule        │  │
│              │    │  │ Loader    │    │ Loader   │    │ Registry    │  │
└──────────────┘    │  │           │    │          │    │             │  │
                    │  │ pxr.Usd   │    │ JSON ──▶ │    │ code ──▶   │  │
                    │  │ .Stage    │    │ Caps +   │    │ BaseRule    │  │
                    │  │ .Open()   │    │ Features │    │ subclass    │  │
                    │  └─────┬─────┘    └────┬─────┘    └──────┬──────┘  │
                    │        │               │                 │         │
                    │        ▼               ▼                 ▼         │
                    │  ┌─────────────────────────────────────────────┐   │
                    │  │           Validation Engine                 │   │
                    │  │                                             │   │
                    │  │  Profile ──▶ Features ──▶ Requirement Codes │   │
                    │  │                              │              │   │
                    │  │              ┌───────────────┘              │   │
                    │  │              ▼                              │   │
                    │  │  For each code with an implementation:     │   │
                    │  │    rule = Registry.get(code)               │   │
                    │  │    issues = rule.check(stage)              │   │
                    │  │                                             │   │
                    │  └──────────────────┬──────────────────────────┘   │
                    │                     │                              │
                    │                     ▼                              │
                    │  ┌─────────────────────────────────────────────┐   │
                    │  │           Validation Report                 │   │
                    │  │                                             │   │
                    │  │  [PASS] asset.usd (Prop-Robotics-Neutral)  │   │
                    │  │    Rules: 23  Errors: 0  Warnings: 1       │   │
                    │  │    [HI.004] StageHasDefaultPrim ✓          │   │
                    │  │    [VG.014] MeshTopologyCheck ✓            │   │
                    │  │    [RB.COL.001] ColliderCapability ✓       │   │
                    │  │    ...                                     │   │
                    │  └─────────────────────────────────────────────┘   │
                    └───────────────────────────────────────────────────┘

  Dependencies:  usd-core (pip) ──▶ pxr.Usd, pxr.UsdGeom,
                                     pxr.UsdShade, pxr.UsdPhysics
                 NO Kit, NO Carbonite, NO Omni USD Resolver
```

### File Structure

```
SR-AssetValidator/
├── setup.sh / setup.bat           # One-command setup (Linux/Windows)
├── run_sample.sh / run_sample.bat # Run validation on foundation samples
├── requirements.txt               # pip dependencies
├── pyproject.toml                 # Project config
├── sr_asset_validator/
│   ├── core/                      # Engine, BaseRule, Registry, Spec loader
│   │   ├── engine.py              # ValidationEngine + profile resolver
│   │   ├── registry.py            # Maps requirement codes to rule classes
│   │   ├── rule.py                # BaseRule ABC with requirement_code
│   │   ├── spec.py                # Loads capabilities/features from JSON
│   │   └── stage_loader.py        # USD stage loading via pxr
│   ├── rules/                     # Rule implementations by category
│   │   ├── basic/                 # HI.*, UN.* (hierarchy, units)
│   │   ├── geometry/              # VG.* (mesh topology, normals, extents)
│   │   ├── material/              # VM.* (bindings, shaders, MDL)
│   │   ├── physics/               # RB.* (rigid bodies, colliders)
│   │   ├── layout/                # HI.002, HI.006 (prim hierarchy)
│   │   └── simready/              # SL.* (semantic labels)
│   ├── specs/                     # Profile definitions
│   ├── cli.py                     # Command-line interface
│   └── report.py                  # Console + JSON formatters
├── tests/                         # Unit + integration tests
└── simready-foundation/           # Cloned at setup (git-ignored)
```

## Adding Rules

Create a new rule by subclassing `BaseRule` and registering it with a requirement code:

```python
from sr_asset_validator.core.registry import RuleRegistry
from sr_asset_validator.core.rule import BaseRule, Severity
from sr_asset_validator.core.result import Issue

@RuleRegistry.register
class MyNewRule(BaseRule):
    requirement_code = "XX.001"
    category = "my_category"
    description = "What this rule checks."
    severity = Severity.ERROR

    def check(self, stage):
        issues = []
        # validation logic using pxr
        return issues
```

The rule is automatically discovered and included in any profile that references its requirement code.

## License

Apache 2.0
