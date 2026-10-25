"""Adversarial synthetic-only Coinbase BTC/USD candidate contract suite.

No network calls, provider values, private source files, token or market issuance.
"""
from __future__ import annotations

import copy
import json
import unittest
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlsplit

from scripts.learning.forward_price_public_api_candidate import (
    CONTRACT, COINBASE_URL, GRANULARITIES, REQUEST_CONTRACT,
    existing_source_roles, inspect_candle_response, request_window,
)

START = "2026-10-20T00:00:00Z"
END = "2026-10-20T03:00:00Z"
ASOF = "2026-10-20T03:00:17Z"


def hourly_request():
    return request_window(START, END, "ONE_HOUR")


def hourly_body():
    start = int(datetime(2026, 10, 20, tzinfo=timezone.utc).timestamp())
    candles = []
    for n in range(3):
        point = str(100 + n)
        candles.append({
            "start": str(start + n * 3600), "low": "90",
            "high": "110", "open": point, "close": point,
            "volume": "10.5",
        })
    return {"candles": candles}


def raw(body):
    return json.dumps(body, separators=(",", ":")).encode()


def capture_metadata():
    return {
        "contract": "FORWARD_PRICE_SOURCE_CUSTODY_PUBLIC_BINDING_v1",
        "provider": "KRAKEN", "asset": "BTC", "quote": "USD",
        "instrument_id": "XXBTZUSD", "status": "CAPTURED_NOT_ADMITTED",
        "source_admitted": False, "forecast_issued": False,
    }


def pointers():
    hourly = {"contract": "HOURLY_SEQUENCE_LATEST_POINTER_v2_2",
              "status": "COMPLETE", "spot_complete_hours": 26}
    weekly = {"contract": "WEEKLY_MARKET_CLOSE_POINTER_v3", "status": "PASS",
              "source_base_url": "https://data-api.binance.vision",
              "final": True, "completeness": "COMPLETE"}
    return hourly, weekly, capture_metadata()


