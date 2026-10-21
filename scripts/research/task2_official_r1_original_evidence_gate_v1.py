#!/usr/bin/env python3
"""Task2 R1: source-bound original Compass issuance/outcome CENSUS, never scores.

Research-only on PUBLIC original official forecast/outcome JSONs. This audit does
not re-score source results, infer provider first-known or claim first delivery.
It intentionally preserves non-issued, absent, censored and v1/v2 histories.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import date,datetime,timedelta,timezone
from pathlib import Path

CONTRACT="TASK2_OFFICIAL_ORIGINAL_R1_RECEIPT_CENSUS_v1"
BASE=Path(__file__).resolve().parents[2]/"04_MARKET_LEARNING/handlekompas/official"
FIRST=date(2026,10,12)
LAST=date(2026,10,20)
CUTOFF="2026-10-21T12:00:00Z"
HORIZONS=("12h","72h","168h")
V3="OFFICIAL_DAILY_COMPASS_SCORING_v3"
EXPECTED_CONTRACT="OFFICIAL_DAILY_COMPASS_v1"
EXPECTED_OUTCOME="OFFICIAL_DAILY_COMPASS_OUTCOME_v1"
PRIVATE_GATE="ROUND3_COLLECTION_ONLY_ANALYSIS_OFF"

def utc(stamp):
    if not isinstance(stamp,str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z",stamp):
        raise ValueError("NOT_EXACT_UTC_TIMESTAMP")
    return datetime.fromisoformat(stamp[:-1]+"+00:00")
def blob_sha(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
def days():
    i=FIRST
    while i<=LAST:
        yield i
        i+=timedelta(days=1)
def preflight_forecast(doc,path,day):
    problems=[]
    expected=path.stem
    if doc.get("contract")!=EXPECTED_CONTRACT:problems.append("ORIGINAL_FORECAST_CONTRACT_MISMATCH")
    if doc.get("compass_id")!=expected:problems.append("ORIGINAL_ID_PATH_MISMATCH")
    issued=doc.get("issued_at_utc")
    try:
        t=utc(issued)
        if t.date()!=day:problems.append("ORIGINAL_ISSUE_DATE_FOLDER_MISMATCH")
        if t>utc(CUTOFF):problems.append("ISSUED_AFTER_FROZEN_CUTOFF")
    except (ValueError,TypeError):problems.append("ORIGINAL_ISSUE_CLOCK_INVALID")
    if not re.fullmatch(r"[0-9a-f]{64}",str(doc.get("compass_sha256"))):
        problems.append("ORIGINAL_FORECAST_SHA256_ABSENT")
    source=doc.get("source_bindings",{})
    market=source.get("auto_market_state",{}) if isinstance(source,dict) else {}
    if not isinstance(market,dict) or not isinstance(market.get("packet_path"),str) or not re.fullmatch(r"[0-9a-f]{64}",str(market.get("packet_sha256"))):
        problems.append("ORIGINAL_UPSTREAM_PACKET_BINDING_MISSING")
    version=doc.get("scoring_contract")
    if version not in ("OFFICIAL_DAILY_COMPASS_SCORING_v1","OFFICIAL_DAILY_COMPASS_SCORING_v2",V3):
        problems.append("ORIGINAL_SCORING_VERSION_UNKNOWN")
    if not isinstance(doc.get("outcome_maturity"),dict):
        problems.append("ORIGINAL_MATURITY_DECLARATION_MISSING")
    return problems

def original_outcome_assessment(forecast,forecast_path,outcome,outcome_path,horizon):
    reasons=[]
    if outcome.get("contract")!=EXPECTED_OUTCOME:reasons.append("ORIGINAL_OUTCOME_CONTRACT_MISMATCH")
    if outcome.get("horizon")!=horizon:reasons.append("ORIGINAL_HORIZON_MISMATCH")
    if outcome.get("compass_id")!=forecast.get("compass_id"):reasons.append("OUTCOME_ID_MISMATCH")
    if outcome.get("compass_sha256")!=forecast.get("compass_sha256"):reasons.append("ORIGINAL_FORECAST_HASH_MISMATCH")
    if outcome.get("forecast_path")!=forecast_path:reasons.append("ORIGINAL_FORECAST_PATH_MISMATCH")
    if outcome.get("scoring_contract")!=forecast.get("scoring_contract"):
        reasons.append("ORIGINAL_SCORING_CONTRACT_MISMATCH")
    if outcome.get("issued_at_utc")!=forecast.get("issued_at_utc"):
        reasons.append("OUTCOME_ISSUANCE_CLOCK_MISMATCH")
    try:
        t=utc(outcome.get("target_at_utc"))
        observed=utc(outcome.get("target_observation_at_utc"))
        maturity=utc(outcome.get("matured_at_utc"))
        if maturity<t:reasons.append("MATURITY_BEFORE_OUTCOME_TARGET")
        if maturity>utc(CUTOFF):reasons.append("OUTCOME_MATURITY_AFTER_FROZEN_CUTOFF")
        if t!=observed:reasons.append("TARGET_OBSERVATION_CLOCK_MISMATCH")
    except (ValueError,TypeError):reasons.append("ORIGINAL_OUTCOME_CLOCK_INVALID")
    classes=Counter()
    direction=outcome.get("direction_accuracy")
    if not isinstance(direction,dict):
        reasons.append("MISSING_RECORDED_DIRECTION_RESULT")
    else:
        for asset in ("btc","eth"):
            d=direction.get(asset)
            val=d.get("result") if isinstance(d,dict) else None
            if val not in ("CORRECT","INCORRECT","ABSTAINED","UNAVAILABLE","UNKNOWN"):
                reasons.append("UNRECOGNIZED_RECORDED_DIRECTION_RESULT")
            else:classes[val]+=1
    return reasons,dict(classes)

def census(base=BASE):
    dates=[]
    original_records=[]
    unmatched=[]
    counts=Counter()
    original_states=Counter()
    by_version=Counter()
    by_horizon=Counter()
    outcomes_extra=Counter()
    by_horizon_receipt=Counter()
    integrity_exceptions=Counter()
    for day in days():
        sub=day.strftime("%Y/%m/%d")
        daily=base/"daily"/sub
        outdir=base/"outcomes"/sub
        forecasts=sorted(daily.glob("*.json"))
        outcomes=sorted(outdir.glob("*.json"))
        dates.append({"day":day.isoformat(),"original_forecast_files":len(forecasts),
                      "original_outcome_files":len(outcomes)})
        indexed_outcomes={p.name:p for p in outcomes}
        matched=set()
        for p in forecasts:
            raw=p.read_bytes()
            doc=json.loads(raw)
            reasons=preflight_forecast(doc,p,day)
            version=doc.get("scoring_contract") or "VERSION_MISSING"
            by_version[version]+=1
            counts["original_forecasts"]+=1
            for horizon in HORIZONS:
                by_horizon[horizon]+=1
                filename=p.stem+"_"+horizon+".json"
                path=indexed_outcomes.get(filename)
                row_reasons=list(reasons)
                labels={}
                original_outcome_blob=None
                if path is None:
                    state="NO_ORIGINAL_OUTCOME_FILE_AT_SNAPSHOT"
                    counts["missing_original_outcome_files"]+=1
                    # Missing future outcome does not establish an error/censor:
                    # forecast may not have reached due time.
                else:
                    matched.add(path.name)
                    outbytes=path.read_bytes()
                    outcome=json.loads(outbytes)
                    original_outcome_blob=blob_sha(outbytes)
                    more,labels=original_outcome_assessment(
                        doc,"04_MARKET_LEARNING/handlekompas/official/daily/"+sub+"/"+p.name,
                        outcome,path,horizon)
                    row_reasons+=more
                    state=("LINKED_PUBLIC_ORIGINAL_NOT_PIT_ADMITTED"
                           if not row_reasons else "ORIGINAL_LINKAGE_OR_CLOCK_QUARANTINED")
                    counts["original_outcome_files_matched"]+=1
                    for key,n in labels.items():
                        original_states[key]+=n
                if version!=V3:
                    row_reasons.append("HISTORICAL_V1_V2_MUST_NOT_RECLASSIFY_AS_V3")
                if state=="NO_ORIGINAL_OUTCOME_FILE_AT_SNAPSHOT" and row_reasons:
                    state="ORIGINAL_FORECAST_QUARANTINED_NO_OUTCOME"
                elif row_reasons:
                    state="ORIGINAL_LINKAGE_OR_CLOCK_QUARANTINED"
                counts[state]+=1
                by_horizon_receipt[horizon+"::"+state]+=1
                integrity_exceptions.update(set(row_reasons))
                original_records.append({
                    "original_forecast_path":"04_MARKET_LEARNING/handlekompas/official/daily/"+sub+"/"+p.name,
                    "original_forecast_git_blob_sha1":blob_sha(raw),
                    "original_outcome_git_blob_sha1":original_outcome_blob,
                    "original_outcome_path":("04_MARKET_LEARNING/handlekompas/official/outcomes/"+sub+"/"+path.name) if path else None,
                    "scoring_contract":version,"horizon":horizon,
                    "original_maturity_claim":doc.get("outcome_maturity",{}).get(horizon) if isinstance(doc.get("outcome_maturity"),dict) else None,
                    "source_packet_binding_declared":isinstance(doc.get("source_bindings"),dict) and isinstance(doc["source_bindings"].get("auto_market_state"),dict),
                    "original_outcome_recorded_direction_label_counts":labels,
                    "receipt_state":state,
                    "integrity_exceptions":sorted(set(row_reasons)),
                    "provider_first_publication_verified":False,
                    "original_public_delivery_verified":False,
                    "scientific_pit_admitted":False})
        for p in outcomes:
            if p.name not in matched:
                counts["unmatched_outcome_files"]+=1
                unmatched.append({"path":"04_MARKET_LEARNING/handlekompas/official/outcomes/"+sub+"/"+p.name,
                                  "git_blob_sha1":blob_sha(p.read_bytes()),
                                  "status":"OUTCOME_WITHOUT_MATCHED_ORIGINAL_FORECAST"})
    n=counts["original_forecasts"]
    if n<20 or len(original_records)!=n*len(HORIZONS):raise ValueError("ORIGINAL_ISSUANCE_CENSUS_INCOMPLETE")
    if counts["original_outcome_files_matched"]+counts["unmatched_outcome_files"]!=sum(d["original_outcome_files"] for d in dates):
        raise ValueError("ORIGINAL_OUTCOME_CENSUS_INCONSISTENT")
    return {"contract":CONTRACT,"classification":"SOURCE_BOUND_ORIGINAL_RECEIPT_CENSUS_NO_SCIENTIFIC_EDGE",
            "frozen_cutoff_utc":CUTOFF,"first_day":FIRST.isoformat(),"last_day":LAST.isoformat(),
            "source_label":"PUBLIC_ORIGINAL_OFFICIAL_FORECAST_AND_OUTCOME_GIT_BLOB_ONLY",
            "private_round3_gate":PRIVATE_GATE,"source_era":"v1_v2_v3_MUST_REMAIN_SEPARATE",
            "counts":dict(counts),"forecasts_by_scoring_contract":dict(by_version),
            "original_integrity_exception_counts":dict(integrity_exceptions),
            "per_horizon_receipt_states":dict(by_horizon_receipt),
            "forecast_horizon_attempt_counts":dict(by_horizon),
            "original_published_direction_labels_only":dict(original_states),
            "days":dates,"original_records":original_records,
            "unmatched_outcome_files":unmatched,
            "provider_first_publication_verified":False,
            "actual_delivery_first_known_verified":False,
            "independent_shock_families_certified":0,
            "model_skill_or_return_estimated":False,
            "first_known_market_value_eligibility_unlocked":False,
            "original_forecasts_rewritten":False,
            "research_only":True,
            "next_step":"R1 EVIDENCE RECEIPT PER SOURCE + INDEPENDENT ISSUE/DELIVERY BEFORE SAME_CLOCK_SCIENTIFIC_BASELINE"}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--base",type=Path,default=BASE)
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    out=census(args.base)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"contract":CONTRACT,"counts":out["counts"],
                      "by_version":out["forecasts_by_scoring_contract"],
                      "by_horizon":out["forecast_horizon_attempt_counts"],
                      "original_labels":out["original_published_direction_labels_only"],
                      "integrity_exceptions":out["original_integrity_exception_counts"],
                      "per_horizon":out["per_horizon_receipt_states"]},sort_keys=True))
if __name__=="__main__":main()
