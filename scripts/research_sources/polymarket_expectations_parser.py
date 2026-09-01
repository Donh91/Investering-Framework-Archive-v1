#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any

CONTRACT="POLYMARKET_EXPECTATIONS_OFFLINE_PARSER_v0_1"
AUTHORITY={"binding":False,"canonical_acceptance":False,"state_change":False,"portfolio_action":False,"automatic_promotion":False}
NETWORK_COLLECTION="BLOCKED_PENDING_EXPLICIT_SOURCE_RIGHTS_CONTRACT"

class ProbeError(ValueError): pass
def sha256(b:bytes)->str: return hashlib.sha256(b).hexdigest()

def _point(row:Any)->tuple[float,float]|None:
    if not isinstance(row,dict): return None
    t=row.get("t",row.get("timestamp"))
    p=row.get("p",row.get("price"))
    try: return float(t),float(p)
    except (TypeError,ValueError): return None

def summarize_prices_history(raw:bytes)->dict[str,Any]:
    try: doc=json.loads(raw)
    except json.JSONDecodeError as e: raise ProbeError("invalid_json") from e
    rows=doc.get("history") if isinstance(doc,dict) else doc
    if not isinstance(rows,list): raise ProbeError("history_not_list")
    pts=[x for r in rows if (x:=_point(r)) is not None]
    if not pts: raise ProbeError("no_valid_history_points")
    pts.sort(key=lambda x:x[0])
    prices=[p for _,p in pts]
    if any(p<0 or p>1 for p in prices): raise ProbeError("probability_out_of_range")
    return {
        "contract":CONTRACT,"source":"POLYMARKET","network_collection":NETWORK_COLLECTION,
        "payload_sha256":sha256(raw),"payload_bytes":len(raw),"row_count":len(pts),
        "earliest_timestamp":pts[0][0],"latest_timestamp":pts[-1][0],
        "min_probability":min(prices),"max_probability":max(prices),
        "raw_persisted":False,"authority":AUTHORITY,
    }

def main()->int:
    ap=argparse.ArgumentParser(description="Offline-only parser until Polymarket storage/use contract is explicitly cleared.")
    ap.add_argument("--input",type=Path,required=True)
    a=ap.parse_args()
    raw=a.input.read_bytes()
    print(json.dumps(summarize_prices_history(raw),sort_keys=True,separators=(",",":")))
    return 0

if __name__=="__main__": raise SystemExit(main())
