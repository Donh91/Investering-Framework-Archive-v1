#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, hashlib
from typing import Any, Dict, List
from research_governance_common import GOV, load_json, specialist_states, action_of, target_of, evidence_fp, digest, persist_json, append_csv

BASE=GOV/"meta_orchestrator_v1"
POLICY=BASE/"POLICY.json"
STATE=BASE/"STATE.json"
QUEUE=BASE/"EXECUTION_QUEUE.json"
LEDGER=BASE/"ACTION_LEDGER.csv"
MEMORY=GOV/"memory_novelty_v1/STATE.json"
VOI=GOV/"decision_impact_v1/STATE.json"
SENTINEL=GOV/"adversarial_sentinel_v1/STATE.json"

CANONICAL_REVIEW_ACTIONS={"PROMOTE_FOR_CANONICAL_REVIEW","CANONICAL_REVIEW_JUSTIFIED"}
DATA_ACTIONS={"REPAIR_TRANSFORM","QUARANTINE_STALE_SOURCE","VERIFY_PROVENANCE","CROSSCHECK_APPROVED_FREE_SOURCE","RETRY_SAME_OWNER","REQUEST_BOUNDED_GAPFILL"}
FREEZE_ACTIONS={"OPEN_PROSPECTIVE_FORWARD_TEST","FREEZE_NEW_CHALLENGER"}

def _memory_for(memory,source,action,target):
    for r in memory.get("proposal_results",[]):
        if r.get("source")==source and r.get("action")==action and r.get("target")==target:
            return r.get("novelty_verdict")
    return None

def orchestrate(policy:Dict[str,Any], states:Dict[str,Dict[str,Any]], memory:Dict[str,Any], voi:Dict[str,Any], sentinel:Dict[str,Any]) -> Dict[str,Any]:
    sv=sentinel.get("verdict","PASS")
    conflicts=[]
    rawq=voi.get("queue",[])
    for i,a in enumerate(rawq):
        for b in rawq[i+1:]:
            ta=str(a.get("target") or "").strip().lower(); tb=str(b.get("target") or "").strip().lower()
            if ta and ta==tb:
                aa=str(a.get("action") or ""); ab=str(b.get("action") or "")
                if ({aa,ab} & CANONICAL_REVIEW_ACTIONS) and ({aa,ab} & {"DEPRIORITIZE","ARCHIVE_UNTESTABLE","STOP_RETRYING"}):
                    conflicts.append({"target":ta,"source_a":a.get("source"),"action_a":aa,"source_b":b.get("source"),"action_b":ab})
    if conflicts:
        sv="BLOCK_RESEARCH_ESCALATION"
    if sv in {"FIREWALL_BREACH","BLOCK_RESEARCH_ESCALATION"}:
        primary={
            "orchestrator_action":"HALT_ESCALATION_AND_AUDIT","source":"ADVERSARIAL_SENTINEL",
            "target":sv,"execution_mode":"AUTO_LOCAL_RESEARCH",
            "reason":"adversarial sentinel blocks escalation until governance finding is resolved",
            "impact_tier":"HIGH",
        }
        queue=[primary]
    else:
        queue=[]
        for item in voi.get("queue",[]):
            source=item.get("source"); action=item.get("action"); target=item.get("target")
            tier=item.get("impact_tier","LOW")
            novelty=_memory_for(memory,source,action,target)
            if tier=="BLOCKED" or novelty in {"DUPLICATE_EXACT","DUPLICATE_NEAR"}:
                oa="SUPPRESS_DUPLICATE_RESEARCH"; mode="AUTO_LOCAL_RESEARCH"
            elif action in CANONICAL_REVIEW_ACTIONS and tier=="HIGH":
                oa="PREPARE_CANONICAL_REVIEW"; mode="REQUIRES_CANONICAL_REVIEW"
            elif source=="SOURCE_RECOVERY" and action in DATA_ACTIONS and tier=="HIGH":
                oa="PRIORITIZE_DATA_INTEGRITY"; mode="AUTO_LOCAL_RESEARCH"
            elif action=="GENERATE_PAID_DATA_VOI_PACKET":
                oa="QUEUE_VOI_REVIEW"; mode="REQUIRES_VOI_REVIEW"
            elif tier in {"HIGH","MEDIUM"}:
                oa="QUEUE_BOUNDED_RESEARCH"; mode="REQUIRES_PROSPECTIVE_FREEZE" if action in FREEZE_ACTIONS else "AUTO_LOCAL_RESEARCH"
            elif tier=="LOW":
                oa="WAIT_FOR_EVIDENCE"; mode="AUTO_OBSERVE"
            else:
                oa="CONTINUE_MONITORING"; mode="AUTO_OBSERVE"
            queue.append({
                "orchestrator_action":oa,"source":source,"specialist_action":action,"target":target,
                "impact_tier":tier,"decision_surface":item.get("decision_surface"),
                "execution_mode":mode,"novelty_verdict":novelty,
                "reason":item.get("reason",""),"evidence_fingerprint":item.get("evidence_fingerprint",""),
                "canonical_effect":False,"portfolio_execution":False,"paid_data_authorized":False,
            })
        rank={
            "PREPARE_CANONICAL_REVIEW":0,"PRIORITIZE_DATA_INTEGRITY":1,"QUEUE_BOUNDED_RESEARCH":2,
            "QUEUE_VOI_REVIEW":3,"SUPPRESS_DUPLICATE_RESEARCH":4,"WAIT_FOR_EVIDENCE":5,"CONTINUE_MONITORING":6,
        }
        queue.sort(key=lambda x:(rank.get(x["orchestrator_action"],99), {"HIGH":0,"MEDIUM":1,"LOW":2,"NONE":3,"BLOCKED":4}.get(x.get("impact_tier"),9), str(x.get("source"))))
        primary=queue[0] if queue else {
            "orchestrator_action":"WAIT_FOR_EVIDENCE","source":"NONE","target":"NONE",
            "execution_mode":"AUTO_OBSERVE","reason":"no actionable specialist research state","impact_tier":"LOW"
        }
    maxheavy=int(policy.get("max_concurrent_heavy_workstreams",1))
    active=[]
    for q in queue:
        if q["orchestrator_action"] in {"PREPARE_CANONICAL_REVIEW","PRIORITIZE_DATA_INTEGRITY","QUEUE_BOUNDED_RESEARCH","QUEUE_VOI_REVIEW"}:
            if len(active)<maxheavy: active.append(q)
    return {
        "contract":"RESEARCH_META_ORCHESTRATOR_STATE_v1",
        "authority":"RESEARCH_ONLY_NON_CANONICAL",
        "primary_action":primary["orchestrator_action"],"primary_source":primary.get("source"),
        "primary_target":primary.get("target"),"primary_execution_mode":primary.get("execution_mode"),
        "reason":primary.get("reason"),"queue":queue,"queue_n":len(queue),
        "active_heavy_workstreams":active,"max_concurrent_heavy_workstreams":maxheavy,
        "sentinel_verdict":sv,"controller_conflicts":conflicts,
        "evidence_fingerprint":digest({"memory":memory,"voi":voi,"sentinel":sentinel,"states":states}),
        "canonical_effect":False,"portfolio_execution":False,"paid_data_authorized":False,
        "deep_research_authorized":False,"external_provider_calls_authorized":False,
    }

