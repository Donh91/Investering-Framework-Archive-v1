"""W45 prospective lab: no pre-close scoring, no Monday forecast promotion."""
import copy
import hashlib
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.research.w45_rehearsal_outcomes import (
    CONTRACT, compile_outcomes, parse_utc,
)

ROOT = Path(__file__).resolve().parents[2]
PACKET_FILE = ROOT / "06_RESEARCH_LAB/mission_packets/2026-11-05__W45_MIDWEEK_PROSPECTIVE_BENCHMARK_v1.json"
RAW = PACKET_FILE.read_bytes()
PACKET = json.loads(RAW)
SHA = hashlib.sha256(RAW).hexdigest()
ANCHOR = parse_utc("2026-11-04T22:00:00Z")
FIRST = parse_utc("2026-11-06T00:00:00Z")


def public_source(cutoff=ANCHOR, *, issue=32):
    rows = PACKET["observations"][-70:]
    btc = [{"observed_at_utc": r["candle_close_at_utc"], "close": r["BTC_USDT"]} for r in rows]
    eth = [{"observed_at_utc": r["candle_close_at_utc"], "close": r["ETH_USDT"]} for r in rows]
    moment = ANCHOR + timedelta(hours=1)
    while moment <= cutoff:
        at = moment.isoformat().replace("+00:00", "Z")
        btc.append({"observed_at_utc": at, "close": 79900.0 + (moment - ANCHOR).total_seconds() / 3600.0})
        eth.append({"observed_at_utc": at, "close": 2420.0 + (moment - ANCHOR).total_seconds() / 3600.0})
        moment += timedelta(hours=1)
    return {"public_live_precision": {
        "contract": "CN_PUBLIC_LIVE_PRICE_PRECISION_v1",
        "forecast_week": "2026-W45",
        "public_issue_number": issue,
        "live_as_of_utc": cutoff.isoformat().replace("+00:00", "Z"),
        "price_quote_labels": {
            "contract": "CN_PUBLIC_PRICE_QUOTE_LABELS_v1",
            "actual_native_spot": {"BTC": "USDT", "ETH": "USDT"},
            "forecast_model_declared": {"BTC": "UNAVAILABLE", "ETH": "UNAVAILABLE"},
            "conversion_applied": False,
            "proof_authority": False,
            "comparison_precision_eligible": False,
        },
        "hourly_price_path": {
            "contract": "CN_PUBLIC_HOURLY_PRICE_PATH_v1",
            "source": "HOURLY_SPOT_PASS_ONLY",
            "semantics": "OBSERVED_HOURLY_CLOSE_NOT_A_PROSPECTIVE_FORECAST",
            "forecast_week": "2026-W45",
            "public_issue_number": issue,
            "observed_through_utc": cutoff.isoformat().replace("+00:00", "Z"),
            "BTC": btc, "ETH": eth,
        },
    }}


def calculate(source, at, packet=None, mode="PUBLIC_LIVE_W45"):
    return compile_outcomes(copy.deepcopy(packet or PACKET), copy.deepcopy(source), at,
                            source_mode=mode, original_research_sha256=SHA)


