"""Pure synthetic adversarial Binance BTCUSDT candidate testing; NO HTTP."""
from __future__ import annotations

import copy
import json
import unittest
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

from scripts.learning.forward_price_binance_usdt_candidate import (
    BASE, CONTRACT, REQUEST_CONTRACT, inspect_response, request_window,
)

T0 = datetime(2026, 10, 25, 10, tzinfo=timezone.utc)
fmt = lambda d: d.isoformat().replace("+00:00", "Z")

def sample(count=3, interval="1h"):
    step = timedelta(hours=1) if interval == "1h" else timedelta(days=1)
    start = T0 if interval == "1h" else T0.replace(hour=0)
    end = start + count * step
    req = request_window(fmt(start), fmt(end), interval)
    bars = []
    for i in range(count):
        open_ms = int((start + i * step).timestamp() * 1000)
        bars.append([open_ms, "100.0", "111.0", "99.0", "110.0", "3.0",
                     open_ms + int(step.total_seconds()*1000) - 1,
                     "312.0", 5, "1.0", "104.0", "0"])
    return req, bars, fmt(end + timedelta(minutes=3))

def inspect(req, bars, received):
    return inspect_response(json.dumps(bars, separators=(",", ":")).encode(),
                            req, received_at_utc=received)

class ForwardPriceBinanceUsdtCandidateTests(unittest.TestCase):
    def test_exact_public_spot_usdt_not_usd(self):
        req, _, _ = sample()
        self.assertEqual(req["symbol"], "BTCUSDT")
        self.assertEqual(req["quote"], "USDT")
        self.assertEqual(req["provider"], "BINANCE")
        self.assertFalse(req["requires_api_key"])
        self.assertFalse(req["usd_equivalent_assumed"])
        self.assertEqual(req["contract"], REQUEST_CONTRACT)
        url = urlparse(req["url"])
        self.assertTrue(req["url"].startswith(BASE+"?"))
        pars = parse_qs(url.query)
        self.assertEqual(pars["symbol"], ["BTCUSDT"])
        self.assertEqual(pars["interval"], ["1h"])
        self.assertEqual(pars["limit"], ["3"])
        self.assertEqual(int(pars["endTime"][0]), int(pars["startTime"][0]) + 3*3600000-1)

    def test_valid_hourly_is_metadata_only(self):
        req, bars, received = sample()
        before = copy.deepcopy(bars)
        result = inspect(req, bars, received)
        self.assertEqual(result["contract"], CONTRACT)
        self.assertEqual(result["status"], "RESEARCH_CAPTURE_ONLY_NOT_ADMITTED")
        self.assertEqual(result["quote"], "USDT")
        self.assertEqual(result["verified_closed_candles"], 3)
        for flag in ("forecast_issued", "source_admitted", "original_scoring_eligible",
                     "public_price_eligible", "historical_provider_first_known_verified",
                     "versioned_collector_verified", "independent_recovery_verified",
                     "portfolio_action", "usd_fx_conversion_performed", "usd_equivalent_assumed"):
            self.assertFalse(result[flag], flag)
        self.assertEqual(bars, before)
        self.assertNotIn("111.0", str(result))
        self.assertNotIn("110.0", str(result))

    def test_valid_daily_300_candles_research_only(self):
        req, bars, received = sample(300, "1d")
        result = inspect(req, bars, received)
        self.assertEqual(result["verified_closed_candles"], 300)
        self.assertFalse(result["source_admitted"])

    def test_max_1000_and_excess_1001_rejected(self):
        req, bars, received = sample(1000, "1h")
        self.assertEqual(inspect(req, bars, received)["verified_closed_candles"], 1000)
        with self.assertRaisesRegex(ValueError, "LIMIT_OR_WINDOW"):
            sample(1001, "1h")

    def test_invalid_interval_alignment_and_timestamp_rejected(self):
        for args in (
            (fmt(T0), fmt(T0), "1h"),
            (fmt(T0), fmt(T0 + timedelta(days=1)), "4h"),
            (fmt(T0 + timedelta(minutes=1)), fmt(T0 + timedelta(hours=3, minutes=1)), "1h"),
            (fmt(T0), fmt(T0 + timedelta(minutes=90)), "1h"),
            ("2026-10-25T10:00:00+00:00", fmt(T0+timedelta(hours=2)), "1h"),
            ("bad", fmt(T0+timedelta(hours=1)), "1h"),
        ):
            with self.subTest(args=args), self.assertRaises(ValueError):
                request_window(*args)

    def test_reject_request_spoof_usd_source_and_self_admission(self):
        req, bars, received = sample()
        for key, value in (
            ("symbol", "BTCUSD"), ("quote", "USD"), ("provider", "OTHER"),
            ("market", "FUTURES"), ("url", "https://evil.invalid/path"),
            ("requires_api_key", True), ("usd_equivalent_assumed", True),
            ("source_admitted", True), ("forecast_issued", True),
            ("expected_candles", 6),
        ):
            with self.subTest(key=key):
                changed = dict(req); changed[key] = value
                with self.assertRaisesRegex(ValueError, "IDENTITY_OR_AUTHORITY_CONFLICT"):
                    inspect(changed, bars, received)

    def test_reject_before_last_candle_closes(self):
        req, bars, _ = sample()
        with self.assertRaisesRegex(ValueError, "BEFORE_CANDLE_WINDOW_CLOSED"):
            inspect(req, bars, fmt(T0+timedelta(hours=2, minutes=59)))

    def test_reject_missing_and_duplicate_candles(self):
        req, bars, received = sample()
        with self.assertRaisesRegex(ValueError, "COUNT_OR_GAP"):
            inspect(req, bars[:-1], received)
        modified = copy.deepcopy(bars)
        modified[1][0] = modified[0][0]
        modified[1][6] = modified[0][6]
        with self.assertRaisesRegex(ValueError, "NONCONTIGUOUS_OR_DUPLICATED"):
            inspect(req, modified, received)

    def test_reject_shifted_time_or_wrong_close_millisecond(self):
        req, bars, received = sample()
        moved = copy.deepcopy(bars)
        moved[-1][0] += 3600000
        moved[-1][6] += 3600000
        with self.assertRaisesRegex(ValueError, "OUTSIDE_CLOSED_WINDOW"):
            inspect(req, moved, received)
        broken = copy.deepcopy(bars)
        broken[0][6] += 1
        with self.assertRaisesRegex(ValueError, "OUTSIDE_CLOSED_WINDOW"):
            inspect(req, broken, received)

    def test_unordered_but_complete_candles_pass(self):
        req, bars, received = sample()
        self.assertEqual(inspect(req, list(reversed(bars)), received)["verified_closed_candles"], 3)

    def test_wrong_ohlc_and_bad_numbers_fail(self):
        req, bars, received = sample()
        for pos, value in ((3, "120"), (2, "95"), (4, "NaN"),
                           (4, "Infinity"), (5, "-1.0"), (7, "1e999"),
                           (9, "nan"), (10, "abc")):
            with self.subTest(pos=pos,value=value):
                modified = copy.deepcopy(bars)
                modified[0][pos] = value
                with self.assertRaises(ValueError):
                    inspect(req, modified, received)

    def test_boolean_tradecount_rejected(self):
        req, bars, received = sample()
        bars[0][8] = True
        with self.assertRaisesRegex(ValueError, "TRADE_COUNT"):
            inspect(req, bars, received)

    def test_wrong_schema_provider_error_and_nonarray_rejected(self):
        req, bars, received = sample()
        for payload in ({"code":-1003,"msg":"Too many requests"}, {"candles":bars}, None, [],
                        [row[:-1] for row in bars]):
            with self.subTest(payload_type=str(type(payload))):
                with self.assertRaises(ValueError):
                    inspect(req, payload, received)

    def test_bad_json_and_raw_type_rejected(self):
        req, _, received = sample()
        for raw in (b"{bad", b"", "not bytes", b"[NaN]", b"\xff"):
            with self.subTest(raw=repr(raw)[:10]), self.assertRaises(ValueError):
                inspect_response(raw,req,received_at_utc=received)

    def test_missing_request_provenance_rejected(self):
        req, bars, received = sample()
        for key in ("contract", "interval", "window_end_utc"):
            modified = dict(req); del modified[key]
            with self.subTest(key=key),self.assertRaises(ValueError):
                inspect(modified,bars,received)

    def test_empty_and_bad_candle_numeric_are_rejected(self):
        req, bars, received = sample()
        bad = copy.deepcopy(bars); bad[0][1] = ""
        with self.assertRaises(ValueError):
            inspect(req,bad,received)

if __name__ == "__main__":
    unittest.main()
