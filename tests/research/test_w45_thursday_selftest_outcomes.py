"""Adversarial, no-hindsight controls for immutable Thursday W45 self-test."""
import copy
import csv
import json
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from scripts.research.verify_w45_midweek_shadow_benchmark import parse_utc
from scripts.research.w45_thursday_selftest_outcomes import (
    PACKET, HOURLY, ISSUE, FIRST_FUTURE_HOUR, CONTRACT, ANCHOR,
    compile_outcomes, verify_freeze,
)

ROOT = Path(__file__).resolve().parents[2]
FROZEN = json.loads((ROOT / PACKET).read_text(encoding="utf-8"))
HEADER = ["timestamp_utc", "source_window_end_utc", "spot_status",
          "btc_open", "btc_high", "btc_low", "btc_close",
          "eth_open", "eth_high", "eth_low", "eth_close"]


def utc(dt):
    return dt.isoformat().replace("+00:00", "Z")


def candle(opened, btc=75500.0, eth=2240.0, *, btc_width=0.001,
           eth_width=0.001):
    end = opened + timedelta(hours=1)
    return {
        "timestamp_utc": utc(opened), "source_window_end_utc": utc(end),
        "spot_status": "PASS",
        "btc_open": btc, "btc_high": btc * (1 + btc_width),
        "btc_low": btc * (1 - btc_width), "btc_close": btc,
        "eth_open": eth, "eth_high": eth * (1 + eth_width),
        "eth_low": eth * (1 - eth_width), "eth_close": eth,
    }


def seed(include_thursday=False, include_friday=False):
    by_day = {
        "2026-11-04": [candle(parse_utc("2026-11-04T17:00:00Z"),
                              btc=ANCHOR["BTC"][1], eth=ANCHOR["ETH"][1])],
        "2026-11-05": [candle(parse_utc("2026-11-05T17:00:00Z"),
                              btc=ANCHOR["BTC"][0], eth=ANCHOR["ETH"][0])],
    }
    if include_thursday:
        for hour in (21, 22, 23):
            by_day["2026-11-05"].append(
                candle(parse_utc(f"2026-11-05T{hour:02d}:00:00Z"),
                       btc=75100 + hour, eth=2220 + hour))
    if include_friday:
        by_day["2026-11-06"] = [
            candle(parse_utc(f"2026-11-06T{hour:02d}:00:00Z"),
                   btc=74300 + hour, eth=2210 + hour)
            for hour in range(24)
        ]
    return by_day


def write_source(root, grouped):
    for day, rows in grouped.items():
        year, month, _ = day.split("-")
        file = root / HOURLY / year / month / (day + ".csv")
        file.parent.mkdir(parents=True, exist_ok=True)
        with file.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=HEADER)
            writer.writeheader()
            writer.writerows(rows)


class ThursdaySelfTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def evaluate(self, now, packet=None):
        return compile_outcomes(copy.deepcopy(packet or FROZEN), self.root,
                                parse_utc(now))

    def test_freeze_exact_original_comment_and_8_futures_not_monday(self):
        verify_freeze(FROZEN)
        self.assertEqual(FROZEN["first_public_issue_utc"], "2026-11-05T20:11:38Z")
        self.assertEqual(FROZEN["original_comment_id"], 6668153478)
        self.assertEqual(FROZEN["original_monday_W45_daily_issued"],
                         {"BTC": 0, "ETH": 0})
        self.assertGreater(FIRST_FUTURE_HOUR, ISSUE)
        self.assertEqual([len(FROZEN["assets"][a]["forecasts"])
                          for a in ("BTC", "ETH")], [4, 4])

    def test_tampered_forecast_metadata_price_or_research_authority_rejected(self):
        changes = [
            lambda p: p["assets"]["BTC"]["forecasts"][0].update(B1_conditional_close=76573.64),
            lambda p: p["assets"]["ETH"]["forecasts"][3].update(low=1),
            lambda p: p.update(first_public_issue_utc="2026-11-05T18:00:00Z"),
            lambda p: p.update(first_wholly_prospective_hour_open_utc="2026-11-05T18:00:00Z"),
            lambda p: p.update(official_scoring_eligible=True),
            lambda p: p["assets"]["BTC"].update(quote="USD"),
            lambda p: p["input_source_git_blobs"].update({"2026-11-05": "f" * 40}),
            lambda p: p["original_monday_W45_daily_issued"].update(BTC=7),
        ]
        for change in changes:
            packet = copy.deepcopy(FROZEN)
            change(packet)
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    verify_freeze(packet)

    def test_before_actual_github_issue_no_maturity_or_range_score(self):
        write_source(self.root, seed(include_thursday=True, include_friday=True))
        receipt = self.evaluate("2026-11-05T20:00:00Z")
        self.assertEqual(receipt["source_state"], "ISSUE_NOT_YET_PUBLIC")
        self.assertEqual(receipt["matured_observations"], 0)
        self.assertTrue(all(row["observed_close_USDT"] is None
                            for row in receipt["rows"]))

    def test_thursday_partial_only_3_full_post_issue_hours_never_6hour_hit(self):
        fixture = seed(include_thursday=True)
        # A huge preissue bar from 18-19Z must not contaminate the 21Z+ range.
        fixture["2026-11-05"].append(candle(
            parse_utc("2026-11-05T18:00:00Z"), btc=88000, eth=2800))
        write_source(self.root, fixture)
        receipt = self.evaluate("2026-11-06T00:08:00Z")
        self.assertEqual(receipt["contract"], CONTRACT)
        self.assertEqual(receipt["matured_observations"], 2)
        self.assertEqual(receipt["full_daily_range_scored"], 0)
        self.assertEqual(receipt["original_monday_daily_issued"], {"BTC": 0, "ETH": 0})
        for row in (receipt["rows"][0], receipt["rows"][4]):
            self.assertEqual(row["source_hours_required"], 3)
            self.assertEqual(row["source_hours_complete"], 3)
            self.assertEqual(row["range_state"],
                             "PARTIAL_THURSDAY_SIX_HOUR_COVERAGE_UNSCORABLE")
            self.assertEqual(row["outcome_state"], "MATURED_PUBLIC_HOURLY_CAPTURE")
            self.assertIsNotNone(row["B1_absolute_pct_error"])
            self.assertIsNotNone(row["B0_absolute_pct_error"])
            self.assertIsNotNone(row["observed_close_USDT"])
        self.assertLess(receipt["rows"][0]["observed_post_issue_high_USDT"], 77000)
        self.assertTrue(all(r["outcome_state"] == "PENDING_UTC_TARGET"
                            for i, r in enumerate(receipt["rows"]) if i not in (0, 4)))
        for key in ("provider_first_known_verified", "scientific_edge_proven",
                    "official_scoring_eligible", "portfolio_action_authority"):
            self.assertIs(receipt[key], False)

    def test_friday_complete_24hours_is_scored_without_rewriting_thursday(self):
        write_source(self.root, seed(include_thursday=True, include_friday=True))
        receipt = self.evaluate("2026-11-07T00:08:00Z")
        self.assertEqual(receipt["matured_observations"], 4)
        self.assertEqual(receipt["full_daily_range_scored"], 2)
        for row in (receipt["rows"][1], receipt["rows"][5]):
            self.assertEqual(row["source_hours_complete"], 24)
            self.assertEqual(row["range_state"], "FULL_UTC_DAY_CONTAINED")
            self.assertIsNotNone(row["observed_close_USDT"])
        self.assertEqual(receipt["rows"][0]["range_state"],
                         "PARTIAL_THURSDAY_SIX_HOUR_COVERAGE_UNSCORABLE")

    def test_missing_one_hour_never_scores_full_day_even_with_last_close(self):
        fixture = seed(include_thursday=True, include_friday=True)
        fixture["2026-11-06"].pop(7)
        write_source(self.root, fixture)
        receipt = self.evaluate("2026-11-07T00:08:00Z")
        self.assertEqual(receipt["matured_observations"], 2)
        self.assertEqual(receipt["full_daily_range_scored"], 0)
        for row in (receipt["rows"][1], receipt["rows"][5]):
            self.assertEqual(row["source_hours_complete"], 23)
            self.assertEqual(row["outcome_state"],
                             "AWAITING_COMPLETE_FUTURE_UTC_CANDLES")
            self.assertIsNone(row["observed_close_USDT"])

    def test_duplicate_hour_and_earlier_anchor_rewrite_fail_closed(self):
        fixture = seed(include_thursday=True, include_friday=True)
        fixture["2026-11-06"].append(copy.deepcopy(fixture["2026-11-06"][0]))
        write_source(self.root, fixture)
        receipt = self.evaluate("2026-11-07T00:08:00Z")
        self.assertEqual(receipt["source_state"], "UNAVAILABLE_FAIL_CLOSED")
        self.assertIn("DUPLICATE_SOURCE_HOUR", receipt["source_failure"])
        self.assertEqual(receipt["matured_observations"], 0)
        fixture = seed(include_thursday=True)
        fixture["2026-11-05"][0]["btc_close"] += 10
        fixture["2026-11-05"][0]["btc_high"] += 10
        write_source(self.root, fixture)
        receipt = self.evaluate("2026-11-06T00:08:00Z")
        self.assertEqual(receipt["source_state"], "UNAVAILABLE_FAIL_CLOSED")
        self.assertIn("ANCHOR_OR_PRIOR24", receipt["source_failure"])

    def test_future_known_source_and_unqualified_status_never_score(self):
        write_source(self.root, seed(include_thursday=True, include_friday=True))
        before_target = self.evaluate("2026-11-05T22:08:00Z")
        self.assertEqual(before_target["matured_observations"], 0)
        self.assertTrue(all(r["outcome_state"] == "PENDING_UTC_TARGET"
                            for r in before_target["rows"]))
        fixture = seed(include_thursday=True)
        fixture["2026-11-05"][-1]["spot_status"] = "NOT_READY"
        write_source(self.root, fixture)
        receipt = self.evaluate("2026-11-06T00:08:00Z")
        self.assertEqual(receipt["source_state"], "UNAVAILABLE_FAIL_CLOSED")
        self.assertEqual(receipt["matured_observations"], 0)
