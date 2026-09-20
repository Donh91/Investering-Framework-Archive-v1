#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

ROUTES={"SELF_HEAL_SAFE","DETERMINISTIC_REPAIR","SOURCE_OWNER","SPECIALIST_AGENT","RESEARCH_EXPERIMENT","CODEX_REQUIRED","GOVERNANCE_REVIEW","WAIT_FOR_EVIDENCE","HUMAN_AUTHORITY","NO_ACTION"}

def read(p, default=None):
    try: return json.loads(p.read_text()) if p.exists() else default
    except Exception: return default

def h(x): return hashlib.sha256(json.dumps(x,sort_keys=True,default=str).encode()).hexdigest()[:20]

def finding(module,severity,route,reason,evidence,owner,next_action,stop,gate,confidence="MEDIUM"):
    assert route in ROUTES
    core={"module":module,"severity":severity,"route":route,"reason":reason,"evidence_refs":evidence,"owner":owner}
    return {**core,"fingerprint":h(core),"dedup_key":h({"m":module,"r":reason,"o":owner}),"root_cause_confidence":confidence,
            "cheapest_sufficient_executor":"DETERMINISTIC" if route in {"SELF_HEAL_SAFE","DETERMINISTIC_REPAIR","NO_ACTION","WAIT_FOR_EVIDENCE"} else "OWNER_OR_SPECIALIST",
            "next_action":next_action,"stop_condition":stop,"acceptance_gate":gate}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo-root",default="."); ap.add_argument("--output-root",default="research/framework_learning/weekly_forensics"); ap.add_argument("--mode",choices=["PRELIMINARY","FINAL"],default="FINAL"); ap.add_argument("--as-of-utc"); a=ap.parse_args()
    root=Path(a.repo_root); out=root/a.output_root
    now=datetime.fromisoformat(a.as_of_utc.replace("Z","+00:00")) if a.as_of_utc else datetime.now(timezone.utc)
    y,w,_=now.isocalendar(); gen=now.isoformat().replace("+00:00","Z")
    paths={
      "pullback":root/"04_MARKET_LEARNING/pullback_learning/LATEST.json",
      "eligibility":root/"04_MARKET_LEARNING/pullback_learning/ELIGIBILITY_STATUS_v1.json",
      "automation":root/"research/architecture_health/LATEST_AUTOMATION_HEALTH.json",
      "architecture":root/"research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json",
      "remediation":root/"research/remediation/LATEST_REMEDIATION_QUEUE.json",
      "compounding":root/"00_ARCHIVE_CONTROL/research_governance_v1/compounding_learning_v1/STATE.json",
      "phase1":root/"research/framework_intelligence/phase1/LATEST.json",
    }
    src={k:read(p,{}) or {} for k,p in paths.items()}; findings=[]

    pb=src["pullback"]; elig=src["eligibility"]
    suspended=(str(pb.get("eligibility_status",{}).get("status","")).startswith("SUSPENDED") or str(elig.get("status","")).startswith("SUSPENDED"))
    if suspended:
      findings.append(finding("PULLBACK_REENTRY","HIGH","GOVERNANCE_REVIEW","pullback episode eligibility is suspended; descriptive learning may continue but episode creation/maturation must remain blocked",
        ["04_MARKET_LEARNING/pullback_learning/LATEST.json","04_MARKET_LEARNING/pullback_learning/ELIGIBILITY_STATUS_v1.json"],"PULLBACK_ELIGIBILITY_OWNER",
        "resolve the existing eligibility-owner contract without inventing episodes or bypassing suspension","stop if a valid superseding eligibility contract already exists","VALID_ELIGIBILITY_CONTRACT_PLUS_EXISTING_PULLBACK_TESTS", "HIGH"))
    obs=pb.get("observation_count")
    findings.append(finding("PULLBACK_REENTRY","INFO","WAIT_FOR_EVIDENCE",f"preserve point-in-time pullback observations for weekly descriptive and near-miss learning; observation_count={obs}",
      ["04_MARKET_LEARNING/pullback_learning/LATEST.json"],"PULLBACK_LEARNING_LEDGER","continue observation collection and evaluate only fields available at observation time","stop if provenance/timestamps are incomplete","POINT_IN_TIME_PROVENANCE_PRESENT"))

    auto=src["automation"]; red=auto.get("red_count"); amber=auto.get("amber_count")
    blockers=auto.get("blockers") or []
    if red or blockers:
      findings.append(finding("META_HEALTH","HIGH","DETERMINISTIC_REPAIR",f"automation health contains active RED/blocker evidence (red={red}, amber={amber}, blockers={len(blockers)})",
        ["research/architecture_health/LATEST_AUTOMATION_HEALTH.json","research/remediation/LATEST_REMEDIATION_QUEUE.json"],"REMEDIATION_MATURATION",
        "deduplicate against the existing remediation queue and route only unresolved reproducible signatures","stop when finding is absent, superseded, already fixed, or requires semantic/budget change","EXISTING_TASK_SPECIFIC_POST_FIX_GATE","HIGH"))

    phase=src["phase1"]
    if phase.get("would_offer_to_master_monday") and not phase.get("live_consumed"):
      findings.append(finding("CONSUMPTION_HEALTH","MEDIUM","SOURCE_OWNER","high-value advisory evidence exists but is intentionally/not yet consumed by Master Monday",
        ["research/framework_intelligence/phase1/LATEST.json"],"FRAMEWORK_LEARNING_SUPERVISOR","carry only a compact advisory delta; do not grant live authority","stop if phase gate forbids consumption","MASTER_MONDAY_ADVISORY_FIREWALL_PASS"))

    comp=src["compounding"]; families=comp.get("hypothesis_families") or []
    matured=sum(int(x.get("matured_outcome_count_total") or 0) for x in families if isinstance(x,dict))
    findings.append(finding("LEARNING_MATURATION","INFO","NO_ACTION",f"weekly maturation snapshot: families={len(families)}, matured_outcomes={matured}",
      ["00_ARCHIVE_CONTROL/research_governance_v1/compounding_learning_v1/STATE.json"],"COMPOUNDING_LEARNING_CONTROLLER","retain delta-only learning and negative memory; no automatic promotion","stop if source authority is not research-only","NO_CANONICAL_PROMOTION"))

    missing=[str(p.relative_to(root)) for p in paths.values() if not p.exists()]
    if missing:
      findings.append(finding("DATA_EVIDENCE_INTEGRITY","HIGH","SOURCE_OWNER","required weekly evidence inputs are missing",
        missing,"FRAMEWORK_LEARNING_SUPERVISOR","restore or explicitly quarantine missing evidence; never coerce UNKNOWN to zero/false","stop if missing inputs are optional under current phase","REQUIRED_INPUTS_PRESENT_OR_EXPLICITLY_QUARANTINED","HIGH"))

    actionable=[x for x in findings if x["route"] not in {"NO_ACTION","WAIT_FOR_EVIDENCE"}]
    doc={"contract":"WEEKLY_FORENSICS_PACK_v1","authority":"RESEARCH_ONLY_NON_CANONICAL","mode":a.mode,"generated_at_utc":gen,"iso_year":y,"iso_week":w,
         "canonical_effect":False,"portfolio_execution":False,"automatic_market_semantic_change":False,"automatic_budget_guard_change":False,"automatic_promotion":False,
         "point_in_time_required":True,"unknown_is_not_zero":True,"existing_remediation_queue_is_sole_repair_queue":True,
         "modules":["PULLBACK_REENTRY","FORECAST_DECISION","ROTATION_TRANSMISSION","META_HEALTH","LEARNING_MATURATION","DATA_EVIDENCE_INTEGRITY"],
         "findings":findings,"actionable_count":len(actionable),"routing_contract":sorted(ROUTES),
         "master_monday_delta":{"authority":"ADVISORY_ONLY","items":[{"module":x["module"],"severity":x["severity"],"reason":x["reason"],"route":x["route"]} for x in actionable[:8]]}}
    out.mkdir(parents=True,exist_ok=True); (out/"LATEST.json").write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
    snap=out/"snapshots"/str(y)/f"W{w:02d}"; snap.mkdir(parents=True,exist_ok=True); (snap/f"{a.mode}.json").write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"PASS","mode":a.mode,"findings":len(findings),"actionable":len(actionable)}))
if __name__=="__main__": main()