class W45Rehearsal(unittest.TestCase):
    def test_rehearsal_all_eight_forecasts_are_preissued_and_stay_pending_nov5(self):
        at = parse_utc("2026-11-05T09:00:00Z")
        receipt = calculate(public_source(), at)
        self.assertEqual(receipt["contract"], CONTRACT)
        self.assertEqual(receipt["original_research_issued_at_utc"], PACKET["generated_at_utc"])
        self.assertEqual(receipt["original_research_source_sha256"], SHA)
        self.assertEqual(receipt["source_state"], "VERIFIED_PUBLIC_CAPTURE_NOT_INDEPENDENT_FIRST_KNOWN")
        self.assertEqual(receipt["observed_hours"], 70)
        self.assertEqual(receipt["matured_observations"], 0)
        self.assertEqual(len(receipt["rows"]), 8)
        self.assertEqual([(r["asset"], r["day"]) for r in receipt["rows"]],
                         [("BTC", d) for d in range(4, 8)] + [("ETH", d) for d in range(4, 8)])
        for row in receipt["rows"]:
            self.assertEqual(row["outcome_state"], "PENDING_UTC_TARGET")
            self.assertIsNone(row["observed_close_USDT"])
            self.assertIsNone(row["B0_absolute_percentage_error"])
            self.assertIsNone(row["B1_absolute_percentage_error"])
            self.assertGreater(parse_utc(row["target_close_at_utc"]),
                               parse_utc(receipt["original_research_issued_at_utc"]))
        for k in ("research_only",):
            self.assertIs(receipt[k], True)
        for k in ("official_scoring_eligible", "portfolio_action_authority",
                  "provider_first_known_verified", "independent_scientific_edge_proven"):
            self.assertIs(receipt[k], False)
        self.assertEqual(PACKET_FILE.read_bytes(), RAW)

    def test_first_matured_utc_close_scores_btc_and_eth_only_without_future_days(self):
        at = parse_utc("2026-11-06T00:08:00Z")
        receipt = calculate(public_source(FIRST), at)
        self.assertEqual(receipt["matured_observations"], 2)
        self.assertEqual([receipt["assets"][x]["matured_days"] for x in ("BTC", "ETH")], [1, 1])
        for index in (0, 4):
            row = receipt["rows"][index]
            self.assertEqual(row["outcome_state"], "MATURED_PUBLIC_CAPTURE")
            self.assertGreater(row["observed_close_USDT"], 0)
            self.assertAlmostEqual(row["B1_absolute_percentage_error"],
                                   100 * abs(row["B1_original_expected_close_USDT"] /
                                             row["observed_close_USDT"] - 1), places=4)
        self.assertTrue(all(row["outcome_state"] == "PENDING_UTC_TARGET"
                            for i, row in enumerate(receipt["rows"]) if i not in (0, 4)))
        self.assertFalse(receipt["assets"]["BTC"]["claim_of_edge"])
        self.assertFalse(receipt["assets"]["ETH"]["claim_of_edge"])

    def test_closed_day_with_missing_exact_hour_does_not_get_nearest_price(self):
        # Source still has only 22:00 UTC on Nov 4, despite midnight on Nov 6 passing.
        receipt = calculate(public_source(), parse_utc("2026-11-06T01:00:00Z"))
        self.assertEqual(receipt["matured_observations"], 0)
        self.assertEqual(receipt["rows"][0]["outcome_state"], "AWAITING_VERIFIED_SOURCE")
        self.assertEqual(receipt["rows"][4]["outcome_state"], "AWAITING_VERIFIED_SOURCE")
        self.assertIsNone(receipt["rows"][0]["observed_close_USDT"])

    def test_future_known_source_does_not_get_admitted_before_target(self):
        receipt = calculate(public_source(FIRST), parse_utc("2026-11-05T09:00:00Z"))
        self.assertEqual(receipt["source_state"], "UNAVAILABLE_FAIL_CLOSED")
        self.assertEqual(receipt["source_failure"], "FUTURE_KNOWN_SOURCE_REJECTED")
        self.assertEqual(receipt["matured_observations"], 0)
        self.assertTrue(all(r["observed_close_USDT"] is None for r in receipt["rows"]))

    def test_source_mismatch_bad_quote_duplicate_and_eth_clock_divergence_fail_closed(self):
        changes = [
            lambda s: s["public_live_precision"].update(public_issue_number=34),
            lambda s: s["public_live_precision"]["price_quote_labels"]["actual_native_spot"].update(ETH="USD"),
            lambda s: s["public_live_precision"]["hourly_price_path"]["ETH"][0].update(
                observed_at_utc="2026-11-02T05:00:00Z"),
            lambda s: s["public_live_precision"]["hourly_price_path"]["BTC"][1].update(
                observed_at_utc=s["public_live_precision"]["hourly_price_path"]["BTC"][0]["observed_at_utc"]),
            lambda s: s["public_live_precision"]["hourly_price_path"]["ETH"][5].update(close=-1),
        ]
        for mutate in changes:
            with self.subTest(change=mutate):
                src = public_source(FIRST)
                mutate(src)
                receipt = calculate(src, parse_utc("2026-11-06T01:00:00Z"))
                self.assertEqual(receipt["source_state"], "UNAVAILABLE_FAIL_CLOSED")
                self.assertEqual(receipt["matured_observations"], 0)
                self.assertTrue(all(x["observed_close_USDT"] is None for x in receipt["rows"]))

    def test_all_four_days_score_only_after_sunday_utc_midnight_target(self):
        at = parse_utc("2026-11-09T00:08:00Z")
        receipt = calculate(public_source(parse_utc("2026-11-09T00:00:00Z")), at)
        self.assertEqual(receipt["matured_observations"], 8)
        self.assertTrue(all(x["outcome_state"] == "MATURED_PUBLIC_CAPTURE" for x in receipt["rows"]))
        self.assertEqual([receipt["assets"][a]["matured_days"] for a in ("BTC", "ETH")], [4, 4])
        self.assertFalse(receipt["independent_scientific_edge_proven"])

    def test_archived_w45_public_capture_can_replace_w46_latest_only_after_original_week_closes(self):
        pairs = public_source(FIRST)["public_live_precision"]["hourly_price_path"]
        archived = {
            "contract": "CN_GRAPH_HISTORY_ACTUAL_v1",
            "forecast_week": "2026-W45",
            "actual_quote_unit": "USDT",
            "semantics": "PASS_HOURLY_CLOSE_ONLY",
            "observed_hours": len(pairs["BTC"]),
            "points": [{"observed_at_utc": b["observed_at_utc"],
                        "BTC": b["close"], "ETH": e["close"]}
                       for b, e in zip(pairs["BTC"], pairs["ETH"])],
        }
        receipt = calculate(archived, parse_utc("2026-11-09T00:08:00Z"),
                            mode="IMMUTABLE_W45_HISTORY")
        self.assertEqual(receipt["source_mode"], "IMMUTABLE_W45_HISTORY")
        self.assertEqual(receipt["matured_observations"], 2)
        self.assertFalse(receipt["official_scoring_eligible"])
        archived["actual_quote_unit"] = "USD"
        result = calculate(archived, parse_utc("2026-11-09T00:08:00Z"),
                           mode="IMMUTABLE_W45_HISTORY")
        self.assertEqual(result["source_state"], "UNAVAILABLE_FAIL_CLOSED")

    def test_rewritten_research_issue_is_rejected_even_if_source_matches(self):
        packet = copy.deepcopy(PACKET)
        packet["forecast"]["assets"]["ETH"]["forecast"][0]["B1_decay_momentum_expected_close"] += 1
        with self.assertRaisesRegex(ValueError, "RESEARCH_FORECAST_SOURCE_RECOMPUTATION_MISMATCH"):
            calculate(public_source(), parse_utc("2026-11-05T09:00:00Z"), packet=packet)
        packet = copy.deepcopy(PACKET)
        packet["forecast"]["official_scoring_eligible"] = True
        with self.assertRaisesRegex(ValueError, "RESEARCH_AUTHORITY_LEAK"):
            calculate(public_source(), parse_utc("2026-11-05T09:00:00Z"), packet=packet)


if __name__ == "__main__":
    unittest.main()
