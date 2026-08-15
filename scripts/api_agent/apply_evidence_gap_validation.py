from __future__ import annotations
import argparse,json
from datetime import datetime,timezone
from pathlib import Path
from typing import Any

def cb(v:Any)->bytes:return (json.dumps(v,sort_keys=True,separators=(",",":"))+"\n").encode()
def now()->str:return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument("--registry",type=Path,required=True);ap.add_argument("--audit",type=Path,required=True);ap.add_argument("--min-episodes",type=int,default=3);ap.add_argument("--min-days",type=int,default=14);a=ap.parse_args()
    reg=json.loads(a.registry.read_text()) if a.registry.exists() else {"items":{}};audit=json.loads(a.audit.read_text()) if a.audit.exists() else {"results":[]};ts=now();touched=[]
    for r in audit.get("results",[]):
        gid=r.get("gap_id");item=(reg.get("items") or {}).get(gid)
        if not isinstance(item,dict):continue
        first=item.get("first_seen_utc");days=0
        try:days=max(0,(datetime.now(timezone.utc)-datetime.fromisoformat(str(first).replace("Z","+00:00"))).days)
        except Exception:pass
        n=int(r.get("non_discovery_episode_count",0) or 0);state=r.get("validation_state")
        eligible=bool(state=="USEFUL_RESEARCH_EVIDENCE" and r.get("incremental_value")=="SUPPORTED" and r.get("source_reliability")=="PASS" and n>=a.min_episodes and days>=a.min_days)
        item["validation"]={"updated_at_utc":ts,"state":"PROMOTION_REVIEW_ELIGIBLE" if eligible else state,"non_discovery_episode_count":n,"prospective_age_days":days,"incremental_value":r.get("incremental_value"),"source_reliability":r.get("source_reliability"),"decision_timing_value":r.get("decision_timing_value"),"false_signal_value":r.get("false_signal_value"),"evidence_references":r.get("evidence_references",[]),"counterevidence_references":r.get("counterevidence_references",[]),"rationale":r.get("rationale"),"discovery_episode_counts_as_validation":False,"automatic_promotion":False,"promotion_review_eligible":eligible}
        if state in {"REJECTED_NO_INCREMENTAL_VALUE","REJECTED_UNRELIABLE_SOURCE"}:item["closure_state"]="CLOSED";item["rejection_reason"]=state
        touched.append(gid)
    reg["updated_at_utc"]=ts;a.registry.write_bytes(cb(reg));print(json.dumps({"status":"PASS","touched":len(touched),"promotion_review_eligible":sum(1 for gid in touched if reg["items"][gid].get("validation",{}).get("promotion_review_eligible"))},sort_keys=True))
if __name__=="__main__":main()
