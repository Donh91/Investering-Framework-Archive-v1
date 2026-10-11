#!/usr/bin/env python3
"""Prospective public CN v2 statement freeze for the existing Monday CN owner.

No extra cron, trading, forecasting model, scoring, or privacy-sensitive fields.
Does not claim that GitHub bytes have independent external time proof. The
separate public score repository remains the publication / verifier owner.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

UTC=timezone.utc


def canon(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))+"\n").encode("utf-8")


def load(path: Path) -> tuple[dict, bytes]:
    raw=path.read_bytes()
    value=json.loads(raw)
    if not isinstance(value,dict):
        raise ValueError("invalid_json_object")
    return value,raw


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def utc(s: str) -> datetime:
    dt=datetime.fromisoformat(str(s).replace("Z","+00:00"))
    if dt.tzinfo is None:
        raise ValueError("timestamp_naive")
    return dt.astimezone(UTC)


def fmt(dt: datetime) -> str:
    return dt.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00","Z")


def next_hour_after(dt: datetime) -> datetime:
    return dt.replace(minute=0,second=0,microsecond=0)+timedelta(hours=1)


def path_bound(root: Path, rel: str) -> Path:
    if not isinstance(rel,str) or not rel or rel.startswith("/") or "\\" in rel:
        raise ValueError("invalid_source_path")
    target=(root/rel).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError("path_escape")
    return target


def build(root: Path, now: datetime) -> tuple[dict,str] | None:
    """Returns (frozen bundle, repo-relative output) or None before CN29."""
    root=root.resolve()
    ptr,_=load(root/"05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json")
    year,week=int(ptr["iso_year"]),int(ptr["iso_week"])
    issue=int(ptr.get("public_issue_number") or 0)
    if (year,week)<(2026,42) or issue<29:
        return None
    forecast_week=f"{year:04d}-W{week:02d}"
    d=path_bound(root,str(ptr["week_dir"]))
    machine,mraw=load(d/"CYCLE_NAVIGATOR_MACHINE_PACKAGE.json")
    freeze,fraw=load(d/"CYCLE_NAVIGATOR_FORECAST_FREEZE.json")
    receipt,_=load(d/"CYCLE_NAVIGATOR_SITE_PUBLIC_FREEZE_RECEIPT.json")
    binding,_=load(d/"CYCLE_NAVIGATOR_PUBLIC_SERIES_BINDING.json")
    for label,x in [("machine",machine),("receipt",receipt),("binding",binding)]:
        if int(x.get("public_issue_number",-1))!=issue:
            raise ValueError("public_cn_identity_mismatch:"+label)
    for label,x in [("receipt",receipt),("binding",binding)]:
        if x.get("forecast_week")!=forecast_week:
            raise ValueError("forecast_week_mismatch:"+label)
    if freeze.get("scoring_contract")!="CN_PUBLIC_CONTINUITY_v1":
        raise ValueError("not_a_registered_frozen_week")
    if receipt.get("source_forecast_freeze_sha256")!=digest(fraw):
        raise ValueError("forecast_source_digest_mismatch")
    if receipt.get("score_window_policy")!="FIRST_COMPLETE_UTC_HOUR_AT_OR_AFTER_FREEZE_v1":
        raise ValueError("wrong_forward_scoring_policy")
    if now.tzinfo is None:
        raise ValueError("now_must_be_timezone_aware")
    now=now.astimezone(UTC)
    frozen_at=datetime.fromtimestamp(int(receipt["frozen_unix"]), tz=UTC)
    if now<frozen_at:
        raise ValueError("cannot_issue_claims_before_source_was_frozen")
    # The claim is issued now, after this supplemental source snapshot is constructed.
    # Start >= one full UTC hour after issuance. Public time attestation must STILL
    # prove it was delivered before the scoring start or evaluation is PROVISIONAL.
    issued=fmt(now)
    start=next_hour_after(now)
    existing_scoring_start=utc(receipt["scoring_valid_from_utc"])
    if start<existing_scoring_start:
        start=existing_scoring_start

    compass={}
    compass_context={"availability":"UNAVAILABLE","source_sha256":None,"compass_id":None,
                     "issued_at_utc":None,"risk_state":"UNAVAILABLE","eta_window":"UNKNOWN"}
    compass_source=None
    pointer_path=root/"04_MARKET_LEARNING/handlekompas/official/PUBLIC_LATEST_COMPASS.json"
    if pointer_path.exists():
        cp,_=load(pointer_path)
        try:
            source_path=path_bound(root,str(cp["public_projection_path"]))
            cand,cbytes=load(source_path)
            if cand.get("contract")!="PUBLIC_COMPASS_PROJECTION_v1":
                raise ValueError("wrong_compass_contract")
            if (cand.get("compass_id")!=cp.get("compass_id") or
                digest(cbytes)!=cp.get("public_projection_content_sha256")):
                raise ValueError("compass_source_digest_mismatch")
            source_time=utc(cand["issued_at_utc"])
            if source_time>now:
                raise ValueError("future_compass_not_eligible")
            freshness=(now-source_time).total_seconds()
            if freshness<=24*3600 and cand.get("data_status")=="OK":
                compass=cand
                compass_source=str(source_path.relative_to(root))
                risk=cand.get("protection_tracker") or {}
                compass_context={"availability":"OK","source_sha256":digest(cbytes),
                    "compass_id":cand.get("compass_id"),"issued_at_utc":cand.get("issued_at_utc"),
                    "risk_state":risk.get("pullback_risk_state") or "UNAVAILABLE",
                    "distribution_risk":risk.get("distribution_risk") or "UNKNOWN",
                    "eta_window":risk.get("eta_window") or "UNKNOWN",
                    "reentry_state":risk.get("reentry_state") or "UNAVAILABLE"}
            else:
                compass_context["availability"]="STALE_OR_UNAVAILABLE"
        except (FileNotFoundError, ValueError, KeyError):
            compass_context["availability"]="UNVERIFIABLE_SOURCE"
    manifest={
        "contract":"CN_V2_SOURCE_MANIFEST_v1",
        "public_issue_number":issue,"forecast_week":forecast_week,
        "weekly_machine_sha256":digest(mraw),
        "weekly_forecast_freeze_sha256":digest(fraw),
        "weekly_forecast_source_path":str((d/"CYCLE_NAVIGATOR_FORECAST_FREEZE.json").relative_to(root)),
        "compass_projection_source_path":compass_source,
        "compass_projection_sha256":compass_context["source_sha256"],
        "compass_id":compass_context["compass_id"],
    }
    manifest_sha=digest(canon(manifest))
    claims=[]
    def add(*,family: str,kind: str,code: str,duration_days: float,da: str,en: str,
            source: str, declared_state: str, extra: dict | None=None) -> None:
        record={
            "claim_id":f"CN{issue}-{forecast_week}-{code}",
            "family":family,"kind":kind,
            "public_issue_number":issue,"forecast_week":forecast_week,
            "source_sha256":manifest_sha,"issued_at_utc":issued,
            "evaluation_start_utc":fmt(start),
            "evaluation_end_utc":fmt(start+timedelta(days=duration_days)),
            "statement_da":da,"statement_en":en,
            "metric_source_id":source,
            "declared_state":declared_state,
        }
        if extra:
            record.update(extra)
        claims.append(record)

    # Record all source text before the outcome. Natural-language claims remain
    # ABSTAIN, never silently converted to a measurable price/rotation predicate.
    descriptive=[
      ("WEEKLY_ETHBTC",7,"ETH/BTC: se kildens frosne ugeudsagn.",freeze.get("ethbtc_condition","")),
      ("WEEKLY_BREADTH",7,"Bredde: se kildens frosne ugeudsagn.",freeze.get("breadth_condition","")),
      ("WEEKLY_REGIME",7,"Regime: se kildens frosne ugeudsagn.",(freeze.get("structural_calls") or [""])[0]),
      ("WEEKLY_ROTATION",7,"Rotation: se kildens frosne ugeudsagn.",(freeze.get("structural_calls") or ["","",""])[2]),
      ("WEEKLY_FLOW",7,"Flow: se kildens frosne ugeudsagn.",(freeze.get("structural_calls") or ["","","","",""])[4]),
      ("DIRECTION_14D",14,"To-ugers retning: kildeanalyse, endnu ikke objektiv binær prognose.",machine.get("base_case_2_3_weeks","")),
      ("DIRECTION_21D",21,"Tre-ugers retning: kildeanalyse, endnu ikke objektiv binær prognose.",machine.get("base_case_2_3_weeks","")),
      ("DIRECTION_28D",28,"Fire-ugers retning: kildeanalyse, endnu ikke objektiv binær prognose.",machine.get("base_case_4_8_weeks","")),
      ("DIRECTION_56D",56,"Otte-ugers retning: kildeanalyse, endnu ikke objektiv binær prognose.",machine.get("base_case_4_8_weeks","")),
    ]
    for code,days,da,en in descriptive:
        add(family="DIRECTION_ROTATION_CLAIMS",kind="METRIC_COMPARISON",code=code,
            duration_days=days,da=da,en=str(en or "No objective typed market predicate published."),
            source="CN_WEEKLY_ANALYSIS_ONLY_v1",declared_state="ABSTAIN")
    # Compass categorical risk is an observable public risk statement, NOT
    # independently a numeric >=5% forecast. We explicitly score only NORMAL
    # as NO_WARNING or HIGH/CONFIRMED as material warning; BUILDING/ELEVATED
    # are watch-only and MUST NOT be promoted to quantitative alarms.
    risk_state=str(compass_context.get("risk_state") or "UNAVAILABLE").upper()
    if risk_state=="NORMAL":
        predicted_event=False;state="ELIGIBLE"
    elif risk_state in {"HIGH","CONFIRMED"}:
        predicted_event=True;state="ELIGIBLE"
    else:
        predicted_event=None;state="ABSTAIN"
    add(family="PULLBACK_EDGE",kind="EVENT_OCCURRENCE",code="PB24H",
        duration_days=1,
        da=("Ingen advarsel om materialt BTC-pullback i næste 24 timer." if predicted_event is False
           else "Materialt BTC-pullback er advaret af officiel risikotracker." if predicted_event is True
           else "Pullback-risiko er observeret, men et numerisk 24-timers udsagn er ikke givet."),
        en=("No warning for a material BTC pullback in the next 24 hours." if predicted_event is False
            else "Official risk tracker warns of material BTC pullback." if predicted_event is True
            else "Risk tracker observed, but no material 24-hour drawdown prediction is made."),
        source="BTC_USD_HOURLY_V1",declared_state=state,
        extra=({"expected_event":predicted_event,"asset":"BTC","threshold_pct":5}
               if predicted_event is not None else {}))
    bundle={
        "contract":"CN_V2_FROZEN_CLAIMS_v1",
        "scoring_contract":"CN_EDGE_BINARY_v2_0",
        "authority":"ACCOUNTABILITY_ONLY_NO_PORTFOLIO_EXECUTION",
        "proof_status":"PROVISIONAL_UNLESS_EXTERNALLY_ANCHORED_PRE_OUTCOME",
        "public_issue_number":issue,"forecast_week":forecast_week,
        "issued_at_utc":issued,"scoring_valid_from_utc":fmt(start),
        "source_sha256":manifest_sha,
        "source_manifest":manifest,
        "compass_risk_snapshot":compass_context,
        "weekly_frozen_context":{
            "flow_rotation_analyses":freeze.get("market_structure_analysis"),
            "intraday_map":freeze.get("intraday_map"),
            "btc_weekly_range":[freeze.get("btc_range_low"),freeze.get("btc_range_high")],
            "eth_weekly_range":[freeze.get("eth_range_low"),freeze.get("eth_range_high")],
            "score_owner":"EXISTING_PUBLIC_PRICE_RANGE_MATERIALIZER",
        },
        "claims":claims,
        "guardrails":{
            "price_formula_unchanged":True,
            "qualitative_unquantified_claims_are_abstentions":True,
            "compass_watch_is_not_material_pullback_prediction":True,
            "no_warning_is_explicit_when_risk_NORMAL":True,
            "no_wallet_data":True,
            "public_git_commit_does_not_establish_external_ex_ante_proof":True,
            "long_claims_are_immutable_across_later_issues":True,
        },
    }
    rel=str((d/"CYCLE_NAVIGATOR_V2_EDGE_FREEZE.json").relative_to(root))
    return bundle,rel


def main() -> None:
    cli=argparse.ArgumentParser()
    cli.add_argument("--repo-root",type=Path,default=Path("."))
    cli.add_argument("--now-utc",help="Only for deterministic tests; never set in production")
    args=cli.parse_args()
    if args.now_utc:
        raise SystemExit("override_now_utc_not_permitted_in_production_cli")
    result=build(args.repo_root,datetime.now(UTC))
    if result is None:
        print(json.dumps({"status":"NOOP_PRE_V2_ERA"}))
        return
    bundle,rel=result
    target=args.repo_root/rel
    serialized=canon(bundle)
    # Never rewrite a prospective freeze, even in a workflow retry.
    if target.exists():
        if target.read_bytes()!=serialized:
            print(json.dumps({"status":"EXISTING_FREEZE_PRESERVED", "path":rel,
                              "note":"No rewrite; inspect original source and scorebook governance."}))
            return
        print(json.dumps({"status":"EXACT_EXISTING_FREEZE", "path":rel}))
        return
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(serialized)
    print(json.dumps({"status":"FROZEN_PROVISIONAL","path":rel,
                      "sha256":digest(serialized),
                      "eligible_claims":sum(c["declared_state"]=="ELIGIBLE" for c in bundle["claims"]),
                      "abstained_claims":sum(c["declared_state"]!="ELIGIBLE" for c in bundle["claims"])}))


if __name__=="__main__":
    main()
