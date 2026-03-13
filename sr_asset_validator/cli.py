"""CLI entry point for sr-validate."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core.engine import ValidationEngine
from .core.registry import RuleRegistry
from .specs.simready_foundations import PROFILES, SimReadyFoundations
from .report import format_console, format_json, format_batch_summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sr-validate",
        description="Validate USD assets against SimReady Foundation specifications (no Kit required).",
    )
    parser.add_argument(
        "paths", nargs="*",
        help="USD file(s) or directory to validate.",
    )
    parser.add_argument(
        "--profile",
        default="Prop-Robotics-Neutral-v1",
        help=f"Profile name. Available: {', '.join(PROFILES.keys())}",
    )
    parser.add_argument(
        "--format", choices=["console", "json"], default="console",
        dest="output_format",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--list-rules", action="store_true")
    parser.add_argument("--list-profiles", action="store_true")

    args = parser.parse_args(argv)
    RuleRegistry.discover()

    if args.list_profiles:
        for name, spec in PROFILES.items():
            codes = spec.requirement_codes()
            print(f"  {name}: {len(codes)} requirements, {len(spec.rules)} implemented rules")
        return 0

    if args.list_rules:
        for code, cls in sorted(RuleRegistry.all_by_code().items()):
            print(f"  [{code}] {cls.rule_name()}: {cls.description}")
        return 0

    if not args.paths:
        parser.print_help()
        return 1

    spec = PROFILES.get(args.profile, SimReadyFoundations)
    engine = ValidationEngine()
    reports = []

    for path_str in args.paths:
        p = Path(path_str)
        if p.is_dir():
            reports.extend(engine.validate_directory(str(p), spec))
        elif p.is_file():
            reports.append(engine.validate_file(str(p), spec))
        else:
            print(f"Path not found: {path_str}", file=sys.stderr)
            return 1

    if not reports:
        print("No USD files found.", file=sys.stderr)
        return 1

    for report in reports:
        if args.output_format == "json":
            print(format_json(report))
        else:
            print(format_console(report, verbose=args.verbose))
            print()

    if len(reports) > 1:
        print(format_batch_summary(reports))

    return 0 if all(r.passed for r in reports) else 1


if __name__ == "__main__":
    sys.exit(main())
