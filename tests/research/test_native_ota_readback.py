from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts/research/native_ota_readback.py"
spec = importlib.util.spec_from_file_location("native_ota_readback", MODULE_PATH)
assert spec and spec.loader
ota = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ota)

UTC = timezone.utc


def hour(day: int, h: int, *, btc: float = 100.0, eth: float = 10.0, ratio: float = 0.031) -> ota.Hour:
    ts = datetime(2026, 9, day, h, tzinfo=UTC)
    return ota.Hour(
        ts,
        btc, btc + 1, btc - 1, btc,
        eth, eth + 0.1, eth - 0.1, eth,
        ratio, ratio + 0.0001, ratio - 0.0001, ratio,
    )


def session(day: str, btc_ret: float, eth_ret: float, ratio_close: float, ratio_low: float | None = None) -> dict:
    return {
        "date_utc": day,
        "session_status": "SETTLED_COMPLETE_24H",
        "hour_count": 24,
        "btc": {"return_pct": btc_ret},
        "eth": {"return_pct": eth_ret},
        "ethbtc": {
            "close": ratio_close,
            "low": ratio_close if ratio_low is None else ratio_low,
        },
        "eth_minus_btc_return_pp": eth_ret - btc_ret,
    }


class NativeOtaTests(unittest.TestCase):
    def test_incomplete_day_high_never_contaminates_settled_session(self):
        rows = [hour(3, h, btc=100 + h) for h in range(24)]
        rows += [hour(4, h, btc=1_000_000 + h) for h in range(5)]
        settled, incomplete = ota.build_daily(rows)
        self.assertEqual(len(settled), 1)
        self.assertEqual(settled[0]["date_utc"], "2026-09-03")
        self.assertEqual(settled[0]["session_status"], "SETTLED_COMPLETE_24H")
        self.assertLess(settled[0]["btc"]["high"], 1_000_000)
        self.assertIsNotNone(incomplete)
        self.assertEqual(incomplete["date_utc"], "2026-09-04")
        self.assertEqual(incomplete["session_status"], "IN_PROGRESS_INCOMPLETE")

    def test_missing_hour_keeps_session_in_progress(self):
        rows = [hour(3, h) for h in range(24) if h != 17]
        settled, incomplete = ota.build_daily(rows)
        self.assertEqual(settled, [])
        self.assertIsNotNone(incomplete)
        self.assertEqual(incomplete["hour_count"], 23)

    def test_registered_level_cross_is_settled_only(self):
        settled = [
            session("2026-09-01", 1.0, 1.1, 0.0305),
            session("2026-09-02", 1.0, 0.9, 0.0302),
            session("2026-09-03", -1.0, -1.2, 0.0299),
        ]
        result = ota.threshold_analysis(settled, None)
        self.assertTrue(result["settled_close_crossed_below_on_latest"])
        self.assertFalse(result["settled_close_reclaimed_on_latest"])
        self.assertEqual(result["consecutive_settled_closes_at_or_above"], 0)
        self.assertEqual(result["registered_level_read_only"], 0.03)

    def test_in_progress_dip_does_not_create_settled_break(self):
        settled = [
            session("2026-09-01", 1.0, 1.1, 0.0305),
            session("2026-09-02", 1.0, 0.9, 0.0302),
        ]
        incomplete = session("2026-09-03", -1.0, -2.0, 0.0297, 0.0295)
        incomplete["session_status"] = "IN_PROGRESS_INCOMPLETE"
        incomplete["hour_count"] = 12
        result = ota.threshold_analysis(settled, incomplete)
        self.assertFalse(result["settled_close_crossed_below_on_latest"])
        self.assertEqual(result["in_progress"]["semantics"], "IN_PROGRESS_NEVER_SETTLED_EVIDENCE")

    def test_relative_leadership_is_counted_on_settled_sessions(self):
        settled = [
            session("2026-08-29", 2.0, 3.0, 0.031),
            session("2026-08-30", 2.0, 1.0, 0.031),
            session("2026-08-31", 2.0, 1.5, 0.031),
            session("2026-09-01", 2.0, 1.0, 0.031),
            session("2026-09-02", 2.0, 1.8, 0.031),
            session("2026-09-03", 2.0, 1.9, 0.031),
        ]
        result = ota.leadership_analysis(settled, None)
        self.assertEqual(result["settled_eth_led_last_4"], 0)
        self.assertEqual(result["settled_eth_led_last_6"], 1)
        self.assertEqual(result["consecutive_btc_led_settled"], 5)

    def test_native_etf_owner_prevents_false_framework_gap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "research/etf_owner/LATEST_FARSIDE_ETF_OWNER.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({
                "contract": "FARSIDE_ETF_OWNER_SNAPSHOT_v4",
                "authority": "SHADOW_ONLY",
                "history_rows": {
                    "BTC": [{"date": "2026-09-03", "reported_total": 730.8, "session_final": True, "total_parity": True}],
                    "ETH": [{"date": "2026-09-03", "reported_total": 141.4, "session_final": True, "total_parity": True}],
                },
            }))
            result = ota.latest_etf(root)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["latest_final"]["BTC"]["reported_total"], 730.8)
            self.assertEqual(result["latest_final"]["ETH"]["reported_total"], 141.4)

    def test_options_lane_never_mislabels_moneyness_as_25_delta(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "03_DAILY_CAPTURE_LOGS/pullback_forensics/LATEST.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({
                "contract": "PULLBACK_FORENSICS_PASSIVE_CAPTURE_v1",
                "lane1_liquidations": {"BTC": {"status": "PASS"}},
                "lane2a_dvol": {"status": "DEFERRED_FULLY_BACKFILLABLE"},
                "lane2b_moneyness_skew": {"BTC": {"status": "PASS"}},
            }))
            result = ota.pullback_status(root)
            self.assertEqual(result["lane1_executed_liquidations"]["status_by_asset"]["BTC"], "PASS")
            self.assertEqual(result["lane2b_moneyness_skew"]["semantics"], "MONEYNESS_BUCKET_SKEW_NOT_25_DELTA")
            self.assertEqual(result["lane3_orderbook"]["status"], "DEFERRED_BY_RATIFIED_PILOT")

    def test_trigger_only_fires_on_settled_cross_not_live_noise(self):
        below = [session("2026-09-01", 1.0, 1.0, 0.0302), session("2026-09-02", -1.0, -1.0, 0.0299)]
        gate = ota.threshold_analysis(below, None)
        self.assertTrue(gate["settled_close_crossed_below_on_latest"])
        above = [session("2026-09-01", 1.0, 1.0, 0.0302), session("2026-09-02", -1.0, -1.0, 0.0301)]
        noisy = session("2026-09-03", -1.0, -1.5, 0.0296, 0.0294)
        noisy["hour_count"] = 8
        gate2 = ota.threshold_analysis(above, noisy)
        self.assertFalse(gate2["settled_close_crossed_below_on_latest"])


if __name__ == "__main__":
    unittest.main()
