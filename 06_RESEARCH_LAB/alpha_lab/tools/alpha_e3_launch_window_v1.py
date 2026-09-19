#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, re, sys, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from scripts.api_agent.meme_alpha_robinhood_pons_v2 import (
    CHAIN_ID_HEX, PONS_V2_FACTORY, TOKEN_LAUNCHED_TOPIC0, parse_token_launched_log, rpc_call
)

UA="alpha-lab-e3-launch-window/1.0"
CA_RE=re.compile(r"0x[a-fA-F0-9]{40}")
OVERLAP=5

def now()->str: return datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
def sha(b:bytes)->str: return hashlib.sha256(b).hexdigest()
def atomic(p:Path,obj:Any):
    p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+".tmp")
    t.write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n"); t.replace(p)
def fetch(url:str,timeout=15):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"text/html,application/xhtml+xml"})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        b=r.read(); return b, int(getattr(r,"status",200)), now()
def rpc_health(url:str):
    cid=rpc_call(url,"eth_chainId",[],timeout=15,attempts=2)
    if str(cid).lower()!=CHAIN_ID_HEX: raise RuntimeError(f"WRONG_CHAIN:{cid}")
    head=int(rpc_call(url,"eth_blockNumber",[],timeout=15,attempts=2),16)
    return head
def logs(url:str,a:int,b:int):
    q={"address":PONS_V2_FACTORY,"topics":[TOKEN_LAUNCHED_TOPIC0],"fromBlock":hex(a),"toBlock":hex(b)}
    rows=rpc_call(url,"eth_getLogs",[q],timeout=20,attempts=2)
    if not isinstance(rows,list): raise RuntimeError("LOG_RESULT_NOT_LIST")
    return rows
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--prereg",type=Path,required=True); ap.add_argument("--state",type=Path,required=True)
    ap.add_argument("--evidence",type=Path,required=True); ap.add_argument("--max-seconds",type=int,default=3300)
    ap.add_argument("--poll-seconds",type=int,default=15); ap.add_argument("--lag",type=int,default=5)
    a=ap.parse_args()
    spec=json.loads(a.prereg.read_text())
    required=("experiment_id","first_party_surface_url","first_party_surface_content_sha256","external_benchmark_definition_sha256","external_edge_budget_minutes","first_party_authentication_status","frozen_at_utc")
    missing=[k for k in required if spec.get(k) in (None,"")]
    if missing: raise SystemExit("E3_PREREG_INVALID:MISSING:"+",".join(missing))
    if spec.get("experiment_id")!="E3_DELTA_PUBLISH": raise SystemExit("E3_PREREG_INVALID:EXPERIMENT")
    if spec.get("first_party_authentication_status")!="AUTHENTICATED_FIRST_PARTY": raise SystemExit("E3_PREREG_INVALID:SOURCE_AUTH")
    for k in ("first_party_surface_content_sha256","external_benchmark_definition_sha256"):
        v=str(spec.get(k,"")).lower()
        if len(v)!=64 or any(c not in "0123456789abcdef" for c in v): raise SystemExit("E3_PREREG_INVALID:HASH:"+k)
    try:
        if float(spec["external_edge_budget_minutes"])<=0: raise ValueError
    except (TypeError,ValueError): raise SystemExit("E3_PREREG_INVALID:EDGE_BUDGET")
    surface=str(spec["first_party_surface_url"])
    rpcs=[x.strip() for x in os.environ.get("ROBINHOOD_RPC_URLS","").split(",") if x.strip()]
    if len(rpcs)<2: raise SystemExit("TWO_RPCS_REQUIRED")
    state=json.loads(a.state.read_text()) if a.state.exists() else {"cursor":None,"seen_logs":[],"seen_ca":[],"started_at":now(),"last_safe_head":None}
    out=a.evidence; out.parent.mkdir(parents=True,exist_ok=True)
    deadline=time.time()+a.max_seconds; deadman=time.time(); seq=0
    while time.time()<deadline:
        seq+=1; obs={"observed_at_utc":now(),"seq":seq,"surface":surface,"data_health":"UNKNOWN","rpc":[]}
        try:
            heads=[]
            for u in rpcs:
                try: h=rpc_health(u); heads.append(h); obs["rpc"].append({"provider":u.split("/")[2],"ok":True,"head":h})
                except Exception as e: obs["rpc"].append({"provider":u.split("/")[2],"ok":False,"error":type(e).__name__})
            if len(heads)<2: raise RuntimeError("REDUNDANT_RPC_HEALTH_FAILED")
            safe=min(heads)-a.lag
            if state["cursor"] is None: state["cursor"]=max(0,safe-OVERLAP)
            start=max(0,int(state["cursor"])-OVERLAP); requested=max(0,safe-start+1)
            sets=[]; decoded=[]
            for u in rpcs[:2]:
                raw=logs(u,start,safe); keys={json.dumps({k:x.get(k) for k in ("address","topics","data","blockNumber","blockHash","transactionHash","transactionIndex","logIndex","removed")},sort_keys=True,separators=(",",":")) for x in raw}; sets.append(keys)
                for x in raw:
                    ev=parse_token_launched_log(x,rpc_source=u.split("/")[2])
                    if ev: decoded.append(ev)
            if sets[0]!=sets[1]: raise RuntimeError("PROVIDER_DISAGREEMENT")
            ded={f"{e.get('block_hash')}:{e.get('transaction_hash')}:{e.get('log_index')}":e for e in decoded}
            new=[e for k,e in ded.items() if k not in state["seen_logs"]]
            state["seen_logs"]=list(dict.fromkeys(state["seen_logs"]+list(ded.keys())))[-5000:]
            state["cursor"]=safe+1; obs.update({"requested_coverage":requested,"returned_coverage":requested,"safe_head":safe,"new_launches":new})
            body,status,content_observed_at=fetch(surface); text=body.decode("utf-8","replace"); cas=sorted(set(x.lower() for x in CA_RE.findall(text)))
            newca=[x for x in cas if x not in state["seen_ca"]]; state["seen_ca"]=sorted(set(state["seen_ca"]+cas))
            obs.update({"content_observed_at_utc":content_observed_at,"surface_http_status":status,"source_content_sha256":sha(body),"published_ca_candidates":cas,"new_ca_candidates":newca,"data_health":"PASS"})
            if state.get("last_safe_head") is None or safe>int(state["last_safe_head"]):
                state["last_safe_head"]=safe
                deadman=time.time()
        except Exception as e:
            obs.update({"data_health":"DEGRADED","error":type(e).__name__+":"+str(e)[:300],"requested_coverage":None,"returned_coverage":None})
        with out.open("a") as f: f.write(json.dumps(obs,sort_keys=True)+"\n")
        atomic(a.state,state)
        if time.time()-deadman>60: raise SystemExit("DEADMAN_EXCEEDED")
        time.sleep(a.poll_seconds)
    return 0
if __name__=="__main__": raise SystemExit(main())
