#!/usr/bin/env python3
"""Bounded adversarial tests for ex-post research, not trading signals."""
from __future__ import annotations
import unittest
import csv
from pathlib import Path
from datetime import datetime, timedelta, timezone

from scripts.research.rqs_five_lanes_expost import analyze, verified_primitive_rows


def fixture():
    start = datetime(2026,10,1,tzinfo=timezone.utc)
    prices=[]
    for i in range(132):
        if i < 30:
            value=100.0
        elif i < 36:
            value=100.0 - (i-29)*0.75
        elif i < 40:
            value=95.5 + (i-35)*0.55
        elif i < 66:
            value=97.7
        elif i < 72:
            value=97.7 - (i-65)*0.7
        else:
            value=93.5
        prices.append(value)
    rows=[]
    for i,p in enumerate(prices):
        begin=start+timedelta(hours=i)
        row={
            "timestamp_utc":begin.isoformat().replace("+00:00","Z"),
            "source_window_end_utc":(begin+timedelta(hours=1)).isoformat().replace("+00:00","Z"),
            "btc_close":str(p), "btc_quote_volume":"1000",
            "btc_taker_buy_quote_volume":"550",
            "ethbtc_close":str(.030 + i*.000002),
            "btc_open_interest":str(1000-i*.3),
            "spot_status":"PASS","derivatives_status":"PASS",
        }
        rows.append(row)
    return rows


ASOF="2026-10-06T12:00:00Z"


