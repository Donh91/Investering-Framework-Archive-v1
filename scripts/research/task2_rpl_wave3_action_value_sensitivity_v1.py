#!/usr/bin/env python3
"""Task2 #1596, bounded Wave3 action utility sensitivity, no hypothetical fill.

Scores only original public binary outcome receipts and archived historic M1
latency summary. A unit misclassification-loss ratio is NOT a market PnL,
portfolio payoff, executable trade, original holdout, or financial edge.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path

from scripts.research import task2_archive_first_edge_matrix_v1 as prior
from scripts.research import task2_r1_first_known_and_cadence_preflight_v1 as preflight

ROOT=Path(__file__).resolve().parents[2]
CONTRACT="TASK2_RPL_WAVE3_ACTION_VALUE_SENSITIVITY_v1"
OLD_CUTOFF="2026-11-06T14:30:00Z"
NEW_CUTOFF="2026-11-07T09:00:10Z"
LATENCY_PATH="06_RESEARCH_LAB/audit_summaries/sensor_survival_v1/data/M4_STRATEGY_OPERATIONAL_LATENCY_TEST.csv"
LATENCY_BLOB="5689ebe69096ef6e348146c1408be447a85469d0"
M1_PATH="06_RESEARCH_LAB/audit_summaries/sensor_survival_v1/data/M1_RULE_TIMING_ATLAS.csv"
M1_BLOB="4ad596248bbee55aa8fc6aad596b5feab3d427eb"
REQUIRE_CANDIDATES=("C02_BREADTH","C07_SIMPLE_3","B0_ALWAYS_POSITIVE")

def read_csv(root:Path, name:str, frozen_blob:str) -> list[dict]:
    path=root/name
    if (not path.is_file() or path.is_symlink()
            or not path.resolve().is_relative_to(root.resolve())):
        raise ValueError("INVALID_ORIGINAL_PUBLIC_CSV")
    raw=path.read_bytes()
    sha=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()
    if sha!=frozen_blob:
        raise ValueError("SOURCE_BLOB_DRIFT "+name)
    return list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))

def errors(matrix:dict,*,fp_loss:float=1.0,fn_loss:float=1.0) -> float:
    """Unit binary decision loss, NOT trading cost or realised performance."""
    if fp_loss<0 or fn_loss<0 or fp_loss!=fp_loss or fn_loss!=fn_loss:
        raise ValueError("INVALID_HYPOTHETICAL_LOSS")
    if any(matrix[k]<0 for k in ("fp","fn","tp","tn")):
        raise ValueError("INVALID_CONFUSION_COUNTS")
    if matrix["tp"]+matrix["tn"]+matrix["fp"]+matrix["fn"]!=matrix["n"]:
        raise ValueError("MATRIX_DENOMINATOR_CHANGED")
    return round(matrix["fp"]*fp_loss+matrix["fn"]*fn_loss,6)

def fp_to_fn_break_even(candidate:dict, positive_baseline:dict)->float|None:
    """If baseline always positive, compute exactly WHEN it has higher unit loss.

    The ratio is a pure loss-utility thought experiment, not an estimate of
    transaction costs, trade profitability, or performance probability.
    """
    if (candidate["n"]!=positive_baseline["n"]
            or positive_baseline["fn"]!=0 or positive_baseline["tn"]!=0
            or positive_baseline["fp"]<=0):
        raise ValueError("UNMATCHED_ALWAYS_POSITIVE_BASELINE")
    if candidate["fp"]!=0:
        raise ValueError("CANDIDATE_FALSE_POSITIVE_REQUIRES_GENERALIZED_FORMULA")
    return round(candidate["fn"]/positive_baseline["fp"],6)

def latency_cohorts(rows:list[dict])->dict:
    cohorts={}
    for row in rows:
        name=row["strategy"]
        lag=int(row["extra_operational_delay_days_beyond_existing_1d_lag"])
        if lag not in (0,1,2,3):
            raise ValueError("INVALID_OPERATIONAL_LAG")
        group=cohorts.setdefault(name,{})
        if lag in group:raise ValueError("DUPLICATE_OPERATIONAL_SCENARIO")
        group[lag]={
            "total_return_pct_expost":float(row["total_return_pct"]),
            "max_drawdown_pct_expost":float(row["max_drawdown_pct"]),
            "exposure_pct":float(row["exposure_pct"]),
            "switches":int(row["switches"]),
        }
    if set(cohorts)!={"DEPLOYMENT_EXPANDING","JOINT_TRANSMISSION"}:
        raise ValueError("STRATEGY_ROSTER_CHANGED")
    for name,values in cohorts.items():
        if set(values)!={0,1,2,3}:
            raise ValueError("MISSING_OPERATIONAL_DELAY_SCENARIO")
        if len({v["switches"] for v in values.values()})!=1:
            raise ValueError("ORIGINAL_SWITCHES_CHANGED")
    return {name:{
        "historical_0_extra_delay_return_pct":vals[0]["total_return_pct_expost"],
        "historical_1_extra_delay_return_pct":vals[1]["total_return_pct_expost"],
        "extra_day_return_change_pp":round(vals[1]["total_return_pct_expost"]-vals[0]["total_return_pct_expost"],6),
        "historical_no_extra_delay_max_drawdown_pct":vals[0]["max_drawdown_pct_expost"],
        "historical_1_extra_day_max_drawdown_pct":vals[1]["max_drawdown_pct_expost"],
        "switches_existing_original_development":vals[0]["switches"],
        "additional_transaction_fees_and_slippage_modeled_here":False,
    } for name,vals in cohorts.items()}

def build(root:Path=ROOT)->dict:
    root=Path(root).resolve()
    data,provenance=prior.read_sources(root)
    old=prior.audit_e2(data,prior.utc(OLD_CUTOFF))
    new=prior.audit_e2(data,prior.utc(NEW_CUTOFF))
    early=preflight.build(root)
    if new["matured_7d_rows"]!=23 or old["matured_7d_rows"]!=20:
        raise ValueError("FROZEN_MATURITY_COHORT_DRIFT")
    if (new["matured_7d_positive"]!=21 or new["matured_7d_negative"]!=2
            or new["fixed_28d_block_n"]!=1):
        raise ValueError("ORIGINAL_BLOCK_OR_LABEL_DENOMINATOR_DRIFT")
    m1=read_csv(root,M1_PATH,M1_BLOB)
    false_alarms=[row for row in m1 if row["rule"]=="C2" and row["family"]=="C"]
    if len(false_alarms)!=1 or int(false_alarms[0]["unique_signal_dates"])!=14 or int(false_alarms[0]["unique_false_alarm_dates"])!=2:
        raise ValueError("M1_C2_FALSE_ALARM_OR_DENOMINATOR_DRIFT")
    lag=latency_cohorts(read_csv(root,LATENCY_PATH,LATENCY_BLOB))
    base_old=old["models"]["B0_ALWAYS_POSITIVE"]
    base=new["models"]["B0_ALWAYS_POSITIVE"]
    co=new["models"]["C02_BREADTH"]
    cn=new["models"]["C07_SIMPLE_3"]
    threshold_old=fp_to_fn_break_even(old["models"]["C02_BREADTH"],base_old)
    threshold_new=fp_to_fn_break_even(co,base)
    threshold_c07=fp_to_fn_break_even(cn,base)
    # Same fixed source labels, each under identical unit-loss assumptions.
    compare={
        name:{
            "original_confusion":{k:m[k] for k in ("n","tp","tn","fp","fn")},
            "unit_loss_if_fp_equals_fn":errors(m),
            "unit_loss_if_fp_5x_fn":errors(m,fp_loss=5),
            "unit_loss_if_fp_8x_fn":errors(m,fp_loss=8),
            "original_binary_classification_accuracy_pct":m["accuracy_pct"],
        }
        for name,m in (("C02_BREADTH",co),("C07_SIMPLE_3",cn),("B0_ALWAYS_POSITIVE",base))
    }
    if (compare["C02_BREADTH"]["original_confusion"]!={"n":23,"tp":7,"tn":2,"fp":0,"fn":14}
            or compare["C07_SIMPLE_3"]["original_confusion"]!={"n":23,"tp":0,"tn":2,"fp":0,"fn":21}
            or compare["B0_ALWAYS_POSITIVE"]["original_confusion"]!={"n":23,"tp":21,"tn":0,"fp":2,"fn":0}):
        raise ValueError("ORIGINAL_OBSERVED_CONFUSION_DRIFT")
    if (lag["DEPLOYMENT_EXPANDING"]["extra_day_return_change_pp"] >= 0
            or lag["JOINT_TRANSMISSION"]["extra_day_return_change_pp"] <= 0):
        raise ValueError("HISTORICAL_LATENCY_HETEROGENEITY_CHANGED")
    r1=early["first_issue_preflight"]
    receipts=early["original_outcome_receipts"]
    return {
        "contract":CONTRACT,"original_owner_issue":1596,
        "asof_utc":NEW_CUTOFF,
        "original_public_source_blob_ids":{
            "original_r1":preflight.FROZEN_BLOBS[preflight.SOURCE_PATH],
            "original_outcome_gate":preflight.FROZEN_BLOBS[preflight.GATE_PATH],
            "M1_original_timing_csv":M1_BLOB,"M4_original_latency_csv":LATENCY_BLOB,
            "shared_rows":provenance["shared_rows"]["git_blob_sha1"],
            "shared_outcomes":provenance["shared_outcomes"]["git_blob_sha1"],
        },
        "P3_action_eligibility":{
            "original_11_R1_issuances":r1["original_attempts"],
            "R1_original_user_deliveries_authenticated":r1["user_delivery_known_count"],
            "original_824_price_joined":receipts["retrospective_price_joined"],
            "original_814_outcome_receipts":receipts["original_matured"]+receipts["original_censored"],
            "original_censored":receipts["original_censored"],
            "original_missing_receipt":receipts["original_receipt_missing"],
            "M1_C2_original_signal_dates":int(false_alarms[0]["unique_signal_dates"]),
            "M1_C2_original_false_alarm_dates":int(false_alarms[0]["unique_false_alarm_dates"]),
            "M1_C2_population_false_positive_rate":None,
            "all_no_warning_opportunities_registered":False,
            "first_user_delivered_warning_clock_authenticated":False,
            "original_executable_sell_fill_authenticated":False,
            "matched_HOLD_after_cost_utility_scored":False,
            "state":"ACTION_CHAIN_BROKEN_NO_LIVE_ECONOMIC_CLAIM",
        },
        "P3_latency_strategies":{
            "historical_derived_scenarios":lag,
            "different_strategies_show_opposite_one_day_delay_effect":True,
            "tested_against_executable_after_cost_HOLD":False,
            "live_trading_or_market_rule_inferred":False,
        },
        "P4_eight_independent_questions":{
            "W3_L01_first_PIT_case":{
                "frozen_issued":r1["first_case_preselected_by_issue_clock_only"]["original_forecast_id"],
                "original_full_PIT_admitted":r1["full_original_R1_PIT_admitted"],
                "state":"BLOCKED_ORIGINAL_VENDOR_FIRST_KNOWN"
            },
            "W3_L02_direct_causal_sign":{
                "direct_prior_packet_delta_field_instances":r1["original_direction_delta_field_instances"],
                "index_context_not_direct_sign_instances":r1["original_non_direct_sign_evidence_index_instances"],
                "state":"ORIGINAL_CAUSAL_ROLE_FROZEN_NOT_EDGE"
            },
            "W3_L03_early_warning_absence":{
                "M1_C2_false_alarm_dates_over_signal_dates":[2,14],
                "negative_no_warning_universe_known":False,
                "state":"DESCRIPTIVE_EVENT_SIGNAL_DATES_NOT_FPR"
            },
            "W3_L04_shared_row_cost_sensitivity":{
                "source_matured_labels":new["matured_7d_rows"],
                "source_positive":new["matured_7d_positive"],
                "source_negative":new["matured_7d_negative"],
                "independent_market_shock_n":None,
                "fixed_28_day_calendar_blocks":new["fixed_28d_block_n"],
                "only_one_28d_block":True,
                "newly_matured_since_old_cutoff":new["matured_7d_rows"]-old["matured_7d_rows"],
                "C02_correct_old":[old["models"]["C02_BREADTH"]["tp"]+old["models"]["C02_BREADTH"]["tn"],old["matured_7d_rows"]],
                "C02_correct_new":[co["tp"]+co["tn"],new["matured_7d_rows"]],
                "C02_vs_always_positive_break_even_FP_to_FN_ratio_old":threshold_old,
                "C02_vs_always_positive_break_even_FP_to_FN_ratio_new":threshold_new,
                "C07_vs_always_positive_break_even_FP_to_FN_ratio_new":threshold_c07,
                "interpretation":"C02 has lower unit-loss only ABOVE ratio 7:1 new; labels are ETHBTC directional sign, not investable wealth",
                "candidate_loss_table":compare,
                "after_cost_profit_established":False,
                "state":"DESCRIPTIVE_HYPOTHETICAL_UNIT_LOSS_NO_PIT_EDGE",
            },
            "W3_L05_M1_latency":{"strategy_one_day_changes_pp":{k:v["extra_day_return_change_pp"] for k,v in lag.items()},
                                  "state":"EXPOSED_HISTORICAL_NONUNIVERSAL_LATENCY"},
            "W3_L06_breadth_ETF":{
                "prior_owner": "existing Task2 Wave2 / original breadth and ETF source adjudications",
                "after_price_breadth_predictive_gate":"NOT_SUPPORTED",
                "strong_ETF_flow_persistence_edge":"REJECTED",
                "state":"EXISTING_NEGATIVE_RESULTS_PRESERVED_NOT_RERUN"
            },
            "W3_L07_derivatives_cfgi":{
                "prior_owner":"existing Ironflow 18m / original CFGI chronology",
                "incremental_after_price_replication":"NOT_ESTABLISHED",
                "original_provider_first_known":"UNVERIFIED",
                "state":"EXISTING_NULL_RESULTS_PRESERVED_NOT_RERUN"
            },
            "W3_L08_delivery_to_HOLD":{
                "original_11_deliveries_authenticated":r1["user_delivery_known_count"],
                "after_cost_HOLD_with_real_fills_possible":False,
                "state":"BLOCKED_SOURCE_DELIVERY_AND_FILL"
            }
        },
        "research_only":True,"round3_private_values_used":False,
        "forecast_reissued":False,"retrospective_signal_fabricated":False,
        "model_promotion_authorized":False,"portfolio_execution_authorized":False,
        "no_new_automation":True,"no_new_paid_api":True,
        "scientific_verdict":"NO_NEW_PROVEN_INCREMENTAL_OR_AFTER_COST_EDGE",
        "next_original_owner":"Gather immutable first delivered+source vintage, prospective independent shocks, complete eligible HOLD/no-warning set, fee/slippage/fill policy before investor utility."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    report=build()
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps({
        "contract":CONTRACT,
        "P3_deliveries_verified":report["P3_action_eligibility"]["R1_original_user_deliveries_authenticated"],
        "C02_FP_to_FN_break_even":report["P4_eight_independent_questions"]["W3_L04_shared_row_cost_sensitivity"]["C02_vs_always_positive_break_even_FP_to_FN_ratio_new"],
        "eight_lane_count":len(report["P4_eight_independent_questions"]),
        "scientific_verdict":report["scientific_verdict"]
    },sort_keys=True))

if __name__=="__main__":
    main()
