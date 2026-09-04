import csv
import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts/research/framework_research_watch.py"
spec = importlib.util.spec_from_file_location("framework_research_watch", MODULE_PATH)
watch = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(watch)

FIELDS = [
    "timestamp_utc",
    "btc_open", "btc_high", "btc_low", "btc_close",
    "eth_open", "eth_high", "eth_low", "eth_close",
    "ethbtc_open", "ethbtc_high", "ethbtc_low", "ethbtc_close",
]


def write_day(repo: Path, date: str, hours: int, btc_high: float, ethbtc_close: float, ethbtc_low: float | None = None,
              btc_return_bias: float = 1.0, eth_return_bias: float = 0.5):
    year, month, _ = date.split("-")
    root = repo / "03_DAILY_CAPTURE_LOGS/hourly" / year / month
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{date}.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for hour in range(hours):
            btc_open = 80000.0
            eth_open = 2500.0
            btc_close = btc_open * (1 + btc_return_bias / 100.0 * (hour + 1) / max(hours, 1))
            eth_close = eth_open * (1 + eth_return_bias / 100.0 * (hour + 1) / max(hours, 1))
            ratio_open = 0.0310
            ratio_close = ethbtc_close if hour == hours - 1 else ratio_open + (ethbtc_close - ratio_open) * (hour + 1) / max(hours, 1)
            writer.writerow({
                "timestamp_utc": f"{date}T{hour:02d}:00:00Z",
                "btc_open": btc_open,
                "btc_high": btc_high if hour == max(hours - 1, 0) else btc_close + 10,
                "btc_low": btc_open - 100,
                "btc_close": btc_close,
                "eth_open": eth_open,
                "eth_high": eth_close + 5,
                "eth_low": eth_open - 10,
                "eth_close": eth_close,
                "ethbtc_open": ratio_open,
                "ethbtc_high": max(ratio_open, ratio_close) + 0.00001,
                "ethbtc_low": ethbtc_low if hour == max(hours - 1, 0) and ethbtc_low is not None else min(ratio_open, ratio_close) - 0.00001,
                "ethbtc_close": ratio_close,
            })
    return path


class FrameworkResearchWatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_in_progress_high_never_replaces_settled_cycle_high(self):
        write_day(self.repo, "2026-09-03", 24, 82300.0, 0.03086)
        write_day(self.repo, "2026-09-04", 10, 90000.0, 0.03070)
        analysis = watch.settled_analysis(watch.load_sessions(self.repo))
        self.assertEqual(analysis["settled_cycle_high"]["high"], 82300.0)
        self.assertEqual(analysis["settled_cycle_high"]["status"], "SETTLED_ONLY")
        self.assertEqual(analysis["in_progress_high"]["high"], 90000.0)
        self.assertEqual(analysis["in_progress_high"]["status"], "IN_PROGRESS_HIGH_NOT_SETTLED_CYCLE_HIGH")

    def test_settled_close_below_registered_floor_emits_trigger(self):
        write_day(self.repo, "2026-09-03", 24, 82300.0, 0.02990)
        analysis = watch.settled_analysis(watch.load_sessions(self.repo))
        triggers = watch.early_triggers(analysis, {"daily_director": {"warning": None}})
        self.assertEqual(triggers[0]["id"], "ETHBTC_SETTLED_CLOSE_BELOW_REGISTERED_0_0300")

    def test_in_progress_low_below_floor_is_not_settled_gate_failure(self):
        write_day(self.repo, "2026-09-03", 24, 82300.0, 0.03086)
        write_day(self.repo, "2026-09-04", 8, 82400.0, 0.03020, ethbtc_low=0.02950)
        analysis = watch.settled_analysis(watch.load_sessions(self.repo))
        self.assertLess(analysis["gate"]["latest_in_progress_low"], 0.0300)
        triggers = watch.early_triggers(analysis, {"daily_director": {"warning": None}})
        self.assertEqual(triggers, [])

    def test_current_etf_owner_pointer_beats_stale_external_bridge(self):
        target = self.repo / "03_DAILY_CAPTURE_LOGS/etf/2026/09/04/111101_2026-09-03.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({
            "authority": "SHADOW_CALIBRATION_INPUT_ONLY",
            "session_date": "2026-09-03",
            "retrieved_at_utc": "2026-09-04T11:10:59Z",
            "rows": [
                {"asset": "BTC", "reported_total": 730.8, "session_final": True},
                {"asset": "ETH", "reported_total": 141.4, "session_final": True},
            ],
        }))
        pointer = self.repo / "03_DAILY_CAPTURE_LOGS/etf/LATEST.json"
        pointer.parent.mkdir(parents=True, exist_ok=True)
        pointer.write_text(json.dumps({"path": str(target.relative_to(self.repo)), "status": "PASS"}))
        owners = watch.owner_snapshot(self.repo, datetime(2026, 9, 4, 21, 0, tzinfo=timezone.utc))
        self.assertEqual(owners["settled_etf"]["session_date"], "2026-09-03")
        self.assertEqual(owners["settled_etf"]["reported_totals"], {"BTC": 730.8, "ETH": 141.4})
        self.assertTrue(owners["settled_etf"]["session_final"])

    def test_report_has_zero_execution_authority(self):
        write_day(self.repo, "2026-09-03", 24, 82300.0, 0.03086)
        out = self.repo / "research/framework_research_watch"
        report, emit = watch.build_report(
            self.repo,
            out,
            datetime(2026, 9, 4, 21, 0, tzinfo=timezone.utc),
            "fixed",
        )
        self.assertTrue(emit)
        self.assertFalse(report["authority"]["canonical_market_state"])
        self.assertFalse(report["authority"]["portfolio_action"])
        self.assertFalse(report["authority"]["threshold_change"])
        self.assertFalse(report["external_ai_required"])


if __name__ == "__main__":
    unittest.main()
