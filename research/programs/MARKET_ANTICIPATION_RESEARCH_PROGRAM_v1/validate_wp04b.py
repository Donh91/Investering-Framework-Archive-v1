#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
contract = json.loads((ROOT / "WP04B_TRIGGER_ADDENDUM_v1.json").read_text())
state = json.loads((ROOT / "WP04B_EXECUTION_STATE_v1.json").read_text())

assert contract["scope"] == "PROSPECTIVE_TRIGGER_FREEZE_ONLY"
assert contract["historical_event_counts_inspected"] is False
assert contract["post_event_outcomes_inspected"] is False
assert contract["final_holdout_accessed"] is False
assert state["historical_enumeration_performed"] is False
assert state["historical_event_counts_known"] is False
assert state["economic_analysis_authorized"] is False

chains = {c["chain_id"]: c for c in contract["chains"]}
assert set(chains) == {"LSP_MACRO_TO_CRYPTO", "LSP_LEVERAGE_TO_SPOT", "LSP_ROTATION_FAILURE"}

macro = chains["LSP_MACRO_TO_CRYPTO"]
assert macro["macro_state"]["minimum_history"] == 252
assert macro["macro_state"]["persistence"] == "AT_LEAST_2_OF_3_REQUIRED_COMPONENTS_TRUE_ON_2_CONSECUTIVE_ELIGIBLE_DAYS"
assert macro["crypto_transmission"]["maximum_lag"] == "3_SETTLED_CRYPTO_DAYS_AFTER_MACRO_STATE_FIRST_QUALIFIES"

lev = chains["LSP_LEVERAGE_TO_SPOT"]
assert lev["leverage_state"]["minimum_history"] == 720
assert lev["leverage_state"]["persistence"] == "REQUIRED_CONDITIONS_TRUE_IN_SAME_SETTLED_HOUR_OR_ADJACENT_HOURS_WITHIN_2H"
assert lev["spot_transmission"]["maximum_lag"] == "4_SETTLED_HOURS_AFTER_LEVERAGE_STATE_FIRST_QUALIFIES"

assert chains["LSP_ROTATION_FAILURE"]["status"] == "INHERITED_UNCHANGED"
assert contract["versioning"]["immutable_after_merge"] is True
assert "FORWARD_RETURN_INSPECTION" in contract["common_rules"]["forbidden"]
print("WP04B_VALIDATION_PASS")
