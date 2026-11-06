#!/usr/bin/env python3
"""PIT-safe role and clock inventory for the 11 ORIGINAL Task2 R1 V3 attempts.

No outcome, raw provider values, action recommendations, forecast rescoring,
model tuning, historical edge promotion, external calls or live writer.
Distinguishes the evidence_snapshot's 24-field index from the actual
NEXT_12H directional computation and separate source-health gates.

The original producer's immutable Git blob and all original forecast
blobs are verified against the already frozen 2026-10-14 cohort.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import hashlib
import json
import re
from pathlib import Path

from scripts.research import task2_r1_original_admission as original
from scripts.research.task2_r1_scoped_readiness_v1 import (
    ROOT, FROZEN_MAIN, pinned_inputs, reconcile, need, utc,
)
from scripts.research.task2_r1_original_publication_recovery_v1 import (
    load_witness, recover,
)

CONTRACT = "TASK2_R1_ORIGINAL_12H_CAUSAL_SOURCE_ROLE_VINTAGE_MATRIX_v1"
ENGINE_PATH = "scripts/data_ping/native_handlekompas.py"
ENGINE_SHA = "d00d38bed517861fa2487dce42d330bf05812f6d"
ORIGINAL_ENGINE_REF = "4dc4a52d897b298b3b016b622b4315f52b30ec54"

# Exact original evidence_snapshot() _feature IDs, no new trading feature.
# Explicitly: a field being present in an official evidence index does NOT
# establish that it influenced the original 12H sign.
ROLES = {
    "btc_delta_since_prior_packet_pct": "DIRECT_12H_DIRECTION_DELTA",
    "eth_delta_since_prior_packet_pct": "DIRECT_12H_DIRECTION_DELTA",
    "btc_usdt": "ORIGINAL_PRICE_INPUT_TO_DIRECTION_DELTA_AND_REFERENCE",
    "eth_usdt": "ORIGINAL_PRICE_INPUT_TO_DIRECTION_DELTA_AND_REFERENCE",
    "ethbtc": "RELATIVE_DIRECTION_CONTEXT_NOT_BTC_ETH_12H_SIGN",
    "ethbtc_delta_since_prior_packet_pct": "RELATIVE_DIRECTION_CONTEXT_NOT_BTC_ETH_12H_SIGN",
    "breadth_advance_ratio": "EVIDENCE_INDEX_NOT_DIRECT_12H_SIGN",
    "breadth_advancers": "EVIDENCE_INDEX_NOT_DIRECT_12H_SIGN",
    "breadth_decliners": "EVIDENCE_INDEX_NOT_DIRECT_12H_SIGN",
    "breadth_equal_weight_24h": "EVIDENCE_INDEX_NOT_DIRECT_12H_SIGN",
    "btc_dominance_pct": "EVIDENCE_INDEX_NOT_DIRECT_12H_SIGN",
    "btc_etf_musd": "EVIDENCE_INDEX_NOT_DIRECT_12H_SIGN",
    "eth_etf_musd": "EVIDENCE_INDEX_NOT_DIRECT_12H_SIGN",
    "stablecoin_total_usd": "EVIDENCE_INDEX_NOT_DIRECT_12H_SIGN",
    "btc_open_interest": "EVIDENCE_INDEX_NOT_DIRECT_12H_SIGN",
    "eth_open_interest": "EVIDENCE_INDEX_NOT_DIRECT_12H_SIGN",
    "btc_funding": "EVIDENCE_INDEX_NOT_DIRECT_12H_SIGN",
    "eth_funding": "EVIDENCE_INDEX_NOT_DIRECT_12H_SIGN",
    "sentiment_state": "EVIDENCE_INDEX_NOT_DIRECT_12H_SIGN",
    "sentiment_market_score": "EVIDENCE_INDEX_NOT_DIRECT_12H_SIGN",
    "sentiment_btc_score": "EVIDENCE_INDEX_NOT_DIRECT_12H_SIGN",
    "sentiment_eth_score": "EVIDENCE_INDEX_NOT_DIRECT_12H_SIGN",
    "altseason_score_90d": "EVIDENCE_INDEX_NOT_DIRECT_12H_SIGN",
    "entry_signal_state": "EVIDENCE_INDEX_NOT_DIRECT_12H_SIGN",
}
DIRECTION_DELTAS = frozenset(("btc_delta_since_prior_packet_pct", "eth_delta_since_prior_packet_pct"))
DIRECTION_PRICE = frozenset(("btc_usdt", "eth_usdt"))
RELATIVE_CONTEXT = frozenset(("ethbtc", "ethbtc_delta_since_prior_packet_pct"))
REQUIRED_HEALTH_LANES = frozenset((
    "hourly_market", "live_anchor", "btc_dominance", "derivatives",
    "breadth", "settled_etf", "stablecoin_liquidity", "macro_risk",
    "sentiment", "altseason_context", "entry_signal_reference",
))
OPTIONAL_HEALTH_LANES = frozenset(("catalyst_context",))

def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\x00"+raw).hexdigest()

def functions(source: str):
    tree = ast.parse(source)
    return {item.name: item for item in tree.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))}

def calls(node, function):
    """Only exact literal calls in the original AST, no heuristic free text."""
    found = []
    for item in ast.walk(node):
        if isinstance(item, ast.Call) and isinstance(item.func, ast.Name) and item.func.id == function:
            found.append(item)
    return found

def literal_delta_keys(fn):
    result = []
    for call in calls(fn, "_delta_pct"):
        need(len(call.args) == 2 and isinstance(call.args[1], ast.Constant) and
             isinstance(call.args[1].value, str), "ORIGINAL_DELTA_DYNAMIC_OR_UNKNOWN")
        result.append(call.args[1].value)
    return set(result)

def audited_original_engine(source_bytes: bytes):
    need(git_blob(source_bytes) == ENGINE_SHA, "ORIGINAL_ENGINE_BLOB_CHANGED")
    source = source_bytes.decode("utf-8")
    funcs = functions(source)
    needed = (
        "derive_market_now", "horizon_map", "_delta_pct",
        "owner_freshness", "_health_ok", "action_context",
        "evidence_snapshot", "build_official_compass",
    )
    need(all(name in funcs for name in needed), "ORIGINAL_ENGINE_ENTRYPOINT_REMOVED")
    delta_keys = literal_delta_keys(funcs["derive_market_now"])
    need(delta_keys == {"btc_usdt", "eth_usdt", "ethbtc"}, "ORIGINAL_12H_DIRECTION_INPUTS_CHANGED")
    # Cross-check not just the existence of three deltas but their role.
    direction=funcs["derive_market_now"]
    source_direction=ast.get_source_segment(source,direction) or ""
    need("btc > 0 and eth > 0" in source_direction and
         "btc < 0 and eth < 0" in source_direction and
         'direction = "BULLISH"' in source_direction and
         'direction = "BEARISH"' in source_direction,
         "ORIGINAL_12H_SIGN_LOGIC_CHANGED")
    horizon=funcs["horizon_map"]
    need(any(isinstance(x,ast.Constant) and x.value=="NEXT_12H" for x in ast.walk(horizon)) and
         bool(calls(horizon,"derive_market_now")) and
         bool(calls(horizon,"_health_ok")),
         "ORIGINAL_12H_HORIZON_WIRING_CHANGED")
    snapshot_calls=calls(funcs["evidence_snapshot"],"_feature")
    ids=[]
    for call in snapshot_calls:
        need(len(call.args)>0 and isinstance(call.args[0],ast.Constant) and
             isinstance(call.args[0].value,str), "ORIGINAL_EVIDENCE_INDEX_DYNAMIC")
        ids.append(call.args[0].value)
    need(len(ids)==24 and len(set(ids))==24 and set(ids)==set(ROLES),
         "ORIGINAL_24_FEATURE_INDEX_CHANGED")
    need(bool(calls(funcs["build_official_compass"],"evidence_snapshot")) and
         bool(calls(funcs["build_official_compass"],"horizon_map")),
         "ORIGINAL_OFFICIAL_FORECAST_WIRING_CHANGED")
    need(len(DIRECTION_DELTAS)==2 and len(DIRECTION_PRICE)==2 and
         len(RELATIVE_CONTEXT)==2 and
         len([k for k,v in ROLES.items() if v=="EVIDENCE_INDEX_NOT_DIRECT_12H_SIGN"])==18,
         "ROLE_DENOMINATOR_CHANGED")
    return {
        "source_git_blob": ENGINE_SHA,
        "original_12h_direction_delta_source_keys": sorted(delta_keys),
        "direction_sign_required_deltas": sorted(DIRECTION_DELTAS),
        "direction_delta_price_lineage": sorted(DIRECTION_PRICE),
        "relative_context_non_sign": sorted(RELATIVE_CONTEXT),
        "evidence_snapshot_index_ids": sorted(ids),
        "entrypoint_check":"PINNED_AST_AND_ORIGINAL_SIGN_PREDICATES",
    }

def build(source_bytes: bytes | None = None, originals=None):
    inputs = pinned_inputs() if originals is None else originals
    prior = reconcile(inputs)
    publication = recover(inputs, load_witness())
    need(publication["scoped_original_publication_witnesses"]==11 and
         publication["full_R1_scientific_PIT_admissions"]==0 and
         prior["counts"]["full_historical_pit_admissions"]==0,
         "PUBLICATION_SCOPED_NOT_SCIENTIFIC")
    engine_bytes = source_bytes
    if engine_bytes is None:
        engine_bytes = original.git("show", f"{ORIGINAL_ENGINE_REF}:{ENGINE_PATH}")
    engine = audited_original_engine(engine_bytes)
    ledger = inputs["ledger"]
    need(len(ledger["rows"])==11,"ORIGINAL_ROSTER_CHANGED")
    rows=[]
    counts=Counter()
    statuses=Counter()
    owners=Counter()
    required_health_statuses=Counter()
    optional_health_statuses=Counter()
    for row in ledger["rows"]:
        fid=row["forecast_id"]
        bound=row["original_bound_main_sha"]
        exact_blob=original.git("rev-parse", f"{bound}:{ENGINE_PATH}").decode().strip()
        need(exact_blob==ENGINE_SHA==row["model_version"]["engine_git_blob_sha_at_bound_main"],
             "ORIGINAL_FORECAST_ENGINE_DRIFT_"+fid)
        original_forecast,blob=original.original(
            FROZEN_MAIN,row["original_forecast_path"],row["original_forecast_git_blob_sha"])
        need(blob==row["original_forecast_git_blob_sha"] and
             original_forecast["compass_id"]==fid and
             original_forecast["issued_at_utc"]==row["issued_at_utc"] and
             original_forecast["bound_main_sha"]==bound and
             original_forecast["scoring_contract"]=="OFFICIAL_DAILY_COMPASS_SCORING_v3",
             "ORIGINAL_FORECAST_IDENTITY_"+fid)
        original_features=original_forecast["evidence_snapshot"]["selected_features"]
        need(len(original_features)==24,"ORIGINAL_FORECAST_INDEX_LENGTH_"+fid)
        mapped={}
        for feature in original_features:
            key=feature.get("feature_id")
            need(key in ROLES and key not in mapped,"ORIGINAL_FORECAST_FEATURE_ID_"+fid)
            mapped[key]=feature
        need(set(mapped)==set(ROLES),"ORIGINAL_FORECAST_FEATURE_ROSTER_"+fid)
        meta={f["feature_id"]:f for f in row["selected_feature_clocks"]}
        need(set(meta)==set(ROLES),"ORIGINAL_LEDGER_FEATURE_ROSTER_"+fid)
        issue=utc(row["issued_at_utc"])
        # Exact original packet snapshot: source health can affect NO_EDGE and
        # decision availability even when feature values do not determine sign.
        packet, packet_blob = original.original(
            row["source_packet"]["first_git_commit_sha"],
            row["source_packet"]["path"],
            row["source_packet"]["git_blob_sha"],
        )
        need(packet_blob==row["source_packet"]["git_blob_sha"] and
             packet.get("packet_sha256")==original_forecast["source_bindings"]["auto_market_state"]["packet_sha256"],
             "ORIGINAL_HEALTH_PACKET_IDENTITY_"+fid)
        denominator=packet.get("replacement_score",{}).get("denominator",{})
        need(denominator.get("decision_context_required_lanes")==11 and
             set(denominator.get("decision_context_lanes") or ())==REQUIRED_HEALTH_LANES,
             "ORIGINAL_REQUIRED_HEALTH_ROSTER_"+fid)
        statuses_by_lane=packet.get("source_health",{})
        need(isinstance(statuses_by_lane,dict) and
             set(statuses_by_lane)==REQUIRED_HEALTH_LANES | OPTIONAL_HEALTH_LANES,
             "ORIGINAL_HEALTH_LANE_UNIVERSE_"+fid)
        need(packet.get("decision_context_status")=="PASS" and
             packet.get("validation_status") in {"PASS","DEGRADED"} and
             packet.get("blockers")==[],
             "ORIGINAL_PACKET_DECISION_CONTEXT_CHANGED_"+fid)
        need(original_forecast["source_bindings"]["auto_market_state"]["freshness"]["status"]=="PASS",
             "ORIGINAL_ISSUANCE_FRESHNESS_CHANGED_"+fid)
        for lane in sorted(REQUIRED_HEALTH_LANES):
            state=statuses_by_lane[lane].get("status")
            need(state=="PASS","ORIGINAL_REQUIRED_HEALTH_CHANGED_"+fid+"_"+lane)
            required_health_statuses[state]+=1
        for lane in sorted(OPTIONAL_HEALTH_LANES):
            state=statuses_by_lane[lane].get("status")
            need(state in {"PASS", "DEGRADED"},
                 "ORIGINAL_OPTIONAL_HEALTH_SEMANTICS_"+fid+"_"+lane)
            if state=="DEGRADED":
                need(lane in set(packet.get("optional_degraded_lanes") or ()),
                     "ORIGINAL_OPTIONAL_DEGRADATION_UNDECLARED_"+fid+"_"+lane)
            optional_health_statuses[state]+=1
        for key in sorted(ROLES):
            source=meta[key]
            feature=mapped[key]
            need(feature.get("source_owner")==source["source_owner"] and
                 feature.get("observed_at")==source["declared_observed_at"] and
                 feature.get("retrieved_at")==source["declared_retrieved_at"] and
                 feature.get("source_path")==row["source_packet"]["path"],
                 "ORIGINAL_FIELD_SOURCE_OR_CLOCK_MISMATCH_"+fid+"_"+key)
            clock_state=source["observation_clock_status"]
            need(isinstance(clock_state,str) and clock_state in {
                "ARCHIVE_CLOCK_PREISSUE_PROVIDER_FIRST_KNOWN_UNKNOWN",
                "RETRIEVAL_CLOCK_UNKNOWN",
                "SETTLEMENT_IS_NOT_QUOTE_OBSERVATION",
                "NOT_ADMITTED_RETRIEVED_AFTER_ISSUE",
                "NOT_ADMITTED_OBSERVATION_AFTER_ISSUE",
            }, "UNKNOWN_SOURCE_CLOCK_CATEGORY_"+fid+"_"+key)
            if feature.get("retrieved_at") is not None:
                stamp=feature["retrieved_at"]
                # Original issuer-supplied retrieval is only an archive clock,
                # not actual provider publication / revision.
                need(utc(stamp)<=issue,"ORIGINAL_RETRIEVAL_POST_ISSUE_"+fid+"_"+key)
            counts[ROLES[key]]+=1
            statuses[clock_state]+=1
            owners[source["source_owner"]]+=1
        need(row["admissibility"]=="NOT_ADMITTED" and
             row["information_edge_gate"]["status"]=="NOT_ADMITTED" and
             row["investor_action_edge_gate"]["status"]=="NOT_ADMITTED" and
             original_forecast["authority"]["portfolio_execution"] is False,
             "INVALID_ORIGINAL_ADMISSION_OR_AUTHORITY_"+fid)
        rows.append({
            "original_forecast_id":fid,
            "original_forecast_git_blob":blob,
            "source_packet_git_blob":row["source_packet"]["git_blob_sha"],
            "engine_git_blob":exact_blob,
            "selected_feature_index_size":24,
            "required_original_source_health_lanes":11,
            "optional_source_health_lanes":1,
            "original_health_gate":"REPORTED_PASS_NOT_INDEPENDENT_VENDOR_FIRST_KNOWN",
            "direct_12h_direction_deltas_present":sorted(DIRECTION_DELTAS),
            "original_packet_issued_utc":row["issued_at_utc"],
            "original_outcome_state":row["original_outcome_status"],
            "admission":"NOT_ADMITTED",
        })
    need(len(rows)==11 and sum(counts.values())==264,
         "ORIGINAL_CAUSAL_CENSUS_DRIFT")
    expected={
        "DIRECT_12H_DIRECTION_DELTA":22,
        "ORIGINAL_PRICE_INPUT_TO_DIRECTION_DELTA_AND_REFERENCE":22,
        "RELATIVE_DIRECTION_CONTEXT_NOT_BTC_ETH_12H_SIGN":22,
        "EVIDENCE_INDEX_NOT_DIRECT_12H_SIGN":198,
    }
    need(dict(counts)==expected,"ROLE_COUNTS_DRIFT")
    need(sum(statuses.values())==264, "SOURCE_CLOCK_COUNT_DRIFT")
    need(required_health_statuses==Counter({"PASS":121}) and
         sum(optional_health_statuses.values())==11,
         "ORIGINAL_REQUIRED_HEALTH_DENOMINATOR_CHANGED")
    return {
        "contract":CONTRACT,
        "classification":"NO_VALUES_OR_SCORING_PUBLIC_SAFE_FROZEN_ORIGINAL_SOURCE_DEPENDENCY_INDEX",
        "owner_issue":1596,
        "frozen_snapshot_git_commit":FROZEN_MAIN,
        "original_engine":engine,
        "source_role_counts":dict(sorted(counts.items())),
        "selected_feature_clock_status_counts":dict(sorted(statuses.items())),
        "selected_feature_owner_counts":dict(sorted(owners.items())),
        "original_required_health_lanes":sorted(REQUIRED_HEALTH_LANES),
        "original_optional_health_lanes":sorted(OPTIONAL_HEALTH_LANES),
        "required_health_census_status":dict(sorted(required_health_statuses.items())),
        "optional_health_census_status":dict(sorted(optional_health_statuses.items())),
        "original_forecasts":11,
        "selected_feature_instances":264,
        "scoped_original_packet_publication_witnesses":11,
        "scoped_engine_replays":11,
        "full_original_R1_PIT_admissions":0,
        "independent_12h_market_event_families_certified":0,
        "source_authentication_semantics":{
            "source_packet_git_first_publication":"VERIFIED_SCOPED_ONLY",
            "original_hourly_and_engine_replay":"REPRODUCED_DEVELOPMENT_ONLY",
            "entire_upstream_vendor_revision_first_known":"NOT_VERIFIED",
            "all_source_health_predicates_independently_vintaged":"NOT_VERIFIED",
            "CN_original_package_and_validity_full_admission":"NOT_VERIFIED",
            "actual_first_user_visibility":"NOT_VERIFIED",
            "full_model_future_12h_skill":"NOT_ESTABLISHED",
            "full_model_historical_backtest_authorized":False,
            "original_12h_direction":"NOWCAST_DELTA_CONTINUATION_NOT_PROVEN_PREDICTIVE_EDGE",
        },
        "next_executable_source_priority":[
            "SOURCE_OWNER_1596: ORIGINAL HOURLY BTC/ETH THEN PRIOR DELTA CHAIN + ORIGINAL FIRST-KNOWN RAW RESPONSE",
            "SOURCE_OWNER_1596: ORIGINAL 11 SOURCE_HEALTH/FRESHNESS BOOLEAN PREDICATES THAT MAY CHANGE NO_EDGE OR ISSUANCE",
            "SOURCE_OWNER_1596: ORIGINAL CYCLE_NAVIGATOR-PACKAGE BINDING AND TRUE SOURCE AVAILABILITY FOR 1-3D AND 5-7D",
            "SOURCE_OWNER_1596: ALL ATTEMPTED/NO_FORECAST/MISSING/ABSTAIN/NEGATIVE EPISODE DENOMINATOR, CLOSED UTC TARGETS",
            "AFTER PIT AND UNTOUCHED PROSPECTIVE N: MATCH B2/B0 BASELINES, SCORE ONLY MATURED PREDECLARED HOLDOUT",
            "ORIGINAL_ALPHA_98_AND_EDGE_1530: FIRST EXECUTABLE FULL SELL, COSTS AND MATCHED NET LIQUIDATABLE WEALTH",
        ],
        "original_rows":rows,
        "prohibitions":{
            "historical_PIT_promoted":False,
            "new_future_predictions":False,
            "historical_outcomes_rescored":False,
            "private_market_or_wallet_values_copied":False,
            "Round3_analysis_authorized":False,
            "live_buy_sell":False,
            "original_forecasts_edited":False,
        },
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    output=build()
    payload=json.dumps(output,indent=2,sort_keys=True)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(payload)
    else:
        print(payload,end="")

if __name__=="__main__":
    main()