def persist(state):
    persist_json(STATE,state)
    persist_json(QUEUE,{"contract":"RESEARCH_META_EXECUTION_QUEUE_v1","authority":"RESEARCH_ONLY_NON_CANONICAL","queue":state["queue"],"active_heavy_workstreams":state["active_heavy_workstreams"],"canonical_effect":False})
    aid=hashlib.sha256((state["primary_action"]+"|"+str(state["primary_source"])+"|"+str(state["primary_target"])+"|"+state["evidence_fingerprint"]).encode()).hexdigest()[:20]
    append_csv(LEDGER,["action_id","primary_action","primary_source","primary_target","execution_mode","sentinel_verdict","evidence_fingerprint","canonical_effect"],{
        "action_id":aid,"primary_action":state["primary_action"],"primary_source":state["primary_source"],
        "primary_target":state["primary_target"],"execution_mode":state["primary_execution_mode"],
        "sentinel_verdict":state["sentinel_verdict"],"evidence_fingerprint":state["evidence_fingerprint"],"canonical_effect":"false"
    },"action_id",aid)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--dry-run",action="store_true"); args=ap.parse_args()
    policy=load_json(POLICY,{})
    if policy.get("authority")!="RESEARCH_ONLY_NON_CANONICAL" or any(policy.get(k) is not False for k in ("canonical_effect","automatic_canonical_write","automatic_paid_data_authorization","portfolio_execution")):
        raise SystemExit("meta orchestrator firewall invalid")
    state=orchestrate(policy,specialist_states(),load_json(MEMORY,{}),load_json(VOI,{}),load_json(SENTINEL,{}))
    if args.dry_run: print(json.dumps(state,indent=2,sort_keys=True)); return
    persist(state); print(json.dumps(state,indent=2,sort_keys=True))
if __name__=="__main__": main()
