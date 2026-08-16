from __future__ import annotations
import argparse, hashlib, json, os, time, urllib.error, urllib.request
from pathlib import Path
from typing import Any

MODEL="gpt-5.6-luna"
PRICE_INPUT_PER_M=1.0; PRICE_OUTPUT_PER_M=6.0
PHASES=["PRE_BUY","BUY_TRANSITION","ALTSEASON_ROTATION","PULLBACK_DE_RISK","PULLBACK_REENTRY","DISTRIBUTION","EXIT","POST_CYCLE_LEARNING","UNKNOWN_PHASE"]
MISSES=["FALSE_BUY","MISSED_BUY","LATE_BUY","FALSE_DE_RISK","MISSED_DE_RISK_BEFORE_PULLBACK","LATE_DE_RISK_BEFORE_PULLBACK","MISSED_PULLBACK_REENTRY","LATE_PULLBACK_REENTRY","FALSE_REENTRY","MISSED_DISTRIBUTION_WARNING","LATE_EXIT","FALSE_EXIT","RANGE_MISS","PATH_MISS","TIMING_MISS","REGIME_MISS","DATA_GAP_ONLY","UNKNOWN_MISS"]
HINTS=["HOURLY_SEQUENCE","LIVE_BREADTH","PULLBACK_FORENSICS","SETTLED_ETF","FRED_MACRO","STABLECOIN_LIQUIDITY","EXISTING_REPO_DERIVATION","UNKNOWN_SOURCE"]
ATTR_ROLES=["SUPPORTED_DECISION","CONTRADICTED_DECISION","REDUNDANT_OR_DUPLICATIVE","CONTEXT_ONLY","UNKNOWN"]
INCREMENTAL=["DIRECTLY_SUPPORTED","OVERLAP_SUSPECTED","NOT_ESTABLISHED"]

def cb(v:Any)->bytes:return (json.dumps(v,sort_keys=True,separators=(",",":"))+"\n").encode()
def sh(v:Any)->str:return hashlib.sha256(cb(v)).hexdigest()

def docs(roots:list[Path],limit:int)->list[dict[str,Any]]:
    paths=[]
    for r in roots:
        if r.exists():paths.extend(p for p in r.rglob("*.json") if p.is_file())
    paths.sort(key=lambda p:p.stat().st_mtime,reverse=True);out=[]
    for p in paths:
        if len(out)>=limit:break
        try:v=json.loads(p.read_text())
        except Exception:continue
        if not isinstance(v,dict):continue
        text=json.dumps(v,sort_keys=True).lower()
        if not any(x in text for x in ("forecast","outcome","mature","actual","calibration","precision","miss","false_positive","false_negative","summary")):continue
        out.append({"path":str(p),"sha256":sh(v),"value":v})
    return out

def schema()->dict[str,Any]:
    attribution={
        "type":"array","maxItems":10,
        "items":{
            "type":"object","additionalProperties":False,
            "required":["signal_name","evidence_reference","observed_role","incremental_value_status","confidence","notes"],
            "properties":{
                "signal_name":{"type":"string","minLength":1,"maxLength":160},
                "evidence_reference":{"type":"string","minLength":1,"maxLength":300},
                "observed_role":{"type":"string","enum":ATTR_ROLES},
                "incremental_value_status":{"type":"string","enum":INCREMENTAL},
                "confidence":{"type":"string","enum":["LOW","MODERATE","HIGH"]},
                "notes":{"type":"string","minLength":1,"maxLength":400},
            },
        },
    }
    miss_properties={
        "phase":{"type":"string","enum":PHASES},
        "miss_type":{"type":"string","enum":MISSES},
        "decision_reference":{"type":"string","minLength":1,"maxLength":300},
        "outcome_reference":{"type":"string","minLength":1,"maxLength":300},
        "miss_description":{"type":"string","minLength":3,"maxLength":500},
        "proposed_metric_name":{"type":"string","minLength":3,"maxLength":160},
        "decision_relevance":{"type":"string","minLength":3,"maxLength":500},
        "missing_history_problem":{"type":"string","minLength":3,"maxLength":500},
        "desired_history_days":{"type":"integer","minimum":1,"maximum":730},
        "desired_cadence_minutes":{"type":"integer","minimum":1,"maximum":10080},
        "data_shape":{"type":"string","enum":["TIME_SERIES","POINT_IN_TIME","EVENT_STREAM","DERIVED_SERIES","CROSS_SECTION"]},
        "capability_hint":{"type":"string","enum":HINTS},
        "counterfactual_theory":{"type":"string","minLength":3,"maxLength":500},
        "confidence":{"type":"string","enum":["LOW","MODERATE","HIGH"]},
        "signal_attribution":attribution,
    }
    required=list(miss_properties.keys())
    return {
        "type":"object","additionalProperties":False,
        "required":["status","misses"],
        "properties":{
            "status":{"type":"string","enum":["READY","NO_SUPPORTED_MISSES"]},
            "misses":{
                "type":"array","maxItems":8,
                "items":{"type":"object","additionalProperties":False,"required":required,"properties":miss_properties},
            },
        },
    }

