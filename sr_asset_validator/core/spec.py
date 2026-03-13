"""Specification — capabilities, features, profiles loaded from simready-foundation configs."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Requirement:
    code: str
    name: str
    compatibility: str
    tags: str
    message: str
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class Capability:
    id: str
    version: str
    name: str
    description: str
    requirements: list[Requirement] = field(default_factory=list)


@dataclass
class Feature:
    id: str
    version: str
    name: str
    requirement_codes: list[str] = field(default_factory=list)
    dependencies: list[tuple[str, str]] = field(default_factory=list)  # (feature_id, version)


@dataclass
class Profile:
    name: str
    version: str
    features: list[tuple[str, str]] = field(default_factory=list)  # (feature_id, version)


@dataclass
class Specification:
    """A resolved profile with all requirements expanded."""
    name: str
    description: str = ""
    requirements: list[Requirement] = field(default_factory=list)
    rules: list[Any] = field(default_factory=list)  # BaseRule subclasses

    def requirement_codes(self) -> set[str]:
        return {r.code for r in self.requirements}

    def rule_names(self) -> list[str]:
        return [r.rule_name() for r in self.rules]


def load_capability(path: str | Path) -> Capability:
    """Load a capability from a JSON config file."""
    with open(path) as f:
        data = json.load(f)
    cap = data["capability"]
    reqs = [
        Requirement(
            code=r["code"],
            name=r["name"],
            compatibility=r.get("compatibility", ""),
            tags=r.get("tags", ""),
            message=r.get("message", ""),
            metadata=r.get("metadata", {}),
        )
        for r in cap.get("requirements", [])
    ]
    return Capability(
        id=cap["id"],
        version=cap.get("version", "0.1.0"),
        name=cap.get("name", cap["id"]),
        description=cap.get("description", ""),
        requirements=reqs,
    )


def load_all_capabilities(config_dir: str | Path) -> dict[str, Capability]:
    """Load all capability JSON files from a config directory."""
    config_dir = Path(config_dir)
    caps: dict[str, Capability] = {}
    for f in config_dir.glob("*.json"):
        try:
            cap = load_capability(f)
            caps[cap.id] = cap
        except (json.JSONDecodeError, KeyError):
            continue
    return caps


def load_feature(path: str | Path) -> Feature:
    """Load a feature from a JSON file."""
    with open(path) as f:
        data = json.load(f)
    feat = data.get("feature", data)
    raw_reqs = feat.get("requirements", [])
    req_codes = []
    for r in raw_reqs:
        if isinstance(r, str):
            req_codes.append(r)
        elif isinstance(r, dict):
            req_codes.append(r.get("code", ""))
    deps = []
    for dep in feat.get("dependencies", []):
        if isinstance(dep, dict):
            for k, v in dep.items():
                deps.append((k, v.get("version", "0.1.0") if isinstance(v, dict) else v))
        elif isinstance(dep, str):
            deps.append((dep, "0.1.0"))
    return Feature(
        id=feat.get("id", ""),
        version=feat.get("version", "0.1.0"),
        name=feat.get("name", feat.get("display_name", "")),
        requirement_codes=req_codes,
        dependencies=deps,
    )


def load_all_features(features_dir: str | Path) -> dict[tuple[str, str], Feature]:
    """Load all feature JSON files. Keyed by (id, version)."""
    features_dir = Path(features_dir)
    feats: dict[tuple[str, str], Feature] = {}
    for f in features_dir.glob("*.json"):
        try:
            feat = load_feature(f)
            feats[(feat.id, feat.version)] = feat
        except (json.JSONDecodeError, KeyError):
            continue
    return feats
