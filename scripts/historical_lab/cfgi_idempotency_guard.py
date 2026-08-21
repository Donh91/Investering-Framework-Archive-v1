#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

LAB=Path("06_RESEARCH_LAB/historical_altseason_pullback_v1");ART=LAB/"artifacts";CONFIG=LAB/"config.json";CATALOG=ART/"EPISODE_CATALOG.json";BILLING=ART/"CFGI_BILLING.json";SUMMARY=ART/"BACKTEST_SUMMARY.json"
REQUIRED_PRIOR_OUTPUTS=["CFGI_BILLING.json","CFGI_COVERAGE.json","CFGI_FIELD_COVERAGE.json","cfgi_targeted.jsonl.gz","CFGI_EVENT_SIGNATURES.json","CFGI_EVENT_PATHS.jsonl.gz","RESEARCH_READINESS_MANIFEST.json","CFGI_CUMULATIVE_BILLING.json"]


def load(path:Path)->dict:return json.loads(path.read_text(encoding="utf-8"))


def candidate_events(catalog:dict)->list[dict]:
    c=catalog.get("cfgi_candidate_windows") or {};rows=[]
    for kind,key in (("PULLBACK","pullbacks"),("CONTROL","controls")):
        for row in c.get(key,[]):rows.append({"kind":kind,**row})
    return sorted(rows,key=lambda x:(x.get("event_utc",""),x.get("episode_id",x.get("control_id","")),x["kind"]))


def fingerprint()->str:
    cfg=load(CONFIG);catalog=load(CATALOG);payload={"contract":"CFGI_TARGETED_INPUT_FINGERPRINT_v1","cfgi_config":cfg["cfgi"],"candidate_events":candidate_events(catalog),"authority":cfg["authority"]};return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def existing_is_complete(fp:str)->bool:
    for name in REQUIRED_PRIOR_OUTPUTS:
        p=ART/name
        if not p.exists() or p.stat().st_size==0:return False
    try:billing=load(BILLING);manifest=load(ART/"RESEARCH_READINESS_MANIFEST.json");cumulative=load(ART/"CFGI_CUMULATIVE_BILLING.json")
    except Exception:return False
    if billing.get("status")!="PASS" or billing.get("input_fingerprint_sha256")!=fp:return False
    if cumulative.get("status")!="PASS" or cumulative.get("input_fingerprint_sha256")!=fp:return False
    if manifest.get("contract")!="RESEARCH_READINESS_MANIFEST_v3" or manifest.get("readiness_verdict")!="PASS" or manifest.get("blockers"):return False
    if manifest.get("automatic_promotion") is not False or manifest.get("historical_findings_max_classification")!="FORWARD_TEST":return False
    cfgi=manifest.get("cfgi") or {}
    if cfgi.get("time_alignment_contract")!="CFGI_ASOF_1H_NO_LOOKAHEAD_v1" or cfgi.get("no_lookahead") is not True:return False
    symbol_cov=cfgi.get("symbol_coverage") or {}
    for sym in load(CONFIG)["cfgi"]["symbols"]:
        if int((symbol_cov.get(sym) or {}).get("asof_available_slots") or 0)<=0:return False
    return True


def restore_summary_from_billing():
    if not SUMMARY.exists() or not BILLING.exists():return
    summary=load(SUMMARY);billing=load(BILLING);cumulative=load(ART/"CFGI_CUMULATIVE_BILLING.json") if (ART/"CFGI_CUMULATIVE_BILLING.json").exists() else {}
    summary.update({"cfgi_status":"TARGETED_ENRICHMENT_COMPLETE","cfgi_selected_event_count":len(billing.get("selected_events") or []),"cfgi_expected_worst_case_credits":billing.get("expected_worst_case_credits"),"cfgi_actual_credits_used_from_headers":billing.get("actual_credits_used_from_headers"),"cfgi_cumulative_actual_credits_used":cumulative.get("cumulative_actual_credits_used"),"cfgi_final_credits_remaining":billing.get("final_credits_remaining"),"cfgi_comparison_artifact":"CFGI_EVENT_SIGNATURES.json","interpretation_status":"DESCRIPTIVE_BOOTSTRAP_NOT_PROMOTED_TO_RULES","cfgi_idempotent_reuse":True,"cfgi_input_fingerprint_sha256":billing.get("input_fingerprint_sha256")});SUMMARY.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")


def stamp(fp:str):
    billing=load(BILLING)
    if billing.get("status")!="PASS":raise SystemExit("CFGI_IDEMPOTENCY_STAMP_BLOCKED billing_not_pass")
    billing["input_fingerprint_contract"]="CFGI_TARGETED_INPUT_FINGERPRINT_v1";billing["input_fingerprint_sha256"]=fp;BILLING.write_text(json.dumps(billing,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    cumulative_path=ART/"CFGI_CUMULATIVE_BILLING.json";cumulative=load(cumulative_path) if cumulative_path.exists() else {}
    if cumulative:cumulative["input_fingerprint_sha256"]=fp;cumulative_path.write_text(json.dumps(cumulative,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if SUMMARY.exists():summary=load(SUMMARY);summary["cfgi_input_fingerprint_sha256"]=fp;summary["cfgi_cumulative_actual_credits_used"]=cumulative.get("cumulative_actual_credits_used") if cumulative else None;SUMMARY.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"STAMPED","input_fingerprint_sha256":fp,"cumulative_actual_credits_used":cumulative.get("cumulative_actual_credits_used")},sort_keys=True))


def verify_budget()->dict:
    proc=subprocess.run(["python","scripts/historical_lab/cfgi_recovery_budget_guard.py"],check=True,capture_output=True,text=True)
    lines=[x.strip() for x in proc.stdout.splitlines() if x.strip()]
    if not lines:raise SystemExit("CFGI_BUDGET_GUARD_EMPTY_OUTPUT")
    guard=json.loads(lines[-1])
    if guard.get("status")!="PASS" or guard.get("blockers"):raise SystemExit("CFGI_BUDGET_GUARD_NOT_PASS")
    return guard


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--mode",choices=["check","stamp"],required=True);args=ap.parse_args();fp=fingerprint()
    if args.mode=="stamp":stamp(fp);return 0
    skip=existing_is_complete(fp);guard=None
    if skip:restore_summary_from_billing()
    else:guard=verify_budget()
    print(json.dumps({"contract":"CFGI_IDEMPOTENCY_GUARD_v2","input_fingerprint_sha256":fp,"skip_paid":skip,"reason":"EXACT_COMPLETE_PRIOR_ENRICHMENT_V3" if skip else "PAID_GAPFILL_OR_RECOVERY_REQUIRED_BUDGET_PASS","budget_plan":None if guard is None else guard.get("plan")},sort_keys=True));return 0


if __name__=="__main__":raise SystemExit(main())
