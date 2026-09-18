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
    rows = registry.get("rows") or registry.get("experiments") or registry.get("items") or []
    if not isinstance(rows, list):
        rows = []
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
    return {
        "contract": CONTRACT,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "mode": "SHADOW_OBSERVE_ONLY",
        "rows": classified,
        "summary": {
            "row_count": len(classified),
            "observe_count": sum(r["shadow_state"] == "OBSERVE" for r in classified),
            "baseline_count": sum(r["shadow_state"] == "SHADOW_BASELINE" for r in classified),
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
