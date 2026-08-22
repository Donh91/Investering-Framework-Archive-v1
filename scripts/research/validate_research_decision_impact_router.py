#!/usr/bin/env python3
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("v",ROOT/"scripts/research/research_decision_impact_router.py")
v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
states={
 "SHARED_ROW":{"selected_action":"RESEARCH_NEW_HYPOTHESIS","target":"C01","evidence_fingerprint":"x"},
 "CYCLE_NAVIGATOR":{"selected_action":"CONTINUE_CALIBRATION","evidence_fingerprint":"c"},
 "SHADOW_REGISTRY":{"selected_action":"RECOVER_EVALUATOR","target_sensor_id":"S1","evidence_fingerprint":"s"},
 "SOURCE_RECOVERY":{"selected_action":"DECLARE_NOT_TESTABLE","target_receipt":"old.json","evidence_fingerprint":"r"}
}
state=v.route({},states,{})
assert state["selected_source"]=="SHARED_ROW" and state["selected_impact_tier"]=="HIGH",state
assert state["resolved_specialist_state_n"]==4 and state["actionable_specialist_state_n"]==4,state
print("PASS high_value_beats_watch")
memory={"proposal_results":[{"source":"SHARED_ROW","action":"RESEARCH_NEW_HYPOTHESIS","target":"C01","novelty_verdict":"DUPLICATE_EXACT"}]}
state=v.route({},states,memory)
item=[x for x in state["queue"] if x["source"]=="SHARED_ROW"][0]
assert item["impact_tier"]=="BLOCKED"; print("PASS duplicate_blocked")
paid=v.route({}, {"SOURCE_RECOVERY":{"selected_action":"GENERATE_PAID_DATA_VOI_PACKET","target_receipt":"x","evidence_fingerprint":"p"}}, {})
assert paid["queue"][0]["paid_review_only"] is True and paid["paid_data_authorized"] is False; print("PASS paid_is_review_only")
term=v.route({}, {"SOURCE_RECOVERY":{"selected_action":"DECLARE_NOT_TESTABLE","target_receipt":"x","evidence_fingerprint":"t"}}, {})
assert term["selected_impact_tier"]=="NONE"; print("PASS terminal_closeout_no_independent_voi")
resolved_idle=v.route({}, {"A":{"status":"INITIALIZED"},"B":{"status":"INITIALIZED"}}, {})
assert resolved_idle["queue_n"]==0
assert resolved_idle["resolved_specialist_state_n"]==2 and resolved_idle["actionable_specialist_state_n"]==0
assert resolved_idle["reason"]=="specialist states resolved, but no actionable research proposal is active"
print("PASS resolved_idle_not_mislabeled_missing")
missing=v.route({}, {}, {})
assert missing["resolved_specialist_state_n"]==0 and missing["reason"]=="no specialist states resolved"
print("PASS true_missing_distinguished")
print("RESEARCH_DECISION_IMPACT_GATE_v2 PASS")
