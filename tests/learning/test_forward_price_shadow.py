"""Synthetic adversarial tests; no real market data or provider read access."""
from __future__ import annotations

import copy
import hashlib
import json
import unittest
from datetime import datetime, timedelta, timezone

from scripts.learning.forward_price_shadow import INPUT_CONTRACT, build_shadow, canonical


def fixture(n=365):
    first = datetime(2025, 10, 20, tzinfo=timezone.utc)
    bars = []
    for i in range(n):
        day = first + timedelta(days=i)
        price = 100 + 0.07 * i
        bars.append({
            "day_utc": day.strftime("%Y-%m-%d"),
            "low_usd": price * .987,
            "high_usd": price * 1.013,
            "close_usd": price,
            "first_known_at_utc": (day + timedelta(days=1, minutes=15)).strftime("%Y-%m-%dT%H:%M:%SZ")
        })
    cutoff = first + timedelta(days=n, hours=2)
    return {
        "contract": INPUT_CONTRACT, "asset": "BTC", "quote": "USD", "venue": "SYNTHETIC_TEST_ONLY",
        "issued_at_utc": (cutoff + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "cutoff_utc": cutoff.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "provider_first_known_proven": True, "source_manifest_sha256": "a" * 64,
        "source_rows_sha256": hashlib.sha256(canonical(bars)).hexdigest(),
        "bars": bars,
    }


class ShadowPriceTests(unittest.TestCase):
    def test_deterministic_source_bound_research_only(self):
        doc = fixture()
        before = copy.deepcopy(doc)
        a = build_shadow(doc)
        self.assertEqual(build_shadow(doc), a)
        self.assertEqual(doc, before)
        self.assertEqual(a["authority"], "SHADOW_NOT_ISSUED")
        self.assertFalse(a["direction_used_in_price_construction"])
        self.assertTrue(a["no_portfolio_action"])
        self.assertFalse(a["source_first_known_independently_rechecked"])
        self.assertEqual(a["candidate_sha256"], hashlib.sha256((json.dumps(
            {k:v for k,v in a.items() if k != "candidate_sha256"},
            sort_keys=True,separators=(",", ":"),allow_nan=False)+"\n").encode()).hexdigest())
        for h in ("1", "7", "14", "21"):
            band = a["horizons_days"][h]
            self.assertEqual(band["status"], "SHADOW_BASELINE_ONLY")
            self.assertLess(band["low_usd"], band["high_usd"])
            self.assertIsNone(band["coverage_probability"])

    def reject(self, fn, *, rehash=True):
        data = fixture()
        fn(data)
        if rehash:
            data["source_rows_sha256"] = hashlib.sha256(canonical(data["bars"])).hexdigest()
        with self.assertRaises(ValueError):
            build_shadow(data)

    def test_tamper_frozen_source_rows(self):
        self.reject(lambda x: x["bars"][-1].update(close_usd=x["bars"][-1]["close_usd"] + 1.0), rehash=False)

    def test_no_provider_proof(self):
        self.reject(lambda x: x.update(provider_first_known_proven=False))

    def test_lookahead_row(self):
        self.reject(lambda x: x["bars"][-1].update(first_known_at_utc="2027-01-01T00:00:00Z"))

    def test_partial_bar(self):
        self.reject(lambda x: x["bars"][-1].update(first_known_at_utc=x["bars"][-1]["day_utc"]+"T12:00:00Z"))

    def test_future_cutoff(self):
        self.reject(lambda x: x.update(cutoff_utc="2027-01-01T00:00:00Z"))

    def test_stale_cutoff(self):
        self.reject(lambda x: x.update(issued_at_utc="2027-01-01T00:00:00Z"))

    def test_end_to_end_source_age_prevents_chained_96h_lag(self):
        data = fixture()
        last_day = datetime.strptime(data["bars"][-1]["day_utc"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        last_closed = last_day + timedelta(days=1)
        data["cutoff_utc"] = (last_closed + timedelta(hours=47)).strftime("%Y-%m-%dT%H:%M:%SZ")
        data["issued_at_utc"] = (last_closed + timedelta(hours=94)).strftime("%Y-%m-%dT%H:%M:%SZ")
        # Each prior age gate alone is <48h, but the original issue is 94h stale.
        with self.assertRaisesRegex(ValueError, "issued_forecast_older_than_closed_source"):
            build_shadow(data)

    def test_recent_original_issue_within_48h_still_accepted(self):
        data = fixture()
        last_day = datetime.strptime(data["bars"][-1]["day_utc"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        last_closed = last_day + timedelta(days=1)
        data["issued_at_utc"] = (last_closed + timedelta(hours=47)).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.assertEqual(build_shadow(data)["authority"], "SHADOW_NOT_ISSUED")

    def test_gapped_bars(self):
        self.reject(lambda x: x["bars"].pop(25))

    def test_duplicate_bar(self):
        self.reject(lambda x: x["bars"].insert(40, copy.deepcopy(x["bars"][39])))

    def test_nonpositive_or_nonfinite(self):
        for value in (-1, 0, True):
            with self.subTest(x=value):
                self.reject(lambda x: x["bars"][0].update(low_usd=value))

    def test_nonfinite_source_values_fail_canonical_input_binding(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                data=fixture()
                data["bars"][0]["low_usd"]=value
                with self.assertRaises(ValueError):
                    canonical(data["bars"])

    def test_close_outside_daily_high(self):
        self.reject(lambda x: x["bars"][0].update(close_usd=999999))

    def test_extra_price_or_outcome_key(self):
        self.reject(lambda x: x.update(next_price_usd=140))
        self.reject(lambda x: x.update(outcome_correct=True))

    def test_require_exact_usd(self):
        self.reject(lambda x: x.update(quote="USDT"))

    def test_insufficient_history(self):
        self.reject(lambda x: x.update(bars=x["bars"][:200]))

    def test_abstain_if_nonoverlap_count_too_small(self):
        # 252 days is enough for short horizons, but only ~11 distinct 21d blocks.
        d=fixture(252)
        out=build_shadow(d)
        self.assertEqual(out["horizons_days"]["21"]["status"], "ABSTAIN")
        self.assertEqual(out["horizons_days"]["21"]["nonoverlap_upper_bound"], 11)

    def test_253_bars_has_twelve_disjoint_21d_blocks(self):
        data=fixture(253)
        result=build_shadow(data)["horizons_days"]["21"]
        self.assertEqual(result["nonoverlap_upper_bound"], 12)
        self.assertEqual(result["status"], "SHADOW_BASELINE_ONLY")

    def test_source_first_known_cannot_equal_day_close(self):
        def boundary(x):
            last=x["bars"][-1]
            day=datetime.strptime(last["day_utc"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            last["first_known_at_utc"]=(day+timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.reject(boundary)

    def test_small_positive_prices_not_rounded_to_zero(self):
        data=fixture()
        for bar in data["bars"]:
            p=bar["close_usd"]*1e-12
            bar["close_usd"]=p
            bar["low_usd"]=p*.99
            bar["high_usd"]=p*1.01
        data["source_rows_sha256"]=hashlib.sha256(canonical(data["bars"])).hexdigest()
        out=build_shadow(data)
        for v in out["horizons_days"].values():
            if v["status"] == "SHADOW_BASELINE_ONLY":
                self.assertGreater(v["low_usd"],0)
                self.assertGreater(v["high_usd"],v["low_usd"])

    def test_numeric_oracle_known_geometric_path_extrema(self):
        """Catch wrong target-window endpoints, min/max choice and sample counts."""
        data = fixture(253)
        for i, bar in enumerate(data["bars"]):
            close = 100.0 * (1.001 ** i)
            bar["close_usd"] = close
            bar["low_usd"] = 0.99 * close
            bar["high_usd"] = 1.01 * close
        data["source_rows_sha256"] = hashlib.sha256(canonical(data["bars"])).hexdigest()
        output = build_shadow(data)
        anchor = data["bars"][-1]["close_usd"]
        for h in (1, 7, 14, 21):
            with self.subTest(horizon=h):
                candidate = output["horizons_days"][str(h)]
                self.assertEqual(candidate["status"], "SHADOW_BASELINE_ONLY")
                self.assertEqual(candidate["overlapping_windows"], 253 - h)
                self.assertEqual(candidate["nonoverlap_upper_bound"], 252 // h)
                self.assertAlmostEqual(candidate["low_usd"], anchor * 0.99 * 1.001, delta=anchor*1e-12)
                self.assertAlmostEqual(candidate["high_usd"], anchor * 1.01 * (1.001 ** h), delta=anchor*1e-12)

    def test_individually_finite_extrema_without_sum_overflow(self):
        """Two finite endpoints are not invalid just because their sum overflows."""
        data = fixture(253)
        for bar in data["bars"]:
            bar["low_usd"] = 9e307
            bar["close_usd"] = 1e308
            bar["high_usd"] = 1.1e308
        data["source_rows_sha256"] = hashlib.sha256(canonical(data["bars"])).hexdigest()
        result = build_shadow(data)
        for h in (1, 7, 14, 21):
            with self.subTest(horizon=h):
                row = result["horizons_days"][str(h)]
                self.assertEqual(row["status"], "SHADOW_BASELINE_ONLY")
                self.assertAlmostEqual(row["low_usd"] / 1e308, 0.9, places=14)
                self.assertAlmostEqual(row["high_usd"] / 1e308, 1.1, places=14)

    def test_q25_q75_is_explicitly_distinct_uncalibrated_comparator(self):
        data = fixture(365)
        result = build_shadow(data)
        self.assertEqual(result["method"], "CLOSED_DAILY_HISTORICAL_BLOCK_EXTREMA_Q10_Q90_v0_1")
        self.assertEqual(result["descriptive_alternative_method"],
                         "CLOSED_DAILY_HISTORICAL_BLOCK_EXTREMA_Q25_Q75_DESCRIPTIVE_v0_1")
        self.assertTrue(result["alternative_is_unissued_non_authoritative"])
        self.assertFalse(result["probabilities_claimed"])
        for horizon in ("1", "7", "14", "21"):
            with self.subTest(horizon=horizon):
                primary = result["horizons_days"][horizon]
                alt = result["descriptive_q25_q75_horizons_days"][horizon]
                self.assertEqual(alt["status"], "SHADOW_BASELINE_ONLY")
                self.assertEqual(alt["marginal_low_quantile"], 0.25)
                self.assertEqual(alt["marginal_high_quantile"], 0.75)
                self.assertIsNone(alt["joint_coverage_probability"])
                self.assertIsNone(primary["coverage_probability"])
                self.assertGreaterEqual(alt["low_usd"], primary["low_usd"])
                self.assertLessEqual(alt["high_usd"], primary["high_usd"])
                self.assertEqual(alt["overlapping_windows"], primary["overlapping_windows"])
                self.assertEqual(alt["nonoverlap_upper_bound"], primary["nonoverlap_upper_bound"])

    def test_q25_q75_quantile_numeric_oracle_from_frozen_bars(self):
        data = fixture(253)
        # Independently enumerate eligible windows at the ORIGINAL issue cutoff.
        result = build_shadow(data)
        bars = data["bars"]
        anchor = bars[-1]["close_usd"]
        for horizon in (1, 7, 14, 21):
            with self.subTest(horizon=horizon):
                lows, highs = [], []
                for j in range(1, len(bars) - horizon + 1):
                    reference = bars[j - 1]["close_usd"]
                    period = bars[j:j + horizon]
                    lows.append(min(row["low_usd"] for row in period) / reference)
                    highs.append(max(row["high_usd"] for row in period) / reference)
                def linear_percentile(values, q):
                    ordered = sorted(values)
                    p = (len(ordered) - 1) * q
                    n = int(p)
                    return ordered[n] * (1 - (p - n)) + ordered[min(n + 1, len(ordered) - 1)] * (p - n)
                alt = result["descriptive_q25_q75_horizons_days"][str(horizon)]
                self.assertAlmostEqual(alt["low_usd"], anchor * linear_percentile(lows, 0.25),
                                       delta=anchor * 1e-10)
                self.assertAlmostEqual(alt["high_usd"], anchor * linear_percentile(highs, 0.75),
                                       delta=anchor * 1e-10)
                self.assertEqual(alt["overlapping_windows"], 253 - horizon)

    def test_alternative_21_day_abstention_matches_source_gate(self):
        result = build_shadow(fixture(252))
        alt = result["descriptive_q25_q75_horizons_days"]["21"]
        self.assertEqual(alt["status"], "ABSTAIN")
        self.assertIsNone(alt["low_usd"])
        self.assertIsNone(alt["high_usd"])
        self.assertIsNone(alt["joint_coverage_probability"])

    def test_missing_source_manifest_sha(self):
        self.reject(lambda x: x.update(source_manifest_sha256="x"))

    def test_different_asset_must_not_share_same_forecast_id(self):
        a=fixture(); b=fixture();b["asset"]="ETH"
        self.assertNotEqual(build_shadow(a)["candidate_sha256"],build_shadow(b)["candidate_sha256"])


if __name__ == "__main__":
    unittest.main()
