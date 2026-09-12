from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

CONTRACT = "OUTCOME_CENSOR_REASON_SUMMARY_v1"
OUTCOME_CONTRACT = "MATURED_OUTCOME_v3"

DELIBERATE_LEGACY_QUARANTINE = frozenset({
    "LEGACY_V1_TARGET_UNIT_AMBIGUOUS",
})
EVIDENCE_AVAILABILITY = frozenset({
    "NO_EXACT_TARGET_TIME_EVIDENCE_WITHIN_PUBLICATION_GRACE",
    "NO_EVIDENCE_WITHIN_MAX_LAG",
})
PROVENANCE_RESOLVER = frozenset({
    "METRIC_UNAVAILABLE",
    "EVIDENCE_NAMESPACE_UNAVAILABLE",
    "METRIC_PATH_ROOT_AMBIGUOUS",
    "METRIC_PATH_ROOT_UNDECLARED",
})


def classify_reason(reason: str) -> str:
    if reason in DELIBERATE_LEGACY_QUARANTINE:
        return "DELIBERATE_LEGACY_QUARANTINE"
    if reason in EVIDENCE_AVAILABILITY:
        return "EVIDENCE_AVAILABILITY"
    if reason in PROVENANCE_RESOLVER:
        return "PROVENANCE_OR_RESOLVER"
    return "UNCLASSIFIED_FAIL_CLOSED"


def build_summary(outcome_root: Path) -> dict[str, Any]:
    reason_counts: Counter[str] = Counter()
    class_counts: Counter[str] = Counter()
    total_outcomes = 0
    censored_outcomes = 0
    skipped_non_outcome_json = 0

    for path in sorted(outcome_root.rglob("*.json")) if outcome_root.exists() else []:
        value = json.loads(path.read_text())
        if value.get("contract") != OUTCOME_CONTRACT:
            skipped_non_outcome_json += 1
            continue
        total_outcomes += 1
        if value.get("status") != "CENSORED":
            continue
        censored_outcomes += 1
        reason = value.get("reason")
        if not isinstance(reason, str) or not reason:
            reason = "MISSING_REASON"
        reason_counts[reason] += 1
        class_counts[classify_reason(reason)] += 1

    return {
        "contract": CONTRACT,
        "authority": {
            "read_only": True,
            "outcome_status_change": False,
            "retrospective_uncensoring": False,
            "model_weight_change": False,
            "portfolio_action": False,
        },
        "total_outcomes": total_outcomes,
        "censored_outcomes": censored_outcomes,
        "reason_counts": dict(sorted(reason_counts.items())),
        "reason_class_counts": dict(sorted(class_counts.items())),
        "skipped_non_outcome_json": skipped_non_outcome_json,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outcome-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    summary = build_summary(args.outcome_root)
    payload = json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload)
    print(payload, end="")


if __name__ == "__main__":
    main()
