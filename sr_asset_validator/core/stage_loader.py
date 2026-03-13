"""USD stage loading utilities."""

from __future__ import annotations

from pathlib import Path
from pxr import Usd, Sdf

USD_EXTENSIONS = {".usd", ".usda", ".usdc", ".usdz"}


def load_stage(path: str) -> Usd.Stage:
    """Open a USD stage from *path*.

    Uses Usd.Stage.Open with a non-editing session layer so we never
    modify the source file.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"USD file not found: {path}")
    if p.suffix.lower() not in USD_EXTENSIONS:
        raise ValueError(f"Not a USD file: {path}")

    stage = Usd.Stage.Open(str(p), Usd.Stage.LoadAll)
    if stage is None:
        raise RuntimeError(f"Failed to open USD stage: {path}")
    return stage


def discover_usd_files(directory: str) -> list[Path]:
    """Recursively find all USD files under *directory*."""
    root = Path(directory)
    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")
    files: list[Path] = []
    for ext in USD_EXTENSIONS:
        files.extend(root.rglob(f"*{ext}"))
    return sorted(set(files))
