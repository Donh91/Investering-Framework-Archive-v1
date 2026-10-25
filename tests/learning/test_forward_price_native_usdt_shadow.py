"""Adversarial quote-native USDT tests; pure synthetic OHLC, no provider access."""
from __future__ import annotations

import copy
import hashlib
import json
import unittest
from datetime import datetime, timedelta, timezone

from scripts.learning.forward_price_shadow import (
    HORIZONS, INPUT_CONTRACT, USDT_CONTRACT, USDT_HORIZONS,
    USDT_INPUT_CONTRACT, build_native_usdt_shadow, build_shadow, canonical,
)


def daily_bars(*, n=365, quote="USDT"):
    first = datetime(2025, 10, 20, tzinfo=timezone.utc)
    out = []
    for i in range(n):
        day = first + timedelta(days=i)
        center = 100 + 0.07 * i
        out.append({
            "day_utc": day.strftime("%Y-%m-%d"),
            f"low_{quote.lower()}": center * .987,
            f"high_{quote.lower()}": center * 1.013,
            f"close_{quote.lower()}": center,
            "first_known_at_utc": (day+timedelta(days=1, minutes=15)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        })
    return out


def fixture(*, quote="USDT", n=365):
    first = datetime(2025, 10, 20, tzinfo=timezone.utc)
    bars = daily_bars(n=n, quote=quote)
    cutoff = first + timedelta(days=n, hours=2)
    return {
        "contract": USDT_INPUT_CONTRACT if quote == "USDT" else INPUT_CONTRACT,
        "asset": "BTC",
        "quote": quote,
        "venue": "BINANCE_SPOT_BTCUSDT" if quote == "USDT" else "SYNTHETIC_TEST_ONLY",
        "issued_at_utc": (cutoff+timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "cutoff_utc": cutoff.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "provider_first_known_proven": True,  # synthetic assertion only, never real source proof
        "source_manifest_sha256": "a" * 64,
        "source_rows_sha256": hashlib.sha256(canonical(bars)).hexdigest(),
        "bars": bars,
    }


class NativeUsdtShadowPriceTests(unittest.TestCase):
    def reject(self, change, *, n=365, rehash=True):
        p = fixture(n=n)
        change(p)
        if rehash:
            p["source_rows_sha256"] = hashlib.sha256(canonical(p["bars"])).hexdigest()
        with self.assertRaises(ValueError):
            build_native_usdt_shadow(p)

    def test_native_usdt_quote_is_not_usd_and_never_issued(self):
        p = fixture()
        frozen = copy.deepcopy(p)
        out = build_native_usdt_shadow(p)
        self.assertEqual(p, frozen)
        self.assertEqual(build_native_usdt_shadow(p), out)
        self.assertEqual(out["contract"], USDT_CONTRACT)
        self.assertEqual(out["quote"], "USDT")
        self.assertEqual(out["venue"], "BINANCE_SPOT_BTCUSDT")
        self.assertTrue(out["anchor_usdt"] > 0)
        self.assertNotIn("anchor_usd", out)
        self.assertEqual(out["authority"], "SHADOW_NOT_ISSUED")
        self.assertTrue(out["no_publication"])
        self.assertTrue(out["no_portfolio_action"])
        self.assertTrue(out["no_model_selection"])
        self.assertTrue(out["no_autonomous_reweight"])
        self.assertFalse(out["source_first_known_independently_rechecked"])
        self.assertFalse(out["probabilities_claimed"])
        self.assertFalse(out["outcome_matured"])
        self.assertFalse(out["direction_used_in_price_construction"])
        self.assertEqual(len(out["candidate_sha256"]), 64)

    def test_binance_usdt_horizons_include_30d_and_abstain_56d(self):
        self.assertEqual(HORIZONS, (1, 7, 14, 21))
        self.assertEqual(USDT_HORIZONS, (1, 7, 14, 21, 30, 56))
        out = build_native_usdt_shadow(fixture())
        self.assertEqual(set(out["horizons_days"]), set(map(str, USDT_HORIZONS)))
        for h in ("1", "7", "14", "21", "30"):
            with self.subTest(h=h):
                row = out["horizons_days"][h]
                self.assertEqual(row["status"], "SHADOW_BASELINE_ONLY")
                self.assertLess(row["low_usdt"], row["high_usdt"])
                self.assertNotIn("low_usd", row)
                self.assertNotIn("high_usd", row)
                self.assertIsNone(row["coverage_probability"])
                self.assertEqual(row["calibration_status"], "NOT_CALIBRATED")
        self.assertEqual(out["horizons_days"]["56"]["status"], "ABSTAIN")
        self.assertEqual(out["horizons_days"]["56"]["reason"],
                         "TOO_FEW_INDEPENDENT_HORIZON_BLOCKS")
        self.assertEqual(out["horizons_days"]["56"]["nonoverlap_upper_bound"], 6)
        self.assertIsNone(out["horizons_days"]["56"]["low_usdt"])
        self.assertIsNone(out["horizons_days"]["56"]["high_usdt"])

    def test_usdt_and_usd_same_synthetic_bars_yield_numeric_math_parity_but_different_quotes(self):
        native = build_native_usdt_shadow(fixture(quote="USDT"))
        original = build_shadow(fixture(quote="USD"))
        self.assertEqual(original["quote"], "USD")
        self.assertNotIn("anchor_usdt", original)
        self.assertNotIn("anchor_usd", native)
        self.assertEqual(native["anchor_usdt"], original["anchor_usd"])
        for h in map(str, HORIZONS):
            self.assertEqual(original["horizons_days"][h]["status"],
                             native["horizons_days"][h]["status"])
            self.assertAlmostEqual(original["horizons_days"][h]["low_usd"],
                                   native["horizons_days"][h]["low_usdt"], places=12)
            self.assertAlmostEqual(original["horizons_days"][h]["high_usd"],
                                   native["horizons_days"][h]["high_usdt"], places=12)
        self.assertNotEqual(original["contract"], native["contract"])
        self.assertNotEqual(original["candidate_sha256"], native["candidate_sha256"])
        self.assertEqual(set(original["horizons_days"]), {"1", "7", "14", "21"})

    def test_usd_original_rejects_native_usdt_without_coercion(self):
        with self.assertRaises(ValueError):
            build_shadow(fixture(quote="USDT"))
        with self.assertRaises(ValueError):
            build_native_usdt_shadow(fixture(quote="USD"))

    def test_usdt_rejects_false_venue_or_asset(self):
        for field, value in (
            ("venue", "KRAKEN_SPOT_XXBTZUSD"),
            ("venue", "BINANCE_FUTURES_BTCUSDT"),
            ("venue", "SYNTHETIC_TEST_ONLY"),
            ("venue", "BINANCE_SPOT_BTCUSD"),
            ("asset", "ETH"),
            ("quote", "USD"),
            ("quote", "USDC"),
            ("contract", INPUT_CONTRACT),
        ):
            with self.subTest(field=field):
                self.reject(lambda p, field=field, value=value: p.__setitem__(field, value))

    def test_reject_usdt_payload_with_mixed_usd_fields(self):
        for f in ("low_usdt", "high_usdt", "close_usdt"):
            def ch(p):
                value = p["bars"][0].pop(f)
                p["bars"][0][f.replace("usdt", "usd")] = value
            with self.subTest(field=f):
                self.reject(ch)
        self.reject(lambda p: p["bars"][0].update(extra_usd=999))
        self.reject(lambda p: p.update(next_price_usd=999))
        self.reject(lambda p: p.update(forecaster_status="ISSUED"))

    def test_reject_unverified_provider_or_untimestamped_vintage(self):
        self.reject(lambda p: p.update(provider_first_known_proven=False))
        self.reject(lambda p: p.update(provider_first_known_proven=1))
        self.reject(lambda p: p["bars"][0].update(first_known_at_utc="2030-01-01T00:00:00Z"))
        self.reject(lambda p: p["bars"][0].update(first_known_at_utc=p["bars"][0]["day_utc"]+"T00:00:00Z"))

    def test_reject_tampered_source_hash_or_malformed_git_manifest_hash(self):
        self.reject(lambda p: p["bars"][0].update(close_usdt=p["bars"][0]["close_usdt"]+3),
                    rehash=False)
        self.reject(lambda p: p.update(source_manifest_sha256="INVALID"))
        self.reject(lambda p: p.update(source_rows_sha256="0"*64), rehash=False)

    def test_reject_gaps_and_duplicates(self):
        self.reject(lambda p: p["bars"].pop(33))
        self.reject(lambda p: p["bars"].insert(44, copy.deepcopy(p["bars"][43])))

    def test_reject_negative_zero_nonfinite_and_boolean_price(self):
        for value in (-1, 0, True, float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                if isinstance(value, float) and (value != value or abs(value) == float("inf")):
                    p = fixture()
                    p["bars"][0]["low_usdt"] = value
                    with self.assertRaises(ValueError):
                        canonical(p["bars"])
                else:
                    self.reject(lambda p, value=value: p["bars"][0].update(low_usdt=value))
        self.reject(lambda p: p["bars"][0].update(high_usdt=0.01))
        self.reject(lambda p: p["bars"][0].update(close_usdt=100000))

    def test_reject_future_issue_stale_and_unsettled(self):
        self.reject(lambda p: p.update(issued_at_utc="2031-01-01T00:00:00Z"))
        self.reject(lambda p: p.update(cutoff_utc="2031-01-01T00:00:00Z"))
        self.reject(lambda p: p["bars"][-1].update(
            first_known_at_utc=p["bars"][-1]["day_utc"]+"T12:00:00Z"))

    def test_research_only_21_and_30d_abstain_on_252_rows(self):
        out = build_native_usdt_shadow(fixture(n=252))
        self.assertEqual(out["horizons_days"]["21"]["status"], "ABSTAIN")
        self.assertEqual(out["horizons_days"]["30"]["status"], "ABSTAIN")
        self.assertEqual(out["horizons_days"]["56"]["status"], "ABSTAIN")
        self.assertEqual(out["horizons_days"]["21"]["nonoverlap_upper_bound"], 11)
        self.assertEqual(out["horizons_days"]["56"]["nonoverlap_upper_bound"], 4)

    def test_reject_insufficient_or_oversized_history(self):
        for n in (1, 21, 250, 251, 367):
            with self.subTest(n=n):
                p = fixture(n=n)
                with self.assertRaises(ValueError):
                    build_native_usdt_shadow(p)

    def test_reject_unsafe_object_or_hidden_market_action_keys(self):
        for payload in (None, [], "", 1):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                build_native_usdt_shadow(payload)
        self.reject(lambda p: p.update(portfolio_action=True))
        self.reject(lambda p: p.update(publish_forecast=True))

    def test_prospective_source_quote_identity_not_model_skill(self):
        out = build_native_usdt_shadow(fixture())
        self.assertTrue(out["source_first_known_asserted"])
        self.assertFalse(out["source_first_known_independently_rechecked"])
        self.assertFalse(out["probabilities_claimed"])
        self.assertIsNone(out["horizons_days"]["30"]["coverage_probability"])
        self.assertNotIn("low_usd", str(out))
        self.assertNotIn("high_usd", str(out))
        self.assertNotIn("anchor_usd", str(out))
        self.assertTrue(out["alternative_is_unissued_non_authoritative"])
        self.assertTrue(out["no_publication"])


if __name__ == "__main__":
    unittest.main()