class FiveResearchLanes(unittest.TestCase):
    def test_real_83_day_source_archive_expost_only(self):
        files=[Path(f"03_DAILY_CAPTURE_LOGS/weekly/2026/W{w:02d}/WEEKLY_HOURLY_ENRICHED.csv")
               for w in range(32,44)]
        files += [Path(f"03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-{d:02d}.csv")
                  for d in range(26,31)]
        rows=[]
        for path in files:
            with path.open(newline="", encoding="utf-8") as handle:
                rows.extend(csv.DictReader(handle))
        result=analyze(rows, "2026-10-30T21:00:00Z")
        self.assertEqual(result["source"]["input_unique_candles"],2005)
        self.assertGreater(result["source"]["run_coverage_over_1h_after_candle_count"],1000)
        self.assertGreater(result["source_complete_24h_features"],1900)
        self.assertGreater(result["five_lanes"]["rebound_failure_detector"]["raw_candidate_hours"],20)
        self.assertFalse(result["source_first_known_verified"])
        self.assertEqual(result["trade_permission"],"NONE")
        self.assertEqual(result["five_lanes"]["capital_rotation_and_breadth"]["independent_same_clock_altcoin_breadth"],"UNAVAILABLE")
        self.assertIsNone(result["five_lanes"]["decision_utility_learning"]["realized_pnl_or_action_edge"])

    def test_all_five_research_lanes_are_non_authoritative(self):
        out=analyze(fixture(),ASOF)
        self.assertEqual(set(out["five_lanes"]),{
            "rebound_failure_detector","early_pullback_warning",
            "regime_conditional_recovery","capital_rotation_and_breadth",
            "decision_utility_learning",
        })
        self.assertEqual(out["trade_permission"],"NONE")
        self.assertFalse(out["official_forecast_or_trade_signal"])
        self.assertFalse(out["source_first_known_verified"])
        self.assertFalse(out["automatic_episode_creation"])
        self.assertIsNone(out["calibrated_edge"])

    def test_rebound_failure_has_mature_future_24h_and_72h(self):
        out=analyze(fixture(),ASOF)["five_lanes"]["rebound_failure_detector"]
        self.assertGreater(out["raw_candidate_hours"],0)
        self.assertGreater(out["illustrative_12h_event_groups"],0)
        self.assertGreater(out["24h_outcomes"]["mature_n"],0)
        self.assertGreaterEqual(out["24h_nonpositive_close_events"],0)
        self.assertGreaterEqual(out["24h_pre_event_trough_retests"],0)

    def test_early_warning_is_only_historical_and_cannot_approve_risk(self):
        out=analyze(fixture(),ASOF)
        e=out["five_lanes"]["early_pullback_warning"]
        self.assertGreater(e["mature_24h_decision_clocks"],0)
        self.assertGreater(e["warning_clocks"],0)
        self.assertGreater(e["future_fall_decision_clocks"],0)
        self.assertEqual(e["official_3of5_lead_time_comparison"],
                         "UNAVAILABLE_NO_FROZEN_AS_ISSUED_WARNING_CLOCKS")
        self.assertEqual(out["scientific_gates"]["automatic_forecast_or_market_action"],"BLOCKED")

    def test_regime_uses_only_past_24h_and_is_not_calibrated(self):
        out=analyze(fixture(),ASOF)
        r=out["five_lanes"]["regime_conditional_recovery"]
        self.assertEqual(r["research_only_past_24h_range_threshold_pct"],3.0)
        self.assertIn("HIGH_PRE24H_RANGE",r["by_pre_event_range"])
        self.assertEqual(r["statistical_independence"],"UNVERIFIED_OVERLAPPING_CLUSTERS")

    def test_breadth_missing_does_not_become_spot_or_oi(self):
        r=analyze(fixture(),ASOF)["five_lanes"]["capital_rotation_and_breadth"]
        self.assertEqual(r["independent_same_clock_altcoin_breadth"],"UNAVAILABLE")
        self.assertIn("OI_FALLING",r["oi_groups"])
        self.assertIn("ETHBTC_UP_3H",r["ethbtc_3h_groups"])

    def test_net_cost_reduces_hypothetical_gross_value(self):
        result=analyze(fixture(),ASOF)["five_lanes"]["decision_utility_learning"]
        gross=result["one_per_12h_group_24h"]["mean_pct"]
        small=result["round_trip_cost_sensitivity"]["0.2"]["hypothetical_net_24h_mean_pct"]
        big=result["round_trip_cost_sensitivity"]["0.6"]["hypothetical_net_24h_mean_pct"]
        self.assertAlmostEqual(gross-small,0.2,delta=0.0002)
        self.assertAlmostEqual(small-big,0.4,delta=0.0002)
        self.assertIsNone(result["realized_pnl_or_action_edge"])

    def test_reaggregated_weekly_coverage_is_not_pit(self):
        rows=fixture()
        rows[3]["source_window_end_utc"]="2026-10-05T18:00:00Z"
        _,p=verified_primitive_rows(rows,ASOF)
        self.assertGreaterEqual(p["run_coverage_over_1h_after_candle_count"],1)
        self.assertFalse(p["source_first_known_verified"])

    def test_half_hour_source_rejected(self):
        rows=fixture()
        rows[4]["timestamp_utc"]="2026-10-01T04:30:00Z"
        with self.assertRaisesRegex(ValueError,"CANDLE_OPEN_NOT_UTC_HOUR_ALIGNED"):
            analyze(rows,ASOF)

    def test_conflicting_duplicate_rejected(self):
        rows=fixture()
        row=dict(rows[2]);row["btc_close"]="111"
        with self.assertRaisesRegex(ValueError,"CONFLICTING_DUPLICATE_CANDLE"):
            analyze(rows+[row],ASOF)

    def test_missing_source_cannot_create_new_decision_window(self):
        rows=fixture()
        full=analyze(rows,ASOF)
        subset=analyze([r for r in rows if r["timestamp_utc"]!="2026-10-02T17:00:00Z"],ASOF)
        self.assertLess(subset["source_complete_24h_features"],full["source_complete_24h_features"])

    def test_past_cutoff_excludes_future_candles_and_labels(self):
        rows=fixture()
        stop="2026-10-02T00:00:00Z"
        out=analyze(rows,stop)
        self.assertEqual(out["source"]["input_unique_candles"],24)
        self.assertTrue(out["five_lanes"]["decision_utility_learning"]["one_per_12h_group_24h"]["mature_n"]==0)
        self.assertEqual(out["trade_permission"],"NONE")


if __name__=="__main__":
    unittest.main()
