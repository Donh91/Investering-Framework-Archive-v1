#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from shared_row_tournament_weekly import filter_consumer_rows

ROOT = Path("06_RESEARCH_LAB/shared_row_model_tournament_v1")
REGISTRY = Path("04_MARKET_LEARNING/shadow_registry/REGISTRY.json")
CORE_FAMILIES = {"ETHBTC_PERSISTENCE", "BREADTH_SURVIVAL", "BTCD_PATH_RECLAIM"}
ACTIVE = "ACTIVE_POST_REPAIR_PROSPECTIVE_COLLECTION"
INTEGRITY = "SHARED_ROW_P0_BINDING_v1"


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def verified_matured_divergence_counts(valid_rows: list[dict], divergences: list[dict]) -> dict:
    """A timestamp marker is NOT an outcome; only admitted parent receipts count.

    The shared consumer gate already checked each parent outcome against its
    immutable owner receipt and all copied pairwise outcome columns.
    """
    parents = {row["event_id"]: row for row in valid_rows}
    return {
        horizon: sum(
            str(parents.get(div.get("event_id"), {}).get(f"outcome_{horizon}", "")) in {"0", "1"}
            and str(div.get(f"outcome_{horizon}", "")) in {"0", "1"}
            for div in divergences
        )
        for horizon in ("24h", "72h", "7d")
    }


def verified_matured_shared_row_counts(valid_rows: list[dict]) -> dict:
    """Count parent outcomes only AFTER the shared consumer integrity gate.

    Consensus rows can mature without any pairwise divergence. These are row
    counts, not independent trials or evidence of predictive/economic edge.
    """
    return {
        horizon: sum(str(row.get(f"outcome_{horizon}", "")) in {"0", "1"} for row in valid_rows)
        for horizon in ("24h", "72h", "7d")
    }


