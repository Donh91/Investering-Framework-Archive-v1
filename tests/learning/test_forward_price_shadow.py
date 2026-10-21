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

    def reject(self, fn):
        data = fixture()
        fn(data)
        with self.assertRaises(ValueError):
            build_shadow(data)

    def test_tamper_frozen_source_rows(self):
        self.reject(lambda x: x["bars"][-1].update(close_usd=x["bars"][-1]["close_usd"] + 1.0))

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

    def test_gapped_bars(self):
        self.reject(lambda x: x["bars"].pop(25))

    def test_duplicate_bar(self):
        self.reject(lambda x: x["bars"].insert(40, copy.deepcopy(x["bars"][39])))

    def test_nonpositive_or_nonfinite(self):
        for value in (-1,0,float("inf"),float("nan"),True):
            with self.subTest(x=value):
                self.reject(lambda x: x["bars"][0].update(low_usd=value))

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

    def test_missing_source_manifest_sha(self):
        self.reject(lambda x: x.update(source_manifest_sha256="x"))

    def test_different_asset_must_not_share_same_forecast_id(self):
        a=fixture(); b=fixture();b["asset"]="ETH"
        self.assertNotEqual(build_shadow(a)["candidate_sha256"],build_shadow(b)["candidate_sha256"])


if __name__ == "__main__":
    unittest.main()
