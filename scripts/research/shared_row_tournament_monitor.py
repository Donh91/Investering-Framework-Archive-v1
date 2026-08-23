#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("06_RESEARCH_LAB/shared_row_model_tournament_v1")
REGISTRY = Path("04_MARKET_LEARNING/shadow_registry/REGISTRY.json")
CORE_FAMILIES = {"ETHBTC_PERSISTENCE", "BREADTH_SURVIVAL", "BTCD_PATH_RECLAIM"}
ACTIVE = "ACTIVE_POST_REPAIR_PROSPECTIVE_COLLECTION"
INTEGRITY = "SHARED_ROW_P0_BINDING_v1"


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    required = [
        ROOT / "OWNER_BINDING_MATRIX.json",
        ROOT / "TRANSFORM_FREEZE_REGISTRY.json",
        ROOT / "03_CANDIDATE_REGISTRY.json",
        ROOT / "04_SHARED_ROW_SCHEMA.json",
        ROOT / "data/PROSPECTIVE_SHARED_ROW_LEDGER.csv",
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
    valid_rows = [row for row in all_rows if row.get("row_integrity_contract") == INTEGRITY]
    valid_ids = {row.get("event_id") for row in valid_rows}
    all_divergences = read_csv(ROOT / "14_DIVERGENCE_FNP_LEDGER.csv")
    divergences = [row for row in all_divergences if row.get("event_id") in valid_ids]
    unresolved = [
        family["family_id"]
        for family in matrix["families"]
        if family["status"] != "READY" or family["candidate_decision_contract_status"] != "READY"
    ]
    core_unresolved = [family for family in unresolved if family in CORE_FAMILIES]
    optional_unresolved = [family for family in unresolved if family not in CORE_FAMILIES]
    matured = {
        horizon: sum(bool(row.get(f"matured_{horizon}_utc")) for row in divergences)
        for horizon in ["24h", "72h", "7d"]
    }
    rule = freeze.get("core_activation_rule", {})
    collection_state = rule.get("collection_state")
    quarantined = collection_state != ACTIVE or rule.get("containment_floor_sentinel") is not False
    if quarantined:
        next_event = "COMPLETE_POST_REPAIR_OWNERS_THEN_SEPARATE_FUTURE_FLOOR_REVIEW"
        readiness = "QUARANTINED_P0_REPAIR"
    elif core_unresolved:
        next_event = "FREEZE_CORE:" + ",".join(core_unresolved)
        readiness = "NOT_READY_CORE_BINDING"
    elif not valid_rows:
        next_event = "FIRST_P0_BOUND_SHARED_ROW_AFTER_ACTIVE_FLOOR"
        readiness = "NOT_READY_NO_SHARED_ROWS"
    elif matured["24h"] == 0:
        next_event = "FIRST_MATURED_24H_OUTCOME"
        readiness = "READY_FOR_AVAILABLE_MATURED_OUTCOMES"
    elif matured["72h"] == 0:
        next_event = "FIRST_MATURED_72H_OUTCOME"
        readiness = "READY_FOR_AVAILABLE_MATURED_OUTCOMES"
    elif matured["7d"] == 0:
        next_event = "FIRST_MATURED_7D_OUTCOME"
        readiness = "READY_FOR_AVAILABLE_MATURED_OUTCOMES"
    else:
        next_event = "CONTINUE_PROSPECTIVE_ACCUMULATION_AND_WEEKLY_TOURNAMENT_REVIEW"
        readiness = "READY_FOR_AVAILABLE_MATURED_OUTCOMES"
    output = {
        "contract": "SHARED_ROW_TOURNAMENT_MONITOR_v1",
        "contract_revision": "1.1-p0-integrity",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": "PASS" if not issues else "FAIL",
        "collection_state": collection_state,
        "scoring_readiness": readiness,
        "eligible_row_n": len(valid_rows),
        "excluded_pre_repair_row_n": len(all_rows) - len(valid_rows),
        "divergence_n": len(divergences),
        "excluded_unbound_divergence_n": len(all_divergences) - len(divergences),
        "matured": matured,
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
