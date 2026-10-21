#!/usr/bin/env python3
"""Task2: 71 nonoverlapping 14d windows, NOT thousands of independent trials.

Evaluate the same already frozen 144 price-only parameter configurations at
each cost and aggregate FIRST BY WINDOW. Research-only, synthetic survivor index,
no sample splitting, no original forecast, no CFGI, no edge, no trade.
"""
from __future__ import annotations
import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

from scripts.research import task2_archive_price_only_stress_v1 as original
from scripts.research import task2_matched_windows_v1 as matched

CONTRACT="TASK2_14D_WINDOW_UNIT_ROBUSTNESS_v1"
AUTHORITY={"research_only":True,"original_forecasts_scored":False,
           "cfgi_tested":False,"out_of_sample":False,"portfolio_action":False}
CONFIRMED_SHOCK_FAMILIES=0

def window_aggregates(windows, configs):
    if len(configs)!=576 or len(set(configs))!=576:
        raise ValueError("FROZEN_576_CONFIGS_REQUIRED")
    out=[]
    for w in windows:
        tape=w["tape"]
        triggers={(lb,threshold): matched.first_price_trigger(tape,lb,threshold)
                  for threshold in original.THRESHOLDS for lb in original.LOOKBACK_H}
        costs=defaultdict(list)
        trades=defaultdict(int)
        for threshold,lb,trim,reentry,cost in configs:
            x=matched.evaluate_window(tape,triggers[(lb,threshold)],trim,reentry,cost)
            costs[cost].append(x["delta_vs_hold_pct_initial"])
            if x["sale_attempted"]:
                trades[cost]+=1
        if len(costs)!=4 or any(len(v)!=144 for v in costs.values()):
            raise ValueError("WINDOW_MISSING_ONE_OF_144_CONFIGS_PER_COST")
        vals={}
        for cost in original.COSTS:
            ds=costs[cost]
            avg=sum(ds)/144
            vals[f"{cost:.3f}"]={
                "candidate_settings":144,
                "settings_with_sale":trades[cost],
                "settings_without_sale":144-trades[cost],
                "mean_delta_pct_initial":round(avg,9),
                "positive_settings":sum(v>1e-9 for v in ds),
                "negative_settings":sum(v< -1e-9 for v in ds),
                "ties":sum(abs(v)<=1e-9 for v in ds)}
            if vals[f"{cost:.3f}"]["positive_settings"]+vals[f"{cost:.3f}"]["negative_settings"]+vals[f"{cost:.3f}"]["ties"]!=144:
                raise ValueError("WINDOW_SIGN_DENOMINATOR_MISMATCH")
        out.append({"era":w["era"],"segment_id":w["source_segment"],
                    "window_start_utc":w["score_start_utc"],
                    "window_end_utc":w["score_end_utc"],
                    "cost_arms":vals})
    return out

def aggregate_window_units(window_rows):
    if not window_rows:
        raise ValueError("NO_WINDOW_COHORT")
    by_cost={}
    for cost in original.COSTS:
        k=f"{cost:.3f}"
        values=[row["cost_arms"][k]["mean_delta_pct_initial"] for row in window_rows]
        n=len(values)
        avg=sum(values)/n
        leave_one_out=[(sum(values)-v)/(n-1) for v in values] if n>1 else []
        sale_periods=sum(row["cost_arms"][k]["settings_with_sale"]>0 for row in window_rows)
        by_cost[k]={
            "window_unit_count":n,
            "nominal_correlated_setting_window_cells":n*144,
            "windows_with_any_sale":sale_periods,
            "windows_no_sale_under_all_144_settings":n-sale_periods,
            "mean_window_delta_pct_initial":round(avg,8),
            "median_window_delta_pct_initial":round(statistics.median(values),8),
            "windows_mean_positive":sum(v>1e-9 for v in values),
            "windows_mean_negative":sum(v< -1e-9 for v in values),
            "windows_mean_tied":sum(abs(v)<=1e-9 for v in values),
            "min_window_mean_delta_pct_initial":round(min(values),8),
            "max_window_mean_delta_pct_initial":round(max(values),8),
            "leave_one_window_out_positive_means":sum(v>1e-9 for v in leave_one_out),
            "leave_one_window_out_negative_means":sum(v< -1e-9 for v in leave_one_out),
            "leave_one_window_out_total":len(leave_one_out),
            "scientific_independence_claim":False
        }
        if (by_cost[k]["windows_mean_positive"]+by_cost[k]["windows_mean_negative"]+
            by_cost[k]["windows_mean_tied"]!=n):
            raise ValueError("NONRECONCILING_WINDOW_SIGNS")
    return by_cost

def execute(archive=None):
    if archive is None:archive=original.ART
    originals=original.preflight(archive)
    bars=original.locked_read(archive/original.PRICE.name,original.PRICE_BLOB)
    ws=matched.windows_from_segments(original.load_price_segments(bars))
    if len(ws)!=71 or sum(w["era"]==matched.ERA_NAMES[0] for w in ws)!=30 or sum(w["era"]==matched.ERA_NAMES[1] for w in ws)!=41:
        raise ValueError("ORIGINAL_30_41_WINDOW_CENSUS_CHANGED")
    rows=window_aggregates(ws,original.fixture_grid())
    out={}
    for era in matched.ERA_NAMES:
        these=[w for w in rows if w["era"]==era]
        out[era]={"windows":len(these),"by_cost":aggregate_window_units(these)}
    for era in matched.ERA_NAMES:
        d=out[era]["by_cost"]
        for a,b in zip(original.COSTS,original.COSTS[1:]):
            if d[f"{a:.3f}"]["mean_window_delta_pct_initial"]+1e-7<d[f"{b:.3f}"]["mean_window_delta_pct_initial"]:
                raise ValueError("COST_DID_NOT_REDUCE_WINDOW_AVERAGE")
    return {"contract":CONTRACT,"authority":AUTHORITY,"classification":"EX_POST_14D_WINDOW_UNIT_SENSITIVITY_NOT_EDGE",
            "source_git_blob_sha1":original.PRICE_BLOB,"source_preflight":originals,
            "window_unit_count":71,"original_frozen_scenario_variants_per_cost":144,
            "by_era":out,"window_unit_rows":rows,
            "known_independent_shock_family_count":CONFIRMED_SHOCK_FAMILIES,
            "hypothesis_freeze_before_outcomes":False,
            "model_parameter_winner_selected":False,"p_value":None,
            "confidence_interval":None,"market_values_not_reproduced":True,
            "original_compass_or_cfgi_tested":False,
            "note":"One unit per nonoverlapping 14-day window, not 144 independent trades; common era exposure remains dependent and original results ex post."}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path);args=ap.parse_args()
    d=execute()
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print(json.dumps({e:d["by_era"][e] for e in matched.ERA_NAMES},sort_keys=True))
if __name__=="__main__":main()
