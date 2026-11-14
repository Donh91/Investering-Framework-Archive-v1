"""No-network regression for 2x30s empty recovery and truthful live state."""
import json
import unittest
from unittest import mock

from scripts.data_terminal import cfgi_owner_collector as C
from scripts.data_terminal import top100_breadth_owner_collector as B
from scripts.data_ping.auto_market_state import (
    live_cfgi_has_observation, live_altseason_has_observation,
)


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
        self.assertFalse(live_cfgi_has_observation({"cfgi":{"symbols":{}}}))
        self.assertFalse(live_cfgi_has_observation({"cfgi":{"symbols":{"BTC":{"owner_status":"PASS","score":None}}}}))
        self.assertFalse(live_cfgi_has_observation({"cfgi":{"symbols":{"BTC":{"owner_status":"STALE","score":55}}}}))
        self.assertTrue(live_cfgi_has_observation({"cfgi":{"symbols":{"BTC":{"owner_status":"PASS","score":0}}}}))
        self.assertFalse(live_altseason_has_observation({"blockchaincenter_altcoin_season":{"status":"PASS","horizons":{}}}))
        self.assertFalse(live_altseason_has_observation({"coinmarketcap_altcoin_season":{"status":"PASS","published_score":None}}))
        self.assertTrue(live_altseason_has_observation({"blockchaincenter_altcoin_season":{"status":"PASS","horizons":{"90":{"published_score":0}}}}))
        self.assertTrue(live_altseason_has_observation({"coinmarketcap_altcoin_season":{"status":"PASS","published_score":0}}))


if __name__ == "__main__":
    unittest.main()
