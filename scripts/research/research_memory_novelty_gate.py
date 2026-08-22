#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, hashlib
from pathlib import Path
from typing import Any, Dict, List
from research_governance_common import ROOT, GOV, load_json, load_csv, normalize_text, jaccard, digest, current_proposals, specialist_states, persist_json, append_csv

BASE = GOV / "memory_novelty_v1"
POLICY = BASE / "POLICY.json"
STATE = BASE / "STATE.json"
INDEX = BASE / "MEMORY_INDEX.json"
LEDGER = BASE / "NOVELTY_LEDGER.csv"

def _prior_records() -> List[Dict[str,Any]]:
    records=[]
    for r in load_csv(LEDGER):
        records.append({
            "record_type":"NOVELTY_LEDGER",
            "source":r.get("source",""),
            "action":r.get("action",""),
            "target":r.get("target",""),
            "reason":r.get("reason",""),
            "evidence_fingerprint":r.get("evidence_fingerprint",""),
            "novelty_verdict":r.get("novelty_verdict",""),
        })
    for path in sorted(ROOT.glob("06_RESEARCH_LAB/**/25_FINAL_MACHINE_READABLE_VERDICT.json")):
        d=load_json(path,{})
        if isinstance(d,dict):
            records.append({
                "record_type":"FINAL_VERDICT",
                "path":path.relative_to(ROOT).as_posix(),
                "target":str(d.get("target") or d.get("sensor_id") or d.get("candidate_id") or ""),
                "action":str(d.get("verdict") or d.get("terminal_verdict") or ""),
                "reason":str(d.get("reason") or d.get("summary") or ""),
                "evidence_fingerprint":digest(d),
            })
    reg=load_json(ROOT/"04_MARKET_LEARNING/shadow_registry/REGISTRY.json",{})
    for s in (reg or {}).get("sensors",[]):
        records.append({
            "record_type":"EXISTING_SENSOR",
            "target":str(s.get("sensor_id","")),
            "family":str(s.get("family","")),
            "action":str(s.get("relevance_state","")),
            "reason":str(s.get("description") or s.get("notes") or ""),
            "evidence_fingerprint":digest(s),
        })
    return records

def classify(policy: Dict[str,Any], proposal: Dict[str,Any], records: List[Dict[str,Any]]) -> Dict[str,Any]:
    source, action, target = proposal["source"], proposal["action"], proposal["target"]
    fp=proposal.get("evidence_fingerprint","")
    same=[r for r in records if r.get("record_type")=="NOVELTY_LEDGER" and r.get("source")==source and r.get("action")==action and r.get("target")==target]
    for r in reversed(same):
        oldfp=r.get("evidence_fingerprint","")
        if oldfp and fp and oldfp==fp:
            verdict="DUPLICATE_EXACT"; reason="same source/action/target and same evidence fingerprint already passed through novelty gate"
            return _result(proposal,verdict,reason,r,1.0)
    if same and fp and any(r.get("evidence_fingerprint") and r.get("evidence_fingerprint")!=fp for r in same):
        r=same[-1]
        return _result(proposal,"REOPEN_WITH_NEW_EVIDENCE","same research target is recurring, but the evidence fingerprint changed",r,1.0)

    threshold=float(policy.get("near_duplicate_jaccard_min",0.78))
    ptext=" ".join([action,target,proposal.get("family",""),proposal.get("reason","")])
    best=None; bestsim=0.0
    for r in records:
        if r.get("record_type")!="NOVELTY_LEDGER":
            continue
        same_target=bool(target and normalize_text(target)==normalize_text(r.get("target","")))
        fam=proposal.get("family",""); same_family=bool(fam and normalize_text(fam)==normalize_text(r.get("family","")))
        if not (same_target or same_family):
            continue
        rtext=" ".join([r.get("action",""),r.get("target",""),r.get("family",""),r.get("reason","")])
        sim=jaccard(ptext,rtext)
        if sim>bestsim: bestsim,best=sim,r
    if best is not None and bestsim>=threshold:
        return _result(proposal,"DUPLICATE_NEAR",f"proposal is semantically near a prior gated proposal at deterministic token Jaccard {bestsim:.3f}",best,bestsim)
    return _result(proposal,"NOVEL","no prior gated proposal clears the conservative exact/near duplicate conditions",None,bestsim)

