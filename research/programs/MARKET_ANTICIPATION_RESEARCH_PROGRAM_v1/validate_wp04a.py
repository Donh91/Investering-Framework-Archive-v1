#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def load(name):
    return json.loads((ROOT / name).read_text())

inventory = load("WP04A_OWNER_SOURCE_INVENTORY_v1.json")
triggers = load("WP04A_TRIGGER_READINESS_AUDIT_v1.json")
ledger = load("WP04A_CANDIDATE_EVENT_LEDGER_v1.json")
lineage = load("WP04A_LINEAGE_AUDIT_v1.json")
state = load("WP04A_EXECUTION_STATE_v1.json")

assert inventory["substitution_forbidden"] is True
assert triggers["outcome_data_inspected"] is False
assert len(triggers["chains"]) == 3
assert sum(c["trigger_status"] == "BLOCKED" for c in triggers["chains"]) == 2
assert len(ledger["independent_candidates"]) == 1
assert ledger["independent_candidates"][0]["lineage_class"] == "OWNER_PARTIAL"
assert ledger["independent_candidates"][0]["outcome_fields_materialized"] is False
assert ledger["blocked_chain_candidate_counts"]["LSP_MACRO_TO_CRYPTO"] is None
assert ledger["blocked_chain_candidate_counts"]["LSP_LEVERAGE_TO_SPOT"] is None
assert lineage["summary"]["fully_replayable"] == 0
assert lineage["descriptive_audit_eligible"] == 0
for key in ["outcomes_inspected", "forward_returns_computed", "hit_rates_computed", "economic_ranking_performed", "parameter_search_performed", "model_weights_changed", "final_holdout_accessed"]:
    assert state[key] is False
assert state["framework_promotion"] == "NONE"
assert state["portfolio_effect"] == "NONE"
print("WP04A_VALIDATION_PASS")
