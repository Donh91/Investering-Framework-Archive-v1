#!/usr/bin/env python3
"""Task2 R1 chronologically-first original issuance and Round3 cadence metadata preflight.

Public original source/clock metadata, original owner receipt only. No source
values, outcomes, remote fetch, private source analysis, live rule or trading.
Unverified original-vintage evidence never becomes point-in-time permission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from scripts.research import task2_r1_original_causal_source_matrix_v1 as causal

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = "TASK2_R1_FIRST_KNOWN_AND_R3_CADENCE_PREFLIGHT_v1"
ISSUE = 1596
SOURCE_PATH = ("04_MARKET_LEARNING/handlekompas/research/"
               "2026-10-15__TASK2_R1_NATIVE_V3_ORIGINAL_ADMISSION_v2.json")
GATE_PATH = ("04_MARKET_LEARNING/handlekompas/research/"
             "2026-10-13__TASK_1_5_EDGE_ADMISSION_GATE_v1.json")
FROZEN_BLOBS = {
    SOURCE_PATH: "9e728b835de294e5777222c171a89874a69dae95",
    GATE_PATH: "b7e3dc8c1b1e8f948df72ef32fa762e7667a6bde",
}
ROLE_ALLOWED = {
    "DIRECT_12H_DIRECTION_DELTA", "ORIGINAL_PRICE_INPUT_TO_DIRECTION_DELTA_AND_REFERENCE",
    "RELATIVE_DIRECTION_CONTEXT_NOT_BTC_ETH_12H_SIGN", "EVIDENCE_INDEX_NOT_DIRECT_12H_SIGN",
}
CLOCK_KINDS = {
    "RETRIEVAL_CLOCK_UNKNOWN", "ARCHIVE_CLOCK_PREISSUE_PROVIDER_FIRST_KNOWN_UNKNOWN",
    "SETTLEMENT_IS_NOT_QUOTE_OBSERVATION", "NOT_ADMITTED_RETRIEVED_AFTER_ISSUE",
    "NOT_ADMITTED_OBSERVATION_AFTER_ISSUE",
}
SCHEDULES = {
    "SC01_OKX_ETH_OI_HOURLY_V1": {"target_interval_minutes":60,"observed_runs_per_day":2},
    "SC03_OKX_ETH_REALIZED_FUNDING_V1": {"target_interval_minutes":15,"observed_runs_per_day":2},
    "SC14_DERIBIT_ETH_TRUE_25D_SKEW_V1": {"target_interval_minutes":60,"observed_runs_per_day":2},
}
PRIVATE_REF = "c9e16b72585d5d22442f8239f6e8432dc241ec0e"
PRIVATE_ACTIVATION_BLOB = "ff3a4489d22ba005a86b7902ed407d6be58e6758"
PRIVATE_HEALTH_BLOB = "490bd232e78f35899af61b6d14a6a0382fbe4294"

def utc(value: str) -> datetime:
    if not isinstance(value,str) or not value:
        raise ValueError("BAD_ISSUE_OR_RETRIEVAL_CLOCK")
    parsed = datetime.fromisoformat(value.replace("Z","+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("NAIVE_CLOCK_FORBIDDEN")
    return parsed.astimezone(timezone.utc)

def bound_json(root: Path,path: str):
    file=root/path
    if not file.is_file() or file.is_symlink() or not file.resolve().is_relative_to(root.resolve()):
        raise ValueError("UNSAFE_ORIGINAL_SOURCE")
    raw=file.read_bytes()
    sha=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()
    if sha!=FROZEN_BLOBS[path]:
        raise ValueError("ORIGINAL_PINNED_SOURCE_BLOB_DRIFT "+path)
    return json.loads(raw)

def source_matrix(original: dict) -> dict:
    cohort=original["cohort"]
    rows=original["rows"]
    if (len(rows)!=11 or cohort["original_attempts"]!=11
            or cohort["admitted"]!=0 or cohort["independent_market_event_families_certified"]!=0):
        raise ValueError("ORIGINAL_COHORT_CHANGED")
    by_id=set()
    case_rows=[]
    role_counts=Counter()
    clock_counts=Counter()
    per_feature=Counter()
    issuer_delivery=0
    source_after_issue=0
    verified_vendor_publication=0
    for row in sorted(rows,key=lambda x:x["issued_at_utc"]):
        fid=row["forecast_id"]
        if fid in by_id:
            raise ValueError("DUPLICATE_ORIGINAL_ISSUE")
        by_id.add(fid)
        issue=utc(row["issued_at_utc"])
        features=row["selected_feature_clocks"]
        if len(features)!=24 or len({f["feature_id"] for f in features})!=24 or set(f["feature_id"] for f in features)!=set(causal.ROLES):
            raise ValueError("ORIGINAL_FEATURE_ROSTER_DRIFT")
        packet=utc(row["source_packet"]["first_git_commit_at_utc"])
        capture=utc(row["raw_capture"]["captured_at_utc"])
        capture_committed=utc(row["raw_capture"]["git_commit_at_utc"])
        if packet>issue or capture_committed>issue or capture>issue:
            source_after_issue+=1
            raise ValueError("ORIGINAL_SOURCE_PUBLISHED_AFTER_ISSUE")
        missing_release=0
        known_archive_retrieval=0
        for field in features:
            key=field["feature_id"]
            role=causal.ROLES[key]
            state=field["observation_clock_status"]
            if state not in CLOCK_KINDS or role not in ROLE_ALLOWED:
                raise ValueError("ORIGINAL_FIELD_CLOCK_ROLE_UNEXPECTED")
            retrieval=field.get("declared_retrieved_at")
            if retrieval is not None:
                known_archive_retrieval+=1
                if utc(retrieval)>issue:
                    raise ValueError("RETRIEVAL_AFTER_ORIGINAL_ISSUE")
            if field.get("vendor_first_publication_at") is None:
                missing_release+=1
            else:
                verified_vendor_publication+=1
                # Presence alone is not independent verification or issuer proof.
            role_counts[role]+=1
            clock_counts[state]+=1
            per_feature[key]+=1
        issuer_delivery+=int(bool(row.get("first_user_delivery_at_utc")))
        case_rows.append({
            "original_forecast_id":fid,
            "issued_utc":row["issued_at_utc"],
            "source_packet_first_git_commit_utc":row["source_packet"]["first_git_commit_at_utc"],
            "original_raw_capture_utc":row["raw_capture"]["captured_at_utc"],
            "original_raw_capture_first_git_commit_utc":row["raw_capture"]["git_commit_at_utc"],
            "issue_minus_packet_commit_seconds":int((issue-packet).total_seconds()),
            "issue_minus_capture_committed_seconds":int((issue-capture_committed).total_seconds()),
            "capture_age_at_issue_seconds":int((issue-capture).total_seconds()),
            "original_source_retrieval_clocks_present":known_archive_retrieval,
            "feature_fields_without_vendor_first_publication":missing_release,
            "first_user_delivery_documented":bool(row.get("first_user_delivery_at_utc")),
            "original_outcome_status":row["original_outcome_status"],
            "source_packet_blob":row["source_packet"]["git_blob_sha"],
            "raw_capture_blob":row["raw_capture"]["git_blob_sha"],
            "original_forecast_blob":row["original_forecast_git_blob_sha"],
            "source_internal_provenance_pass":row["data_quality"]["internal_packet_and_capture_blobs_verified"],
            "source_legal_admission":"BLOCKED_VENDOR_FIRST_PUBLICATION_AND_INDEPENDENCE",
        })
    if (sum(role_counts.values())!=264 or sum(clock_counts.values())!=264
            or len(per_feature)!=24 or any(x!=11 for x in per_feature.values())
            or verified_vendor_publication!=0 or issuer_delivery!=0
            or dict(role_counts)!={"DIRECT_12H_DIRECTION_DELTA":22,
                "ORIGINAL_PRICE_INPUT_TO_DIRECTION_DELTA_AND_REFERENCE":22,
                "RELATIVE_DIRECTION_CONTEXT_NOT_BTC_ETH_12H_SIGN":22,
                "EVIDENCE_INDEX_NOT_DIRECT_12H_SIGN":198}):
        raise ValueError("ORIGINAL_SOURCE_ROLE_OR_DELIVERY_DRIFT")
    return {"original_attempts":len(rows),
        "source_field_instances":264,
        "original_direction_delta_field_instances":role_counts["DIRECT_12H_DIRECTION_DELTA"],
        "original_non_direct_sign_evidence_index_instances":role_counts["EVIDENCE_INDEX_NOT_DIRECT_12H_SIGN"],
        "role_counts":dict(sorted(role_counts.items())),
        "clock_counts":dict(sorted(clock_counts.items())),
        "vendor_first_publication_authenticated_count":0,
        "user_delivery_known_count":issuer_delivery,
        "first_case_preselected_by_issue_clock_only":case_rows[0],
        "original_11_case_clock_ledger":case_rows,
        "full_original_R1_PIT_admitted":0,
        "missing_no_forecast_hours": "UNKNOWN_NOT_ENUMERATED",
        "independent_market_shocks":"UNKNOWN_NOT_PROVEN",
    }

def cadence_preflight(schedules=None):
    schedules=SCHEDULES if schedules is None else schedules
    if set(schedules)!=set(SCHEDULES):
        raise ValueError("PRIVATE_SOURCE_CONTRACT_UNEXPECTED")
    out={}
    daily_proposed=0
    daily_actual=0
    for name,entry in schedules.items():
        interval=entry["target_interval_minutes"]
        observed=entry["observed_runs_per_day"]
        if interval not in (15,60) or observed!=2:
            raise ValueError("CADENCE_OBSERVATION_DRIFT")
        target=1440//interval
        daily_proposed+=target
        daily_actual+=observed
        out[name]={
            "frozen_nominal_interval_minutes":interval,
            "observed_scheduled_runs_per_day":observed,
            "nominal_target_runs_per_day":target,
            "nominal_schedule_shortfall_runs_per_day":target-observed,
            "source_interval_compliance":False,
            "genuine_capture_coverage_from_schedule_alone":"NOT_IDENTIFIABLE",
        }
    return {
        "private_main_snapshot":PRIVATE_REF,
        "private_activation_git_blob":PRIVATE_ACTIVATION_BLOB,
        "private_health_git_blob":PRIVATE_HEALTH_BLOB,
        "activation_authority":"ACTIVE_PROSPECTIVE_COLLECTION_ONLY",
        "source_contracts":out,
        "combined_scheduled_runs_daily":daily_actual,
        "combined_nominal_target_runs_daily":daily_proposed,
        "additional_scheduled_runs_per_30d_if_naively_restored":30*(daily_proposed-daily_actual),
        "monthly_actions_minutes_known":False,
        "estimated_actions_minutes_from_schedule_alone":None,
        "restoring_nominal_cadence_approved_without_budget_measurement":False,
        "round3_hypothesis_testing_allowed":False,
        "round3_outcome_scoring_allowed":False,
        "required_followup":"MEASURE_JOB_RUNTIME_P50_P95_AND_MONTHLY_ACTIONS_MINUTES_THEN_REVIEW_CADENCE_WITHIN_BUDGET",
    }

def build(root: Path=ROOT) -> dict:
    original=bound_json(root,SOURCE_PATH)
    gate=bound_json(root,GATE_PATH)
    first=source_matrix(original)
    pub=gate["checks"]["owner_publication_by_exact_due_cutoff"]
    owner=gate["checks"]["original_forecast_cohort_replay"]
    if pub["original_matured_count"]!=314 or pub["original_censored_count"]!=500 or owner["missing_original_outcome_receipt_count"]!=10:
        raise ValueError("ORIGINAL_PUBLICATION_OUTCOME_GATE_DRIFT")
    return {
        "contract":CONTRACT,
        "original_scientific_owner":"Donh91/Investering-Framework-Archive-v1#1596",
        "authority":"RESEARCH_ONLY_PUBLIC_SOURCE_METADATA",
        "source_public_blob_ids":FROZEN_BLOBS,
        "first_issue_preflight":first,
        "private_round3_schedule_metadata":cadence_preflight(),
        "original_outcome_receipts":{"retrospective_price_joined":824,
                                     "original_matured":314,
                                     "original_censored":500,
                                     "original_receipt_missing":10},
        "separate_baseline_and_delivery_gate":"BLOCKED_UNVERIFIED_ORIGINAL_FIRST_KNOWN",
        "prospective_frozen_new_cohort_registered":False,
        "source_clock_and_no_forecast_denominator_complete":False,
        "live_market_model_or_cadence_changed":False,
        "private_values_processed":False,
        "economic_signal_or_trading_authority":False
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    report=build()
    out=json.dumps(report,sort_keys=True,indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(out)
    print(json.dumps({
        "contract":CONTRACT,
        "r1_original_attempts":report["first_issue_preflight"]["original_attempts"],
        "first_original_issue":report["first_issue_preflight"]["first_case_preselected_by_issue_clock_only"]["original_forecast_id"],
        "verified_vendor_first_publication":report["first_issue_preflight"]["vendor_first_publication_authenticated_count"],
        "R3_actual_scheduled_daily":report["private_round3_schedule_metadata"]["combined_scheduled_runs_daily"],
        "R3_nominal_target_daily":report["private_round3_schedule_metadata"]["combined_nominal_target_runs_daily"],
        "scientific_edge_proven":False
    },sort_keys=True))

if __name__=="__main__":
    main()
