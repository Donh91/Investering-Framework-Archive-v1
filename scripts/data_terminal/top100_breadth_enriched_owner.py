#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, statistics, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE="https://api.coingecko.com/api/v3/coins/markets"
UA={"User-Agent":"Investering-Breadth-Enriched-Owner/1.0","Accept":"application/json"}
STABLE={"usdt","usdc","dai","fdusd","usde","usds","tusd","usdd","pyusd","frax","usdp","gusd","lusd","susd","crvusd"}
AUTHORITY={"binding":False,"canonical_acceptance":False,"state_change":False,"portfolio_action":False}

def canonical(v:Any)->bytes:return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()

def fetch()->bytes:
    q={"vs_currency":"usd","order":"market_cap_desc","per_page":150,"page":1,"sparkline":"false","price_change_percentage":"24h"}
    req=urllib.request.Request(BASE+"?"+urllib.parse.urlencode(q),headers=UA)
    with urllib.request.urlopen(req,timeout=25) as r: raw=r.read()
    if not raw: raise RuntimeError("empty_coingecko_payload")
    return raw

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument("--output-dir",type=Path,required=True);a=ap.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
    raw=fetch(); rows=json.loads(raw)
    if not isinstance(rows,list) or len(rows)<100: raise RuntimeError("incomplete_universe")
    benchmark={}; filtered=[]
    for rank,row in enumerate(rows,1):
        if not isinstance(row,dict): continue
        symbol=str(row.get("symbol") or "").lower(); ch=row.get("price_change_percentage_24h")
        if symbol in {"btc","eth"} and isinstance(ch,(int,float)): benchmark[symbol]=float(ch)
        if symbol in STABLE or ch is None or row.get("market_cap") is None: continue
        filtered.append({"asset_id":row.get("id"),"symbol":symbol,"source_rank":rank,"market_cap_usd":float(row["market_cap"]),"price_usd":float(row["current_price"]),"change_24h_pct":float(ch)})
    universe=filtered[:100]
    if len(universe)!=100 or "btc" not in benchmark or "eth" not in benchmark: raise RuntimeError("breadth_identity_or_benchmark_missing")
    changes=[r["change_24h_pct"] for r in universe]; adv=sum(x>0 for x in changes); dec=sum(x<0 for x in changes); flat=100-adv-dec
    membership=[{"rank":i+1,"asset_id":r["asset_id"]} for i,r in enumerate(universe)]
    agg={
      "constituent_count":100,"advancers":adv,"decliners":dec,"flat":flat,"advance_ratio":round(adv/100,6),
      "median_return_24h_pct":round(statistics.median(changes),6),"equal_weight_mean_return_24h_pct":round(statistics.fmean(changes),6),
      "btc_return_24h_pct":benchmark["btc"],"eth_return_24h_pct":benchmark["eth"],
      "outperforming_btc_count":sum(x>benchmark["btc"] for x in changes),"outperforming_eth_count":sum(x>benchmark["eth"] for x in changes),
      "membership_hash":sha(canonical(membership))
    }
    now=datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
    out={"contract":"TOP100_BREADTH_ENRICHED_OWNER_v1","status":"PASS","retrieved_at_utc":now,"source":"COINGECKO_MARKET_CAP","aggregate":agg,"constituents":universe,"interpolation":False,"forward_fill":False,"authority":AUTHORITY}
    (a.output_dir/"raw_source_payload.json").write_bytes(raw);(a.output_dir/"owner_snapshot.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    (a.output_dir/"receipt.json").write_text(json.dumps({"contract":"TOP100_BREADTH_ENRICHED_RECEIPT_v1","status":"PASS","payload_sha256":sha(raw),"owner_sha256":sha(canonical(out)),"membership_hash":agg["membership_hash"],"authority":AUTHORITY},indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"PASS",**{k:agg[k] for k in ("advancers","decliners","flat","advance_ratio","median_return_24h_pct","equal_weight_mean_return_24h_pct","outperforming_btc_count","outperforming_eth_count")}},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
