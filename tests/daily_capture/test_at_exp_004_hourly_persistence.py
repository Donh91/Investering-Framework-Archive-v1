import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from scripts.daily_capture import build_hourly_sequence as hourly


PROVENANCE_EXCLUSIONS = {"source_window_end_utc"}


class AtExp004HourlyPersistenceTests(unittest.TestCase):
    @staticmethod
    def candle(open_, close):
        high = max(open_, close) * 1.01
        low = min(open_, close) * 0.99
        return {
            "open": float(open_), "high": float(high), "low": float(low), "close": float(close),
            "volume": 10.0, "quote_volume": 1000.0, "trade_count": 10,
            "taker_buy_base_volume": 5.0, "taker_buy_quote_volume": 520.0,
            "taker_sell_quote_volume": 480.0, "taker_buy_quote_share": 0.52,
        }

    @staticmethod
    def panel(start, hours=8):
        spot = {symbol: {} for symbol in hourly.SPOT_SYMBOLS}
        oi = {symbol: {} for symbol, _, _ in hourly.DERIVATIVE_SYMBOLS}
        for i in range(hours):
            stamp = hourly.to_ms(start + timedelta(hours=i))
            spot["BTCUSDT"][stamp] = AtExp004HourlyPersistenceTests.candle(100 + i, 101 + i)
            spot["ETHUSDT"][stamp] = AtExp004HourlyPersistenceTests.candle(50 + i, 51 + i)
            spot["ETHBTC"][stamp] = AtExp004HourlyPersistenceTests.candle(0.05 + i * 0.001, 0.051 + i * 0.001)
            oi["BTCUSDT"][stamp] = {"oi": 1000.0 + i * 10, "value": 1.0, "source": "FIXTURE"}
            oi["ETHUSDT"][stamp] = {"oi": 500.0 + i * 5, "value": 1.0, "source": "FIXTURE"}
        return spot, oi

    @staticmethod
    def read_rows(root):
        rows = {}
        for path in root.rglob("*.csv"):
            with path.open(newline="", encoding="utf-8") as handle:
                for row in csv.DictReader(handle):
                    rows[row["timestamp_utc"]] = row
        return rows

    @staticmethod
    def direct_row(timestamp, quality="PASS", close="101", state="PRICE_UP_OI_UP"):
        value = {field: "" for field in hourly.FIELDS}
        value.update({
            "timestamp_utc": timestamp,
            "timestamp_copenhagen": timestamp,
            "source_window_end_utc": timestamp,
            "btc_close": close,
            "eth_close": close,
            "spot_status": "PASS" if quality == "PASS" else "PARTIAL",
            "derivatives_status": "PASS" if quality == "PASS" else "PARTIAL",
            "btc_return_1h_pct": "1" if quality == "PASS" else "",
            "eth_return_1h_pct": "1" if quality == "PASS" else "",
            "btc_oi_change_1h_pct": "1" if quality == "PASS" else "",
            "eth_oi_change_1h_pct": "1" if quality == "PASS" else "",
            "btc_price_oi_state": state if quality == "PASS" else "",
            "eth_price_oi_state": state if quality == "PASS" else "",
        })
        return value

    def test_missing_previous_close_never_uses_current_open_as_one_hour_return(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        spot, oi = self.panel(start, 1)
        rows = hourly.build_rows(start, start, spot, oi, {}, {}, "PASS", "PASS")
        row = rows[0]
        self.assertIsNone(row.get("btc_return_1h_pct"))
        self.assertIsNone(row.get("eth_return_1h_pct"))
        self.assertIsNone(row.get("btc_price_oi_state"))
        self.assertIsNone(row.get("eth_price_oi_state"))

    def test_complete_derived_inputs_produce_authoritative_state(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        spot, oi = self.panel(start, 2)
        rows = hourly.build_rows(start, start + timedelta(hours=1), spot, oi, {}, {}, "PASS", "PASS")
        second = rows[1]
        for prefix in ("btc", "eth"):
            self.assertIsNotNone(second[f"{prefix}_return_1h_pct"])
            self.assertIsNotNone(second[f"{prefix}_oi_change_1h_pct"])
            self.assertNotIn(second[f"{prefix}_price_oi_state"], (None, "", "UNAVAILABLE"))
        self.assertEqual(hourly.hourly_row_quality(second), "PASS")

    def test_good_then_degraded_preserves_good_and_audits_refused_attempt(self):
        stamp = "2026-01-01T01:00:00Z"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            good = self.direct_row(stamp, "PASS", close="101")
            bad = self.direct_row(stamp, "DEGRADED", close="999")
            hourly.merge_rows(root, [good])
            before = self.read_rows(root)[stamp]
            hourly.merge_rows(root, [bad])
            after = self.read_rows(root)[stamp]
            self.assertEqual(after, before)
            self.assertEqual(after["btc_close"], "101")
            audit = root / "_integrity" / "SUPERSEDED_ATTEMPTS.jsonl"
            self.assertTrue(audit.exists())
            self.assertIn("LOWER_QUALITY_RERUN_REJECTED", audit.read_text())

    def test_degraded_then_good_upgrades(self):
        stamp = "2026-01-01T01:00:00Z"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hourly.merge_rows(root, [self.direct_row(stamp, "DEGRADED", close="100")])
            hourly.merge_rows(root, [self.direct_row(stamp, "PASS", close="101")])
            row = self.read_rows(root)[stamp]
            self.assertEqual(row["btc_close"], "101")
            self.assertEqual(row["btc_price_oi_state"], "PRICE_UP_OI_UP")
            self.assertEqual(hourly.hourly_row_quality(row), "PASS")

    def test_equal_quality_existing_row_wins_deterministically(self):
        stamp = "2026-01-01T01:00:00Z"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hourly.merge_rows(root, [self.direct_row(stamp, "PASS", close="101")])
            hourly.merge_rows(root, [self.direct_row(stamp, "PASS", close="202")])
            row = self.read_rows(root)[stamp]
            self.assertEqual(row["btc_close"], "101")
            audit = (root / "_integrity" / "SUPERSEDED_ATTEMPTS.jsonl").read_text()
            self.assertIn("EQUAL_QUALITY_EXISTING_ROW_WINS", audit)

    def test_first_degraded_interval_remains_explicit_without_fabricated_state(self):
        stamp = "2026-01-01T00:00:00Z"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hourly.merge_rows(root, [self.direct_row(stamp, "DEGRADED", close="100")])
            row = self.read_rows(root)[stamp]
            self.assertEqual(row["btc_close"], "100")
            self.assertEqual(row["btc_return_1h_pct"], "")
            self.assertEqual(row["btc_price_oi_state"], "")
            self.assertEqual(hourly.hourly_row_quality(row), "DEGRADED")

    def test_every_bar_and_every_sixth_replay_common_rows_are_semantically_equal(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        spot, oi = self.panel(start, 7)
        with tempfile.TemporaryDirectory() as a_tmp, tempfile.TemporaryDirectory() as b_tmp:
            every_bar = Path(a_tmp)
            every_sixth = Path(b_tmp)

            for i in range(1, 7):
                rows = hourly.build_rows(
                    start + timedelta(hours=i - 1),
                    start + timedelta(hours=i),
                    spot, oi, {}, {}, "PASS", "PASS",
                )
                hourly.merge_rows(every_bar, rows)

            rows = hourly.build_rows(
                start, start + timedelta(hours=6), spot, oi, {}, {}, "PASS", "PASS"
            )
            hourly.merge_rows(every_sixth, rows)

            a = self.read_rows(every_bar)
            b = self.read_rows(every_sixth)
            self.assertEqual(set(a), set(b))
            for key in sorted(a):
                left = {k: v for k, v in a[key].items() if k not in PROVENANCE_EXCLUSIONS}
                right = {k: v for k, v in b[key].items() if k not in PROVENANCE_EXCLUSIONS}
                self.assertEqual(left, right, key)


if __name__ == "__main__":
    unittest.main()
