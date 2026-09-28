from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONTRACT = "EXPERIMENT_YIELD_SHADOW_v1"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError("INVALID_JSON_OBJECT")
    return value


def classify(row: dict[str, Any], consumer_rows: dict[str, dict[str, Any]]) -> tuple[str, list[str]]:
    reasons: list[str] = []
    state = str(row.get("state") or row.get("status") or "")
    if state in {"BLOCKED", "WAITING_FOR_DATA", "WAITING_FOR_MAPPING", "TARGET_UNIT_QUARANTINED"}:
        reasons.append("BLOCKED_OR_WAITING")
    duplicate_of = row.get("duplicate_of") or row.get("superseded_by") or row.get("duplicate_group_id")
    if duplicate_of:
        reasons.append("DUPLICATE_OR_SUPERSEDED")
    outputs = row.get("output_artifacts") if isinstance(row.get("output_artifacts"), list) else []
    if outputs and all(
        consumer_rows.get(str(name), {}).get("use_state") == "NO_REGISTERED_CONSUMER"
        for name in outputs
        if str(name) in consumer_rows
    ) and any(str(name) in consumer_rows for name in outputs):
        reasons.append("NO_REGISTERED_CONSUMER")
    observations = row.get("observation_count")
    if isinstance(observations, int) and observations == 0 and state in {"MATURED_INCONCLUSIVE", "MATURED_NOT_SUPPORTED"}:
        reasons.append("LOW_OBSERVED_YIELD")
    return ("OBSERVE" if reasons else "SHADOW_BASELINE"), reasons


def build_shadow(registry: dict[str, Any], consumer_index: dict[str, Any]) -> dict[str, Any]:
    source_field = next((key for key in ("candidates", "rows", "experiments", "items") if key in registry), None)
    raw_rows = registry.get(source_field) if source_field is not None else []
    if not isinstance(raw_rows, list):
        raw_rows = []
    malformed_row_count = 0
    rows: list[dict[str, Any]] = []
    for row in raw_rows:
        if not isinstance(row, dict):
            malformed_row_count += 1
            continue
        experiment_id = row.get("experiment_id") or row.get("candidate_id") or row.get("id")
        if not isinstance(experiment_id, str) or not experiment_id.strip():
            malformed_row_count += 1
            continue
        rows.append(row)
    consumer_rows = {
        str(row.get("artifact")): row
        for row in consumer_index.get("rows", [])
        if isinstance(row, dict) and row.get("artifact")
    }
    classified = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        experiment_id = row.get("experiment_id") or row.get("candidate_id") or row.get("id")
        shadow_state, reasons = classify(row, consumer_rows)
        classified.append({
            "experiment_id": experiment_id,
            "shadow_state": shadow_state,
            "reasons": reasons,
            "production_suppression": False,
        })
    state_counts: dict[str, int] = {}
    zero_observation_count = 0
    with_matured_outcomes_count = 0
    incubating_zero_matured_outcome_count = 0
    created_at_values: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        state = str(row.get("state") or row.get("status") or "UNKNOWN")
        state_counts[state] = state_counts.get(state, 0) + 1
        observations = row.get("observation_count")
        matured = row.get("matured_outcome_count")
        if observations == 0:
            zero_observation_count += 1
        if isinstance(matured, int) and matured > 0:
            with_matured_outcomes_count += 1
        if state == "INCUBATING" and (not isinstance(matured, int) or matured == 0):
            incubating_zero_matured_outcome_count += 1
        created = row.get("created_at_utc")
        if isinstance(created, str) and created:
            created_at_values.append(created)

    registry_declared = registry.get("candidate_count")
    registry_consistency = (
        "PASS"
        if source_field == "candidates"
        and isinstance(registry_declared, int)
        and not isinstance(registry_declared, bool)
        and registry_declared == len(raw_rows)
        and malformed_row_count == 0
        else "UNVERIFIED_OR_MISMATCH"
    )
    return {
        "contract": CONTRACT,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "mode": "SHADOW_OBSERVE_ONLY",
        "rows": classified,
        "summary": {
            "row_count": len(classified),
            "observe_count": sum(r["shadow_state"] == "OBSERVE" for r in classified),
            "baseline_count": sum(r["shadow_state"] == "SHADOW_BASELINE" for r in classified),
            "state_counts": dict(sorted(state_counts.items())),
            "incubating_count": state_counts.get("INCUBATING", 0),
            "waiting_count": sum(count for state, count in state_counts.items() if state.startswith("WAITING_")),
            "matured_count": sum(count for state, count in state_counts.items() if state.startswith("MATURED_")),
            "zero_observation_count": zero_observation_count,
            "with_matured_outcomes_count": with_matured_outcomes_count,
            "incubating_zero_matured_outcome_count": incubating_zero_matured_outcome_count,
            "duplicate_candidate_file_count": registry.get("duplicate_candidate_file_count"),
            "oldest_candidate_created_at_utc": min(created_at_values) if created_at_values else None,
            "newest_candidate_created_at_utc": max(created_at_values) if created_at_values else None,
            "registry_source_field": source_field,
            "registry_raw_row_count": len(raw_rows),
            "registry_malformed_row_count": malformed_row_count,
            "registry_declared_candidate_count": registry_declared,
            "registry_consistency": registry_consistency,
        },
        "research_debt_semantics": {
            "descriptive_only": True,
            "candidate_state_change": False,
            "automatic_age_expiry": False,
            "automatic_retirement": False,
            "note": "Backlog metrics describe lifecycle load only. They do not retire, suppress, rank, or promote experiments.",
        },
        "promotion_policy": {
            "natural_observation_window_required": True,
            "automatic_retirement_allowed": False,
            "automatic_suppression_allowed": False,
            "automatic_promotion_allowed": False,
        },
        "authority": {
            "production_suppression": False,
            "canonical_promotion": False,
            "model_weight_change": False,
            "portfolio_action": False,
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--consumer-index", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = build_shadow(load(args.registry), load(args.consumer_index))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