def _result(p,v,reason,match,sim):
    return {
        **p, "novelty_verdict":v, "novelty_reason":reason,
        "matched_record":match, "similarity":round(float(sim),6),
        "canonical_effect":False, "portfolio_execution":False,
        "paid_data_authorized":False, "deep_research_authorized":False,
    }

def evaluate(policy: Dict[str,Any], proposals: List[Dict[str,Any]], records: List[Dict[str,Any]]) -> Dict[str,Any]:
    results=[classify(policy,p,records) for p in proposals]
    if not results:
        selected={"novelty_verdict":"NO_NEW_HYPOTHESIS","source":"NONE","action":"NONE","target":"NONE","novelty_reason":"no active research-escalation proposal in specialist controller states"}
    else:
        order={"NOVEL":0,"REOPEN_WITH_NEW_EVIDENCE":1,"DUPLICATE_NEAR":2,"DUPLICATE_EXACT":3}
        selected=sorted(results,key=lambda r:(order.get(r["novelty_verdict"],9),r["source"],r["target"]))[0]
    fp=digest([{"source":p["source"],"action":p["action"],"target":p["target"],"evidence_fingerprint":p.get("evidence_fingerprint","")} for p in proposals])
    return {
        "contract":"RESEARCH_MEMORY_NOVELTY_STATE_v1",
        "authority":"RESEARCH_ONLY_NON_CANONICAL",
        "selected_verdict":selected["novelty_verdict"],
        "selected_source":selected.get("source"),
        "selected_action":selected.get("action"),
        "selected_target":selected.get("target"),
        "reason":selected.get("novelty_reason"),
        "proposal_n":len(results),
        "proposal_results":results,
        "evidence_fingerprint":fp,
        "canonical_effect":False,"portfolio_execution":False,
        "paid_data_authorized":False,"deep_research_authorized":False,
    }

def persist(state, records):
    persist_json(STATE,state)
    persist_json(INDEX,{"contract":"RESEARCH_MEMORY_INDEX_v1","authority":"RESEARCH_ONLY_NON_CANONICAL","records":records,"record_n":len(records),"canonical_effect":False})
    fields=["memory_id","source","action","target","reason","evidence_fingerprint","novelty_verdict","similarity","canonical_effect"]
    for r in state.get("proposal_results",[]):
        mid=hashlib.sha256((r["source"]+"|"+r["action"]+"|"+r["target"]+"|"+r.get("evidence_fingerprint","")).encode()).hexdigest()[:20]
        append_csv(LEDGER,fields,{
            "memory_id":mid,"source":r["source"],"action":r["action"],"target":r["target"],"reason":r.get("reason",""),
            "evidence_fingerprint":r.get("evidence_fingerprint",""),"novelty_verdict":r["novelty_verdict"],
            "similarity":r["similarity"],"canonical_effect":"false"
        },"memory_id",mid)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--dry-run",action="store_true"); args=ap.parse_args()
    policy=load_json(POLICY,{})
    if policy.get("authority")!="RESEARCH_ONLY_NON_CANONICAL" or policy.get("canonical_effect") is not False:
        raise SystemExit("memory novelty firewall invalid")
    records=_prior_records()
    state=evaluate(policy,current_proposals(specialist_states()),records)
    if args.dry_run: print(json.dumps(state,indent=2,sort_keys=True)); return
    persist(state,records); print(json.dumps(state,indent=2,sort_keys=True))
if __name__=="__main__": main()