def main() -> None:
    required = [
        ROOT / "OWNER_BINDING_MATRIX.json",
        ROOT / "TRANSFORM_FREEZE_REGISTRY.json",
        ROOT / "03_CANDIDATE_REGISTRY.json",
        ROOT / "04_SHARED_ROW_SCHEMA.json",
        ROOT / "data/PROSPECTIVE_SHARED_ROW_LEDGER.csv",
        ROOT / "data/OUTCOME_DETAIL_LEDGER.csv",
        ROOT / "RUNTIME_STATUS.json",
        ROOT / "14_DIVERGENCE_FNP_LEDGER.csv",
        ROOT / "RELEVANCE_STATE.json",
        REGISTRY,
    ]
    issues = [f"MISSING:{path}" for path in required if not path.exists()]
    matrix = json.loads((ROOT / "OWNER_BINDING_MATRIX.json").read_text())
    freeze = json.loads((ROOT / "TRANSFORM_FREEZE_REGISTRY.json").read_text())
    registry = json.loads(REGISTRY.read_text())
    if "SHARED_ROW_MODEL_TOURNAMENT_V1" not in {item["sensor_id"] for item in registry["sensors"]}:
        issues.append("SHADOW_REGISTRY_NOT_REGISTERED")
    all_rows = read_csv(ROOT / "data/PROSPECTIVE_SHARED_ROW_LEDGER.csv")
    all_divergences = read_csv(ROOT / "14_DIVERGENCE_FNP_LEDGER.csv")
    outcome_details = read_csv(ROOT / "data/OUTCOME_DETAIL_LEDGER.csv")
    runtime = json.loads((ROOT / "RUNTIME_STATUS.json").read_text())
    valid_rows, divergences, excluded = filter_consumer_rows(
        all_rows, all_divergences, runtime, outcome_details=outcome_details
    )
    # Zero rows is a legitimate collecting state. An untrusted *present* row
    # is NOT: the monitor must never claim PASS by trusting a contract label.
    rejected_rows = len(all_rows) - len(valid_rows)
    rejected_divergences = len(all_divergences) - len(divergences)
    if runtime.get("collection_state") == ACTIVE and (rejected_rows or rejected_divergences):
        issues.append("UNVERIFIED_PROSPECTIVE_ROW_OR_DIVERGENCE")
    unresolved = [
        family["family_id"]
        for family in matrix["families"]
        if family["status"] != "READY" or family["candidate_decision_contract_status"] != "READY"
    ]
    core_unresolved = [family for family in unresolved if family in CORE_FAMILIES]
    optional_unresolved = [family for family in unresolved if family not in CORE_FAMILIES]
    matured = verified_matured_divergence_counts(valid_rows, divergences)
    matured_shared_rows = verified_matured_shared_row_counts(valid_rows)
    rule = freeze.get("core_activation_rule", {})
    collection_state = rule.get("collection_state")
    quarantined = collection_state != ACTIVE or rule.get("containment_floor_sentinel") is not False
    if issues and "UNVERIFIED_PROSPECTIVE_ROW_OR_DIVERGENCE" in issues:
        next_event = "RECONCILE_ORIGINAL_ROW_HASH_GIT_SOURCE_AND_OUTCOME_DETAILS"
        readiness = "FAIL_CLOSED_UNVERIFIED_RESEARCH_EVIDENCE"
    elif quarantined:
        next_event = "COMPLETE_POST_REPAIR_OWNERS_THEN_SEPARATE_FUTURE_FLOOR_REVIEW"
        readiness = "QUARANTINED_P0_REPAIR"
    elif core_unresolved:
        next_event = "FREEZE_CORE:" + ",".join(core_unresolved)
        readiness = "NOT_READY_CORE_BINDING"
    elif not valid_rows:
        next_event = "FIRST_P0_BOUND_SHARED_ROW_AFTER_ACTIVE_FLOOR"
        readiness = "NOT_READY_NO_SHARED_ROWS"
    elif matured_shared_rows["24h"] == 0:
        next_event = "FIRST_MATURED_24H_OUTCOME"
        readiness = "READY_FOR_AVAILABLE_MATURED_OUTCOMES"
    elif matured_shared_rows["72h"] == 0:
        next_event = "FIRST_MATURED_72H_OUTCOME"
        readiness = "READY_FOR_AVAILABLE_MATURED_OUTCOMES"
    elif matured_shared_rows["7d"] == 0:
        next_event = "FIRST_MATURED_7D_OUTCOME"
        readiness = "READY_FOR_AVAILABLE_MATURED_OUTCOMES"
    else:
        next_event = "CONTINUE_PROSPECTIVE_ACCUMULATION_AND_WEEKLY_TOURNAMENT_REVIEW"
        readiness = "READY_FOR_AVAILABLE_MATURED_OUTCOMES"
    output = {
        "contract": "SHARED_ROW_TOURNAMENT_MONITOR_v1",
        "contract_revision": "1.3-separate-parent-and-divergence-maturity",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": "PASS" if not issues else "FAIL",
        "collection_state": collection_state,
        "scoring_readiness": readiness,
        "eligible_row_n": len(valid_rows),
        "excluded_pre_repair_row_n": len(all_rows) - len(valid_rows),
        "divergence_n": len(divergences),
        "excluded_unbound_divergence_n": len(all_divergences) - len(divergences),
        "consumer_integrity_filter": {
            "raw_rows": len(all_rows),
            "raw_divergences": len(all_divergences),
            "eligible_rows": len(valid_rows),
            "eligible_divergences": len(divergences),
            "excluded": excluded,
        },
        "matured": matured,
        "matured_shared_rows": matured_shared_rows,
        "maturity_count_semantics": {
            "matured": "VERIFIED_PAIRWISE_DIVERGENCE_COMPARISONS_LEGACY",
            "matured_shared_rows": "VERIFIED_PARENT_OUTCOME_RECEIPTS_INCLUDING_CONSENSUS",
            "independent_trial_count": None,
            "row_counts_are_independent_trials": False,
        },
        "core_unresolved_family_bindings": core_unresolved,
        "optional_unresolved_family_bindings": optional_unresolved,
        "unresolved_family_bindings": unresolved,
        "issues": issues,
        "exact_next_evidence_event": next_event,
        "canonical_effect": False,
    }
    directory = ROOT / "monitor"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "LATEST.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output, sort_keys=True))
    raise SystemExit(0 if not issues else 2)


if __name__ == "__main__":
    main()
