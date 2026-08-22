#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, hashlib
from typing import Any, Dict, List
from research_governance_common import ROOT, GOV, load_json, specialist_states, action_of, target_of, evidence_fp, firewall_flags, digest, persist_json, append_csv

BASE=GOV/"adversarial_sentinel_v1"
POLICY=BASE/"POLICY.json"
STATE=BASE/"STATE.json"
LEDGER=BASE/"FINDINGS_LEDGER.csv"
MEMORY=GOV/"memory_novelty_v1/STATE.json"
VOI=GOV/"decision_impact_v1/STATE.json"

def _finding(severity,code,source,detail):
    return {"severity":severity,"code":code,"source":source,"detail":detail}

def _shared_promotion_valid(state:Dict[str,Any]) -> bool:
    if action_of(state)!="PROMOTE_FOR_CANONICAL_REVIEW": return True
    target=target_of(state)
    ev=state.get("evidence_summary") or {}
    pair=(ev.get("pairwise_vs_baseline_7d") or {}).get(target)
    policy=load_json(ROOT/"06_RESEARCH_LAB/shared_row_model_tournament_v1/RESEARCH_NEXT_ACTION_POLICY_v1.json",{})
    try:
        pp=policy["trigger_floors"]["pairwise_relevance_decision"]
        return bool(
            pair and
            int(pair.get("resolved",0))>=int(pp["resolved_7d_divergences_min"]) and
            int(pair.get("distinct_regimes",0))>=int(pp["distinct_regimes_min"]) and
            int(pair.get("net_unique_wins",0))>=int(pp["net_unique_wins_or_failures_min"]) and
            float(pair.get("wilson_lower",-1))>float(pp["promotion_requires_unique_win_share_lower_bound_gt"]) and
            (pair.get("tail_non_deterioration") is True or not pp["tail_error_non_deterioration_required_for_promotion"])
        )
    except Exception:
        return False

def _cn_promotion_valid(state:Dict[str,Any]) -> bool:
    if action_of(state)!="CANONICAL_REVIEW_JUSTIFIED": return True
    packet=load_json(ROOT/"05_CYCLE_NAVIGATOR/autonomous_calibration_v1/PROMOTION_CANDIDATE.json",{})
    try:
        return packet.get("ready") is True and packet.get("prospective_review_required",True) is True and int(state.get("eligible_verified_row_n",0))>=int(packet.get("minimum_verified_rows",10**9))
    except Exception:
        return False

def evaluate(policy:Dict[str,Any], states:Dict[str,Dict[str,Any]], memory:Dict[str,Any], voi:Dict[str,Any]) -> Dict[str,Any]:
    findings=[]
    for source,state in states.items():
        for flag in firewall_flags(state):
            findings.append(_finding("CRITICAL","FIREWALL_FLAG_TRUE",source,f"{flag} violates research-only firewall"))
    if not _shared_promotion_valid(states.get("SHARED_ROW",{})):
        findings.append(_finding("BLOCK","PREMATURE_SHARED_ROW_PROMOTION","SHARED_ROW","promotion recommendation does not reproduce frozen pairwise prospective gate"))
    if not _cn_promotion_valid(states.get("CYCLE_NAVIGATOR",{})):
        findings.append(_finding("BLOCK","PREMATURE_CN_PROMOTION","CYCLE_NAVIGATOR","canonical review recommendation lacks a valid explicit prospective promotion packet/evidence floor"))
    dup={(r.get("source"),r.get("action"),r.get("target")) for r in memory.get("proposal_results",[]) if r.get("novelty_verdict") in {"DUPLICATE_EXACT","DUPLICATE_NEAR"}}
    for item in voi.get("queue",[]):
        key=(item.get("source"),item.get("action"),item.get("target"))
        if key in dup and item.get("impact_tier")!="BLOCKED":
            findings.append(_finding("BLOCK","NOVELTY_BYPASS",str(item.get("source")),"duplicate research proposal escaped novelty suppression"))
    src=states.get("SOURCE_RECOVERY",{})
    if action_of(src) in {"DECLARE_NOT_TESTABLE","STOP_RETRYING"}:
        if src.get("paid_data_authorized") is True or src.get("external_provider_calls_authorized") is True:
            findings.append(_finding("CRITICAL","TERMINAL_SOURCE_REOPENED","SOURCE_RECOVERY","terminal source state contains spend/provider authorization"))
    ledgers={
        "CYCLE_NAVIGATOR":ROOT/"05_CYCLE_NAVIGATOR/autonomous_calibration_v1/ACTION_LEDGER.csv",
        "SHADOW_REGISTRY":ROOT/"04_MARKET_LEARNING/shadow_registry/autonomous_portfolio_v1/ACTION_LEDGER.csv",
        "SOURCE_RECOVERY":ROOT/"00_ARCHIVE_CONTROL/source_recovery_controller_v1/ACTION_LEDGER.csv",
    }
    from research_governance_common import load_csv, AGGRESSIVE_ACTIONS
    for source,path in ledgers.items():
        seen=set()
        for r in load_csv(path):
            a=str(r.get("selected_action") or r.get("primary_action") or "").upper()
            fp=str(r.get("evidence_fingerprint") or "")
            if a in AGGRESSIVE_ACTIONS and fp:
                key=(a,fp)
                if key in seen:
                    findings.append(_finding("WATCH","REPEATED_AGGRESSIVE_FINGERPRINT",source,f"aggressive action {a} repeated with identical evidence fingerprint"))
                    break
                seen.add(key)
    if any(f["severity"]=="CRITICAL" for f in findings):
        verdict="FIREWALL_BREACH"
    elif any(f["severity"]=="BLOCK" for f in findings):
        verdict="BLOCK_RESEARCH_ESCALATION"
    elif findings:
        verdict="WATCH"
    else:
        verdict="PASS"
    return {
        "contract":"INDEPENDENT_RESEARCH_ADVERSARIAL_SENTINEL_STATE_v1",
        "authority":"RESEARCH_ONLY_NON_CANONICAL",
        "verdict":verdict,"finding_n":len(findings),"findings":findings,
        "evidence_fingerprint":digest({"states":states,"memory":memory,"voi":voi}),
        "canonical_effect":False,"portfolio_execution":False,
        "paid_data_authorized":False,"deep_research_authorized":False,
        "external_provider_calls_authorized":False,
    }

def persist(state):
    persist_json(STATE,state)
    for f in state.get("findings",[]):
        fid=hashlib.sha256((f["severity"]+"|"+f["code"]+"|"+f["source"]+"|"+f["detail"]+"|"+state["evidence_fingerprint"]).encode()).hexdigest()[:20]
        append_csv(LEDGER,["finding_id","severity","code","source","detail","evidence_fingerprint","canonical_effect"],{
            "finding_id":fid,**f,"evidence_fingerprint":state["evidence_fingerprint"],"canonical_effect":"false"
        },"finding_id",fid)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--dry-run",action="store_true"); args=ap.parse_args()
    policy=load_json(POLICY,{})
    if policy.get("authority")!="RESEARCH_ONLY_NON_CANONICAL" or policy.get("canonical_effect") is not False:
        raise SystemExit("sentinel firewall invalid")
    state=evaluate(policy,specialist_states(),load_json(MEMORY,{}),load_json(VOI,{}))
    if args.dry_run: print(json.dumps(state,indent=2,sort_keys=True)); return
    persist(state); print(json.dumps(state,indent=2,sort_keys=True))
if __name__=="__main__": main()
