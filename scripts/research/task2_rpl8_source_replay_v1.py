#!/usr/bin/env python3
"""Task 2 #1596, bounded eight-lane public-source reconciliation.

This script only calculates descriptive source/readiness and negative controls
from already archived public evidence. It cannot certify vendor first-known,
independent event-family power, issued original forecasts, economic utility,
or model/trading promotion. No market/network calls or repository writes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.research import task2_archive_first_edge_matrix_v1 as prior
from scripts.research import task2_cfgi_capture_clock_audit_v1 as cfgiclock

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = "TASK2_RESEARCH_PARALLEL_LANES_8_SOURCE_REPLAY_v1"
OWNER = "https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596"
OLD_ASOF = "2026-11-06T14:30:00Z"
NEW_ASOF = "2026-11-07T09:00:10Z"
SOURCES = {
    "r1": "04_MARKET_LEARNING/handlekompas/research/2026-10-15__TASK2_R1_NATIVE_V3_ORIGINAL_ADMISSION_v2.json",
    "official": "06_RESEARCH_LAB/hugging_face_task2_audit_20261022/29_FULL_70_ORIGINAL_AS_ISSUED_HORIZON_COVERAGE_20261023.json",
    "m1": "06_RESEARCH_LAB/audit_summaries/sensor_survival_v1/data/M1_FREQUENCY_MATCHED_TIMING_PLACEBO.csv",
    "gate": "04_MARKET_LEARNING/handlekompas/research/2026-10-13__TASK_1_5_EDGE_ADMISSION_GATE_v1.json",
    "ironflow": "06_RESEARCH_LAB/hugging_face_task2_audit_20261022/IRONFLOW_TEN_LANE_EVIDENCE_SCORECARD_20261107.json",
}

def read_public(root: Path, rel: str) -> tuple[bytes, dict]:
    base = root.resolve()
    source = root / rel
    if ("Donh91/secrets" in rel or not source.is_file()
            or source.is_symlink() or not source.resolve().is_relative_to(base)):
        raise ValueError("INVALID_PUBLIC_SOURCE:" + rel)
    body = source.read_bytes()
    if not body or len(body) > 2_000_000:
        raise ValueError("SOURCE_SIZE_OR_EMPTY:" + rel)
    blob = hashlib.sha1(b"blob " + str(len(body)).encode() + b"\x00" + body).hexdigest()
    identity = {"path":rel,"git_blob_sha1":blob, "sha256":hashlib.sha256(body).hexdigest(),
                "bytes":len(body)}
    return body, identity

def balanced(cm: dict) -> float | None:
    positive = cm["tp"] + cm["fn"]
    negative = cm["tn"] + cm["fp"]
    if positive <= 0 or negative <= 0:
        return None
    return round(100 * (cm["tp"] / positive + cm["tn"] / negative) / 2, 3)

def measures(cm: dict) -> dict:
    if cm["n"] != cm["tp"] + cm["tn"] + cm["fp"] + cm["fn"]:
        raise ValueError("MATRIX_DENOMINATOR_MISMATCH")
    return {
        "n":cm["n"],"tp":cm["tp"],"tn":cm["tn"],
        "fp":cm["fp"],"fn":cm["fn"],
        "correct_total":cm["tp"] + cm["tn"],
        "accuracy_pct":cm["accuracy_pct"],
        "balanced_accuracy_pct":balanced(cm),
        "independent_market_event_n":None
    }

def count_bh_exploratory(table: list[dict], alpha: float = .05) -> dict:
    """Descriptive, NOT valid causal multiplicity-adjusted discovery.

    Original tests across four overlapping time horizons and related rule
    families are NOT independent. Published zero Monte Carlo p is not exact zero.
    """
    tests = []
    for row in table:
        p = float(row["p_random_one_to_one_ge_observed"])
        if not 0 <= p <= 1:
            raise ValueError("UNSAFE_ORIGINAL_PLACEBO_P")
        tests.append(p)
    ordered = sorted(tests)
    passed = [i for i, p in enumerate(ordered, 1) if p <= alpha * i / len(tests)]
    return {
        "exploratory_test_cells":len(tests),
        "naive_BH_cells_meeting_05_threshold":max(passed, default=0),
        "published_zero_p_values_not_exact_zero":tests.count(0),
        "BH_valid_independent_eligible_hypothesis_family":False,
        "after_selection_discovery_or_edge_claim":False,
    }

def build(root: Path = ROOT) -> dict:
    root = Path(root).resolve()
    values = {}
    identity = {}
    for label, rel in SOURCES.items():
        raw, identity[label] = read_public(root, rel)
        values[label] = (list(csv.DictReader(raw.decode().splitlines()))
                         if label == "m1" else json.loads(raw))
    # Frozen as-of replays use the original research scorer, whose source and
    # outcome hash/clock validations are still authoritative within its scope.
    source, _ = prior.read_sources(root)
    earlier = prior.audit_e2(source, prior.utc(OLD_ASOF))
    later = prior.audit_e2(source, prior.utc(NEW_ASOF))
    summary = prior.build(root, prior.utc(NEW_ASOF))
    clock = cfgiclock.audit()
    r1, official, gate, iron = (values[k] for k in ("r1","official","gate","ironflow"))
    cohort = r1["cohort"]
    if (cohort["original_attempts"] != 11 or cohort["admitted"] != 0
            or cohort["original_outcomes_present"] + cohort["original_outcomes_absent"] != 11):
        raise ValueError("ORIGINAL_R1_ADMISSION_DRIFT")
    if (official["original_forecast_files_directly_read_at_pinned_original_main"] != 70
            or sum(official["original_versions"].values()) != 70):
        raise ValueError("ORIGINAL_FORECAST_COHORT_DRIFT")
    if (earlier["matured_7d_rows"] != 20 or earlier["matured_7d_positive"] != 18
            or earlier["matured_7d_negative"] != 2):
        raise ValueError("ORIGINAL_20_ROW_FROZEN_SNAPSHOT_CHANGED")
    original_c02 = earlier["models"]["C02_BREADTH"]
    if (original_c02["tp"] != 7 or original_c02["tn"] != 2
            or original_c02["accuracy_pct"] != 45):
        raise ValueError("ORIGINAL_20_ROW_C02_CORRECTNESS_CHANGED")
    if (later["matured_7d_rows"] != 23 or later["matured_7d_positive"] != 21
            or later["matured_7d_negative"] != 2):
        raise ValueError("ORIGINAL_23_ROW_FROZEN_SNAPSHOT_CHANGED")
    if (iron["observed"]["file_count"] != 72
            or iron["observed"]["scored_months"] != 12):
        raise ValueError("IRONFLOW_SOURCE_SCORECARD_DRIFT")
    pub = gate["checks"]["owner_publication_by_exact_due_cutoff"]
    if pub["original_matured_count"] + pub["original_censored_count"] != 814:
        raise ValueError("ORIGINAL_RECEIPT_DENOMINATOR_MISMATCH")
    registered = gate["checks"]["original_forecast_cohort_replay"]["eligible_issued_asset_horizon_pairs_2026_09_15_to_2026_10_13_06Z"]
    if (registered != 824 or pub["original_matured_count"] + pub["original_censored_count"]
            + gate["checks"]["original_forecast_cohort_replay"]["missing_original_outcome_receipt_count"] != registered):
        raise ValueError("ORIGINAL_PREDICTION_CENSOR_DENOMINATOR_DRIFT")
    if clock["original_capture_count"] != 42 or clock["original_symbol_rows_count"] != 126:
        raise ValueError("CFGI_CAPTURE_CENSUS_DRIFT")
    old, new = earlier["models"], later["models"]
    score = iron["observed"]
    return {
        "contract":CONTRACT, "original_owner":OWNER,
        "status":"RETROSPECTIVE_SOURCE_RECONCILIATION_ONLY",
        "source_class":"PUBLIC_CONTROL_PLANE_ONLY",
        "source_identities":identity,
        "source_cutoffs_utc":[OLD_ASOF,NEW_ASOF],
        "execution_kind":"OFFLINE_DETERMINISTIC_CODE_NOT_AN_AI_AGENT",
        "no_new_automation":True, "no_restricted_source_read":True,
        "no_market_or_model_changes":True, "no_new_api_calls":True,
        "scientific_admission":{
            "original_pit_verified":False,"independent_shock_family_n":None,
            "prospective_incremental_information_edge":False,
            "after_cost_investor_edge":False, "round3_analysis_authorized":False,
        },
        "lanes":{
            "L01_original_PIT":{
                "original_issued_attempts":cohort["original_attempts"],
                "original_outcomes_present":cohort["original_outcomes_present"],
                "original_admitted":cohort["admitted"],"state":"SOURCE_CLOCK_BLOCKED"
            },
            "L02_original_horizon":{
                "original_issuances":70,
                "directional_12h":official["original_12h_U_D_directional_issuances"],
                "directional_72h":official["original_72h_U_D_directional_issuances"],
                "directional_168h":official["original_168h_U_D_directional_issuances"],
                "twelve_hour_coverage_pct":round(100 * official["original_12h_U_D_directional_issuances"] / 70,3),
                "long_horizon_hit_rate":"UNDEFINED_NO_DIRECTIONAL_ISSUES",
                "state":"COVERAGE_ONLY_NOT_MODEL_SKILL"
            },
            "L03_M1_frequency_placebo":{
                **count_bh_exploratory(values["m1"]),
                "C2_30d_reported_exploratory_p":summary["E1_warning"]["reported_comparison"][2]["c2_rule"]["reported_exploratory_p"],
                "C_family_30d_reported_exploratory_p":summary["E1_warning"]["reported_comparison"][2]["c_family"]["reported_exploratory_p"],
                "one_more_day_deployment_return_delta_pp":summary["E3_hidden_deterioration"]["one_day_strategy_sensitivity_pp"],
                "state":"CORRELATED_EX_POST_DEVELOPMENT_ONLY"
            },
            "L04_shared_row":{
                "frozen_earlier_7d":{key:measures(old[key]) for key in ("C02_BREADTH","C07_SIMPLE_3","B0_ALWAYS_POSITIVE")},
                "frozen_later_7d":{key:measures(new[key]) for key in ("C02_BREADTH","C07_SIMPLE_3","B0_ALWAYS_POSITIVE")},
                "independent_28d_blocks":later["fixed_28d_block_n"],
                "newly_matured":later["matured_7d_rows"]-earlier["matured_7d_rows"],
                "candidate_accuracy_change_not_candidate_signal_rewrite":True,
                "state":"SOURCE_MATCHED_DESCRIPTIVE_NOT_INDEPENDENT_EDGE"
            },
            "L05_breadth_ETF":{
                "weekly_frozen_snapshots":summary["E3_hidden_deterioration"]["frozen_breadth_weekly_snapshots"],
                "breadth_forward_MAE_deterioration_pp":summary["E3_hidden_deterioration"]["breadth_added_mae_deterioration_pp"],
                "etf_strong_edge":summary["E3_hidden_deterioration"]["etf_outflow_strong_edge_verdict"],
                "state":"NULL_AND_REJECTED_STRONG_CLAIM"
            },
            "L06_cfgi_clock":{
                "public_capture_runs":clock["original_capture_count"],
                "public_symbol_rows":clock["original_symbol_rows_count"],
                "symbol_clock_skewed_captures":clock["symbol_clock_skewed_captures"],
                "max_symbol_clock_skew_seconds":clock["maximum_original_symbol_clock_skew_seconds"],
                "provider_first_publication_verified":False,
                "state":"CAPTURE_METADATA_ONLY_NO_ORIGINAL_PIT_EDGE"
            },
            "L07_derivatives_18month":{
                "pinned_source_files":score["file_count"],
                "test_months":score["scored_months"],
                "tested_asset_days":score["scored_asset_days"],
                "mean_price_minus_derivatives_brier":score["model_brier_delta_month_mean"],
                "95pct_month_bootstrap_interval":score["model_brier_delta_month_bootstrap_95pct"],
                "original_source_first_known":"UNPROVEN_NOV_2026_HISTORICAL_PUBLICATION",
                "state":"EXISTING_REPLAY_RECONCILED_NO_REPLICATED_LIFT"
            },
            "L08_warning_action_delivery":{
                "registered_original_receipts":pub["original_censored_count"]+pub["original_matured_count"],
                "eligible_price_joined_predictions":registered,
                "original_matured":pub["original_matured_count"],
                "original_censored":pub["original_censored_count"],
                "missing_original_receipt":gate["checks"]["original_forecast_cohort_replay"]["missing_original_outcome_receipt_count"],
                "censored_share_of_price_joined_pct":round(100*pub["original_censored_count"]/registered,3),
                "user_message_delivery_proven":False,
                "after_cost_executable_action_proven":False,
                "state":"DELIVERY_AND_INVESTABILITY_BLOCKED"
            }
        },
        "next":"Original owner #1596: prospective source first-known+delivery and independent event-family outcomes; source-only descriptive negatives cannot be promoted.",
    }

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--output",type=Path)
    args = p.parse_args()
    report = build()
    # Only public-safe derived values, never raw provider rows or future data.
    encoded = json.dumps(report,sort_keys=True,indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(encoded,encoding="utf-8")
    print(json.dumps({"contract":report["contract"],"status":report["status"],
                      "lanes":{k:v["state"] for k,v in report["lanes"].items()},
                      "L04_new_matured":report["lanes"]["L04_shared_row"]["newly_matured"],
                      "L04_C02_correct":report["lanes"]["L04_shared_row"]["frozen_later_7d"]["C02_BREADTH"]["correct_total"],
                      "L06_symbol_clock_skewed":report["lanes"]["L06_cfgi_clock"]["symbol_clock_skewed_captures"]},
                     sort_keys=True))

if __name__ == "__main__":
    main()
