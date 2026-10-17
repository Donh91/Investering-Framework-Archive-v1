#!/usr/bin/env python3
"""Existing-data Task2: original-MATURED-314 frozen vote-family replay.

Read original Actions ZIP, verify exact bytes, read original issued predictions
at pinned Git commit and match their frozen SHA256, then publish aggregates ONLY.
EXPOST DEVELOPMENT, not vendor-first-known / independent PIT / portfolio edge.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.util
import io
import json
import subprocess
import zipfile
from collections import Counter
from pathlib import Path

ZIP_SHA = "4bce43736374b8fcff7aa9ffd1fdac18c303d8b2264b8291bb6e0b80fcde23ae"
CSV_SHA = "616e70fd87a79acf126591c1f8e704c74da7a2bd3b3aa181838ac5f861fea5d9"
CSV_NAME = "TASK15_R0_FROZEN_FORECAST_TAPE_CENSOR_LEDGER.csv"
SOURCE_COMMIT = "0e8c386b5a4ee57a5500cb3d02951c9e398b1b4f"
PREFIX = "04_MARKET_LEARNING/intraday_execution/direction_predictions/"
CANDIDATES = ("PRICE_FAMILY_MAJORITY", "TAKER_ONLY", "ETHBTC_BREADTH_ONLY",
              "PRICE_AND_TAKER_CONFIRM", "PRICE_TAKER_ETH_CROSS_CONFIRM")
STATUS = "EXPOST_MATCHED_MATURED314_DEVELOPMENT_NOT_ORIGINAL_PIT_OR_ACTION"

def source_module(root):
    p = root / "04_MARKET_LEARNING/handlekompas/research/2026-10-13__task15_frozen_vote_ablation_v1.py"
    spec = importlib.util.spec_from_file_location("task15_frozen_votes_original", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def read_artifact(path):
    outer = path.read_bytes()
    if hashlib.sha256(outer).hexdigest() != ZIP_SHA:
        raise ValueError("ORIGINAL_ZIP_SHA_MISMATCH")
    with zipfile.ZipFile(io.BytesIO(outer)) as z:
        ledger = z.read(CSV_NAME)
    if hashlib.sha256(ledger).hexdigest() != CSV_SHA:
        raise ValueError("ORIGINAL_CSV_SHA_MISMATCH")
    rows = list(csv.DictReader(io.StringIO(ledger.decode("utf-8-sig"))))
    if len(rows) != 1140 or len({r["prediction_id"] for r in rows}) != 1140:
        raise ValueError("ORIGINAL_FORECAST_ROSTER_MISMATCH")
    if Counter(r["original_outcome_status"] for r in rows) != {
        "MATURED": 358, "CENSORED": 570, "NO_ORIGINAL_RECEIPT": 212
    }:
        raise ValueError("ORIGINAL_CENSOR_ROSTER_MISMATCH")
    matched = [r for r in rows if r["descriptive_hit"] in ("True","False")
               and r["baseline_hit"] in ("True","False")]
    mature = [r for r in matched if r["original_outcome_status"] == "MATURED"]
    abstain = [r for r in rows if r["original_outcome_status"] == "MATURED"
               and r["original_outcome_result"] == "ABSTAINED"]
    if (len(matched),len(mature),len(abstain)) != (824,314,44):
        raise ValueError("ORIGINAL_MATURED_314_AND_44_ABSTAIN_MISMATCH")
    if any(r["direction"]!="NO_EDGE" for r in abstain):
        raise ValueError("HISTORICAL_ABSTAIN_DIRECTION_CHANGED")
    if any((r["original_outcome_result"]=="HIT") != (r["descriptive_hit"]=="True")
           for r in mature):
        raise ValueError("ORIGINAL_HIT_TAPE_MISMATCH")
    return mature, abstain

def original_files(root, rows):
    by_path = {}
    for r in rows:
        name=r["prediction_id"].split("#",1)[0]
        by_path.setdefault(name,set()).add(r["prediction_sha256"])
    original={}
    for path in sorted(by_path):
        if (not path.startswith(PREFIX) or not path.endswith(".json")
                or path.startswith("/") or ".." in Path(path).parts):
            raise ValueError("UNSAFE_ISSUED_FORECAST_PATH")
        try:
            data=subprocess.check_output(["git","--no-replace-objects","show",
                                          f"{SOURCE_COMMIT}:{path}"],
                                         cwd=root,stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as exc:
            raise ValueError("PINNED_ORIGINAL_GIT_SOURCE_UNREADABLE") from exc
        if by_path[path] != {hashlib.sha256(data).hexdigest()}:
            raise ValueError("ORIGINAL_FORECAST_SHA256_MISMATCH")
        original[path]=json.loads(data)
    return original

def family_choices(target, asset, incumbent, vote_mod):
    choices=vote_mod.frozen_vote_challengers(target,asset,incumbent)
    votes=target.get("votes")
    if not isinstance(votes,list):
        votes=[]
    choices["TAKER_ONLY"]=vote_mod.majority(votes,vote_mod.TAKER,2,2)
    choices["ETHBTC_BREADTH_ONLY"]=(vote_mod.majority(votes,vote_mod.ETH_CROSS,2,2)
                                   if asset=="ETH" else None)
    return {name:choices.get(name) for name in CANDIDATES}

def summarize(records, name):
    selected=[r for r in records if r["candidate"][name] in ("UP","DOWN")]
    n=len(selected)
    c=sum(r["candidate"][name]==r["observed_direction"] for r in selected)
    b=sum(r["baseline_hit"]=="True" for r in selected)
    m=sum(r["descriptive_hit"]=="True" for r in selected)
    disagree=sum(r["candidate"][name]!=r["baseline_direction"] for r in selected)
    c_only=sum(r["candidate"][name]==r["observed_direction"]
               and r["baseline_hit"]=="False" for r in selected)
    b_only=sum(r["candidate"][name]!=r["observed_direction"]
               and r["baseline_hit"]=="True" for r in selected)
    return {"original_matured_directional_n":len(records),
            "available_n":n,"coverage_pct":round(100*n/len(records),3) if records else None,
            "candidate_hits":c,"same_clock_price_hits":b,"same_clock_compass_hits":m,
            "direction_disagreements_vs_price":disagree,
            "candidate_only_hits":c_only,"price_only_hits":b_only,
            "candidate_minus_price_pp":round(100*(c-b)/n,4) if n else None}

def analyze(root, artifact):
    mature, abstain=read_artifact(artifact)
    frozen=original_files(root,mature)
    vote_mod=source_module(root)
    enriched=[]
    for row in mature:
        path,key=row["prediction_id"].rsplit("#",1)
        horizon,asset=key.split(":")
        target=frozen[path]["horizons"][horizon]["targets"][asset]
        if (target["direction"]!=row["direction"]
                or row["observed_direction"] not in ("UP","DOWN")):
            raise ValueError("ORIGINAL_ISSUED_OR_OUTCOME_IDENTITY_CONFLICT")
        enriched.append({**row,"candidate":family_choices(target,asset,row["direction"],vote_mod)})
    assert len(enriched)==314 and len(frozen)<=len(enriched)
    result={"contract":"TASK2_ORIGINAL_MATURED314_VOTE_FAMILY_DIAGNOSTIC_v1",
            "status":STATUS,
            "source_ref":SOURCE_COMMIT,
            "original_zip_sha256":ZIP_SHA,
            "original_csv_sha256":CSV_SHA,
            "original_forecast_files_replayed":len(frozen),
            "original_matured_directional":314,
            "original_matured_abstentions":len(abstain),
            "not_reclassified":{"original_censored":500,"no_original_receipt":10},
            "family_comparison":{k:summarize(enriched,k) for k in CANDIDATES},
            "by_asset_horizon":[{"asset":a,"horizon":h,"n":sum(r["asset"]==a and r["horizon"]==h for r in enriched),
                                 "families":{k:summarize([r for r in enriched if r["asset"]==a and r["horizon"]==h],k)
                                             for k in CANDIDATES}}
                                for a in ("BTC","ETH") for h in ("1H","4H","24H")],
            "warning":"Availability-conditioned same-clock development only. Feature families correlated, no vendor first-published time, independent shocks or after-cost action validation.",
            "authority":{"certified_historical_performance":False,"portfolio_action":False,
                         "change_live_rules":False,"paid_api":False}}
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=Path("."))
    ap.add_argument("--artifact",type=Path,required=True)
    ap.add_argument("--output",type=Path)
    args=ap.parse_args()
    out=analyze(args.root,args.artifact)
    payload=json.dumps(out,indent=2,sort_keys=True)+"\n"
    if args.output:
        args.output.write_text(payload)
    else:
        print(payload)

if __name__=="__main__":
    main()
