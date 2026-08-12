import datetime as dt
import tempfile
import unittest
from pathlib import Path

from scripts.daily_capture import pullback_forensics_collector as pfr


class PullbackForensicsTests(unittest.TestCase):
    def test_linear_contract_notional_uses_ctval_and_price(self):
        detail = {"sz": "10", "bkPx": "60000", "posSide": "long", "ts": "1", "instId": "BTC-USDT-SWAP"}
        meta = {"ctType": "linear", "ctVal": "0.01", "ctMult": "1", "ctValCcy": "BTC", "settleCcy": "USDT"}
        self.assertEqual(float(pfr.normalized_liquidation_notional_usd(detail, meta)), 6000.0)

    def test_inverse_contract_notional_does_not_multiply_price(self):
        detail = {"sz": "10", "bkPx": "60000", "posSide": "long", "ts": "1", "instId": "BTC-USD-SWAP"}
        meta = {"ctType": "inverse", "ctVal": "100", "ctMult": "1", "ctValCcy": "USD", "settleCcy": "BTC"}
        self.assertEqual(float(pfr.normalized_liquidation_notional_usd(detail, meta)), 1000.0)

    def test_missing_unit_metadata_fails_closed(self):
        detail = {"sz": "10", "bkPx": "60000", "posSide": "long", "ts": "1", "instId": "BTC-USDT-SWAP"}
        meta = {"ctType": "linear", "ctVal": "0.01", "ctMult": "", "ctValCcy": "BTC", "settleCcy": "USDT"}
        with self.assertRaisesRegex(ValueError, "missing_ctMult"):
            pfr.normalized_liquidation_notional_usd(detail, meta)

    def test_non_unit_contract_multiplier_requires_semantic_review(self):
        detail = {"sz": "10", "bkPx": "60000", "posSide": "long", "ts": "1", "instId": "BTC-USDT-SWAP"}
        meta = {"ctType": "linear", "ctVal": "0.01", "ctMult": "2", "ctValCcy": "BTC", "settleCcy": "USDT"}
        with self.assertRaisesRegex(ValueError, "unsupported_ctMult_requires_semantic_review"):
            pfr.normalized_liquidation_notional_usd(detail, meta)

    def test_event_id_is_stable_and_unit_sensitive(self):
        detail = {"sz": "10", "bkPx": "60000", "bkLoss": "1", "posSide": "long", "ts": "1000", "instId": "BTC-USDT-SWAP"}
        meta = {"ctType": "linear", "ctVal": "0.01", "ctMult": "1"}
        self.assertEqual(pfr.event_id(detail, meta), pfr.event_id(dict(detail), dict(meta)))
        meta2 = dict(meta)
        meta2["ctVal"] = "0.1"
        self.assertNotEqual(pfr.event_id(detail, meta), pfr.event_id(detail, meta2))

    def test_gzip_merge_deduplicates_event_ids(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            rows = [
                {"event_id": "a", "event_timestamp_utc": "2026-08-11T01:00:00Z", "event_timestamp_ms": 1, "pos_side": "long", "notional_usd": 1},
                {"event_id": "b", "event_timestamp_utc": "2026-08-11T02:00:00Z", "event_timestamp_ms": 2, "pos_side": "short", "notional_usd": 2},
            ]
            first = pfr.merge_events_by_day(root, rows)
            second = pfr.merge_events_by_day(
                root,
                rows + [{"event_id": "c", "event_timestamp_utc": "2026-08-11T03:00:00Z", "event_timestamp_ms": 3, "pos_side": "long", "notional_usd": 3}],
            )
            self.assertEqual(first["new_unique_events"], 2)
            self.assertEqual(second["new_unique_events"], 1)
            path = root / "liquidations/2026/08/11.jsonl.gz"
            self.assertEqual([row["event_id"] for row in pfr.read_gzip_jsonl(path)], ["a", "b", "c"])

    def test_load_events_since_uses_persisted_deduped_window(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            obs = dt.datetime(2026, 8, 12, 3, 0, tzinfo=dt.UTC)
            rows = [
                {
                    "event_id": "old",
                    "event_timestamp_utc": "2026-08-11T02:00:00Z",
                    "event_timestamp_ms": int(dt.datetime(2026, 8, 11, 2, tzinfo=dt.UTC).timestamp() * 1000),
                    "inst_id": "BTC-USDT-SWAP",
                    "pos_side": "long",
                    "notional_usd": 1,
                },
                {
                    "event_id": "in",
                    "event_timestamp_utc": "2026-08-11T04:00:00Z",
                    "event_timestamp_ms": int(dt.datetime(2026, 8, 11, 4, tzinfo=dt.UTC).timestamp() * 1000),
                    "inst_id": "BTC-USDT-SWAP",
                    "pos_side": "long",
                    "notional_usd": 2,
                },
                {
                    "event_id": "new",
                    "event_timestamp_utc": "2026-08-12T02:00:00Z",
                    "event_timestamp_ms": int(dt.datetime(2026, 8, 12, 2, tzinfo=dt.UTC).timestamp() * 1000),
                    "inst_id": "BTC-USDT-SWAP",
                    "pos_side": "short",
                    "notional_usd": 3,
                },
            ]
            pfr.merge_events_by_day(root, rows)
            got = pfr.load_events_since(root, obs, 24)
            self.assertEqual([row["event_id"] for row in got], ["in", "new"])

    def test_skew_is_explicitly_moneyness_not_25_delta_and_preserves_dte(self):
        obs = dt.datetime(2026, 8, 11, tzinfo=dt.UTC)
        expiry = int((obs + dt.timedelta(days=10)).timestamp() * 1000)
        instruments = {
            "result": [
                {"instrument_name": "BTC-X-90-P", "kind": "option", "expiration_timestamp": expiry, "strike": 90, "option_type": "put"},
                {"instrument_name": "BTC-X-110-C", "kind": "option", "expiration_timestamp": expiry, "strike": 110, "option_type": "call"},
                {"instrument_name": "BTC-X-100-C", "kind": "option", "expiration_timestamp": expiry, "strike": 100, "option_type": "call"},
            ]
        }
        summaries = {
            "result": [
                {"instrument_name": "BTC-X-90-P", "mark_iv": 60, "underlying_price": 100, "open_interest": 1},
                {"instrument_name": "BTC-X-110-C", "mark_iv": 50, "underlying_price": 100, "open_interest": 1},
                {"instrument_name": "BTC-X-100-C", "mark_iv": 52, "underlying_price": 100, "open_interest": 1},
            ]
        }
        result = pfr.build_moneyness_skew(summaries, instruments, obs)
        self.assertEqual(result["method"], "MONEYNESS_BUCKET_SKEW_NOT_25_DELTA")
        self.assertIn("NOT 25-delta", result["method_warning"])
        self.assertAlmostEqual(result["expiries_1_to_60d"][0]["days_to_expiry"], 10.0)
        self.assertEqual(result["expiries_1_to_60d"][0]["moneyness_skew_points"], 10.0)


if __name__ == "__main__":
    unittest.main()
