"""Synthetic fail-closed Binance native BTCUSDT SOURCE (never USD) tests.

This verifies response parsing only, not authority for price forecast publication.
"""
from __future__ import annotations

import copy
import json
import unittest
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlsplit

from scripts.learning.forward_price_public_api_candidate import (
    BINANCE_RESEARCH_CONTRACT, BINANCE_REQUEST_CONTRACT,
    BINANCE_SPOT_CANDLES_URL, binance_request_window,
    inspect_binance_spot_response,
)

START = "2026-10-20T00:00:00Z"
END = "2026-10-20T03:00:00Z"
ASOF = "2026-10-20T03:00:01Z"


def req():
    return binance_request_window(START, END, "1h")


def bars():
    begin = int(datetime(2026, 10, 20, tzinfo=timezone.utc).timestamp()) * 1000
    return [
        [
            begin + n * 3600_000,
            "100", "110", "90", str(101 + n),
            "0.12",
            begin + (n + 1) * 3600_000 - 1,
            "12.3",
            12, "0.09", "9.0", "0"
        ]
        for n in range(3)
    ]


def raw(data):
    return json.dumps(data, separators=(",", ":")).encode()


class BinanceNativeUsdtSourceTests(unittest.TestCase):
    def setUp(self):
        self.request = req()
        self.candles = bars()

    def invalid(self, mutate=None, *, request=None, asof=ASOF, data=None):
        payload = copy.deepcopy(self.candles if data is None else data)
        if mutate:
            mutate(payload)
        with self.assertRaises(ValueError):
            inspect_binance_spot_response(
                raw(payload), self.request if request is None else request,
                received_at_utc=asof)

    def test_public_spot_symbol_usdt_exact(self):
        r = self.request
        self.assertEqual(r["contract"], BINANCE_REQUEST_CONTRACT)
        self.assertEqual(r["symbol"], "BTCUSDT")
        self.assertEqual(r["quote"], "USDT")
        self.assertEqual(r["market"], "SPOT")
        self.assertEqual(r["source"], "PUBLIC_SPOT_MARKET_DATA_ONLY")
        self.assertFalse(r["requires_api_key"])
        self.assertFalse(r["forecast_issued"])
        self.assertFalse(r["source_admitted"])
        parts = urlsplit(r["url"])
        self.assertEqual(parts.scheme + "://" + parts.netloc + parts.path,
                         BINANCE_SPOT_CANDLES_URL)
        params = parse_qs(parts.query)
        self.assertEqual(params["symbol"], ["BTCUSDT"])
        self.assertEqual(params["interval"], ["1h"])
        self.assertEqual(params["limit"], ["3"])
        self.assertEqual(params["startTime"], [str(self.candles[0][0])])
        self.assertEqual(params["endTime"], [str(self.candles[-1][6])])

    def test_one_day_window_and_1000_buckets(self):
        one = binance_request_window(
            "2026-10-20T00:00:00Z", "2026-10-21T00:00:00Z", "1d")
        self.assertEqual(one["requested_candles"], 1)
        self.assertEqual(one["quote"], "USDT")
        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        for interval, delta in (("1h", timedelta(hours=1000)),
                                ("1d", timedelta(days=1000))):
            end = start + delta
            spec = binance_request_window(
                start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                end.strftime("%Y-%m-%dT%H:%M:%SZ"), interval)
            self.assertEqual(spec["requested_candles"], 1000)
        with self.assertRaises(ValueError):
            binance_request_window("2024-01-01T00:00:00Z",
                                   "2026-10-02T00:00:00Z", "1d")

    def test_reject_wrong_timezone_or_non_utc(self):
        for t in ("2026-10-20 00:00:00", "2026-10-20T00:00:00+00:00",
                  "2026-02-30T00:00:00Z", "2026-10-20T00:00:00.000Z",
                  None, True, 3):
            with self.subTest(t=t), self.assertRaises(ValueError):
                binance_request_window(t, END, "1h")

    def test_reject_unaligned_empty_or_unsupported_interval(self):
        for left, right in (
            ("2026-10-20T00:01:00Z", END),
            (START, "2026-10-20T03:05:00Z"),
            (START, START), (END, START),
            (START, "2026-10-20T02:30:00Z"),
        ):
            with self.subTest(left=left, right=right), self.assertRaises(ValueError):
                binance_request_window(left, right, "1h")
        for interval in ("1m", "4h", "3d", "", "1W", None):
            with self.subTest(interval=interval), self.assertRaises(ValueError):
                binance_request_window(START, END, interval)

    def test_complete_usdt_candles_yield_only_metadata(self):
        original = copy.deepcopy(self.candles)
        result = inspect_binance_spot_response(
            raw(self.candles), self.request, received_at_utc=ASOF)
        self.assertEqual(result["contract"], BINANCE_RESEARCH_CONTRACT)
        self.assertEqual(result["source"], "PUBLIC_SPOT_MARKET_DATA_ONLY")
        self.assertEqual(result["quote"], "USDT")
        self.assertEqual(result["symbol"], "BTCUSDT")
        self.assertEqual(result["complete_closed_candles"], 3)
        self.assertEqual(result["gap_count"], 0)
        self.assertEqual(result["source_raw_bytes"], len(raw(self.candles)))
        self.assertEqual(len(result["source_raw_sha256"]), 64)
        self.assertEqual(original, self.candles)
        self.assertFalse(result["source_admitted"])
        self.assertFalse(result["usd_equivalence_assumed"])
        self.assertFalse(result["forecast_issued"])
        self.assertFalse(result["eligible_for_public_price"])
        self.assertFalse(result["eligible_for_canonical_score"])
        self.assertFalse(result["portfolio_action"])
        self.assertFalse(result["historical_provider_first_known_verified"])
        self.assertNotIn("candles", result)
        self.assertNotIn("low_usdt", result)
        self.assertNotIn("close_usd", result)

    def test_reversed_spot_candles_accepted(self):
        self.candles.reverse()
        result = inspect_binance_spot_response(
            raw(self.candles), self.request, received_at_utc=ASOF)
        self.assertEqual(result["complete_closed_candles"], 3)

    def test_zero_volume_and_zero_trades_allowed(self):
        self.candles[0][5] = "0"
        self.candles[0][7] = "0"
        self.candles[0][8] = 0
        self.candles[0][9] = "0"
        self.candles[0][10] = "0"
        self.assertEqual(inspect_binance_spot_response(
            raw(self.candles), self.request, received_at_utc=ASOF)["gap_count"], 0)

    def test_reject_source_or_quote_spoofing(self):
        for key, value in (
            ("quote", "USD"), ("symbol", "BTCUSD"), ("symbol", "BTCUSDC"),
            ("market", "FUTURES"), ("source", "OKX_MARK"),
            ("provider", "KRAKEN"), ("url", "https://evil.example/candle"),
            ("contract", "COINBASE_PUBLIC_BTC_USD_REQUEST_v1"),
            ("source_admitted", True), ("forecast_issued", True),
            ("requires_api_key", True), ("requested_candles", 200),
        ):
            with self.subTest(key=key):
                mutated = dict(self.request)
                mutated[key] = value
                self.invalid(request=mutated)

    def test_reject_wrong_response_schema_or_futures_tuples(self):
        self.invalid(data={"candles": self.candles})
        self.invalid(data={"code": -1021})
        self.invalid(data=[])
        self.invalid(lambda d: d[0].pop())
        self.invalid(lambda d: d[0].append("surprise"))
        self.invalid(lambda d: d.pop())
        self.invalid(lambda d: d[0].__setitem__(0, "not epoch ms"))
        self.invalid(lambda d: d[0].__setitem__(0, True))
        self.invalid(lambda d: d[0].__setitem__(6, "closed"))
        self.invalid(lambda d: d[0].__setitem__(6, False))

    def test_reject_gap_duplicate_or_misaligned_candles(self):
        self.invalid(lambda d: d[1].__setitem__(0, d[0][0]))
        self.invalid(lambda d: d[0].__setitem__(0, d[0][0] + 60_000))
        self.invalid(lambda d: d[2].__setitem__(0, d[2][0] + 3600_000))
        self.invalid(lambda d: d[1].__setitem__(6, d[1][6] + 1))
        self.invalid(lambda d: d[1].__setitem__(6, d[1][6] - 60_000))

    def test_reject_future_or_unclosed_settlement(self):
        self.invalid(asof="2026-10-20T02:59:59Z")
        self.invalid(asof="2026-10-20T03:00:00+00:00")
        self.invalid(lambda d: d[2].__setitem__(6, d[2][0] + 3600_000))
        self.invalid(lambda d: d[2].__setitem__(0, d[2][0] + 3600_000))

    def test_reject_bad_price_extrema_negative_volume_nan(self):
        for index, value in (
            (1, "0"), (1, "120"), (2, "0"),
            (2, "90"), (3, "111"), (4, "-1"),
            (4, "NaN"), (4, "Infinity"), (4, "1e5"),
            (4, "0"), (4, 100), (4, True),
            (5, "-1"), (7, "NaN"), (9, "-2"),
            (10, "inf"), (11, 0), (8, "-1"), (8, False),
        ):
            with self.subTest(index=index,value=value):
                self.invalid(lambda d, index=index, value=value:
                             d[0].__setitem__(index, value))

    def test_valid_daily_closed_candles(self):
        request = binance_request_window(
            "2026-10-20T00:00:00Z", "2026-10-22T00:00:00Z", "1d")
        t = int(datetime(2026, 10, 20, tzinfo=timezone.utc).timestamp()) * 1000
        d = [[t+n*86400_000, "100", "110", "90", "101", "1",
              t+(n+1)*86400_000-1, "101", 8, "0.5", "50", "0"]
             for n in range(2)]
        x = inspect_binance_spot_response(raw(d), request,
                received_at_utc="2026-10-22T00:01:00Z")
        self.assertEqual(x["complete_closed_candles"], 2)
        self.assertEqual(x["quote"], "USDT")

    def test_reject_nan_json_duplicate_keys_invalid_bytes(self):
        for payload in (b"", b"{", b'[NaN]', b'[Infinity]',
                        b'{"a":1,"a":2}', b"x"*750001):
            with self.subTest(length=len(payload)), self.assertRaises(ValueError):
                inspect_binance_spot_response(payload, self.request,
                                               received_at_utc=ASOF)
        with self.assertRaises(ValueError):
            inspect_binance_spot_response("bad", self.request, received_at_utc=ASOF)

    def test_prospective_admission_cannot_be_inferred_from_source_shape(self):
        res = inspect_binance_spot_response(raw(self.candles), self.request,
                                            received_at_utc=ASOF)
        self.assertTrue(res["receiver_first_observed_only"])
        self.assertTrue(res["separate_private_manifest_required"])
        self.assertFalse(res["versioned_collector_verified"])
        self.assertFalse(res["historical_replay_allowed"])
        self.assertFalse(res["source_admitted"])
        self.assertFalse(res["usd_equivalence_assumed"])


if __name__ == "__main__":
    unittest.main()
