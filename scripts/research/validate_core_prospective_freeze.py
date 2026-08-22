#!/usr/bin/env python3
from __future__ import annotations

import csv
import importlib.util
import json
import tempfile
from datetime import timedelta
from pathlib import Path

ROOT=Path("06_RESEARCH_LAB/shared_row_model_tournament_v1")
CORE=ROOT/"CORE_FAMILY_PROSPECTIVE_CONTRACT_v1.json"
OUTCOME=ROOT/"OUTCOME_CONTRACT_v1.json"
LEDGER=ROOT/"data/PROSPECTIVE_SHARED_ROW_LEDGER.csv"
FNP=ROOT/"14_DIVERGENCE_FNP_LEDGER.csv"
DETAIL=ROOT/"data/OUTCOME_DETAIL_LEDGER.csv"

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);assert spec and spec.loader;spec.loader.exec_module(module);return module

def header_only(src,dst):
    first=src.read_text(encoding="utf-8-sig").splitlines()[0]
    dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(first+"\n",encoding="utf-8")

def expect_raises(fn,needle):
    try:fn()
    except Exception as exc:
        if needle not in str(exc):raise AssertionError(f"expected {needle!r}, got {exc!r}")
        return
    raise AssertionError(f"expected exception containing {needle!r}")

def isoz(dt):return dt.replace(microsecond=0).isoformat().replace("+00:00","Z")