def call(key:str,ctx:dict[str,Any])->dict[str,Any]:
    inst=("You are a conservative decision-miss auditor for a shadow investment research system. Identify a miss only when supplied repository evidence contains a decision/forecast available before an outcome and a later outcome that supports the miss. Do not invent trades or claim the user should have acted. DATA_GAP_ONLY is preferred when evidence supports only missing information, not a demonstrated decision failure. For each supported miss, propose one observable evidence metric that might have reduced uncertainty. The miss episode is discovery-only and MUST NOT count as validation of that metric. Also record bounded signal attribution only for signals explicitly present in the supplied decision/outcome evidence. SUPPORTED_DECISION or CONTRADICTED_DECISION describe observed alignment only, not causal edge. Mark DIRECTLY_SUPPORTED incremental value only when the supplied evidence explicitly contains an ablation, paired counterfactual, or other direct unique-contribution test. Otherwise use OVERLAP_SUSPECTED or NOT_ESTABLISHED. Never infer sensor weights, change market semantics, or treat aligned sensor count as independent confirmation. No market rules, thresholds, weights, state or portfolio actions.")
    payload={"model":MODEL,"reasoning":{"effort":"low","context":"current_turn"},"store":False,"max_output_tokens":2600,"instructions":inst,"input":[{"role":"user","content":[{"type":"input_text","text":json.dumps(ctx,sort_keys=True)}]}],"text":{"format":{"type":"json_schema","name":"adaptive_decision_miss_v1_1","strict":True,"schema":schema()}}}
    req=urllib.request.Request("https://api.openai.com/v1/responses",data=cb(payload),headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=180) as r:return json.loads(r.read())
    except urllib.error.HTTPError as e:raise RuntimeError(f"openai_http_{e.code}:{e.read().decode(errors='replace')[:400]}") from e

def extract(resp:dict[str,Any])->dict[str,Any]:
    text=resp.get("output_text") or "".join(c.get("text","") for i in resp.get("output",[]) for c in i.get("content",[]) if c.get("type")=="output_text")
    if not text:raise ValueError("missing_output_text")
    out=json.loads(text)
    if out.get("status") not in {"READY","NO_SUPPORTED_MISSES"}:raise ValueError("invalid_status")
    return out

def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument("--analysis-root",action="append",type=Path,required=True);ap.add_argument("--gap-registry",type=Path,required=True);ap.add_argument("--output-dir",type=Path,required=True);ap.add_argument("--max-documents",type=int,default=24);a=ap.parse_args()
    ds=docs(a.analysis_root,max(1,min(a.max_documents,40)))
    try:gaps=json.loads(a.gap_registry.read_text()) if a.gap_registry.exists() else {}
    except Exception:gaps={}
    ctx={"contract":"ADAPTIVE_DECISION_MISS_AUDIT_INPUT_v1_1","documents":ds,"existing_evidence_gap_registry":gaps,"rules":["Discovery episode cannot validate its proposed metric.","Use only supplied repository evidence.","Prefer NO_SUPPORTED_MISSES over speculative hindsight.","Signal attribution is descriptive unless direct unique-contribution evidence exists.","Aligned sensor count is not proof of independence or marginal value."]}
    a.output_dir.mkdir(parents=True,exist_ok=True);ctx_hash=sh(ctx)
    prior=list(a.output_dir.parent.rglob("MISS_AUDIT_RECEIPT.json")) if a.output_dir.parent.exists() else []
    for p in prior[-100:]:
        try:
            if json.loads(p.read_text()).get("context_sha256")==ctx_hash:
                out={"status":"NO_SUPPORTED_MISSES","misses":[]};resp={"id":None,"usage":{}}
                break
        except Exception:continue
    else:
        key=os.environ.get("OPENAI_API_KEY")
        if not key:raise SystemExit("OPENAI_API_KEY_missing")
        resp=call(key,ctx);out=extract(resp)
    usage=resp.get("usage") if isinstance(resp.get("usage"),dict) else {};it=int(usage.get("input_tokens",0) or 0);ot=int(usage.get("output_tokens",0) or 0);cost=round((it*PRICE_INPUT_PER_M+ot*PRICE_OUTPUT_PER_M)/1_000_000,8)
    if cost>0.30:raise SystemExit(f"miss_audit_cost_exceeded:{cost}")
    gap_candidates=[]
    for m in out.get("misses",[]):
        gap_candidates.append({"metric_name":m["proposed_metric_name"],"decision_relevance":f"{m['phase']} / {m['miss_type']}: {m['decision_relevance']}","missing_history_problem":m["missing_history_problem"],"desired_history_days":m["desired_history_days"],"desired_cadence_minutes":m["desired_cadence_minutes"],"data_shape":m["data_shape"],"capability_hint":m["capability_hint"],"evidence_reference":f"DISCOVERY_ONLY::{m['decision_reference']}::{m['outcome_reference']}"})
    (a.output_dir/"MISS_AUDIT.json").write_bytes(cb(out));(a.output_dir/"GAP_AUDIT_FROM_MISSES.json").write_bytes(cb({"status":"READY" if gap_candidates else "NO_GAPS","candidates":gap_candidates}))
    receipt={"contract":"ADAPTIVE_DECISION_MISS_RECEIPT_v1_1","task":"DECISION_MISS_AUDIT","model":MODEL,"context_sha256":ctx_hash,"response_id":resp.get("id"),"input_tokens":it,"output_tokens":ot,"estimated_cost_usd":cost,"created_unix":int(time.time()),"discovery_events_are_validation":False,"signal_attribution_is_causal":False,"direct_incremental_value_requires_explicit_unique_contribution_evidence":True,"authority":{"market_rule_change":False,"canonical_state":False,"portfolio_action":False,"sensor_weight_change":False,"self_merge":False}}
    (a.output_dir/"MISS_AUDIT_RECEIPT.json").write_bytes(cb(receipt));print(json.dumps({"status":out["status"],"miss_count":len(out.get("misses",[])),"gap_candidate_count":len(gap_candidates),"estimated_cost_usd":cost},sort_keys=True))
if __name__=="__main__":main()
