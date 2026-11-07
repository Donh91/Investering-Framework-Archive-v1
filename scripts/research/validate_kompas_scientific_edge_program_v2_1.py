#!/usr/bin/env python3
"""Validate proposal-only original Task2 Kompas scientific program, no execution.

Does NOT run research, authenticate sources, permit GitHub merge, trigger
agents or API paid work, change market authority, attest a first-known market
clock, or prove that an actual S1 runtime has consumed anything.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DIR=Path("06_RESEARCH_LAB/hugging_face_task2_audit_20261022/kompas_scientific_edge_program_v2_1")
MISSION=DIR/"PROGRAM_MANIFEST_v1.json"
RECEIPT=DIR/"RECEIPT_TEMPLATE_v1.json"
LANES={f"L{i:02d}" for i in range(1,11)}
SOURCE40=re.compile(r"^[0-9a-f]{40}$")
UTC_DATE=re.compile(r"^\d{4}-\d{2}-\d{2}$")
STATUS={"PLANNED","RUNNING","COMPLETE_VERIFIED","FAILED_EVIDENCED","BLOCKED","NOT_EXECUTED"}
DECISIONS={"FIX_NOW","BUILD_SHADOW","SOURCE_REPAIR","AWAIT_MATURITY",
           "SCIENTIFIC_BLOCK","REJECTED","SUPERSEDED","PRODUCTION_READY"}
ZERO_PERMISSION=[
 "no_new_workflow","no_new_schedule","no_new_supervisor","no_new_github_identity",
 "no_new_market_authority","no_live_trading","no_unattested_self_merge",
 "program_is_not_scheduler","program_is_not_production_writer",
]
REQUIRED={
 "lane_id","name","original_owner_issue","wave","depends_on","hypothesis",
 "baseline","falsifier","decision_relevant_output","scientific_stop_condition",
 "reactivation_trigger","first_source_anchor_path","first_source_anchor_blob_sha",
 "source_eligibility","source_first_known_at_utc",
 "original_issue_or_product_clock_at_utc","source_pit_admission",
 "execution_mode","max_one_pass_wall_minutes","independent_research_paid_usd",
 "original_output_home","status","actual_native_run_id",
 "actual_ai_agent_execution_id","release_claim_allowed","latest_original_pr_head_sha",
 "result_claim","finding_disposition",
}

def _graph_issues(edges:dict[str,list[str]])->list[str]:
    problems=[]
    grey=set()
    black=set()
    def visit(key):
        if key in grey:
            problems.append("dependency_cycle:"+key); return
        if key in black: return
        grey.add(key)
        for dep in edges.get(key,()):
            if dep not in edges: problems.append("unknown_dependency:"+key+":"+dep)
            else: visit(dep)
        grey.remove(key)
        black.add(key)
    for key in edges: visit(key)
    return sorted(set(problems))

def validate_manifest(j:dict)->list[str]:
    errors=[]
    if not isinstance(j,dict):return ["program_not_object"]
    if j.get("contract")!="KOMPAS_PRO_SCIENTIFIC_EDGE_PROGRAM_V2_1": errors.append("wrong_contract")
    if j.get("proposal_state")!="OWNER_APPROVAL_PENDING_NO_LIVE_ACTIVATION": errors.append("not_proposal_only")
    if j.get("original_scientific_owner")!="https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596":errors.append("changed_science_owner")
    if j.get("execution_owner")!="https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156":errors.append("changed_s1_owner")
    if j.get("existing_s1_task_id")!="6ae5fd466b48819187abc224ec0f1c5f":errors.append("changed_saved_s1")
    if j.get("monday_readonly_copenhagen")!="09:30-10:30":errors.append("s1_monday_gate_changed")
    if j.get("next_w46_local_date")!="2026-11-09" or j.get("w46_priority") is not True:errors.append("first_w46_priority_changed")
    if not SOURCE40.fullmatch(str(j.get("current_public_main_at_staging",""))):errors.append("source_snapshot_invalid")
    for key in ZERO_PERMISSION:
        if j.get(key) is not True:errors.append("authority_broadened:"+key)
    for key in ("approval_is_release_permission","approval_is_api_payment_release",
                "restricted_round3_hypothesis_testing_allowed","restricted_round3_outcome_scoring_allowed"):
        if j.get(key) is not False:errors.append("permission_bypass:"+key)
    if j.get("max_research_lanes")!=10:errors.append("lane_max_changed")
    if not isinstance(j.get("max_simultaneous_compute_jobs"),int) or not 2<=j["max_simultaneous_compute_jobs"]<=4:errors.append("compute_cap")
    if j.get("max_s1_active_original_prs_per_tick")!=3:errors.append("s1_cap_changed")
    if j.get("max_automatic_paid_usd")!=0 or j.get("approved_paid_spend_in_this_proposal_usd")!=0:errors.append("paid_release_without_native_gate")
    if j.get("program_is_not_scheduler") is not True or j.get("program_is_not_production_writer") is not True:errors.append("parallel_control_plane")
    if set(j.get("claim_classes",()))!={"ORIGINAL_ISSUED","FROZEN_RETROSPECTIVE","CHALLENGER_DEVELOPMENT"}:errors.append("science_class_drift")
    if set(j.get("lane_status_enum",()))!=STATUS:errors.append("lane_status_registry_drift")
    if set(j.get("finding_disposition_enum",()))!=DECISIONS:errors.append("finding_class_drift")
    if j.get("historical_reality_engine")!="METHOD_AND_PRIOR_NEGATIVE_REUSE_ONLY_NOT_THIS_PROGRAM":errors.append("time_machine_scope_collision")
    if j.get("program_is_not_scheduler") is not True:errors.append("scheduler_authority")
    waves=j.get("wave_sequence",[])
    if not isinstance(waves,list) or [x.get("id") for x in waves if isinstance(x,dict)]!=["WAVE_A","WAVE_B","WAVE_C"]:
        errors.append("wave_order_must_be_source_then_science_then_economics")
    else:
        if set(waves[0].get("lanes",()))!={"L01","L04","L06","L09"} or waves[0].get("independent_redteam")!="L10":
            errors.append("waveA_w46_protection")
        if set(waves[1].get("lanes",()))!={"L02","L03","L05","L07"}:
            errors.append("waveB_science")
        if set(waves[2].get("lanes",()))!={"L08","L10"}:
            errors.append("waveC_economics")
    lanes=j.get("lanes")
    if not isinstance(lanes,list) or len(lanes)!=10:return sorted(set(errors+["exactly_ten_lanes_required"]))
    ids=[x.get("lane_id") if isinstance(x,dict) else None for x in lanes]
    if set(ids)!=LANES or len(set(ids))!=10:errors.append("lane_roster_or_duplicate")
    graph={}
    owners={1596,1156,1827,1516,1593,1553,1530}
    for lane in lanes:
        if not isinstance(lane,dict):
            errors.append("lane_not_object");continue
        ident=lane.get("lane_id","UNKNOWN")
        missing=REQUIRED-set(lane)
        if missing:errors.append(f"{ident}:missing:{','.join(sorted(missing))}")
        if not isinstance(lane.get("original_owner_issue"),int) or lane["original_owner_issue"] not in owners:
            errors.append(ident+":owner_scope")
        for key in ("hypothesis","baseline","falsifier","decision_relevant_output","scientific_stop_condition","reactivation_trigger"):
            if not isinstance(lane.get(key),str) or len(lane[key])<24:errors.append(ident+":not_falsifiable:"+key)
        if lane.get("status")!="PLANNED":errors.append(ident+":fake_execution_status")
        if lane.get("result_claim")!="NO_NEW_RESULT_UNTIL_EVIDENCED":errors.append(ident+":preclaimed_result")
        if lane.get("finding_disposition") is not None:errors.append(ident+":predeclared_finding")
        for key in ("actual_native_run_id","actual_ai_agent_execution_id","latest_original_pr_head_sha",
                    "source_first_known_at_utc","original_issue_or_product_clock_at_utc"):
            if lane.get(key) is not None:errors.append(ident+":fabricated_evidence:"+key)
        if lane.get("source_pit_admission")!="NOT_AUTOMATICALLY_ADMITTED" or lane.get("release_claim_allowed") is not False:
            errors.append(ident+":scientific_or_release_bypass")
        if lane.get("source_eligibility")!="UNKNOWN_MUST_RECHECK_AT_RUN":errors.append(ident+":first_known_not_verified")
        if not SOURCE40.fullmatch(str(lane.get("first_source_anchor_blob_sha",""))):
            errors.append(ident+":not_pinned_source")
        p=lane.get("first_source_anchor_path","")
        if (not isinstance(p,str) or p.startswith("/") or "\\" in p
                or ".." in Path(p).parts or not p or p.endswith("/")):errors.append(ident+":unsafe_source_path")
        if lane.get("max_one_pass_wall_minutes") not in (30,60,90,120,180):
            errors.append(ident+":unbounded_compute_duration")
        if lane.get("independent_research_paid_usd")!=0:errors.append(ident+":paid_work_without_authority")
        if lane.get("execution_mode")!="READ_ONLY_RESEARCH_OR_EXISTING_OWNER_PR_NATIVE_CI":
            errors.append(ident+":uncontrolled_executor")
        if not str(lane.get("original_output_home","")).startswith("06_RESEARCH_LAB/hugging_face_task2_audit_20261022/"):
            errors.append(ident+":new_owner_output_path")
        deps=lane.get("depends_on")
        if not isinstance(deps,list) or len(deps)!=len(set(deps)):
            errors.append(ident+":duplicate_or_missing_dependencies")
        else: graph[ident]=deps
    errors.extend(_graph_issues(graph))
    deliveries=j.get("deliverables",[])
    if not isinstance(deliveries,list) or len(deliveries)!=9 or len({d.get("key") for d in deliveries if isinstance(d,dict)})!=9:
        errors.append("nine_real_deliverables")
    elif any(not isinstance(d.get("owner_issue"),int) or not d.get("requires") for d in deliveries):
        errors.append("deliverable_missing_original_owner")
    return sorted(set(errors))

def validate_receipt(j:dict)->list[str]:
    errors=[]
    if not isinstance(j,dict):return ["receipt_not_object"]
    if j.get("contract")!="KOMPAS_PRO_TASK2_LANE_RECEIPT_TEMPLATE_V1":errors.append("receipt_contract")
    if j.get("is_template") is not True or j.get("execution_claim")!="NOT_EXECUTED":errors.append("template_forged_run")
    if j.get("original_scientific_owner_issue")!=1596:errors.append("template_owner")
    src=j.get("source",{})
    if not isinstance(src,dict) or src.get("first_known_admission")!="NOT_VERIFIED" or src.get("restricted_values_in_public") is not False or src.get("source_health_is_scientific_edge") is not False:
        errors.append("template_source_gate")
    for key in ("source_ref_sha","provider_first_publication_at_utc","original_model_issued_at_utc","original_user_delivered_at_utc"):
        if src.get(key) is not None:errors.append("template_original_first_known_fabricated:"+key)
    e=j.get("execution",{})
    for key in ("native_ai_agent_run_id","native_workflow_run_id","native_job_id","github_pr_head_sha",
                "artifact_id","sol_native_release_receipt_url","actual_approval_receipt_url"):
        if e.get(key) is not None:errors.append("template_execution_fabricated:"+key)
    for key in ("native_success_proven","naturally_scheduled_s1_own_merge","new_schedule_created",
                "new_github_identity_created","live_trading"):
        if e.get(key) is not False:errors.append("template_claims_authority:"+key)
    if e.get("max_budget_usd")!=0:errors.append("receipt_paid_cap")
    c=j.get("change",{})
    if c.get("release_claim")!="NO_RELEASE_PROVEN" or c.get("merge_sha") is not None or c.get("new_main_sha") is not None:
        errors.append("template_fake_merge")
    z=j.get("closure",{})
    if z.get("status")!="NOT_EXECUTED":errors.append("template_status")
    for key in ("operational_mission_complete","predictive_edge_proven","economic_edge_proven"):
        if z.get(key) is not False:errors.append("template_unproven_result:"+key)
    return sorted(set(errors))

def validate_bundle(root:Path=ROOT)->list[str]:
    a=root/MISSION;b=root/RECEIPT
    if not a.is_file() or not b.is_file() or a.is_symlink() or b.is_symlink():
        return ["missing_or_unsafe_program_files"]
    if not a.resolve().is_relative_to(root.resolve()) or not b.resolve().is_relative_to(root.resolve()):
        return ["program_source_outside_repository"]
    manifest=json.loads(a.read_text(encoding="utf-8"))
    receipt=json.loads(b.read_text(encoding="utf-8"))
    errors=validate_manifest(manifest)+validate_receipt(receipt)
    for lane in manifest.get("lanes",[]):
        p=(root/lane.get("first_source_anchor_path",""))
        if not p.exists() or not p.is_file() or p.is_symlink() or not p.resolve().is_relative_to(root.resolve()):
            errors.append("missing_source_anchor:"+lane.get("lane_id","?"))
    return sorted(set(errors))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=ROOT)
    args=p.parse_args()
    e=validate_bundle(args.root)
    print(json.dumps({"contract":"KOMPAS_PRO_SCIENTIFIC_EDGE_PROGRAM_V2_1",
                      "structural_plan_only":True,"scientific_admission_claim":False,
                      "real_ai_agents_executed":0,"native_workflow_runs_executed_by_validator":0,
                      "errors":e,"structural_validation":"PASS" if not e else "FAIL"},sort_keys=True))
    if e:raise SystemExit(1)

if __name__=="__main__":
    main()
