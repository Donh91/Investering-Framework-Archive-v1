from __future__ import annotations
import argparse, hashlib, json, os, time, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MODEL="gpt-5.6-luna"; PRICE_INPUT_PER_M=1.0; PRICE_OUTPUT_PER_M=6.0
STATES=["COLLECTING","INCONCLUSIVE_KEEP_COLLECTING","USEFUL_RESEARCH_EVIDENCE","REJECTED_NO_INCREMENTAL_VALUE","REJECTED_UNRELIABLE_SOURCE"]

def cb(v:Any)->bytes:return (json.dumps(v,sort_keys=True,separators=(",",":"))+"\n").encode()
def sh(v:Any)->str:return hashlib.sha256(cb(v)).hexdigest()
def parse_iso(v:Any):
    try:return datetime.fromisoformat(str(v).replace("Z","+00:00")).astimezone(timezone.utc)
    except Exception:return None

def recent_docs(roots:list[Path],limit:int)->list[dict[str,Any]]:
    ps=[]
    for r in roots:
        if r.exists():ps.extend(p for p in r.rglob("*.json") if p.is_file())
    ps.sort(key=lambda p:p.stat().st_mtime,reverse=True);out=[]
    for p in ps:
        if len(out)>=limit:break
        try:v=json.loads(p.read_text())
        except Exception:continue
        if isinstance(v,dict):out.append({"path":str(p),"mtime_utc":datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat().replace("+00:00","Z"),"sha256":sh(v),"value":v})
    return out

def schema()->dict[str,Any]:
    return {"type":"object","additionalProperties":False,"required":["status","results"],"properties":{"status":{"type":"string","enum":["READY","NO_VALIDATABLE_GAPS"]},"results":{"type":"array","maxItems":12,"items":{"type":"object","additionalProperties":False,"required":["gap_id","validation_state","non_discovery_episode_count","incremental_value","source_reliability","decision_timing_value","false_signal_value","evidence_references","counterevidence_references","rationale"],"properties":{"gap_id":{"type":"string"},"validation_state":{"type":"string","enum":STATES},"non_discovery_episode_count":{"type":"integer","minimum":0,"maximum":999},"incremental_value":{"type":"string","enum":["SUPPORTED","NOT_SUPPORTED","INCONCLUSIVE"]},"source_reliability":{"type":"string","enum":["PASS","DEGRADED","FAIL","UNKNOWN"]},"decision_timing_value":{"type":"string","enum":["IMPROVED","NO_CHANGE","WORSE","UNKNOWN"]},"false_signal_value":{"type":"string","enum":["IMPROVED","NO_CHANGE","WORSE","UNKNOWN"]},"evidence_references":{"type":"array","maxItems":12,"items":{"type":"string"}},"counterevidence_references":{"type":"array","maxItems":12,"items":{"type":"string"}},"rationale":{"type":"string","minLength":3,"maxLength":700}}}}}}

def call(key:str,ctx:dict[str,Any])->dict[str,Any]:
    inst=("You validate adaptive evidence gaps using only supplied repository evidence. The discovery episode for each gap is hypothesis-generation only and cannot validate the metric. Evaluate incremental information only in other windows, or historical observations whose source-time provenance clearly predates the discovery. Do not treat correlation or post-hoc fit as decision value. Prefer COLLECTING or INCONCLUSIVE when recurrence is insufficient. Reject when repeated non-discovery evidence shows no incremental value or the source is unreliable. You cannot promote a sensor, change a rule, threshold, weight, market state, or portfolio action.")
    payload={"model":MODEL,"reasoning":{"effort":"low","context":"current_turn"},"store":False,"max_output_tokens":2600,"instructions":inst,"input":[{"role":"user","content":[{"type":"input_text","text":json.dumps(ctx,sort_keys=True)}]}],"text":{"format":{"type":"json_schema","name":"evidence_gap_validation_v1","strict":True,"schema":schema()}}}
    req=urllib.request.Request("https://api.openai.com/v1/responses",data=cb(payload),headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=180) as r:return json.loads(r.read())
    except urllib.error.HTTPError as e:raise RuntimeError(f"openai_http_{e.code}:{e.read().decode(errors='replace')[:400]}") from e

def extract(resp:dict[str,Any])->dict[str,Any]:
    text=resp.get("output_text") or "".join(c.get("text","") for i in resp.get("output",[]) for c in i.get("content",[]) if c.get("type")=="output_text")
    if not text:raise ValueError("missing_output_text")
    out=json.loads(text)
    if out.get("status") not in {"READY","NO_VALIDATABLE_GAPS"}:raise ValueError("invalid_validation_output")
    return out

def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument("--gap-registry",type=Path,required=True);ap.add_argument("--evidence-root",action="append",type=Path,required=True);ap.add_argument("--output-dir",type=Path,required=True);ap.add_argument("--max-documents",type=int,default=60);a=ap.parse_args()
    registry=json.loads(a.gap_registry.read_text()) if a.gap_registry.exists() else {"items":{}}
    items=[]
    for gid,item in (registry.get("items") or {}).items():
        if not isinstance(item,dict):continue
        items.append({"gap_id":gid,"metric_name":item.get("metric_name"),"first_seen_utc":item.get("first_seen_utc"),"discovery_reference":item.get("evidence_reference"),"observation_count":item.get("observation_count"),"closure_state":item.get("closure_state"),"capability_hint":item.get("capability_hint"),"previous_validation":item.get("validation")})
    ds=recent_docs(a.evidence_root,max(1,min(a.max_documents,100)))
    ctx={"contract":"EVIDENCE_GAP_VALIDATION_INPUT_v1","gaps":items,"evidence_documents":ds,"rules":["Discovery episode cannot count as validation.","Require independent non-discovery evidence for incremental value.","Historical evidence is valid only when source-time provenance predates discovery.","Unknown stays unknown."]}
    a.output_dir.mkdir(parents=True,exist_ok=True);ctx_hash=sh(ctx);key=os.environ.get("OPENAI_API_KEY")
    if not items or not ds:out={"status":"NO_VALIDATABLE_GAPS","results":[]};resp={"id":None,"usage":{}}
    else:
        if not key:raise SystemExit("OPENAI_API_KEY_missing")
        resp=call(key,ctx);out=extract(resp)
    usage=resp.get("usage") if isinstance(resp.get("usage"),dict) else {};it=int(usage.get("input_tokens",0) or 0);ot=int(usage.get("output_tokens",0) or 0);cost=round((it*PRICE_INPUT_PER_M+ot*PRICE_OUTPUT_PER_M)/1_000_000,8)
    if cost>0.35:raise SystemExit(f"gap_validation_cost_exceeded:{cost}")
    (a.output_dir/"VALIDATION_AUDIT.json").write_bytes(cb(out));(a.output_dir/"VALIDATION_RECEIPT.json").write_bytes(cb({"contract":"EVIDENCE_GAP_VALIDATION_RECEIPT_v1","task":"EVIDENCE_GAP_VALIDATION","model":MODEL,"context_sha256":ctx_hash,"response_id":resp.get("id"),"input_tokens":it,"output_tokens":ot,"estimated_cost_usd":cost,"created_unix":int(time.time()),"authority":{"automatic_promotion":False,"market_rule_change":False,"canonical_state":False,"portfolio_action":False}}));print(json.dumps({"status":out["status"],"result_count":len(out.get("results",[])),"estimated_cost_usd":cost},sort_keys=True))
if __name__=="__main__":main()
