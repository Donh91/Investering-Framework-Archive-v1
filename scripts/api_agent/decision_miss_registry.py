from __future__ import annotations
import argparse,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from typing import Any

def cb(v:Any)->bytes:return (json.dumps(v,sort_keys=True,separators=(",",":"))+"\n").encode()
def now()->str:return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def key(m:dict[str,Any])->str:
    v={k:m.get(k) for k in ("phase","miss_type","decision_reference","outcome_reference")};return hashlib.sha256(cb(v)).hexdigest()[:16]

def clean_attribution(rows:Any)->list[dict[str,Any]]:
    if not isinstance(rows,list):return []
    out=[]
    for row in rows[:10]:
        if not isinstance(row,dict):continue
        out.append({
            "signal_name":row.get("signal_name"),
            "evidence_reference":row.get("evidence_reference"),
            "observed_role":row.get("observed_role"),
            "incremental_value_status":row.get("incremental_value_status","NOT_ESTABLISHED"),
            "confidence":row.get("confidence"),
            "notes":row.get("notes"),
        })
    return out

def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument("--audit",type=Path,required=True);ap.add_argument("--registry",type=Path,required=True);a=ap.parse_args();audit=json.loads(a.audit.read_text()) if a.audit.exists() else {"misses":[]}
    if a.registry.exists():
        try:reg=json.loads(a.registry.read_text())
        except Exception:reg={}
    else:reg={}
    reg.setdefault("contract","ADAPTIVE_DECISION_MISS_REGISTRY_v1");reg.setdefault("status","ACTIVE_SHADOW_RESEARCH_ONLY");reg.setdefault("items",{});reg.setdefault("authority",{"market_rule_change":False,"canonical_state":False,"portfolio_action":False,"automatic_sensor_promotion":False,"automatic_weight_change":False})
    reg["attribution_semantics"]={"observed_alignment_is_causal_edge":False,"direct_incremental_value_requires_explicit_unique_contribution_evidence":True,"aligned_sensor_count_proves_independence":False,"automatic_weight_change":False}
    ts=now();touched=[]
    for m in audit.get("misses",[]):
        if not isinstance(m,dict):continue
        mid="DM-"+key(m);prev=reg["items"].get(mid,{})
        reg["items"][mid]={"miss_id":mid,"phase":m.get("phase"),"miss_type":m.get("miss_type"),"decision_reference":m.get("decision_reference"),"outcome_reference":m.get("outcome_reference"),"miss_description":m.get("miss_description"),"proposed_metric_name":m.get("proposed_metric_name"),"counterfactual_theory":m.get("counterfactual_theory"),"confidence":m.get("confidence"),"signal_attribution":clean_attribution(m.get("signal_attribution")),"first_seen_utc":prev.get("first_seen_utc") or ts,"last_seen_utc":ts,"observation_count":int(prev.get("observation_count",0) or 0)+1,"validation_semantics":"DISCOVERY_ONLY_DOES_NOT_VALIDATE_PROPOSED_METRIC","attribution_semantics":"DESCRIPTIVE_UNLESS_DIRECT_UNIQUE_CONTRIBUTION_EVIDENCE","authority":{"evidence_only":True,"portfolio_action":False,"market_rule_change":False,"sensor_weight_change":False}}
        touched.append(mid)
    reg["updated_at_utc"]=ts;reg["item_count"]=len(reg["items"]);a.registry.parent.mkdir(parents=True,exist_ok=True);a.registry.write_bytes(cb(reg));print(json.dumps({"status":"PASS","touched":len(touched),"registry_items":len(reg["items"])},sort_keys=True))
if __name__=="__main__":main()
