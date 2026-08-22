#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, hashlib
from pathlib import Path
from typing import Any, Dict, List
from research_governance_common import GOV, load_json, specialist_states, action_of, target_of, evidence_fp, reason_of, digest, persist_json, append_csv

BASE=GOV/"decision_impact_v1"
POLICY=BASE/"POLICY.json"
STATE=BASE/"STATE.json"
LEDGER=BASE/"VOI_LEDGER.csv"
MEMORY=GOV/"memory_novelty_v1/STATE.json"

TIER_ORDER={"HIGH":0,"MEDIUM":1,"LOW":2,"NONE":3,"BLOCKED":4}

ACTION_MAP={
    "PROMOTE_FOR_CANONICAL_REVIEW":("HIGH","ALTSEASON_ENTRY_ROTATION"),
    "INVESTIGATE_DATA_GAP":("HIGH","DATA_INTEGRITY"),
    "INVESTIGATE_DIVERGENCE":("HIGH","ALTSEASON_ENTRY_ROTATION"),
    "STRESS_TEST":("HIGH","ALTSEASON_ENTRY_ROTATION"),
    "RESEARCH_NEW_HYPOTHESIS":("HIGH","ALTSEASON_ENTRY_ROTATION"),
    "DEPRIORITIZE":("MEDIUM","SENSOR_PORTFOLIO_QUALITY"),
    "EXTEND_OBSERVATION":("LOW","CALIBRATION_QUALITY"),
    "CONTINUE_OBSERVING":("LOW","CALIBRATION_QUALITY"),
    "CANONICAL_REVIEW_JUSTIFIED":("HIGH","ALTSEASON_ENTRY_ROTATION"),
    "INVESTIGATE_RANGE_MISS":("HIGH","CALIBRATION_QUALITY"),
    "STRESS_TEST_REANCHOR":("HIGH","CALIBRATION_QUALITY"),
    "AUDIT_TRANSITION_FAKEOUT":("HIGH","ALTSEASON_ENTRY_ROTATION"),
    "INVESTIGATE_SLOW_BLEED_FAKE_ROTATION":("HIGH","ALTSEASON_ENTRY_ROTATION"),
    "AUDIT_GATE_CROSS_SIGNATURE":("HIGH","ALTSEASON_ENTRY_ROTATION"),
    "RESEARCH_NEW_PHASE_HYPOTHESIS":("HIGH","ALTSEASON_ENTRY_ROTATION"),
    "REVIEW_CALIBRATION_EVIDENCE":("MEDIUM","CALIBRATION_QUALITY"),
    "CONTINUE_CALIBRATION":("LOW","CALIBRATION_QUALITY"),
    "RECOVER_EVIDENCE_PATH":("MEDIUM","SENSOR_PORTFOLIO_QUALITY"),
    "RECOVER_EVALUATOR":("MEDIUM","SENSOR_PORTFOLIO_QUALITY"),
    "OPEN_PROSPECTIVE_FORWARD_TEST":("MEDIUM","SENSOR_PORTFOLIO_QUALITY"),
    "RUN_REDUNDANCY_CONFIRMATION":("MEDIUM","SENSOR_PORTFOLIO_QUALITY"),
    "RUN_INCREMENTAL_VALUE_TEST":("MEDIUM","SENSOR_PORTFOLIO_QUALITY"),
    "STRESS_TEST_REGIME_SPECIFICITY":("MEDIUM","SENSOR_PORTFOLIO_QUALITY"),
    "ARCHIVE_UNTESTABLE":("LOW","SENSOR_PORTFOLIO_QUALITY"),
    "REPAIR_TRANSFORM":("HIGH","DATA_INTEGRITY"),
    "QUARANTINE_STALE_SOURCE":("HIGH","DATA_INTEGRITY"),
    "CROSSCHECK_APPROVED_FREE_SOURCE":("MEDIUM","DATA_INTEGRITY"),
    "RETRY_SAME_OWNER":("MEDIUM","DATA_INTEGRITY"),
    "REQUEST_BOUNDED_GAPFILL":("MEDIUM","DATA_INTEGRITY"),
    "VERIFY_PROVENANCE":("MEDIUM","DATA_INTEGRITY"),
    "GENERATE_PAID_DATA_VOI_PACKET":("MEDIUM","DATA_INTEGRITY"),
    "DECLARE_NOT_TESTABLE":("NONE","DATA_INTEGRITY"),
    "STOP_RETRYING":("NONE","DATA_INTEGRITY"),
    "CONTINUE_SOURCE_MONITORING":("LOW","DATA_INTEGRITY"),
}

