#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json,subprocess
from datetime import datetime,timezone,timedelta
from pathlib import Path
from typing import Any

ROOT=Path("06_RESEARCH_LAB/shared_row_model_tournament_v1")
CONTRACT=ROOT/"CORE_FAMILY_PROSPECTIVE_CONTRACT_v1.json"
FREEZE=ROOT/"TRANSFORM_FREEZE_REGISTRY.json"
CATALYST=ROOT/"data/CATALYST_LEDGER.csv"
LEDGER=ROOT/"data/PROSPECTIVE_SHARED_ROW_LEDGER.csv"
HOURLY=Path("03_DAILY_CAPTURE_LOGS/hourly")
BREADTH=Path("03_DAILY_CAPTURE_LOGS/breadth_rich/LATEST.json")
BTCD=Path("03_DAILY_CAPTURE_LOGS/btc_d_cmc/latest/BTC_D_DIRECT_SOURCE_DAILY_2023_CURRENT.csv")

def parse_ts(v:str)->datetime:return datetime.fromisoformat(v.replace("Z","+00:00")).astimezone(timezone.utc)
def iso(x:datetime)->str:return x.replace(microsecond=0).isoformat().replace("+00:00","Z")
def canon(x:Any)->str:return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def git_sha()->str:
    try:return subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    except Exception:return "UNAVAILABLE_LOCAL_GIT_SHA"

def load_hourly(cutoff:datetime)->list[dict[str,Any]]:
    out=[]
    for p in sorted(HOURLY.rglob("*.csv")):
        try:
            with p.open(newline="",encoding="utf-8-sig") as f:
                for r in csv.DictReader(f):
                    t=r.get("timestamp_utc")
                    if not t:continue
                    ts=parse_ts(t)
                    if ts>cutoff:continue
                    try:e=float(r["ethbtc_close"])
                    except Exception:continue
                    out.append({"ts":ts,"ethbtc":e,"path":str(p)})
        except Exception:continue
    out.sort(key=lambda x:x["ts"])
    return out

def read_ledger_ids()->set[str]:
    if not LEDGER.exists():return set()
    with LEDGER.open(newline="",encoding="utf-8-sig") as f:return {r["event_id"] for r in csv.DictReader(f)}

def latest_breadth()->dict[str,Any]|None:
    if not BREADTH.exists():return None
    try:return json.loads(BREADTH.read_text())
    except Exception:return None

