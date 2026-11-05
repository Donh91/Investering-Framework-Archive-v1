#!/usr/bin/env python3
"""Reconcile existing Task2 R1 ORIGINAL receipts before any backtest release.

Public-safe, offline, provenance-only. No forecasts, outcome rescoring, market
data requests or strategy selection. Historical receipt pins are immutable.
Changing the population/receipt requires a separately reviewed new version.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = "06_RESEARCH_LAB/hugging_face_task2_audit_20261022/"
SOURCES = {
    "ledger": (
        "04_MARKET_LEARNING/handlekompas/research/"
        "2026-10-15__TASK2_R1_NATIVE_V3_ORIGINAL_ADMISSION_v2.json",
        "9e728b835de294e5777222c171a89874a69dae95",
    ),
    "source": (
        BASE+"task2_cohort_source_replay_result.json",
        "b7299bd278a860aa1057069103c4504046aeb63d",
    ),
    "comparison": (
        BASE+"task2_scoped_development_comparison_result.json",
        "3a64faccb41a713c8e5f1b1a84a393a3c7917054",
    ),
    "custody": (
        BASE+"23_SOURCE_CUSTODY_BINDINGS_20261023.json",
        "443541e3648df9b993a3e2275f288eb30748f130",
    ),
}
SOURCE_CONTRACT = "TASK2_R1_SCOPED_SOURCE_READINESS_RECONCILIATION_v1"
FROZEN_MAIN = "098c50d36b222c4c8ffa179a5879d36a74194bc4"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
TIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?Z$")


def need(ok, code):
    if not ok:
        raise ValueError("TASK2_RECONCILE_"+code)


def utc(stamp):
    need(isinstance(stamp, str) and TIME.fullmatch(stamp), "NONUTC_OR_MALFORMED_CLOCK")
    try:
        # GitHub server's timestamp can have nanosecond fractional precision.
        return datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("TASK2_RECONCILE_UNREADABLE_UTC_CLOCK") from exc


def pinned_inputs(root=ROOT):
    result = {}
    for label, (path, expected_blob) in SOURCES.items():
        raw = (Path(root) / path).read_bytes()
        git_blob = hashlib.sha1(
            b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
        ).hexdigest()
        need(git_blob == expected_blob, "IMMUTABLE_"+label.upper()+"_BLOB_CHANGED")
        result[label] = json.loads(raw)
    return result


def unique_index(rows, key, label):
    need(isinstance(rows, list), label+"_NOT_LIST")
    entries = {}
    for item in rows:
        need(isinstance(item, dict) and isinstance(item.get(key), str), label+"_INVALID_ID")
        ident = item[key]
        need(ident not in entries, label+"_DUPLICATE_ID")
        entries[ident] = item
    return entries


def components(intervals):
    """Count overlapping forecast/outcome windows, NOT market-shock families."""
    spans = sorted(intervals)
    total = 0
    last_end = None
    for start, end in spans:
        need(start < end, "NONFORWARD_ORIGINAL_TARGET")
        if last_end is None or start > last_end:
            total += 1
            last_end = end
        elif end > last_end:
            last_end = end
    return total


def reconcile(inputs):
    need(isinstance(inputs, dict) and set(inputs) == set(SOURCES), "INPUT_SET")
    ledger, source, compare, custody = (
        inputs["ledger"], inputs["source"], inputs["comparison"], inputs["custody"]
    )
    need(ledger.get("contract") == "TASK2_R1_NATIVE_V3_ORIGINAL_ADMISSION_v2", "ORIGINAL_CONTRACT")
    need(ledger.get("status") == "RESEARCH_ONLY_NOT_ADMITTED", "ORIGINAL_GATE_CHANGED")
    need(ledger.get("original_snapshot_sha") == FROZEN_MAIN, "ORIGINAL_SNAPSHOT_CHANGED")
    need(source.get("contract") == "TASK2_ORIGINAL_11_COHORT_SCOPED_12H_SOURCE_REPLAY_v1", "SOURCE_CONTRACT")
    need(compare.get("contract") == "TASK2_SCOPED_ORIGINAL_12H_B2_DEVELOPMENT_REPRODUCTION_v1", "COMPARISON_CONTRACT")
    need(custody.get("contract") == "TASK2_AUTHORIZED_HISTORICAL_SOURCE_CUSTODY_AND_SCOPED_DEVELOPMENT_v1", "CUSTODY_CONTRACT")
    need(compare.get("frozen_original_snapshot") == FROZEN_MAIN, "COMPARISON_SNAPSHOT_CHANGED")
    need(compare.get("classification") == "EXPOSED_DEVELOPMENT_ONLY_NOT_CERTIFIED_R2_OR_HOLDOUT", "COMPARISON_PROMOTED")
    need(compare.get("source_audit_result_sha256")
         == custody["outputs"]["task2_cohort_source_replay_result.json"]["sha256"],
         "SOURCE_DIGEST_IDENTITY")

    lr = unique_index(ledger.get("rows"), "forecast_id", "ORIGINAL")
    sr = unique_index(source.get("rows"), "forecast_id", "SOURCE")
    cr = unique_index(compare.get("rows"), "forecast_id", "COMPARISON")
    need(len(lr) == len(sr) == len(cr) == 11 and set(lr) == set(sr) == set(cr),
         "ORIGINAL_ATTEMPT_DENOMINATOR")
    need(ledger["cohort"]["original_attempts"] == 11 and
         ledger["cohort"]["admitted"] == 0 and
         ledger["cohort"]["independent_market_event_families_certified"] == 0,
         "ORIGINAL_SCIENCE_GATE")
    summary = source["summary"]
    need(summary["original_forecasts"] == 11 and
         summary["numeric_source_and_original_replay_passed"] == 11 and
         summary["scope_specific_source_chain_complete"] == 10 and
         summary["full_R1_automatic_admissions"] == 0,
         "SOURCE_SUMMARY_CHANGED")
    need(source["provider_exact_first_publication_verified"] is False and
         source["full_compass_or_investor_economics_admitted"] is False and
         source["untouched_holdout"] is False and
         source["outcomes_read_or_scored"] is False and
         source["independent_market_event_count"] is None,
         "SOURCE_SCIENCE_PROMOTION")
    need(compare["R2_release_or_original_R1_ledger_change"] is False and
         compare["generalizable_information_edge_established"] is False and
         compare["investor_delivery_fills_costs_or_economics_verified"] is False and
         compare["untouched_holdout"] is False and
         compare["new_preregistration_before_outcome_exposure"] is False and
         compare["certified_independent_market_event_families"] is None,
         "COMPARISON_SCIENCE_PROMOTION")
    need(custody["restricted_read_authority"]["owner_approved"] is True and
         custody["restricted_read_authority"]["round3_value_analysis_authorized_or_executed"] is False,
         "RESTRICTED_SOURCE_AUTHORITY")
    need(custody["scientific_authority"]["full_R1_automatic_admission"] is False and
         custody["scientific_authority"]["certified_R2_tournament_release"] is False and
         custody["scientific_authority"]["investor_economic_edge_established"] is False,
         "CUSTODY_SCIENCE_PROMOTION")

    complete_ids = []
    unverified_ids = []
    intervals = []
    original_present = 0
    original_absent = 0
    complete_with_outcome = 0
    matched = equal = model_correct = b2_correct = abstained = 0
    for fid, l in lr.items():
        s, c = sr[fid], cr[fid]
        need(l["admissibility"] == "NOT_ADMITTED" and
             l["information_edge_gate"]["status"] == "NOT_ADMITTED" and
             l["investor_action_edge_gate"]["status"] == "NOT_ADMITTED" and
             not l["investor_action_edge_gate"]["portfolio_execution_authorized"] and
             l["first_user_delivery_at_utc"] is None,
             "FORECAST_UNVERIFIED_GATE_"+fid)
        need(s["full_R1_admitted"] is False and c["full_R1_admitted"] is False,
             "FORGED_R1_ADMISSION_"+fid)
        need(s["numeric_source_and_original_replay_passed"] is True and
             s["required_health_lane_count"] == 11 and
             len(s["price_comparisons"]) == 3 and
             all(x["closed_current_prior_raw_csv_and_delta_equal"] is True
                 for x in s["price_comparisons"]),
             "SOURCE_REPLAY_OR_HEALTH_"+fid)
        need(c["forecast_git_blob"] == l["original_forecast_git_blob_sha"] and
             c["issued_at_utc"] == l["issued_at_utc"],
             "COMPARISON_ORIGINAL_IDENTITY_"+fid)
        issue = utc(l["issued_at_utc"])
        need(utc(s["hourly_source_availability_upper_bound_utc"]) <= issue,
             "HOURLY_AFTER_ISSUE_"+fid)
        pub = s["packet_publication"]
        is_complete = s["scope_specific_source_chain_complete"]
        need(type(is_complete) is bool and
             type(c["scoped_source_chain_complete"]) is bool and
             c["scoped_source_chain_complete"] == is_complete and
             pub["source_chain_complete"] == is_complete,
             "SOURCE_PUBLICATION_CONFLICT_"+fid)
        if is_complete:
            need(pub["server_log_commit_binding_verified"] is True and
                 pub["publication_job_conclusion"] == "success" and
                 pub["status"] == "COORDINATOR_BOUND_ORIGINAL_SERVER_SUCCESS_BEFORE_ISSUE" and
                 pub["publication_commit_sha"] ==
                    l["source_packet"]["first_git_commit_sha"] and
                 utc(pub["remote_push_reported_at_utc"]) <= issue and
                 utc(pub["publication_job_completed_at_utc"]) <= issue,
                 "SERVER_PUBLICATION_PROOF_"+fid)
            complete_ids.append(fid)
        else:
            need(pub["status"] == "UNVERIFIED" and
                 pub.get("server_log_commit_binding_verified") is not True,
                 "UNVERIFIED_SOURCE_DISGUISED_AS_COMPLETE_"+fid)
            unverified_ids.append(fid)
        if l["original_outcome_status"] == "PRESENT":
            original_present += 1
            need(c["original_outcome_status"] ==
                 "FROZEN_ORIGINAL_HASH_AND_TARGET_MATCHED" and
                 c["outcome_git_blob"] == l["original_outcome_git_blob_sha"] and
                 c["target_at_utc"] == l["original_target_at_utc"],
                 "ORIGINAL_OUTCOME_OR_TARGET_MISMATCH_"+fid)
            intervals.append((issue, utc(l["original_target_at_utc"])))
            if is_complete:
                complete_with_outcome += 1
        else:
            original_absent += 1
            need(l["original_outcome_status"] == "ABSENT_AT_ORIGINAL_SNAPSHOT" and
                 c.get("outcome_git_blob") is None and
                 c.get("target_at_utc") is None,
                 "BACKFILLED_OUTCOME_"+fid)
        counts = c["counts"]
        matched += counts.get("matched_slots", 0)
        equal += counts.get("direction_equal_slots", 0)
        model_correct += counts.get("model_correct_slots", 0)
        b2_correct += counts.get("B2_correct_slots", 0)
        abstained += counts.get("original_abstained_slots", 0)

    n_overlap = components(intervals)
    expected_counts = {
        "original_attempts": 11, "source_replayed": 11,
        "scoped_source_chain_complete": 10,
        "scoped_source_chain_unverified": 1,
        "original_outcomes_present": 9, "original_outcomes_absent": 2,
        "source_complete_original_outcome_rows": 8,
        "matched_nonabstained_asset_slots": 16, "directions_equal": 16,
        "model_correct": 7, "B2_correct": 7,
        "abstained_asset_slots": 2, "connected_outcome_overlap_blocks": 1,
        "certified_independent_market_event_families": 0,
        "full_historical_pit_admissions": 0,
    }
    observed = {
        "original_attempts": len(lr),
        "source_replayed": len(sr),
        "scoped_source_chain_complete": len(complete_ids),
        "scoped_source_chain_unverified": len(unverified_ids),
        "original_outcomes_present": original_present,
        "original_outcomes_absent": original_absent,
        "source_complete_original_outcome_rows": complete_with_outcome,
        "matched_nonabstained_asset_slots": matched, "directions_equal": equal,
        "model_correct": model_correct, "B2_correct": b2_correct,
        "abstained_asset_slots": abstained,
        "connected_outcome_overlap_blocks": n_overlap,
        "certified_independent_market_event_families": 0,
        "full_historical_pit_admissions": 0,
    }
    need(observed == expected_counts, "INDEPENDENT_DENOMINATOR_OR_RESULT_CHANGED")
    need(compare["counts"]["matched_slots"] == matched and
         compare["counts"]["model_correct_slots"] == model_correct and
         compare["counts"]["B2_correct_slots"] == b2_correct and
         compare["counts"]["original_outcomes_present"] == original_present and
         compare["counts"]["original_outcomes_absent"] == original_absent and
         compare["connected_overlap_blocks_in_nine_target_bound_rows"] == n_overlap and
         custody["results"]["original_attempts"] == 11 and
         custody["results"]["scope_specific_publication_complete_forecasts"] == 10 and
         custody["results"]["connected_overlap_blocks"] == n_overlap and
         custody["results"]["paired_correctness_lift"] == 0,
         "CROSS_RECEIPT_CONFLICT")
    need(len(unverified_ids) == 1 and
         unverified_ids[0] == custody["results"]["publication_unverified_forecast"],
         "MISSING_PUBLICATION_CASE_CHANGED")
    return {
        "contract": SOURCE_CONTRACT,
        "as_of_receipts": "2026-10-23_FROZEN_DEVELOPMENT_NOT_CURRENT_RUNTIME",
        "owner_issue": 1596,
        "source_git_blobs": {k: v[1] for k,v in SOURCES.items()},
        "counts": observed,
        "source_unverified_forecast_id": unverified_ids[0],
        "modes": {
            "ORIGINAL_SOURCE_REPLAY": "REPRODUCED_11_OF_11_DEVELOPMENT_ONLY",
            "EXPOSED_MATCHED_BASELINE": "REPRODUCED_NO_DIRECTIONAL_LIFT_7_OF_16_EACH",
            "HISTORICAL_PIT_MODEL_BACKTEST": "BLOCKED_SOURCE_VINTAGE_AND_INDEPENDENT_N",
            "AFTER_COST_INVESTOR_TOURNAMENT": "BLOCKED_DELIVERY_EXECUTION_SELLABILITY_AND_ORIGINAL_PIT",
            "PROSPECTIVE_HOLDOUT": "MUST_USE_NEW_ORIGINAL_ISSUES_AND_MATURED_TARGETS",
            "ROUND3_OUTCOME_ANALYSIS": "FORBIDDEN_PROSPECTIVE_COLLECTION_ONLY",
        },
        "source_proof_scope": "COORDINATOR_BOUND_ORIGINAL_GITHUB_JOB_LOGS_NOT_REAUTHENTICATED_BY_OFFLINE_RECONCILER",
        "economic_edge_claim": False,
        "forecast_accuracy_edge_claim": False,
        "portfolio_execution_allowed": False,
        "next_gates": {
            "source_owner_1596": "authentic original source vintage for every model-decision field or independently preserved original response; original 10/11 limited scope != whole Compass PIT",
            "publication_owner_1596": "independently recover server publication witness for the single unverified original, or retain exclusion",
            "sample_owner_1596": "new separate prospective issue/target event families with full nonwinner/abstain and same-clock baseline",
            "alpha_owner_98": "first-known original bid-ask+capacity+full SELL and all frictions",
            "round3": "analysis OFF until separate authorized original governance change",
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, help="Optional public-safe receipt destination")
    args = parser.parse_args()
    result = reconcile(pinned_inputs())
    payload = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.out:
        args.out.write_text(payload)
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
