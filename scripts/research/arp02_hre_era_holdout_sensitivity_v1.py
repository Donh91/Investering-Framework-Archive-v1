#!/usr/bin/env python3
"""Risk owner #1553: original HRE five-era leave-one-out warning-loss check.

Deterministic source-blob-pinned price-only research. A historical daily 72h
outcome label is correlated with nearby daily cutoffs and is NOT a separately
delivered investor warning or independent shock sample. Costs are hypothetical
classification units, not fees, PnL, or opportunity costs.
"""
from __future__ import annotations

import json
from pathlib import Path
from scripts.research import arp02_hre_price_control_cost_sensitivity_v1 as base

CONTRACT = "ARP02_HRE_LEAVE_ONE_ERA_OUT_WARNING_LOSS_v1"
ASSETS = base.ASSETS
ERAS = base.ERAS


def evaluate(source: dict) -> dict:
    prior = base.evaluate(source)  # original source authority, roster, quote & 418-row guards
    episodes = prior["per_era"]
    if len(episodes) != 5 or tuple(r["episode_id"] for r in episodes) != ERAS:
        raise ValueError("HRE_ORIGINAL_ERA_ROSTER_CHANGED")
    output = {}
    for asset in ASSETS:
        deltas = {}
        for episode in episodes:
            b = episode[asset]["price_baseline"]
            c = episode[asset]["price_candidate"]
            deltas[episode["episode_id"]] = {
                "extra_false_positive_daily_cutoffs": c["fp"] - b["fp"],
                "extra_true_positive_daily_cutoffs": c["tp"] - b["tp"],
                "fewer_false_negative_daily_cutoffs": b["fn"] - c["fn"],
                "delta_equal_unit_misclassification_loss": (c["fp"] + c["fn"]) - (b["fp"] + b["fn"]),
            }
        leave_one_out = []
        for excluded in ERAS:
            remaining = [deltas[e] for e in ERAS if e != excluded]
            extra_fp = sum(z["extra_false_positive_daily_cutoffs"] for z in remaining)
            fewer_fn = sum(z["fewer_false_negative_daily_cutoffs"] for z in remaining)
            if extra_fp < 0 or fewer_fn < 0:
                raise ValueError("ORIGINAL_SENSITIVITY_DIRECTION_CHANGED")
            leave_one_out.append({
                "held_out_era": excluded,
                "retained_era_count": 4,
                "extra_false_positive_daily_cutoffs": extra_fp,
                "fewer_false_negative_daily_cutoffs": fewer_fn,
                "delta_equal_unit_misclassification_loss": extra_fp - fewer_fn,
                "hypothetical_missed_to_false_penalty_ratio_break_even":
                    round(extra_fp / fewer_fn, 6) if fewer_fn else None,
                "claim": "CORRELATED_RETROSPECTIVE_DAILY_CUTOFFS_NOT_FORWARD_HOLDOUT",
            })
        overall = prior["assets"][asset]
        if (sum(z["extra_false_positive_daily_cutoffs"] for z in deltas.values()) !=
                overall["extra_false_alarms"]
                or sum(z["fewer_false_negative_daily_cutoffs"] for z in deltas.values()) !=
                overall["fewer_missed_outcome_windows"]):
            raise ValueError("HRE_CROSS_SOURCE_SENSITIVITY_MISMATCH")
        # These hypothetical ratios are post-hoc sensitivity probes, NOT
        # predeclared investor weights or observed economic/after-cost outcomes.
        hypothetical_k = (1, 2, 3, 5, 10)
        output[asset] = {
            "break_even_k_by_leave_one_out": [
                row["hypothetical_missed_to_false_penalty_ratio_break_even"]
                for row in leave_one_out
            ],
            "challenger_better_at_k": {
                str(k): sum(
                    row["extra_false_positive_daily_cutoffs"]
                    - k * row["fewer_false_negative_daily_cutoffs"] < 0
                    for row in leave_one_out
                ) for k in hypothetical_k
            },
            "evaluated_cost_ratios_are_posthoc_descriptive": True,
            "investor_miss_cost_predeclared": False,
            "original_deltas_by_selected_era": deltas,
            "leave_one_era_out": leave_one_out,
            "all_five_removals_worse_at_equal_unit_loss":
                all(z["delta_equal_unit_misclassification_loss"] > 0
                    for z in leave_one_out),
            "original_full_418_cutoff_equal_unit_loss_delta":
                overall["delta_equal_unit_classification_loss"],
        }
    return {
        "contract": CONTRACT, "original_risk_owner": "Archive#1553",
        "scientific_source_owner": "Archive#1596",
        "input_source_path": base.SOURCE_PATH,
        "input_git_blob_sha1": base.SOURCE_BLOB_SHA1,
        "source_native_run": prior["source_native_run"],
        "historical_source_class": prior["historical_source_class"],
        "retrospectively_selected_era_count": 5,
        "independent_shock_count_certified": None,
        "original_user_warning_issued_or_delivered_proven": False,
        "original_risk_3_of_5_timing_explained": False,
        "same_clock_noncrisis_control_proven": False,
        "hypothetical_loss_is_executable_investor_cost": False,
        "baseline_or_challenger_promoted": False,
        "live_risk_threshold_changed": False,
        "trading_or_portfolio_authority": False,
        "assets": output,
        "science_grade": "RETROSPECTIVE_PRICE_ONLY_SENSITIVITY_NO_PROSPECTIVE_EDGE",
    }


def build(root: Path = base.ROOT) -> dict:
    return evaluate(base.read_source(root))


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
