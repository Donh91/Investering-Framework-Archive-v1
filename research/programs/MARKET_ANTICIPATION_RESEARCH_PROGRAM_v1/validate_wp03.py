#!/usr/bin/env python3
"""Validate MAR-WP03 preregistration without enumerating events or opening outcomes."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load(name: str):
    with (ROOT / name).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    labels = load("WP03_FAILED_MOVE_LABEL_CONTRACT_v1.json")
    windows = load("WP03_EVENT_WINDOW_AND_CLUSTERING_CONTRACT_v1.json")
    schema = load("WP03_EVENT_ROW_SCHEMA_v1.json")
    state = load("WP03_PREREGISTRATION_STATE_v1.json")

    assert labels["status"] == "PREREGISTERED_BEFORE_OUTCOME_INSPECTION"
    assert labels["global_rules"]["retrospective_event_creation_forbidden"] is True
    assert labels["global_rules"]["economic_execution_allowed"] is False
    assert labels["global_rules"]["final_holdout_opened"] is False

    families = {row["family_id"]: row for row in labels["label_families"]}
    assert len(families) == 4
    assert families["FM_ETHBTC_THRESHOLD_ATTEMPT"]["thresholds"] == [0.0275, 0.03]
    assert families["FM_BREADTH_DISPLACEMENT"]["membership_hash_required"] is True
    assert families["FM_ETF_FLOW_REVERSAL"]["hard_label_eligible"] is False

    assert windows["cluster_rules"]["one_independent_event_per_cluster"] is True
    assert windows["censoring"]["do_not_replace_missing_owner_with_challenger"] is True
    assert windows["windows"]["economic_outcomes_enabled"] is False

    required = set(schema["required"])
    for field in ["event_id", "cluster_id", "knowledge_at_utc", "source_hash", "outcome_accessed"]:
        assert field in required
    assert schema["properties"]["outcome_accessed"]["const"] is False
    assert schema["properties"]["portfolio_effect"]["const"] is False

    assert state["event_rows_created"] == 0
    assert state["outcomes_accessed"] is False
    assert state["economic_tests_run"] == 0
    assert state["final_holdout_opened"] is False
    assert state["next_gate"] == "MAR_WP03A_OWNER_EVENT_ENUMERATION_AND_LINEAGE_AUDIT"

    print("MAR-WP03 validation PASS: labels frozen, zero outcomes accessed, economic execution locked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
