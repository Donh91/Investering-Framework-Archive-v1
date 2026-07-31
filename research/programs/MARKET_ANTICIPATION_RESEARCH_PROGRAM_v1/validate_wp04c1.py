import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
registry = json.loads((ROOT / "WP04C1_OWNER_MATERIALIZATION_REGISTRY_v1.json").read_text())
state = json.loads((ROOT / "WP04C1_EXECUTION_STATE_v1.json").read_text())
request = json.loads((ROOT / "WP04C1_MATERIALIZATION_REQUEST_v1.json").read_text())

assert registry["status"] == "COMPLETE_FAIL_CLOSED_PARTIAL_MATERIALIZATION"
assert registry["materialization_gate"]["current_gate_result"] == "FAIL_CLOSED"
assert registry["materialization_gate"]["legal_event_enumeration_unlocked"] is False
assert state["replayable_owner_dataset_count"] == 0
assert state["event_enumeration_unlocked"] is False
assert state["event_counts_inspected"] is False
assert state["outcomes_inspected"] is False
assert state["final_holdout_accessed"] is False
assert request["status"] == "READY_FOR_ARTIFACT_INTAKE"
assert "threshold changes" in request["forbidden"]
assert all(not p["eligible_for_wp04c_replay"] for p in registry["package_roots"])
assert all(not d["row_level_materialized"] for d in registry["wp04c_required_datasets"])
print("WP04C1_VALIDATION_PASS")