def _memory_verdict(memory: Dict[str,Any], source:str, action:str, target:str) -> str:
    for r in memory.get("proposal_results",[]):
        if r.get("source")==source and r.get("action")==action and r.get("target")==target:
            return str(r.get("novelty_verdict",""))
    return ""

def route(policy:Dict[str,Any], states:Dict[str,Dict[str,Any]], memory:Dict[str,Any]) -> Dict[str,Any]:
    queue=[]
    actionable_state_n=0
    for source,state in states.items():
        action=action_of(state)
        if not action: continue
        actionable_state_n += 1
        tier,surface=ACTION_MAP.get(action,("LOW","RESEARCH_OPERATIONS"))
        target=target_of(state)
        novelty=_memory_verdict(memory,source,action,target)
        rb=(reason_of(state)+" "+target).upper()
        if tier in {"HIGH","MEDIUM"} and any(k in rb for k in ("DISTRIBUTION","EXIT_RISK","EXIT RISK","CYCLE TOP","TOP RISK")):
            surface="DISTRIBUTION_EXIT_RISK"
        blocked=novelty in {"DUPLICATE_EXACT","DUPLICATE_NEAR"}
        if blocked: tier="BLOCKED"
        paid_review_only = action=="GENERATE_PAID_DATA_VOI_PACKET"
        reason=reason_of(state)
        if blocked: reason=f"novelty gate blocked duplicate proposal ({novelty})"
        elif action in {"DECLARE_NOT_TESTABLE","STOP_RETRYING"}:
            reason="terminal/closeout source state has no independent decision upside unless linked to a current high-value blocker"
        elif paid_review_only:
            reason="paid data may be relevant, but this router creates VOI review only and never authorizes spend"
        queue.append({
            "source":source,"action":action,"target":target,"decision_surface":surface,
            "impact_tier":tier,"reason":reason,"novelty_verdict":novelty or None,
            "evidence_fingerprint":evidence_fp(state),
            "paid_review_only":paid_review_only,
            "paid_data_authorized":False,"deep_research_authorized":False,
            "canonical_effect":False,"portfolio_execution":False,
        })
    queue.sort(key=lambda x:(TIER_ORDER.get(x["impact_tier"],9),x["source"],x["action"],x["target"]))
    if queue:
        primary=queue[0]
    else:
        primary={
            "source":"NONE","action":"NONE","target":"NONE","decision_surface":"NONE",
            "impact_tier":"NONE",
            "reason":(
                "specialist states resolved, but no actionable research proposal is active"
                if states else
                "no specialist states resolved"
            ),
            "paid_review_only":False
        }
    return {
        "contract":"RESEARCH_DECISION_IMPACT_VOI_STATE_v1",
        "authority":"RESEARCH_ONLY_NON_CANONICAL",
        "selected_source":primary["source"],"selected_action":primary["action"],"selected_target":primary["target"],
        "selected_decision_surface":primary["decision_surface"],"selected_impact_tier":primary["impact_tier"],
        "reason":primary["reason"],"queue":queue,"queue_n":len(queue),
        "resolved_specialist_state_n":len(states),"actionable_specialist_state_n":actionable_state_n,
        "evidence_fingerprint":digest(queue),
        "paid_data_authorized":False,"deep_research_authorized":False,
        "external_provider_calls_authorized":False,"canonical_effect":False,"portfolio_execution":False,
    }

def persist(state):
    persist_json(STATE,state)
    vid=hashlib.sha256((state["selected_source"]+"|"+state["selected_action"]+"|"+state["selected_target"]+"|"+state["evidence_fingerprint"]).encode()).hexdigest()[:20]
    append_csv(LEDGER,["voi_id","selected_source","selected_action","selected_target","impact_tier","decision_surface","evidence_fingerprint","paid_data_authorized","canonical_effect"],{
        "voi_id":vid,"selected_source":state["selected_source"],"selected_action":state["selected_action"],
        "selected_target":state["selected_target"],"impact_tier":state["selected_impact_tier"],
        "decision_surface":state["selected_decision_surface"],"evidence_fingerprint":state["evidence_fingerprint"],
        "paid_data_authorized":"false","canonical_effect":"false"
    },"voi_id",vid)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--dry-run",action="store_true"); args=ap.parse_args()
    policy=load_json(POLICY,{})
    if policy.get("authority")!="RESEARCH_ONLY_NON_CANONICAL" or any(policy.get(k) is not False for k in ("canonical_effect","automatic_paid_data_authorization","external_provider_calls_authorized")):
        raise SystemExit("VOI firewall invalid")
    state=route(policy,specialist_states(),load_json(MEMORY,{}))
    if args.dry_run: print(json.dumps(state,indent=2,sort_keys=True)); return
    persist(state); print(json.dumps(state,indent=2,sort_keys=True))
if __name__=="__main__": main()
