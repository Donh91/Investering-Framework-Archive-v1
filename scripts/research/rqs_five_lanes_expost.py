#!/usr/bin/env python3
"""Five Kompas research lanes, EX-POST only. NO forecast, scoring or trading.

Only public primitive historical hourly bars. Weekly archives often postdate the
original candle and are NEVER accepted as original-first-known source evidence.
No collector, scheduler, online requests, persistent episodes or state mutation.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

HOUR = timedelta(hours=1)
RECOVERY_DD_PCT = -1.5     # inherited research-only prototype; NOT optimized
RECOVERY_3H_PCT = 0.75
PREWARN_4H_PCT = -1.0      # illustrative baseline, NOT an official risk score
FUTURE_FALL_24H_PCT = -3.0
HIGH_VOL_24H_RANGE_PCT = 3.0
EVENT_GAP_HOURS = 12       # sensitivity example, NOT independent market proof
HORIZONS = (6, 24, 72)
ROUND_TRIP_COST_PCT = (0.2, 0.6)


def parse_utc(value: str) -> datetime:
    v = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if v.utcoffset() != timedelta(0):
        raise ValueError("NON_UTC_TIMESTAMP")
    return v.astimezone(timezone.utc)


def numeric(r: dict[str, str], col: str) -> float | None:
    try:
        value = float(r[col])
    except (ValueError, TypeError, KeyError):
        return None
    return value if math.isfinite(value) else None


def ratio_pct(p0: float, p1: float) -> float:
    return (p1 / p0 - 1.0) * 100


def verified_primitive_rows(rows: list[dict[str, str]], asof_utc: str) -> tuple[dict[datetime, dict[str, str]], dict[str, Any]]:
    """A valid ex-post candle is NOT evidence of a legally issued prediction."""
    asof = parse_utc(asof_utc)
    seen: dict[datetime, dict[str, str]] = {}
    delayed = 0
    source_candles = 0
    for row in rows:
        opened = parse_utc(row["timestamp_utc"])
        if any((opened.minute, opened.second, opened.microsecond)):
            raise ValueError("CANDLE_OPEN_NOT_UTC_HOUR_ALIGNED")
        close = opened + HOUR
        if close > asof:
            continue
        coverage = parse_utc(row["source_window_end_utc"])
        if coverage < close:
            raise ValueError("RUN_COVERAGE_BEFORE_CANDLE_CLOSE")
        if close in seen:
            if seen[close] != row:
                raise ValueError("CONFLICTING_DUPLICATE_CANDLE")
            continue
        seen[close] = row
        source_candles += 1
        if coverage - close > HOUR:
            delayed += 1
    return seen, {
        "input_unique_candles": source_candles,
        "run_coverage_over_1h_after_candle_count": delayed,
        "source_first_known_verified": False,
        "source_clock_warning": "Run coverage can lag source candle by days; NOT original first-known.",
    }


def mean_rates(items: list[dict[str, Any]], horizon: int, key: str = "future_returns") -> dict[str, Any]:
    values = [r[key][horizon] for r in items if r[key][horizon] is not None]
    return {
        "mature_n": len(values),
        "positive_n": sum(x > 0 for x in values),
        "mean_pct": round(statistics.mean(values), 4) if values else None,
        "median_pct": round(statistics.median(values), 4) if values else None,
    }


def analyze(rows: list[dict[str, str]], asof_utc: str) -> dict[str, Any]:
    """Pure retrospective research. All labels use past/future separation."""
    asof = parse_utc(asof_utc)
    bars, provenance = verified_primitive_rows(rows, asof_utc)
    clocks = sorted(bars)
    all_rows = []
    if clocks:
        for idx in range(23, len(clocks)):
            t = clocks[idx]
            hist = clocks[idx-23:idx+1]
            if any(b-a != HOUR for a,b in zip(hist, hist[1:])):
                continue
            w = [bars[u] for u in hist]
            prices = [numeric(x, "btc_close") for x in w]
            if any(x is None or x <= 0 for x in prices) or any(x.get("spot_status") != "PASS" for x in w):
                continue
            now = prices[-1]
            pre = prices[-16:-3]  # 13 completed closes before final three
            peak, dd = pre[0], 0.0
            for price in pre:
                peak = max(peak, price)
                dd = min(dd, ratio_pct(peak, price))
            ret3 = ratio_pct(prices[-4], now)
            ret4 = ratio_pct(prices[-5], now)
            recovery = dd <= RECOVERY_DD_PCT and ret3 >= RECOVERY_3H_PCT
            prev24 = prices[:]
            regime_range = 100.0 * (max(prev24) / min(prev24) - 1.0)
            regime = "HIGH_PRE24H_RANGE" if regime_range >= HIGH_VOL_24H_RANGE_PCT else "LOW_PRE24H_RANGE"
            e0, e1 = numeric(w[-4], "ethbtc_close"), numeric(w[-1], "ethbtc_close")
            eth_relative = ratio_pct(e0, e1) if e0 is not None and e1 is not None and min(e0,e1) > 0 else None
            spot_3 = w[-3:]
            bought = [numeric(x, "btc_taker_buy_quote_volume") for x in spot_3]
            volume = [numeric(x, "btc_quote_volume") for x in spot_3]
            buyshare = None
            if all(x is not None and x >= 0 for x in bought) and all(x is not None and x > 0 for x in volume) and all(x <= y for x,y in zip(bought, volume)):
                buyshare = sum(bought) / sum(volume)
            o0, o1 = numeric(w[-4], "btc_open_interest"), numeric(w[-1], "btc_open_interest")
            oi_change = (ratio_pct(o0,o1) if min(o0 or 0,o1 or 0) > 0 and all(x.get("derivatives_status")=="PASS" for x in w[-4:]) else None)
            fut: dict[int, float | None] = {}
            min24: float | None = None
            for h in HORIZONS:
                future = [bars.get(t + i*HOUR) for i in range(1,h+1)]
                if t+h*HOUR>asof or any(x is None or x.get("spot_status")!="PASS" or not (numeric(x,"btc_close") or 0)>0 for x in future):
                    fut[h] = None
                else:
                    closes = [numeric(x,"btc_close") for x in future]
                    fut[h] = ratio_pct(now, closes[-1])
                    if h==24:
                        min24 = min(closes)
            # Label is deliberately FUTURE-only; never used to define predictor features.
            drop24 = (100*(min24/now-1) if min24 is not None else None)
            # Retest of pre-event trough requires the entire 24-hour future to mature.
            retest24 = (min24 <= min(pre) if min24 is not None else None)
            all_rows.append({
                "end":t, "dd":dd, "recovery": recovery, "ret3":ret3, "ret4":ret4,
                "regime":regime, "eth_relative":eth_relative, "spot_buy_share":buyshare,
                "oi_change":oi_change, "future_returns":fut, "drop24":drop24,
                "retest24":retest24,
                "prewarn":ret4 <= PREWARN_4H_PCT,
            })
    recoveries=[r for r in all_rows if r["recovery"]]
    grouped=[]
    for item in recoveries:
        if not grouped or item["end"]-grouped[-1][-1]["end"]>EVENT_GAP_HOURS*HOUR:
            grouped.append([item])
        else:
            grouped[-1].append(item)
    episodes=[g[0] for g in grouped]
    mature24=[r for r in episodes if r["future_returns"][24] is not None]
    warned=[r for r in all_rows if r["drop24"] is not None and r["prewarn"]]
    risk=[r for r in all_rows if r["drop24"] is not None]
    future_crashes=[r for r in risk if r["drop24"] <= FUTURE_FALL_24H_PCT]

    def split_return(group: list[dict[str, Any]]) -> dict[str, Any]:
        return {"raw_n":len(group),"24h":mean_rates(group,24)}
    regime_split = {k:split_return([r for r in episodes if r["regime"]==k])
                    for k in ("LOW_PRE24H_RANGE","HIGH_PRE24H_RANGE")}
    monthly = {}
    for r in episodes:
        m=r["end"].strftime("%Y-%m")
        monthly.setdefault(m,[]).append(r)
    monthly = {m: split_return(group) for m,group in sorted(monthly.items())}
    relative = {"ETHBTC_UP_3H":split_return([r for r in episodes if r["eth_relative"] is not None and r["eth_relative"]>0]),
                "ETHBTC_NONPOSITIVE_3H":split_return([r for r in episodes if r["eth_relative"] is not None and r["eth_relative"]<=0]),
                "ETHBTC_MISSING":len([r for r in episodes if r["eth_relative"] is None])}
    spot = {"TAKER_BUY_SHARE_GT_50PCT":split_return([r for r in episodes if r["spot_buy_share"] is not None and r["spot_buy_share"]>.5]),
            "TAKER_BUY_SHARE_LE_50PCT":split_return([r for r in episodes if r["spot_buy_share"] is not None and r["spot_buy_share"]<=.5])}
    oi = {"OI_FALLING":split_return([r for r in episodes if r["oi_change"] is not None and r["oi_change"]<0]),
          "OI_NONFALLING":split_return([r for r in episodes if r["oi_change"] is not None and r["oi_change"]>=0])}
    # WAIT is an observational no-entry comparison only; no portfolio PnL.
    net = {}
    for cost in ROUND_TRIP_COST_PCT:
        values=[r["future_returns"][24]-cost for r in mature24]
        net[str(cost)]={
            "mature_n":len(values),
            "hypothetical_net_24h_mean_pct":round(statistics.mean(values),4) if values else None,
            "hypothetical_net_24h_positive_n":sum(x>0 for x in values),
        }
    return {
        "contract":"KOMPAS_5_LANE_EXPOST_RESEARCH_v1",
        "mode":"EX_POST_DESCRIPTIVE_ONLY",
        "asof_utc":asof.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source":provenance,
        "source_complete_24h_features":len(all_rows),
        "source_first_known_verified":False,
        "official_forecast_or_trade_signal":False,
        "automatic_episode_creation":False,
        "calibrated_edge":None,
        "trade_permission":"NONE",
        "five_lanes":{
            "rebound_failure_detector":{
                "raw_candidate_hours":len(recoveries),"illustrative_12h_event_groups":len(episodes),
                "mature_24h_event_groups":len(mature24),
                "24h_nonpositive_close_events":sum(r["future_returns"][24]<=0 for r in mature24),
                "24h_pre_event_trough_retests":sum(r["retest24"] is True for r in mature24),
                "24h_outcomes":mean_rates(episodes,24),
                "72h_outcomes":mean_rates(episodes,72),
            },
            "early_pullback_warning":{
                "warning_rule":"past_4h_btc_return <= -1pct; HISTORICAL CONTROL ONLY",
                "future_target":"lowest_future_24h_close_from_current <= -3pct",
                "mature_24h_decision_clocks":len(risk),
                "future_fall_decision_clocks":len(future_crashes),
                "warning_clocks":len(warned),
                "true_positive_overlapping_clocks":sum(r["drop24"]<=FUTURE_FALL_24H_PCT for r in warned),
                "false_positive_overlapping_clocks":sum(r["drop24"]>FUTURE_FALL_24H_PCT for r in warned),
                "missed_fall_overlapping_clocks":sum(not r["prewarn"] for r in future_crashes),
                "official_3of5_lead_time_comparison":"UNAVAILABLE_NO_FROZEN_AS_ISSUED_WARNING_CLOCKS",
            },
            "regime_conditional_recovery":{
                "research_only_past_24h_range_threshold_pct":HIGH_VOL_24H_RANGE_PCT,
                "by_pre_event_range":regime_split,"monthly":monthly,
                "statistical_independence":"UNVERIFIED_OVERLAPPING_CLUSTERS",
            },
            "capital_rotation_and_breadth":{
                "ethbtc_3h_groups":relative,"spot_quote_flow_groups":spot,
                "oi_groups":oi,
                "independent_same_clock_altcoin_breadth":"UNAVAILABLE",
                "lineage_note":"ETH/BTC and taker flow same spot-family; OI side not causal.",
            },
            "decision_utility_learning":{
                "matched_all_complete_hour_baseline_24h":mean_rates(all_rows,24),
                "raw_rebound_cursors_24h":mean_rates(recoveries,24),
                "one_per_12h_group_24h":mean_rates(episodes,24),
                "wait_24h_hypothetical_return_pct":0.0,
                "round_trip_cost_sensitivity":net,
                "realized_pnl_or_action_edge":None,
                "note":"Hypothetical gross price path - costs, NOT original PIT, fees or execution proof.",
            },
        },
        "scientific_gates":{
            "research_data_history_only":True,
            "first_known_verified":False,
            "pre_registered_event_cluster":False,
            "purged_72h_out_of_sample_test":False,
            "matched_regime_independent_baseline":False,
            "adaptive_pullback_owner":"SUSPENDED_NO_ELIGIBILITY_CONTRACT",
            "automatic_forecast_or_market_action":"BLOCKED",
        },
        "warnings":[
            "No real-time issuance or historical edge claim allowed",
            "Overlapping 24/72h outcomes and 12h arbitrary grouping",
            "Future response labels calculated ONLY after cutoff but ex-post rows may have later source collection",
            "No independent breadth or verified official prior risk timestamps",
            "Source-weekly archives were reaggregated after many candle closes",
        ],
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv",action="append",type=Path,required=True)
    parser.add_argument("--asof",required=True)
    args=parser.parse_args()
    allowed=(Path("03_DAILY_CAPTURE_LOGS/hourly").resolve(),
             Path("03_DAILY_CAPTURE_LOGS/weekly").resolve())
    rows=[]
    for p in args.csv:
        target=p.resolve()
        if not target.suffix==".csv" or not any(target.is_relative_to(root) for root in allowed):
            raise ValueError("OUTSIDE_PUBLIC_HOURLY_RESEARCH_ROOT")
        with target.open("r",newline="",encoding="utf-8") as f:
            rows.extend(csv.DictReader(f))
    print(json.dumps(analyze(rows,args.asof),sort_keys=True,indent=2))


if __name__=="__main__":
    main()
