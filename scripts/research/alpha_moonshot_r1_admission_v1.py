#!/usr/bin/env python3
"""R1 source/clock/route admission. Zero network, no simulation, no trading."""
from __future__ import annotations
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

CONTRACT = "ALPHA_MOONSHOT_R1_CASE_V1"
ENTRY = ("FIRST_PUBLICLY_OBSERVABLE_AND_EXECUTABLE", "+5m", "+15m", "+30m")
EXIT = ("+1h", "+6h", "+24h", "+7d")
TICKETS = (500, 2000)

def stamp(x):
    if not isinstance(x,str) or not x: return None
    try:
        d=datetime.fromisoformat(x.replace("Z","+00:00"))
        return d.astimezone(timezone.utc) if d.tzinfo else None
    except (ValueError,TypeError,OverflowError): return None

def result(case):
    if case.get("contract") != CONTRACT: return {"state":"BLOCKED","reason":"CONTRACT_INVALID"}
    name=case.get("case_id")
    if not isinstance(name,str) or not name: return {"state":"BLOCKED","reason":"CASE_ID_INVALID"}
    missing=[]
    for k in ("chain_id","token_id","pool_id","source_refs","source_exact_version_hash","source_delivery_verified","matched_control_id"):
        v=case.get(k)
        if v in (None,"",[],{}) or (k=="source_delivery_verified" and v is not True):
            missing.append(k)
    if type(case.get("chain_id")) is not int or case.get("chain_id",0)<=0:
        if "chain_id" not in missing:missing.append("chain_id")
    times=("discovery_at_utc","source_first_available_at_utc","pool_first_executable_at_utc","source_version_first_observed_at_utc")
    for k in times:
        if stamp(case.get(k)) is None:missing.append(k)
    if missing:return {"case_id":name,"state":"DATA_BLOCKED","missing":sorted(set(missing)),"economic_edge":"NOT_ASSESSED"}
    if stamp(case["source_version_first_observed_at_utc"])>stamp(case["source_first_available_at_utc"]):
        return {"case_id":name,"state":"DATA_BLOCKED","missing":["source_exact_version_was_not_observed_by_claimed_source_availability"],"economic_edge":"NOT_ASSESSED"}
    eligible=max(stamp(case[k]) for k in times)
    route=case.get("route_proof")
    if not isinstance(route,dict) or route.get("exact_historical_pool_state") is not True or route.get("fee_tax_gas_slippage_proven") is not True:
        return {"case_id":name,"state":"DATA_BLOCKED","missing":["historical_buy_sell_route_and_cost_proof"],"earliest_eligible_at_utc":eligible.isoformat(),"economic_edge":"NOT_ASSESSED"}
    if route.get("exit_endpoint_complete") is not True:
        return {"case_id":name,"state":"DATA_BLOCKED","missing":["complete_exit_endpoint"],"earliest_eligible_at_utc":eligible.isoformat(),"economic_edge":"NOT_ASSESSED"}
    return {"case_id":name,"state":"TECHNICAL_ADMISSION_CANDIDATE","earliest_eligible_at_utc":eligible.isoformat(),"entry_anchors":list(ENTRY),"exit_horizons":list(EXIT),"ticket_usd":list(TICKETS),"economic_edge":"NOT_ASSESSED","trading_authority":False,"note":"Evidence flags are claimant-supplied; independent raw source verification still required."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("case_json",type=Path)
    args=p.parse_args()
    case=json.loads(args.case_json.read_text(encoding="utf-8"))
    print(json.dumps(result(case),indent=2,sort_keys=True))
if __name__=="__main__":main()
