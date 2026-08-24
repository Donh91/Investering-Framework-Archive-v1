#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def candidate_action(row: dict[str, Any], admission: dict[str, Any] | None) -> dict[str, Any]:
    admission_status = (admission or {}).get("status") or row.get("scientific_admission_status") or "UNAVAILABLE"
    state = str(row.get("state") or "UNKNOWN")
    if admission_status == "SEMANTIC_DUPLICATE_KEEP_SHADOW":
        action, reason = "ARCHIVE_ONLY_DUPLICATE", "semantic duplicate, preserve history but do not spend new prospective execution"
    elif admission_status in {"TARGET_UNIT_QUARANTINED", "BLOCKED_INVALID_TARGET", "KEEP_SHADOW_INSUFFICIENT_COMBINATION"}:
        action, reason = "KEEP_QUARANTINED", "scientific admission did not permit forward execution"
    elif admission_status == "WAITING_FOR_MAPPING" or state == "WAITING_FOR_MAPPING":
        action, reason = "WAIT_FOR_MAPPING", "candidate is not machine-mappable yet"
    elif state in {"WAITING_FOR_DATA", "PROPOSED", "INCUBATING", "FIRED_NO_TARGET", "WAITING_FOR_MATURITY"}:
        action, reason = "WAIT_FOR_MORE_PROSPECTIVE_EVIDENCE", "insufficient mature prospective evidence for lifecycle escalation"
    elif state == "MATURED_SUPPORTED":
        action, reason = "RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW", "supportive outcome exists, but promotion still requires baseline, controls, regime and complexity review"
    elif state == "MATURED_NOT_SUPPORTED":
        action, reason = "RUN_FAILURE_AND_RETIREMENT_REVIEW", "negative prospective evidence exists, retirement requires evidence-aware review rather than age expiry"
    elif state == "MATURED_INCONCLUSIVE":
        action, reason = "KEEP_SHADOW_INCONCLUSIVE", "matured evidence is inconclusive"
    elif state == "TARGET_UNIT_QUARANTINED":
        action, reason = "KEEP_QUARANTINED", "legacy target-unit ambiguity"
    else:
        action, reason = "CONTINUE_OBSERVING", "no stronger lifecycle transition is justified"
    return {
        "candidate_id": row.get("candidate_id"),
        "title": row.get("title"),
        "kind": row.get("kind"),
        "lifecycle_state": state,
        "scientific_admission_status": admission_status,
        "matured_outcome_count": row.get("matured_outcome_count", 0),
        "replication_receipts": row.get("replication_receipts", []),
        "selected_action": action,
        "reason": reason,
        "canonical_effect": False,
        "portfolio_execution": False,
    }


def build(lifecycle: dict[str, Any], admissions: dict[str, Any], shadow: dict[str, Any], tournament: dict[str, Any], generated_at: str) -> dict[str, Any]:
    admission_map = {row.get("candidate_id"): row for row in admissions.get("candidates", []) if isinstance(row, dict)}
    actions = [candidate_action(row, admission_map.get(row.get("candidate_id"))) for row in lifecycle.get("candidates", []) if isinstance(row, dict)]
    counts: dict[str, int] = {}
    for row in actions:
        counts[row["selected_action"]] = counts.get(row["selected_action"], 0) + 1
    escalations = [row for row in actions if row["selected_action"] in {"RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW", "RUN_FAILURE_AND_RETIREMENT_REVIEW"}]
    return {
        "contract": "UNIFIED_EXPERIMENTAL_LIFECYCLE_ADJUDICATION_v1",
        "generated_at_utc": generated_at,
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "canonical_effect": False,
        "portfolio_execution": False,
        "automatic_threshold_change": False,
        "automatic_weight_change": False,
        "automatic_market_rule_change": False,
        "inputs": {
            "experiment_lifecycle_contract": lifecycle.get("contract"),
            "scientific_admission_contract": admissions.get("contract"),
            "shadow_registry_contract": shadow.get("contract") if isinstance(shadow, dict) else None,
            "shared_row_tournament_contract": tournament.get("contract") if isinstance(tournament, dict) else None,
        },
        "summary": {
            "candidate_count": len(actions),
            "action_counts": counts,
            "escalation_review_count": len(escalations),
            "shadow_registry_available": bool(shadow and shadow.get("contract")),
            "shared_row_tournament_available": bool(tournament and tournament.get("contract")),
        },
        "candidate_actions": actions,
        "escalation_queue": escalations,
        "shadow_registry_snapshot": {"week": shadow.get("week") if isinstance(shadow, dict) else None, "summary": shadow.get("summary") if isinstance(shadow, dict) else None},
        "shared_row_tournament_snapshot": {"status": tournament.get("status") if isinstance(tournament, dict) else None, "relevance_state": tournament.get("relevance_state") if isinstance(tournament, dict) else None},
        "decision_rule": "Qualification and lifecycle escalation are separate. Supportive outcomes trigger incremental-value and adversarial review, not automatic promotion. Negative outcomes trigger failure/retirement review, not age-based deletion.",
        "method_reference": "06_RESEARCH_LAB/protocols/README.md",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lifecycle-registry", type=Path, required=True)
    ap.add_argument("--admission-registry", type=Path, required=True)
    ap.add_argument("--shadow-registry", type=Path, required=True)
    ap.add_argument("--shared-row-latest", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    lifecycle = read_json(args.lifecycle_registry, {})
    admissions = read_json(args.admission_registry, {})
    if lifecycle.get("contract") != "EXPERIMENT_LIFECYCLE_REGISTRY_v1":
        raise SystemExit("invalid experiment lifecycle registry")
    if admissions.get("contract") != "EXPERIMENT_SCIENTIFIC_ADMISSION_REGISTRY_v1":
        raise SystemExit("invalid scientific admission registry")
    shadow = read_json(args.shadow_registry, {})
    tournament = read_json(args.shared_row_latest, {})
    out = build(lifecycle, admissions, shadow, tournament, datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