def latest_btcd()->list[dict[str,Any]]:
    if not BTCD.exists():return []
    rows=[]
    with BTCD.open(newline="",encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            try:
                if r.get("source_status") not in {"PASS","READY","OK",""}:continue
                rows.append({"date":r["date_utc"],"value":float(r["btc_d_close"]),"provider":r.get("source_provider"),"convention":r.get("source_convention")})
            except Exception:continue
    return rows[-3:]

def catalyst_tags(obs:datetime)->tuple[str,str,str]:
    regime="POST_CAT_STRUCT_ETF_2024" if obs>=datetime(2024,2,1,tzinfo=timezone.utc) else "PRE_CAT_STRUCT_ETF_2024"
    date=obs.date().isoformat()
    if CATALYST.exists():
        with CATALYST.open(newline="",encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                if r.get("tag_type")=="VERIFIED_EXOGENOUS_SHOCK" and r.get("timestamp_or_period")==date:
                    return regime,"VERIFIED_EXOGENOUS_SHOCK",r["catalyst_evidence_id"]
    return regime,"NO_VERIFIED_EXOGENOUS_CATALYST_MATCH","NONE_VERIFIED_AT_CUTOFF"

def build(now_override:str|None=None)->dict[str,Any]:
    contract=json.loads(CONTRACT.read_text()); freeze=json.loads(FREEZE.read_text())
    floor=parse_ts(contract["prospective_eligibility_start"])
    wall=parse_ts(now_override) if now_override else datetime.now(timezone.utc)
    if wall<floor:return {"status":"NOT_ELIGIBLE","reason":"BEFORE_PROSPECTIVE_ELIGIBILITY_START","prospective_eligibility_start":iso(floor)}
    fr={x["family_id"]:x for x in freeze["families"]}
    core=["ETHBTC_PERSISTENCE","BREADTH_SURVIVAL","BTCD_PATH_RECLAIM"]
    if not all(fr[x].get("status")=="READY" and fr[x].get("candidate_decision_contract_status")=="READY" for x in core):
        return {"status":"NOT_ELIGIBLE","reason":"CORE_CONTRACT_NOT_READY"}
    hourly=load_hourly(wall)
    if not hourly:return {"status":"NOT_ELIGIBLE","reason":"DIRECT_ETHBTC_HOURLY_MISSING"}
    obs=hourly[-1]["ts"]
    if obs<floor:return {"status":"NOT_ELIGIBLE","reason":"LATEST_DIRECT_ETHBTC_ROW_PRE_FREEZE"}
    breadth=latest_breadth()
    if not breadth:return {"status":"NOT_ELIGIBLE","reason":"BREADTH_OWNER_LATEST_MISSING"}
    bts=breadth.get("retrieval_timestamp") or breadth.get("retrieved_at_utc") or breadth.get("freeze_timestamp")
    if not bts or parse_ts(str(bts))<floor:return {"status":"NOT_ELIGIBLE","reason":"BREADTH_OWNER_CAPTURE_PRE_FREEZE"}
    agg=breadth.get("aggregate") or {}
    adv,dec=agg.get("advancers"),agg.get("decliners")
    if not isinstance(adv,(int,float)) or not isinstance(dec,(int,float)):
        return {"status":"NOT_ELIGIBLE","reason":"BREADTH_ADVANCER_DECLINER_MISSING"}
    bhash=breadth.get("membership_hash")
    if not bhash:return {"status":"NOT_ELIGIBLE","reason":"BREADTH_MEMBERSHIP_HASH_MISSING"}
    br_state="BROAD_MAJORITY" if adv>dec else "NON_BROAD_MAJORITY"; br_perm=br_state=="BROAD_MAJORITY"
    bt=latest_btcd()
    if len(bt)<3:return {"status":"NOT_ELIGIBLE","reason":"BTCD_THREE_SETTLED_PRINTS_MISSING"}
    a,b,c=[x["value"] for x in bt]
    if c<b<a: bd_state="FALLING_PATH"
    elif b<a and c>b: bd_state="RISING_RECLAIM"
    else: bd_state="MIXED_PATH"
    bd_perm=bd_state=="FALLING_PATH"
    valid=[x for x in hourly if x["ts"]>=obs.replace(microsecond=0)-timedelta(hours=168)]
    if not valid:return {"status":"NOT_ELIGIBLE","reason":"ETHBTC_168H_WINDOW_MISSING"}
    latest=float(valid[-1]["ethbtc"])
    side="ABOVE" if latest>0.03 else "BELOW" if latest<0.03 else "AT"
    consecutive=0
    for x in reversed(valid):
        s="ABOVE" if x["ethbtc"]>0.03 else "BELOW" if x["ethbtc"]<0.03 else "AT"
        if s!=side:break
        consecutive+=1
    eperm=side=="ABOVE"
    decisions={"C01_ETHBTC":eperm,"C02_BREADTH":br_perm,"C03_BTCD":bd_perm,"C04_ETHBTC_BREADTH":eperm and br_perm,"C05_ETHBTC_BTCD":eperm and bd_perm,"C06_BREADTH_BTCD":br_perm and bd_perm,"C07_SIMPLE_3":eperm and br_perm and bd_perm}
    regime,catalyst,ceid=catalyst_tags(obs)
    event_id="PSR_"+obs.strftime("%Y%m%dT%H%M%SZ")
    if event_id in read_ledger_ids():return {"status":"NOOP","reason":"EVENT_ALREADY_FROZEN","event_id":event_id}
    row={"event_id":event_id,"observation_timestamp_utc":iso(obs),"information_cutoff_utc":iso(obs),"source_version_commit":git_sha(),"regime_tag":regime,"catalyst_tag":catalyst,"catalyst_evidence_id":ceid,"ethbtc_raw_source":"BINANCE_DIRECT_ETHBTC_HOURLY","ethbtc_raw_value":latest,"ethbtc_window_inputs":canon({"lookback_hours":168,"sample_count":len(valid),"consecutive_same_side":consecutive}),"ethbtc_derived_state":side,"ethbtc_missing":False,"breadth_membership_version":breadth.get("method_version") or breadth.get("contract") or "C5E_TOP100_BREADTH_OWNER_v1_2","breadth_membership_hash":bhash,"breadth_raw_inputs":canon({"advancers":adv,"decliners":dec,"flat":agg.get("flat"),"advance_ratio":agg.get("advance_ratio")}),"breadth_derived_state":br_state,"breadth_missing":False,"btcd_provider":"CoinMarketCap","btcd_denominator_version":"CMC_DIRECT_SOURCE_CONVENTION","btcd_raw_inputs":canon(bt),"btcd_derived_state":bd_state,"btcd_missing":False,"etf_missing":True,"leverage_missing":True,"stablecoin_missing":True,"cfgi_missing":True,"full_stack_missingness":canon({"status":"NOT_YET_ELIGIBLE","reason":"FULL_STACK_DECISION_CONTRACT_BLOCKED"}),"candidate_decisions":decisions,"preexisting_registered_outcomes":"ETHBTC_FORWARD_RELATIVE_RETURN_OUTCOME_v1"}
    return {"status":"ELIGIBLE_SHARED_ROW","row":row,"event_id":event_id,"candidate_decisions":decisions}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path);ap.add_argument("--now-utc");ap.add_argument("--status-only",action="store_true");a=ap.parse_args()
    result=build(a.now_utc)
    if a.output and result.get("row") is not None:
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result["row"],indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="row"},sort_keys=True))
if __name__=="__main__":main()