class ForwardPricePublicApiCandidateTests(unittest.TestCase):
    def setUp(self):
        self.req = hourly_request()
        self.fixture = hourly_body()

    def check_bad(self, changed=None, *, requested=None, timestamp=ASOF, payload=None):
        doc = copy.deepcopy(self.fixture if payload is None else payload)
        if changed is not None:
            changed(doc)
        with self.assertRaises(ValueError):
            inspect_candle_response(raw(doc), self.req if requested is None else requested,
                                    received_at_utc=timestamp)

    def test_public_request_is_usd_btc_without_api_key(self):
        data = self.req
        self.assertEqual(data["contract"], REQUEST_CONTRACT)
        self.assertEqual(data["product_id"], "BTC-USD")
        self.assertEqual(data["quote"], "USD")
        self.assertFalse(data["requires_api_key"])
        self.assertFalse(data["source_admitted"])
        self.assertFalse(data["forecast_issued"])
        uri = urlsplit(data["url"])
        self.assertEqual(uri.scheme + "://" + uri.netloc + uri.path, COINBASE_URL)
        self.assertEqual(parse_qs(uri.query)["granularity"], ["ONE_HOUR"])
        self.assertEqual(parse_qs(uri.query)["limit"], ["3"])

    def test_daily_one_day_and_350_bucket_limit(self):
        x = request_window("2026-10-20T00:00:00Z", "2026-10-21T00:00:00Z", "ONE_DAY")
        self.assertEqual(x["requested_candles"], 1)
        for grain, delta in (("ONE_HOUR", timedelta(hours=350)),
                             ("ONE_DAY", timedelta(days=350))):
            start = datetime(2026, 1, 1, tzinfo=timezone.utc)
            end = start + delta
            x = request_window(start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                               end.strftime("%Y-%m-%dT%H:%M:%SZ"), grain)
            self.assertEqual(x["requested_candles"], 350)
        with self.assertRaises(ValueError):
            request_window("2026-01-01T00:00:00Z", "2026-12-18T00:00:00Z", "ONE_DAY")

    def test_reject_off_hour_start_and_unaligned_utc(self):
        for st, end in (("2026-10-20T00:01:00Z", END),
                        (START, "2026-10-20T03:01:00Z"),
                        (END, START), (START, START)):
            with self.subTest(st=st, end=end), self.assertRaises(ValueError):
                request_window(st, end, "ONE_HOUR")

    def test_reject_non_explicit_utc_and_unsupported_horizons(self):
        for st in ("2026-10-20 00:00:00", "2026-10-20T00:00:00+00:00",
                   "2026-02-30T00:00:00Z", None, 42):
            with self.subTest(st=st), self.assertRaises(ValueError):
                request_window(st, END, "ONE_HOUR")
        for grain in ("FIVE_MINUTE", "FOUR_HOUR", "ONE_WEEK", "", None):
            with self.subTest(grain=grain), self.assertRaises(ValueError):
                request_window(START, END, grain)

    def test_valid_three_completed_hourly_candles_metadata_only(self):
        original = copy.deepcopy(self.fixture)
        evidence = inspect_candle_response(raw(self.fixture), self.req, received_at_utc=ASOF)
        self.assertEqual(self.fixture, original)
        self.assertEqual(evidence["contract"], CONTRACT)
        self.assertEqual(evidence["complete_closed_candles"], 3)
        self.assertEqual(evidence["gap_count"], 0)
        self.assertEqual(evidence["source_raw_bytes"], len(raw(self.fixture)))
        self.assertEqual(len(evidence["source_raw_sha256"]), 64)
        self.assertEqual(evidence["quote"], "USD")
        self.assertFalse(evidence["historical_provider_first_known_verified"])
        self.assertFalse(evidence["source_admitted"])
        self.assertFalse(evidence["eligible_for_public_price"])
        self.assertFalse(evidence["forecast_issued"])
        self.assertFalse(evidence["portfolio_action"])
        self.assertNotIn("low_usd", evidence)
        self.assertNotIn("close_usd", evidence)
        self.assertNotIn("candles", evidence)

    def test_reversed_api_candle_order_is_valid(self):
        self.fixture["candles"].reverse()
        self.assertEqual(inspect_candle_response(raw(self.fixture), self.req,
                         received_at_utc=ASOF)["complete_closed_candles"], 3)

    def test_accept_realistic_string_prices_with_zero_volume(self):
        self.fixture["candles"][0].update(open="83001.25", close="83001.25",
                                           low="82000", high="84000", volume="0")
        self.assertEqual(inspect_candle_response(raw(self.fixture), self.req,
                         received_at_utc=ASOF)["status"],
                         "CAPTURE_VALIDATED_SOURCE_NOT_ADMITTED")

    def test_reject_malformed_or_extra_schema(self):
        for value in ({}, {"candles": None}, {"candles": []},
                      {"candles": self.fixture["candles"], "source_admitted": True},
                      {"error": "expired"}, []):
            with self.subTest(value=str(value)[:40]):
                self.check_bad(payload=value)
        self.check_bad(lambda d: d["candles"][0].update(quote="USDT"))
        self.check_bad(lambda d: d["candles"][0].pop("volume"))

    def test_reject_mismatched_api_request_authority(self):
        for field, value in (("quote", "USDT"), ("asset", "ETH"),
                             ("product_id", "BTC-USDT"), ("source_admitted", True),
                             ("requires_api_key", True), ("forecast_issued", True),
                             ("provider", "KRAKEN"),
                             ("url", "https://evil.example/candles"),
                             ("requested_candles", 300)):
            with self.subTest(field=field):
                v = dict(self.req)
                v[field] = value
                self.check_bad(requested=v)
        with self.assertRaises(ValueError):
            inspect_candle_response(raw(self.fixture), [], received_at_utc=ASOF)

    def test_reject_candle_missing_gap_duplicated_time(self):
        self.check_bad(lambda d: d["candles"].pop())
        self.check_bad(lambda d: d["candles"][1].update(start=d["candles"][0]["start"]))
        self.check_bad(lambda d: d["candles"][1].update(start="0"))
        self.check_bad(lambda d: d["candles"][1].update(start="bad"))
        self.check_bad(lambda d: d["candles"][1].update(start=0))

    def test_reject_partial_or_future_candle_and_early_receiver(self):
        self.check_bad(timestamp="2026-10-20T02:59:59Z")
        self.check_bad(timestamp="2026-10-20T03:00:00+00:00")
        self.check_bad(lambda d: d["candles"][2].update(start=str(
            int(d["candles"][2]["start"]) + 3600)))
        self.check_bad(lambda d: d["candles"][2].update(start=str(
            int(d["candles"][2]["start"]) + 60)))

    def test_reject_ohlc_inversion_and_nonfinite(self):
        for key, value in (("open", "120"), ("high", "89"), ("low", "111"),
                           ("close", "1000000"), ("volume", "-0.1"),
                           ("close", "NaN"), ("close", "Infinity"),
                           ("close", True), ("close", 99), ("close", "1e5"),
                           ("close", "0"), ("open", "-1"), ("high", "")):
            with self.subTest(key=key, value=value):
                self.check_bad(lambda d, key=key, value=value: d["candles"][0].update({key: value}))

    def test_reject_duplicate_json_keys_in_provider_response(self):
        invalid = b'{"candles":[],"candles":[]}'
        with self.assertRaises(ValueError):
            inspect_candle_response(invalid, self.req, received_at_utc=ASOF)
        invalid = b'{"candles":[{"start":"1","start":"2"}]}'
        with self.assertRaises(ValueError):
            inspect_candle_response(invalid, self.req, received_at_utc=ASOF)

    def test_reject_invalid_json_raw_bytes_and_nan_json(self):
        for payload in (b"", b"{", b'{"candles":NaN}', b'{"candles":Infinity}', b"x" * 500001):
            with self.subTest(size=len(payload)), self.assertRaises(ValueError):
                inspect_candle_response(payload, self.req, received_at_utc=ASOF)
        with self.assertRaises(ValueError):
            inspect_candle_response("not bytes", self.req, received_at_utc=ASOF)

    def test_daily_three_complete_candles(self):
        r = request_window("2026-10-20T00:00:00Z", "2026-10-23T00:00:00Z", "ONE_DAY")
        data = {"candles": []}
        t0 = int(datetime(2026, 10, 20, tzinfo=timezone.utc).timestamp())
        for n in range(3):
            data["candles"].append({
                "start": str(t0+n*86400), "low": "90", "high": "110",
                "open": "100", "close": "100", "volume": "0"
            })
        evidence = inspect_candle_response(raw(data), r,
                                           received_at_utc="2026-10-23T00:01:00Z")
        self.assertEqual(evidence["complete_closed_candles"], 3)
        self.assertEqual(evidence["quote"], "USD")

    def test_source_roles_require_exact_existing_contracts(self):
        h, w, k = pointers()
        x = existing_source_roles(h, w, k)
        self.assertIsNone(x["approved_forecast_price_owner"])
        self.assertEqual([r["id"] for r in x["sources"]],
                         ["EXISTING_BINANCE_SPOT", "EXISTING_KRAKEN_CAPTURE",
                          "COINBASE_PUBLIC_API_CANDIDATE"])
        for row in x["sources"]:
            self.assertIs(row["eligible_for_usd_priced_forecast"], False)
        self.assertEqual(x["sources"][0]["quote"], "USDT")
        self.assertEqual(x["sources"][1]["quote"], "USD")
        self.assertTrue(x["sources"][0]["navigation_hourly_source_present"])
        self.assertTrue(x["sources"][0]["settled_weekly_source_present"])
        self.assertTrue(x["sources"][1]["captured_metadata_matches"])
        self.assertFalse(x["sources"][2]["collector_deployed"])

    def test_tampered_or_missing_existing_pointers_are_not_promoted(self):
        h, w, k = pointers()
        for field, val in (("spot_complete_hours", 0), ("contract", "WRONG"),
                           ("status", "FAIL")):
            bad = dict(h); bad[field] = val
            x = existing_source_roles(bad, w, k)
            self.assertFalse(x["sources"][0]["navigation_hourly_source_present"])
        for field, val in (("final", False), ("source_base_url", "https://fake.example")):
            bad = dict(w); bad[field] = val
            x = existing_source_roles(h, bad, k)
            self.assertFalse(x["sources"][0]["settled_weekly_source_present"])
        for field, val in (("quote", "USDT"), ("source_admitted", True),
                           ("status", "ADMITTED"), ("forecast_issued", True)):
            bad = dict(k); bad[field] = val
            x = existing_source_roles(h, w, bad)
            self.assertFalse(x["sources"][1]["captured_metadata_matches"])
        for bad in ([], None, "invalid", 7):
            with self.subTest(v=bad), self.assertRaises(ValueError):
                existing_source_roles(bad, w, k)

    def test_private_values_and_keys_never_enter_return(self):
        h, w, k = pointers()
        k.update(api_key="secret_private_synthetic", low_usd=100, high_usd=300)
        answer = existing_source_roles(h, w, k)
        self.assertNotIn("secret_private_synthetic", str(answer))
        self.assertNotIn("low_usd", str(answer))
        self.assertNotIn("api_key", str(answer))
        r = self.req
        # Public metadata includes "requires_api_key": False; that label is not a credential.
        self.assertNotIn("api_key", r)
        self.assertFalse(r["requires_api_key"])
        self.assertNotIn("secret_private_synthetic", str(r))
        self.assertNotIn("api_key=", r["url"])

    def test_no_request_network_fetch_or_market_side_effect(self):
        h, w, k = pointers()
        self.assertFalse(existing_source_roles(h, w, k)["market_rule_change"])
        self.assertFalse(existing_source_roles(h, w, k)["portfolio_action"])
        result = inspect_candle_response(raw(self.fixture), self.req, received_at_utc=ASOF)
        self.assertTrue(result["receiver_first_observed_only"])
        self.assertFalse(result["versioned_collector_verified"])
        self.assertTrue(result["separate_private_manifest_required"])
        self.assertFalse(result["historical_replay_allowed"])
        self.assertFalse(result["eligible_for_canonical_score"])


if __name__ == "__main__":
    unittest.main()
