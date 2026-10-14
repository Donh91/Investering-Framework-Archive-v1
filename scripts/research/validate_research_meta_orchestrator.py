#!/usr/bin/env python3
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("o",ROOT/"scripts/research/research_meta_orchestrator.py")
o=importlib.util.module_from_spec(spec); spec.loader.exec_module(o)
pol={"max_concurrent_heavy_workstreams":1}
voi={"queue":[
 {"source":"SOURCE_RECOVERY","action":"DECLARE_NOT_TESTABLE","target":"old","impact_tier":"NONE","decision_surface":"DATA_INTEGRITY","reason":"terminal"},
 {"source":"SHARED_ROW","action":"STRESS_TEST","target":"C01","impact_tier":"HIGH","decision_surface":"ALTSEASON_ENTRY_ROTATION","reason":"errors","evidence_fingerprint":"x"}
]}
r=o.orchestrate(pol,{}, {}, voi, {"verdict":"PASS"})
assert r["primary_source"]=="SHARED_ROW" and r["primary_action"]=="QUEUE_BOUNDED_RESEARCH"; print("PASS terminal_source_does_not_starve_research")
r=o.orchestrate(pol,{}, {}, voi, {"verdict":"BLOCK_RESEARCH_ESCALATION"})
assert r["primary_action"]=="HALT_ESCALATION_AND_AUDIT"; print("PASS sentinel_precedence")
mem={"proposal_results":[{"source":"SHARED_ROW","action":"STRESS_TEST","target":"C01","novelty_verdict":"DUPLICATE_EXACT"}]}
r=o.orchestrate(pol,{},mem,voi,{"verdict":"PASS"})
sr=[x for x in r["queue"] if x.get("source")=="SHARED_ROW"][0]
assert sr["orchestrator_action"]=="SUPPRESS_DUPLICATE_RESEARCH"; print("PASS duplicate_suppression")
canon={"queue":[{"source":"CYCLE_NAVIGATOR","action":"CANONICAL_REVIEW_JUSTIFIED","target":"CN","impact_tier":"HIGH","decision_surface":"ALTSEASON_ENTRY_ROTATION","reason":"pass","evidence_fingerprint":"z"}]}
r=o.orchestrate(pol,{}, {}, canon, {"verdict":"PASS"})
assert r["primary_action"]=="PREPARE_CANONICAL_REVIEW" and r["primary_execution_mode"]=="REQUIRES_CANONICAL_REVIEW"; print("PASS canonical_review_packet_only")
assert len(r["active_heavy_workstreams"])<=1 and r["canonical_effect"] is False and r["paid_data_authorized"] is False
print("RESEARCH_META_ORCHESTRATOR_GATE_v1 PASS")

# Specialist intake bridge is an observation sink, not an executor or owner switch.
import json, tempfile
from pathlib import Path
with tempfile.TemporaryDirectory() as td:
    base=Path(td)
    folder=base/"04_RESEARCH_LAB"/"external_specialist_dissection"
    folder.mkdir(parents=True)
    note=folder/"METHOD_FIXTURE.md"
    note.write_text("# Independent method-only synthetic fixture\n")
    spec={"contract":"RESEARCH_LAB_EXTERNAL_SPECIALIST_DISSECTION_QUEUE_V1",
          "current_next_action":{"id":"UNCHANGED_PONS_OWNER"},
          "lanes":[{"id":"S4_LAUNCH_TRAJECTORY_AND_RETENTION_V1"}],
          "method_intakes":[{
              "id":"TEST_EXTERNAL_METHOD_20261014",
              "owner_lane":"S4_LAUNCH_TRAJECTORY_AND_RETENTION_V1",
              "evidence_note":"04_RESEARCH_LAB/external_specialist_dissection/METHOD_FIXTURE.md",
              "execution_permission":False,"review_state":"METHOD_ONLY_OWNER_REVIEW_PENDING"
          }]}
    queue=folder/"QUEUE_V1.json"
    queue.write_text(json.dumps(spec))
    original=o.orchestrate(pol,{}, {},voi,{"verdict":"PASS"})
    converted=o.attach_specialist_intakes(original,base)
    assert converted["queue_n"]==original["queue_n"]+1
    assert converted["primary_action"]==original["primary_action"]
    assert converted["primary_target"]==original["primary_target"]
    assert converted["active_heavy_workstreams"]==original["active_heavy_workstreams"]
    assert converted["specialist_intake_handoff"]["entries"][0]["market_source_admitted"] is False
    assert converted["queue"][-1]["orchestrator_action"]=="WAIT_FOR_EVIDENCE"
    assert converted["queue"][-1]["execution_mode"]=="AUTO_OBSERVE"
    assert converted["queue"][-1]["paid_data_authorized"] is False
    assert converted["queue"][-1]["canonical_effect"] is False
    assert converted["queue"][-1]["portfolio_execution"] is False
    assert len(converted["queue"][-1]["evidence_fingerprint"])==64
    print("PASS public_specialist_handoff_observation_only")

    blocked=o.orchestrate(pol,{}, {},voi,{"verdict":"FIREWALL_BREACH"})
    result=o.attach_specialist_intakes(blocked,base)
    assert result["queue"]==blocked["queue"] and result["primary_action"]=="HALT_ESCALATION_AND_AUDIT"
    print("PASS specialist_intake_does_not_override_sentinel")

    missing=o.orchestrate(pol,{}, {},voi,{"verdict":"PASS"})
    note.unlink()
    missing=o.attach_specialist_intakes(missing,base)
    assert missing["queue_n"]==original["queue_n"]
    assert missing["specialist_intake_handoff"]["entries"][0]["status"]=="NOTE_NOT_MERGED_OR_MISSING"
    print("PASS draft_or_missing_note_does_not_enter_queue")

    spec["method_intakes"][0]["execution_permission"]=True
    queue.write_text(json.dumps(spec))
    denied=o.specialist_intake_handoff(base)
    assert denied["status"]=="INVALID_INTAKE_AUTHORITY_OR_PATH" and denied["entries"]==[]
    print("PASS method_intake_execution_authority_rejected")

    spec["method_intakes"][0]["execution_permission"]=False
    spec["method_intakes"][0]["evidence_note"]="04_RESEARCH_LAB/external_specialist_dissection/../private.md"
    queue.write_text(json.dumps(spec))
    denied=o.specialist_intake_handoff(base)
    assert denied["status"]=="INVALID_INTAKE_AUTHORITY_OR_PATH" and denied["entries"]==[]
    print("PASS method_intake_path_traversal_rejected")

    spec["method_intakes"]*=21
    queue.write_text(json.dumps(spec))
    denied=o.specialist_intake_handoff(base)
    assert denied["status"]=="INVALID_INTAKE_COUNT_OR_TYPE"
    print("PASS method_intake_unbounded_growth_rejected")

print("RESEARCH_SPECIALIST_HANDOFF_GATE_v1 PASS")

