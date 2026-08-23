#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List

ROOT = Path(__file__).resolve().parents[2]

ALLOWED_EXACT = {
    "06_RESEARCH_LAB/protocols/SHADOW_IDEA_ADMISSION_RULE_v1.md",
    "06_RESEARCH_LAB/protocols/SHADOW_IDEA_ADMISSION_TEMPLATE_v1.json",
    ".github/workflows/buildwithclaude-shadow-round1.yml",
    "scripts/research/validate_buildwithclaude_shadow_round1.py",
}

ALLOWED_PREFIXES = (
    "06_RESEARCH_LAB/buildwithclaude_shadow_round1_v1/",
    "scripts/research/shadow_",
)

PROTECTED_PREFIXES = (
    "00_FMOS/",
    "01_CORE_FRAMEWORK/",
    "02_DATA_PING/",
    "03_DAILY_CAPTURE_LOGS/",
    "03_WEEKLY_OPERATIONS/",
    "04_MARKET_LEARNING/",
    "05_CYCLE_NAVIGATOR/",
    "06_WEEKLY/",
)

PROTECTED_WORKFLOW_PREFIX = ".github/workflows/"


def is_allowed_path(path: str) -> bool:
    return path in ALLOWED_EXACT or any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES)


def classify_path(path: str) -> str:
    if is_allowed_path(path):
        return "ALLOWED_SHADOW"
    if any(path.startswith(prefix) for prefix in PROTECTED_PREFIXES):
        return "PROTECTED"
    if path.startswith(PROTECTED_WORKFLOW_PREFIX):
        return "PROTECTED_WORKFLOW"
    return "OUTSIDE_ADMISSION_SCOPE"


def _run_git(args: List[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=ROOT, text=True, capture_output=True, check=False
    )


def changed_paths(base_ref: str) -> List[str]:
    proc = _run_git(["diff", "--name-only", f"{base_ref}...HEAD"])
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git diff failed")
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def dirty_paths() -> List[str]:
    proc = _run_git(["status", "--porcelain"])
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git status failed")
    out: List[str] = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        raw = line[3:].strip()
        if " -> " in raw:
            raw = raw.split(" -> ", 1)[1]
        out.append(raw)
    return out


def evaluate_paths(paths: Iterable[str]) -> Dict[str, Any]:
    classified = [{"path": path, "class": classify_path(path)} for path in sorted(set(paths))]
    blocked = [row for row in classified if row["class"] != "ALLOWED_SHADOW"]
    return {
        "contract": "SHADOW_GUARDRAIL_PATH_EVALUATION_v1",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "canonical_effect": False,
        "portfolio_execution": False,
        "classified": classified,
        "blocked": blocked,
        "status": "PASS" if not blocked else "BLOCK",
    }


def self_test() -> Dict[str, Any]:
    allowed = [
        "06_RESEARCH_LAB/buildwithclaude_shadow_round1_v1/ROUND_CONTRACT.md",
        "scripts/research/shadow_property_invariant_probe.py",
        ".github/workflows/buildwithclaude-shadow-round1.yml",
    ]
    blocked = [
        "01_CORE_FRAMEWORK/state.json",
        "02_DATA_PING/schema.json",
        ".github/workflows/automation-production-health.yml",
        "scripts/live_market_writer.py",
    ]
    allowed_result = evaluate_paths(allowed)
    blocked_result = evaluate_paths(blocked)
    classes = {row["path"]: row["class"] for row in blocked_result["classified"]}
    checks = {
        "allowed_shadow_paths_pass": allowed_result["status"] == "PASS",
        "protected_paths_block": blocked_result["status"] == "BLOCK",
        "core_classified_protected": classes.get("01_CORE_FRAMEWORK/state.json") == "PROTECTED",
        "data_ping_classified_protected": classes.get("02_DATA_PING/schema.json") == "PROTECTED",
        "production_workflow_classified_protected": classes.get(".github/workflows/automation-production-health.yml") == "PROTECTED_WORKFLOW",
        "unscoped_script_blocked": classes.get("scripts/live_market_writer.py") == "OUTSIDE_ADMISSION_SCOPE",
    }
    return {
        "contract": "SHADOW_GUARDRAIL_SELF_TEST_v1",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "canonical_effect": False,
        "portfolio_execution": False,
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }


def _write(report: Dict[str, Any], output: str | None) -> None:
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if output:
        Path(output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["pre", "post", "self-test"], required=True)
    parser.add_argument("--base-ref", default="origin/main")
    parser.add_argument("--output")
    args = parser.parse_args()

    if args.mode == "self-test":
        report = self_test()
        _write(report, args.output)
        return 0 if report["status"] == "PASS" else 1

    if args.mode == "pre":
        try:
            paths = changed_paths(args.base_ref)
            evaluation = evaluate_paths(paths)
            report = {
                **evaluation,
                "mode": "PRE_FLIGHT",
                "base_ref": args.base_ref,
                "changed_path_count": len(paths),
            }
        except Exception as exc:
            report = {
                "contract": "SHADOW_GUARDRAIL_PRE_FLIGHT_v1",
                "authority": "RESEARCH_ONLY_NON_CANONICAL",
                "canonical_effect": False,
                "portfolio_execution": False,
                "mode": "PRE_FLIGHT",
                "base_ref": args.base_ref,
                "status": "BLOCK",
                "error": str(exc),
            }
        _write(report, args.output)
        return 0 if report["status"] == "PASS" else 2

    try:
        dirty = dirty_paths()
        report = {
            "contract": "SHADOW_GUARDRAIL_POST_FLIGHT_v1",
            "authority": "RESEARCH_ONLY_NON_CANONICAL",
            "canonical_effect": False,
            "portfolio_execution": False,
            "mode": "POST_FLIGHT",
            "dirty_paths": sorted(dirty),
            "status": "PASS" if not dirty else "BLOCK",
        }
    except Exception as exc:
        report = {
            "contract": "SHADOW_GUARDRAIL_POST_FLIGHT_v1",
            "authority": "RESEARCH_ONLY_NON_CANONICAL",
            "canonical_effect": False,
            "portfolio_execution": False,
            "mode": "POST_FLIGHT",
            "status": "BLOCK",
            "error": str(exc),
        }
    _write(report, args.output)
    return 0 if report["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
