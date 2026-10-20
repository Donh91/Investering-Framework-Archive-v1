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

# Specialist intake bridge: no PR-only, outside-repo, untracked or mutable source notes.
import json, subprocess, tempfile
from pathlib import Path
from unittest.mock import patch

def _git(root,*args):
    p=subprocess.run(["git","-C",str(root),*args],capture_output=True,text=True,check=False)
    assert p.returncode==0, (args,p.stderr)
    return p.stdout.strip()

with tempfile.TemporaryDirectory() as td:
    base=Path(td)
    folder=base/"04_RESEARCH_LAB"/"external_specialist_dissection"
    folder.mkdir(parents=True)
    note=folder/"METHOD_FIXTURE.md"
    note.write_text("# Public committed method-only synthetic fixture\n")
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
    _git(base,"init","-b","main")
    def commit_fixture(message):
        _git(base,"add","-A")
        _git(base,"-c","user.name=Research Test","-c","user.email=test@example.invalid",
             "commit","--allow-empty","-m",message)
        _git(base,"update-ref","refs/remotes/origin/main","HEAD")
    commit_fixture("public origin main source")
    original=o.orchestrate(pol,{}, {},voi,{"verdict":"PASS"})
    converted=o.attach_specialist_intakes(original,base)
    assert converted["queue_n"]==original["queue_n"]+1, converted["specialist_intake_handoff"]
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
    print("PASS public_committed_specialist_observation_no_owner_override")

    blocked=o.orchestrate(pol,{}, {},voi,{"verdict":"FIREWALL_BREACH"})
    result=o.attach_specialist_intakes(blocked,base)
    assert result["queue"]==blocked["queue"] and result["primary_action"]=="HALT_ESCALATION_AND_AUDIT"
    print("PASS specialist_does_not_override_sentinel")

    note.unlink()
    missing=o.attach_specialist_intakes(original,base)
    assert missing["queue_n"]==original["queue_n"]
    assert missing["specialist_intake_handoff"]["entries"][0]["status"]=="NOTE_NOT_MERGED_OR_MISSING"
    print("PASS missing_note_not_eligible")

    note.write_text("# Public committed method-only synthetic fixture\n")
    spec["method_intakes"][0]["evidence_note"]="04_RESEARCH_LAB/external_specialist_dissection/DRAFT_ONLY.md"
    queue.write_text(json.dumps(spec))
    commit_fixture("queue references an untracked PR-only note")
    draft=folder/"DRAFT_ONLY.md"
    draft.write_text("# untracked note in checkout, not committed to main")
    untracked=o.attach_specialist_intakes(original,base)
    assert untracked["queue_n"]==original["queue_n"]
    assert untracked["specialist_intake_handoff"]["entries"][0]["status"]=="NOTE_NOT_MERGED_OR_MISSING"
    print("PASS present_but_untracked_draft_note_does_not_enter_queue")

    spec["method_intakes"][0]["evidence_note"]="04_RESEARCH_LAB/external_specialist_dissection/METHOD_FIXTURE.md"
    queue.write_text(json.dumps(spec))
    commit_fixture("queue restores tracked note reference")
    note.write_text("# working tree changed without main commit")
    dirty=o.attach_specialist_intakes(original,base)
    assert dirty["queue_n"]==original["queue_n"]
    assert dirty["specialist_intake_handoff"]["entries"][0]["status"]=="NOTE_NOT_MERGED_OR_MISSING"
    print("PASS modified_worktree_note_never_verified")

    note.write_text("# Public committed method-only synthetic fixture\n")
    _git(base,"checkout","-b","feature/pr-only")
    note.write_text("# PR-only branch source")
    _git(base,"add","-A")
    _git(base,"-c","user.name=Research Test","-c","user.email=test@example.invalid",
         "commit","-m","PR only note")
    pronly=o.attach_specialist_intakes(original,base)
    assert pronly["specialist_intake_handoff"]["status"]=="MAIN_CHECKOUT_NOT_VERIFIED"
    assert pronly["queue_n"]==original["queue_n"]
    _git(base,"checkout","main")
    print("PASS PR_checkout_cannot_authenticate_main_note")

    original_read_bytes=Path.read_bytes
    def disappear_on_read(path):
        if Path(path).name=="METHOD_FIXTURE.md":
            raise FileNotFoundError("simulated note disappearing before read")
        return original_read_bytes(path)
    with patch.object(Path,"read_bytes",disappear_on_read):
        atomic=o.attach_specialist_intakes(original,base)
    assert atomic["queue_n"]==original["queue_n"]
    assert atomic["specialist_intake_handoff"]["entries"][0]["note_sha256"] is None
    print("PASS note_disappearance_cannot_produce_null_hash_observation")

    spec["method_intakes"][0]["execution_permission"]=True
    queue.write_text(json.dumps(spec))
    assert o.specialist_intake_handoff(base)["status"]=="SOURCE_QUEUE_NOT_COMMITTED"
    commit_fixture("invalid permission must fail closed")
    denied=o.specialist_intake_handoff(base)
    assert denied["status"]=="INVALID_INTAKE_AUTHORITY_OR_PATH" and denied["entries"]==[]
    print("PASS uncommitted_queue_and_execution_escalation_rejected")

    spec["method_intakes"][0]["execution_permission"]=False
    spec["method_intakes"][0]["evidence_note"]="04_RESEARCH_LAB/external_specialist_dissection/../private.md"
    queue.write_text(json.dumps(spec))
    commit_fixture("malformed note path must fail closed")
    denied=o.specialist_intake_handoff(base)
    assert denied["status"]=="INVALID_INTAKE_AUTHORITY_OR_PATH" and denied["entries"]==[]
    print("PASS path_traversal_rejected")

    spec["method_intakes"]*=21
    queue.write_text(json.dumps(spec))
    commit_fixture("unbounded note count must fail closed")
    denied=o.specialist_intake_handoff(base)
    assert denied["status"]=="INVALID_INTAKE_COUNT_OR_TYPE"
    print("PASS unbounded_growth_rejected")

    for bad in ("[]","null"):
        queue.write_text(bad)
        commit_fixture("nonobject JSON rejected")
        bad_result=o.specialist_intake_handoff(base)
        assert bad_result["status"]=="INVALID_SOURCE_QUEUE_TYPE"
    print("PASS nonobject_queue_json_rejected_without_uncaught_exception")

with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as external:
    root=Path(td); folder=root/"04_RESEARCH_LAB"; folder.mkdir()
    outside=Path(external); (outside/"QUEUE_V1.json").write_text("{}")
    (folder/"external_specialist_dissection").symlink_to(outside,target_is_directory=True)
    unsafe=o.specialist_intake_handoff(root)
    assert unsafe["status"]=="SOURCE_QUEUE_OUTSIDE_REPO", unsafe
    print("PASS symlinked_source_directory_escape_rejected")

print("RESEARCH_SPECIALIST_HANDOFF_GATE_v1 PASS")