def main():
    m=load_module("core_materializer",Path("scripts/research/core_shared_row_materializer.py"))
    c=load_module("prospective_controller",Path("scripts/research/prospective_evidence_controller.py"))
    o=load_module("outcome_owner",Path("scripts/research/shared_row_outcome_owner.py"))
    contract=json.loads(CORE.read_text());outcome=json.loads(OUTCOME.read_text())
    assert contract["authority"]=="RESEARCH_ONLY_NON_CANONICAL"
    assert contract["legacy_equivalence"] is False and contract["no_backdating"] is True
    assert contract["candidate_decision_contract"]["complete_core_set_required"] is True
    assert contract["family_contracts"]["ETHBTC_PERSISTENCE"]["definition"]["lookback_rows"]==168
    assert outcome["freeze_before_first_eligible_row"] is True
    assert outcome["primary_classification"]["horizons_hours"]=={"24h":24,"72h":72,"7d":168}
    floor=m.parse_ts(contract["prospective_eligibility_start"])
    pre=m.build(isoz(floor-timedelta(seconds=1)))
    assert pre["status"]=="NOT_ELIGIBLE" and pre["reason"]=="BEFORE_PROSPECTIVE_ELIGIBILITY_START"

    with tempfile.TemporaryDirectory() as td_raw:
        td=Path(td_raw);hourly=td/"hourly";hourly.mkdir();breadth=td/"breadth.json";btcd=td/"btcd.csv";catalyst=td/"catalyst.csv";ledger=td/"rows.csv";fnp=td/"fnp.csv";detail=td/"detail.csv"
        header_only(LEDGER,ledger);header_only(FNP,fnp);header_only(DETAIL,detail)
        obs=floor+timedelta(hours=7)
        start=obs-timedelta(hours=199)
        hp=hourly/"fixture.csv"
        with hp.open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=["timestamp_utc","ethbtc_close","btc_close","eth_close"]);w.writeheader()
            for i in range(225):
                ts=start+timedelta(hours=i)
                w.writerow({"timestamp_utc":isoz(ts),"ethbtc_close":0.031+0.000001*i,"btc_close":100000+i,"eth_close":3100+i*0.1})
        breadth.write_text(json.dumps({"retrieval_timestamp":isoz(floor+timedelta(minutes=5)),"membership_hash":"fixture-membership-hash","contract":"C5E_TOP100_BREADTH_OWNER_v1_2","aggregate":{"advancers":60,"decliners":40,"flat":0,"advance_ratio":0.6}})+"\n")
        with btcd.open("w",newline="",encoding="utf-8") as f:
            fields=["date_utc","btc_d_close","source_provider","source_convention","source_verified_timestamp","print_status","data_quality","source_status"]
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
            for date,value in [("2026-08-20",58.0),("2026-08-21",57.0),("2026-08-22",57.5)]:
                w.writerow({"date_utc":date,"btc_d_close":value,"source_provider":"CoinMarketCap","source_convention":"CMC_DIRECT_SOURCE_CONVENTION: fixture","source_verified_timestamp":isoz(floor+timedelta(minutes=10)),"print_status":"SETTLED_COMPLETE_DATE","data_quality":"PASS","source_status":"PUBLIC_SOURCE_BACKED"})
        m.HOURLY=hourly;m.BREADTH=breadth;m.BTCD=btcd;m.CATALYST=catalyst;m.LEDGER=ledger
        result=m.build(isoz(obs))
        assert result["status"]=="ELIGIBLE_SHARED_ROW"
        row=result["row"];window=json.loads(row["ethbtc_window_inputs"])
        assert window["lookback_rows"]==168 and window["sample_count"]==168
        assert row["ethbtc_derived_state"]=="ABOVE" and row["breadth_derived_state"]=="BROAD_MAJORITY" and row["btcd_derived_state"]=="RISING_RECLAIM"
        expected={"C01_ETHBTC":True,"C02_BREADTH":True,"C03_BTCD":False,"C04_ETHBTC_BREADTH":True,"C05_ETHBTC_BTCD":False,"C06_BREADTH_BTCD":False,"C07_SIMPLE_3":False}
        assert result["candidate_decisions"]==expected

        c.LEDGER=ledger;c.FNP=fnp
        validated,_=c.validate_payload(dict(row));assert validated["event_id"]==row["event_id"]
        bad=dict(row);bad["candidate_decisions"]=dict(expected);bad["candidate_decisions"]["C07_SIMPLE_3"]=True
        expect_raises(lambda:c.validate_payload(bad),"violates frozen boolean contract")
        premature=dict(row);premature["outcome_24h"]="1"
        expect_raises(lambda:c.validate_payload(premature),"premature outcome")
        pre_row=dict(row);pre_row["observation_timestamp_utc"]=isoz(floor-timedelta(seconds=1));pre_row["information_cutoff_utc"]=pre_row["observation_timestamp_utc"]
        expect_raises(lambda:c.validate_payload(pre_row),"predates prospective eligibility start")
        zero=dict(row);zero["etf_missing"]=True;zero["etf_raw_value"]=0
        expect_raises(lambda:c.validate_payload(zero),"encoded as zero")
        row_path=td/"row.json";row_path.write_text(json.dumps(row)+"\n")
        first=c.ingest(row_path);assert first["status"]=="PASS" and first["divergences_frozen"]>0
        expect_raises(lambda:c.ingest(row_path),"event_id already frozen")
        noop=m.build(isoz(obs));assert noop["status"]=="NOOP" and noop["reason"]=="EVENT_ALREADY_FROZEN"

        o.ROWS=ledger;o.DETAIL=detail;o.HOURLY=hourly
        before=o.run(isoz(obs+timedelta(hours=23)));assert before["horizons_written"]==0
        after=o.run(isoz(obs+timedelta(hours=24)));assert after["horizons_written"]==1
        rr=o.read_csv(ledger);assert rr[0]["outcome_24h"] in {"0","1"} and rr[0]["outcome_72h"]=="" and rr[0]["outcome_7d"]==""
        dd=o.read_csv(detail);assert len(dd)==1 and dd[0]["horizon"]=="24h"
        repeat=o.run(isoz(obs+timedelta(hours=24)));assert repeat["horizons_written"]==0 and len(o.read_csv(detail))==1

    print(json.dumps({"status":"PASS","contract":"CORE_PROSPECTIVE_FREEZE_SYNTHETIC_GATE_v1","checks":["pre_freeze_rejected","168_retained_rows_exact","post_freeze_materializer","core_boolean_consistency","premature_outcome_rejected","missing_not_zero","duplicate_event_rejected","divergence_frozen","24h_not_early","24h_written_once"]},sort_keys=True))

if __name__=="__main__":main()
