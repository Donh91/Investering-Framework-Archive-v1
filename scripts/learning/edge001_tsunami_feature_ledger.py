#!/usr/bin/env python3
"""EDGE-001 prospective point-in-time feature ledger. Research only."""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math
from datetime import datetime,timezone
from pathlib import Path

FREEZE_CONTRACT="OFFICIAL_DAILY_COMPASS_v1"
PROTECTION_CONTRACT="COMPASS_PROTECTION_TRACKER_v1"
PRIMARY={"ELEVATED","HIGH","CONFIRMED"}
CONTRACT="EDGE001_TSUNAMI_FEATURE_LEDGER_v1"
FREEZES=Path("04_MARKET_LEARNING/handlekompas/official/daily")
HOURLY=Path("03_DAILY_CAPTURE_LOGS/hourly")
BREADTH=Path("03_DAILY_CAPTURE_LOGS/breadth_rich")

def parse(v):
    if not isinstance(v,str): return None
    try:
        d=datetime.fromisoformat(v.replace("Z","+00:00"))
        return d.astimezone(timezone.utc) if d.utcoffset() is not None else None
    except ValueError:return None

def finite(v):
    try:
        x=float(v)
        return x if math.isfinite(x) else None
    except:return None

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def legal_knowledge(f):
    issued=parse(f.get("issued_at_utc")); ref=f.get("market_reference") or {}; obs=parse(ref.get("observation_open_utc"))
    candidates=[x for x in (issued,(obs.replace() if obs else None)) if x]
    if obs: candidates.append(obs.replace())
    # Official M6 contract already applies observation_open + 1h. Reproduce it exactly here.
    from datetime import timedelta
    k=obs+timedelta(hours=1) if obs else issued
    return max(issued,k) if issued and k else issued or k

def eligible(root):
    out=[]
    for p in sorted((root/FREEZES).rglob("CMP-*.json")) if (root/FREEZES).exists() else []:
        try:f=json.loads(p.read_text())
        except:continue
        t=f.get("protection_tracker") or {}; ref=f.get("market_reference") or {}; k=legal_knowledge(f)
        if f.get("contract")==FREEZE_CONTRACT and t.get("contract")==PROTECTION_CONTRACT and t.get("data_quality")=="OK" and t.get("pullback_risk_state") in PRIMARY and k and finite(ref.get("btc_usdt")) and finite(ref.get("eth_usdt")):
            out.append((p,f,t,k))
    return out

def hourly_row(root,k):
    p=root/HOURLY/f"{k:%Y/%m}/{k:%Y-%m-%d}.csv"
    if not p.exists(): return None,None
    best=None
    for r in csv.DictReader(io.StringIO(p.read_text(encoding="utf-8-sig"))):
        end=parse(r.get("source_window_end_utc"))
        if end and end<=k and (best is None or end>best[0]):best=(end,r)
    return (best[1] if best else None),(p if best else None)

def breadth_context(root,k):
    # Breadth is context only. Select only observations legally available by k.
    candidates=[]
    if (root/BREADTH).exists():
        for p in (root/BREADTH).rglob("*.json"):
            if p.name=="LATEST.json": continue
            try:j=json.loads(p.read_text())
            except:continue
            o=parse(((j.get("observation") or {}).get("cutoff_utc")) or j.get("retrieved_at_utc"))
            if o and o<=k:candidates.append((o,p,j))
    if not candidates:return {"status":"UNAVAILABLE","canonical_compatible":False}
    o,p,j=max(candidates,key=lambda x:x[0]); sem=j.get("evidence_semantics") or {}
    return {"status":"CONTEXT_ONLY","path":p.relative_to(root).as_posix(),"source_hash":sha(p),"observation_cutoff_utc":o.isoformat().replace("+00:00","Z"),"canonical_compatible":bool(sem.get("canonical_compatible") is True),"evidence_role":sem.get("evidence_role"),"registered_threshold_compatibility":sem.get("registered_threshold_compatibility"),"aggregate":j.get("aggregate")}

def frow(r,k):
    if not r:return {"state":"UNKNOWN_NO_LEGAL_HOURLY_ROW"}
    spot=r.get("spot_status"); der=r.get("derivatives_status")
    spot_fields={x:finite(r.get(x)) for x in ("btc_close","eth_close","ethbtc_close","btc_taker_buy_quote_share","eth_taker_buy_quote_share","btc_return_1h_pct","eth_return_1h_pct","ethbtc_return_1h_pct")} if spot=="PASS" else {}
    der_fields={x:finite(r.get(x)) for x in ("btc_oi_change_1h_pct","eth_oi_change_1h_pct","btc_funding_event_rate","eth_funding_event_rate","btc_long_short_ratio","eth_long_short_ratio")} if der=="PASS" else {}
    return {"state":"OBSERVED","knowledge_cutoff_utc":k.isoformat().replace("+00:00","Z"),"spot_status":spot,"derivatives_status":der,"spot":spot_fields if spot=="PASS" else None,"derivatives":der_fields if der=="PASS" else None,"btc_price_oi_state":r.get("btc_price_oi_state") if der=="PASS" else None,"eth_price_oi_state":r.get("eth_price_oi_state") if der=="PASS" else None}

def build(root):
    rows=[]
    for p,f,t,k in eligible(root):
        hr,hp=hourly_row(root,k)
        identity=str(f.get("compass_id"))+"|"+k.isoformat()
        rows.append({"feature_row_id":"TSUF-"+hashlib.sha256(identity.encode()).hexdigest()[:16],"compass_id":f.get("compass_id"),"warning_state":t.get("pullback_risk_state"),"warning_issued_at_utc":f.get("issued_at_utc"),"knowledge_timestamp":k.isoformat().replace("+00:00","Z"),"source_freeze_path":p.relative_to(root).as_posix(),"source_freeze_hash":sha(p),"hourly_source_path":hp.relative_to(root).as_posix() if hp else None,"hourly_source_hash":sha(hp) if hp else None,"features":frow(hr,k),"breadth_context":breadth_context(root,k),"labels":{"A0":"BLOCKED_BINARY","A1":"BLOCKED_BINARY","A2":"UNKNOWN_CANONICAL","A3":"CONTINUOUS_ONLY","M1":"CONTINUOUS_PARTIAL","M2":"CONTINUOUS","M3":"ACTIVE_FAIL_CLOSED"},"outcome_joined":False})
    return {"contract":CONTRACT,"row_count":len(rows),"collection_only":True,"outcome_joined":False,"warning_is_sell":False,"live_exit_rule":"NONE","rows":rows}

def main():
    a=argparse.ArgumentParser();a.add_argument("--repo-root",type=Path,default=Path.cwd());a.add_argument("--output",type=Path,required=True);x=a.parse_args()
    j=build(x.repo_root);x.output.parent.mkdir(parents=True,exist_ok=True);x.output.write_text(json.dumps(j,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"contract":j["contract"],"row_count":j["row_count"],"outcome_joined":j["outcome_joined"]}))
if __name__=="__main__":main()
