#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    try: return json.loads(path.read_text())
    except Exception: return None


def latest_hourly(root: Path, limit: int = 240) -> list[dict[str, Any]]:
    rows=[]
    for path in sorted(root.rglob("*.csv")):
        try:
            with path.open(newline="",encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    if row.get("timestamp_utc"):
                        rows.append(row)
        except Exception: continue
    rows.sort(key=lambda r:r.get("timestamp_utc","")); return rows[-limit:]


def f(row:dict[str,Any], key:str)->float|None:
    try:return float(row[key]) if row.get(key) not in (None,"") else None
    except Exception:return None


def ethbtc_block(rows:list[dict[str,Any]])->dict[str,Any]:
    vals=[(r.get("timestamp_utc"),f(r,"ethbtc_close"),f(r,"btc_close"),f(r,"eth_close")) for r in rows]
    vals=[x for x in vals if x[1] is not None]
    if not vals:return {"status":"UNAVAILABLE"}
    last=vals[-1][1]; recent=vals[-24:]
    above=sum(v[1]>=0.03 for v in recent); below=sum(v[1]<0.03 for v in recent)
    consecutive=0; side="ABOVE" if last>=0.03 else "BELOW"
    for v in reversed(vals):
        if (v[1]>=0.03)==(side=="ABOVE"):consecutive+=1
        else:break
    def ret(a,b):return None if a in (None,0) or b is None else round((b/a-1)*100,6)
    anchor=vals[-25] if len(vals)>=25 else vals[0]
    btc=ret(anchor[2],vals[-1][2]); eth=ret(anchor[3],vals[-1][3]); ratio=ret(anchor[1],vals[-1][1])
    mechanism="UNKNOWN"
    if btc is not None and eth is not None:
        if eth>0 and eth>btc: mechanism="POSITIVE_ETH_LEADERSHIP"
        elif eth<=0 and btc is not None and btc<eth: mechanism="DEFENSIVE_RELATIVE_SURVIVAL"
        else: mechanism="MIXED_OR_NO_LEADERSHIP"
    return {"status":"PASS","latest_close":last,"distance_to_0_0300_pct":round((0.03/last-1)*100,6),"recent_24h_closes_above_or_equal_0_0300":above,"recent_24h_closes_below_0_0300":below,"consecutive_side":side,"consecutive_count":consecutive,"latest_24h_mechanism":mechanism,"latest_24h_btc_return_pct":btc,"latest_24h_eth_return_pct":eth,"latest_24h_ethbtc_return_pct":ratio,"semantic_note":"Descriptive evidence only. Existing 0.0300 reference is monitored; no new threshold is created."}


def latest_path(root:Path, name:str)->Path|None:
    p=root/name
    return p if p.exists() else None


def main()->int:
    ap=argparse.ArgumentParser();
    ap.add_argument("--hourly-root",type=Path,required=True);ap.add_argument("--pfr",type=Path,required=True);ap.add_argument("--breadth",type=Path,required=True);ap.add_argument("--stablecoin",type=Path,required=True);ap.add_argument("--etf",type=Path,required=True);ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args(); rows=latest_hourly(a.hourly_root)
    breadth=read_json(a.breadth);stable=read_json(a.stablecoin);pfr=read_json(a.pfr);etf=read_json(a.etf)
    out={"contract":"EVIDENCE_CLOSURE_CONTEXT_v1","created_at_utc":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),"authority":{"canonical_state":False,"portfolio_action":False,"market_rule_change":False},"ethbtc_persistence":ethbtc_block(rows),"breadth_cross_section":breadth if isinstance(breadth,dict) else {"status":"UNAVAILABLE"},"pullback_forensics":pfr if isinstance(pfr,dict) else {"status":"UNAVAILABLE"},"stablecoin_deployment":stable if isinstance(stable,dict) else {"status":"UNAVAILABLE"},"settled_etf":etf if isinstance(etf,dict) else {"status":"UNAVAILABLE"},"frozen_reference_context":{"status":"DEFERRED_UNTIL_EXACT_REPOSITORY_PROVENANCE_IS_BOUND","rule":"Existing frozen references may be serialized only from exact repository provenance; never hardcode from conversation memory."},"notes":["Unknown evidence remains UNKNOWN.","Discovery gaps are not validation evidence.","This context is research/shadow evidence and cannot change market state or portfolio action."]}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"PASS","hourly_rows":len(rows),"ethbtc_status":out["ethbtc_persistence"]["status"],"breadth_status":out["breadth_cross_section"].get("status","PASS"),"pfr_status":out["pullback_forensics"].get("status","PASS")},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
