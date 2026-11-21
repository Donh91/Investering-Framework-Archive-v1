"""No-network regression for 2x30s empty recovery and truthful live state."""
import json
import unittest
from unittest import mock

from scripts.data_terminal import cfgi_owner_collector as C
from scripts.data_terminal import top100_breadth_owner_collector as B
from scripts.data_ping.auto_market_state import (
    derivatives_source_health, live_altseason_has_observation, sentiment_source_health,
)

COMPLETE = {"MARKET": {"score": 22.5, "classification": "Fear", "owner_status": "PASS", "stale": False},
            "BTC": {"score": 15, "classification": "Extreme Fear", "owner_status": "PASS", "stale": False},
            "ETH": {"score": 17.5, "classification": "Extreme Fear", "owner_status": "PASS", "stale": False}}


def cfgi(symbols):
    return {"cfgi": {"symbols": symbols}}


def swaps(btc, eth):
    return {"BTC-USDT-SWAP": {"funding": {"funding_rate": btc}}, "ETH-USDT-SWAP": {"funding": {"funding_rate": eth}}}


class Response:
    def __init__(self, raw):
        self.raw = raw
        self.headers = {"X-Credits-Used": "2", "X-Credits-Remaining": "98"}
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def read(self): return self.raw


class EmptyRecoveryTests(unittest.TestCase):
    def test_cfgi_empty_twice_then_valid_uses_three_attempts_and_30s_waits(self):
        responses = [Response(b'{"data":[]}'), Response(b""), Response(b'{"data":[{"symbol":"BTC","score":0}]}')]
        with mock.patch.object(C.urllib.request, "urlopen", side_effect=responses) as open_call:
            with mock.patch.object(C.time, "sleep") as sleep:
                value, used, remaining, count, samples = C.read_with_empty_retries(mock.Mock())
        self.assertEqual(count, 3)
        self.assertEqual(sleep.call_args_list, [mock.call(30), mock.call(30)])
        self.assertEqual(open_call.call_count, 3)
        self.assertEqual(value["data"][0]["score"], 0)
        self.assertEqual(len(samples), 3)

    def test_cfgi_exhausts_after_three_empty_not_unbounded_or_fake_pass(self):
        with mock.patch.object(C.urllib.request, "urlopen", side_effect=[Response(b"")] * 3) as opened:
            with mock.patch.object(C.time, "sleep") as sleep:
                with self.assertRaisesRegex(SystemExit, "cfgi_empty_after_2_retries"):
                    C.read_with_empty_retries(mock.Mock())
        self.assertEqual(opened.call_count, 3)
        self.assertEqual(sleep.call_count, 2)

    def test_cfgi_bad_schema_is_not_empty_retry(self):
        with mock.patch.object(C.urllib.request, "urlopen", return_value=Response(b'{"data":{}}')) as opened:
            with mock.patch.object(C.time, "sleep") as sleep:
                with self.assertRaisesRegex(SystemExit, "CFGI_SCHEMA_DRIFT"):
                    C.read_with_empty_retries(mock.Mock())
        self.assertEqual(opened.call_count, 1)
        sleep.assert_not_called()

    def test_altseason_empty_retry_only_for_empty_public_html(self):
        empty = B.E("EMPTY_RESPONSE", "empty response")
        with mock.patch.object(B, "fetch", side_effect=[empty, empty, b"ok"]) as fetch:
            with mock.patch.object(B.time, "sleep") as sleep:
                body = B.fetch_optional_html_with_empty_retry(B.BLOCKCHAINCENTER_URL)
        self.assertEqual(body, b"ok")
        self.assertEqual(fetch.call_count, 3)
        self.assertEqual(sleep.call_args_list, [mock.call(30), mock.call(30)])

    def test_altseason_http_error_not_retried(self):
        with mock.patch.object(B, "fetch", side_effect=B.E("HTTP_ERROR", "quota")) as fetch:
            with mock.patch.object(B.time, "sleep") as sleep:
                with self.assertRaises(B.E):
                    B.fetch_optional_html_with_empty_retry(B.COINMARKETCAP_URL)
        self.assertEqual(fetch.call_count, 1)
        sleep.assert_not_called()

    def test_empty_or_metadata_shell_never_passes_market_state(self):
        # Sentiment reuses #2142's single sentiment_source_health(); #2153 adds the stale exclusion.
        self.assertEqual(sentiment_source_health(cfgi(COMPLETE))["status"], "PASS")
        self.assertEqual(sentiment_source_health(cfgi({}))["status"], "UNAVAILABLE")
        for symbol in ("MARKET", "BTC", "ETH"):
            for change in ({"owner_status": "STALE"}, {"stale": True}, {"score": None}):
                with self.subTest(symbol=symbol, change=change):
                    rows = json.loads(json.dumps(COMPLETE))
                    rows[symbol].update(change)
                    self.assertEqual(sentiment_source_health(cfgi(rows))["status"], "UNAVAILABLE")
        legacy = {k: {"score": v["score"], "classification": v["classification"]} for k, v in COMPLETE.items()}
        self.assertEqual(sentiment_source_health(cfgi(legacy))["status"], "PASS")  # #2142 fixtures stay valid
        self.assertFalse(live_altseason_has_observation({"blockchaincenter_altcoin_season":{"status":"PASS","horizons":{}}}))
        self.assertFalse(live_altseason_has_observation({"coinmarketcap_altcoin_season":{"status":"PASS","published_score":None}}))
        self.assertTrue(live_altseason_has_observation({"blockchaincenter_altcoin_season":{"status":"PASS","horizons":{"90":{"published_score":0}}}}))
        self.assertFalse(live_altseason_has_observation({"coinmarketcap_altcoin_season":{"status":"PASS","published_score":0}}))

    def test_altseason_health_tracks_specific_required_source_and_horizon(self):
        cmc = {"status": "PASS", "published_score": 58}
        for bc in (
            {"status": "DEGRADED", "horizons": {}},
            {"status": "PASS", "horizons": {"30": {"published_score": 39}}},
            {"status": "DEGRADED", "horizons": {"90": {"published_score": 49}}},
        ):
            self.assertFalse(live_altseason_has_observation({
                "blockchaincenter_altcoin_season": bc, "coinmarketcap_altcoin_season": cmc}))
        for score in (None, True, "49", float("nan"), float("inf"), -1, 101):
            self.assertFalse(live_altseason_has_observation({
                "blockchaincenter_altcoin_season": {"status": "PASS", "horizons": {"90": {"published_score": score}}},
                "coinmarketcap_altcoin_season": cmc}))
        for score in (0, 49, 100):
            self.assertTrue(live_altseason_has_observation({
                "blockchaincenter_altcoin_season": {"status": "PASS", "horizons": {"90": {"published_score": score}}}}))

    def test_derivatives_truthy_wrapper_is_not_a_pass(self):  # WO-3, auto_market_state :598
        self.assertEqual(derivatives_source_health(swaps(-3.08e-05, -8.17e-05))["status"], "PASS")
        self.assertEqual(derivatives_source_health(swaps(0, 0))["status"], "PASS")  # a zero rate is a real observation
        for bad in ({}, {"BTC-USDT-SWAP": {}, "ETH-USDT-SWAP": {}}, swaps(-3e-05, None),
                    swaps(float("nan"), 1e-05), swaps(True, 1e-05), swaps("-3e-05", 1e-05), []):
            with self.subTest(bad=bad):
                health = derivatives_source_health(bad)
                self.assertEqual(health["status"], "UNAVAILABLE")
                self.assertEqual(health["classification"], "LIVE_ANCHOR_DERIVATIVES_FUNDING_REQUIRED_FIELDS_MISSING")


    def test_assemble_is_wired_to_all_three_completeness_checks(self):
        import inspect
        from scripts.data_ping import auto_market_state as A
        src = inspect.getsource(A.assemble)
        self.assertIn('health["derivatives"] = derivatives_source_health(derivatives)', src)
        self.assertIn('health["sentiment"] = sentiment_source_health(sentiment)', src)
        self.assertIn("live_altseason_has_observation(altseason)", src)
        self.assertNotIn('"PASS" if sentiment else', src)
        self.assertNotIn("and derivatives else", src)
        self.assertNotIn('"PASS" if altseason else', src)


if __name__ == "__main__":
    unittest.main()
