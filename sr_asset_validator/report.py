"""Report formatting for validation results."""

from __future__ import annotations

import json
from pathlib import Path

from .core.result import ValidationReport, Severity


def format_console(report: ValidationReport, verbose: bool = False) -> str:
    lines: list[str] = []
    status = "\033[92mPASS\033[0m" if report.passed else "\033[91mFAIL\033[0m"
    name = Path(report.file_path).name
    lines.append(f"[{status}] {name}  ({report.spec_name})")
    lines.append(
        f"  Rules: {len(report.results)}  "
        f"Errors: {report.error_count}  "
        f"Warnings: {report.warning_count}"
    )
    if verbose or not report.passed:
        for result in report.results:
            if result.passed and not verbose:
                continue
            mark = "\033[92m✓\033[0m" if result.passed else "\033[91m✗\033[0m"
            code = f" [{result.requirement_code}]" if result.requirement_code else ""
            lines.append(f"  {mark}{code} {result.rule_name}")
            for issue in result.issues:
                sev_color = {
                    Severity.ERROR: "\033[91m",
                    Severity.WARNING: "\033[93m",
                    Severity.INFO: "\033[94m",
                }.get(issue.severity, "")
                loc = f" @ {issue.prim_path}" if issue.prim_path else ""
                lines.append(f"    {sev_color}{issue.severity.name}\033[0m{loc}: {issue.message}")
    return "\n".join(lines)


def format_json(report: ValidationReport) -> str:
    data = {
        "file": report.file_path,
        "spec": report.spec_name,
        "passed": report.passed,
        "errors": report.error_count,
        "warnings": report.warning_count,
        "results": [
            {
                "rule": r.rule_name,
                "requirement_code": r.requirement_code,
                "passed": r.passed,
                "issues": [
                    {
                        "severity": i.severity.name,
                        "message": i.message,
                        "prim_path": i.prim_path,
                        "requirement_code": i.requirement_code,
                    }
                    for i in r.issues
                ],
            }
            for r in report.results
        ],
    }
    return json.dumps(data, indent=2)


def format_batch_summary(reports: list[ValidationReport]) -> str:
    total = len(reports)
    passed = sum(1 for r in reports if r.passed)
    failed = total - passed
    return (
        f"\n{'='*60}\n"
        f"Batch Summary: {total} files validated\n"
        f"  \033[92mPassed: {passed}\033[0m  \033[91mFailed: {failed}\033[0m\n"
        f"{'='*60}"
    )
