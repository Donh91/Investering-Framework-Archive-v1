#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "research"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import research_governance_common as baseline_module  # noqa: E402
from shadow_property_invariant_probe import evaluate_module  # noqa: E402


MUTATIONS = [
    {
        "id": "M1_FIREWALL_TRUE_TO_FALSE",
        "old": 'if obj.get(k) is True:',
        "new": 'if obj.get(k) is False:',
    },
    {
        "id": "M2_AUTHORITY_PREDICATE_INVERTED",
        "old": 'if auth not in (None,"","RESEARCH_ONLY_NON_CANONICAL"):',
        "new": 'if auth in (None,"","RESEARCH_ONLY_NON_CANONICAL"):',
    },
    {
        "id": "M3_JACCARD_FORMULA_INVERTED",
        "old": 'return len(x & y) / len(x | y)',
        "new": 'return len(x | y) / max(1, len(x & y))',
    },
    {
        "id": "M4_DIGEST_SHA256_TO_MD5",
        "old": 'return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()',
        "new": 'return hashlib.md5(json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()',
    },
    {
        "id": "M5_APPEND_IDEMPOTENCY_INVERTED",
        "old": 'if id_value in existing:',
        "new": 'if id_value not in existing:',
    },
    {
        "id": "M6_PROPOSAL_CANONICAL_DEFAULT_TRUE",
        "old": 'bool(state.get("canonical_effect", False))',
        "new": 'bool(state.get("canonical_effect", True))',
    },
    {
        "id": "M7_NORMALIZE_DOUBLE_SPACING",
        "old": 'return " ".join(s.split())',
        "new": 'return "  ".join(s.split())',
    },
]


def _load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot create module spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=int, default=250)
    parser.add_argument("--seed", type=int, default=20260823)
    parser.add_argument("--output")
    args = parser.parse_args()

    source_path = SCRIPTS / "research_governance_common.py"
    source = source_path.read_text(encoding="utf-8")

    baseline = evaluate_module(baseline_module, cases=args.cases, seed=args.seed)
    report = {
        "contract": "SHADOW_MUTATION_PROBE_v1",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "canonical_effect": False,
        "portfolio_execution": False,
        "source_path": str(source_path.relative_to(ROOT)),
        "baseline_status": baseline["status"],
        "mutations": [],
        "patterns_missing": [],
    }

    if baseline["status"] != "PASS":
        report["status"] = "HARNESS_BLOCKED_BASELINE_FAILED"
        report["candidate_quality"] = "UNASSESSABLE"
        text = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.output:
            Path(args.output).write_text(text, encoding="utf-8")
        else:
            print(text, end="")
        return 1

    killed = 0
    with tempfile.TemporaryDirectory(prefix="shadow-mutation-") as td:
        tmp = Path(td)
        for index, mutation in enumerate(MUTATIONS):
            old = mutation["old"]
            new = mutation["new"]
            occurrences = source.count(old)
            if occurrences != 1:
                report["patterns_missing"].append(
                    {"id": mutation["id"], "expected_occurrences": 1, "actual_occurrences": occurrences}
                )
                continue

            mutated_source = source.replace(old, new, 1)
            mutant_path = tmp / f"mutant_{index}.py"
            mutant_path.write_text(mutated_source, encoding="utf-8")
            mutant = _load_module(mutant_path, f"shadow_mutant_{index}")
            result = evaluate_module(mutant, cases=args.cases, seed=args.seed)
            is_killed = result["status"] != "PASS"
            killed += int(is_killed)
            report["mutations"].append(
                {
                    "id": mutation["id"],
                    "killed": is_killed,
                    "failure_count": result["failure_count"],
                    "failure_samples": result["failure_samples"][:3],
                }
            )

    executed = len(report["mutations"])
    report["executed_mutations"] = executed
    report["killed_mutations"] = killed
    report["kill_rate"] = round(killed / executed, 4) if executed else 0.0

    if report["patterns_missing"]:
        report["status"] = "HARNESS_STALE_PATTERN_MISSING"
        report["candidate_quality"] = "UNASSESSABLE"
        exit_code = 1
    else:
        report["status"] = "PASS"
        report["candidate_quality"] = (
            "CONTINUE_SHADOW" if report["kill_rate"] >= 0.80 else "COVERAGE_GAP"
        )
        exit_code = 0

    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
