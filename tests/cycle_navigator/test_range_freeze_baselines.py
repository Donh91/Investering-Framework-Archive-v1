import csv
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from scripts.cycle_navigator.range_freeze_baselines import benchmark, freeze_baselines, row_benchmarks
from scripts.cycle_navigator.build_weekly_cycle_navigator import append_forward_ranges


class FreezeBenchmarks(unittest.TestCase):
    def fixture(self, repo):
        monday = datetime(2026, 11, 23, tzinfo=timezone.utc)
        last = None
        for offset in range(9, 0, -1):
            start = monday - timedelta(weeks=offset)
            iso = start.date().isocalendar()
            stem = repo / "03_DAILY_CAPTURE_LOGS/weekly" / str(iso.year) / f"W{iso.week:02d}"
            stem.mkdir(parents=True)
            path = stem / "WEEKLY_HOURLY_ENRICHED.csv"
            def z(t):
                return t.isoformat().replace("+00:00", "Z")
            fields = ["timestamp_utc", "source_window_end_utc", "spot_status"] + [
                a+"_"+k for a in ("btc", "eth") for k in ("open", "high", "low", "close")]
            with path.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                for hour in range(168):
                    at = start+timedelta(hours=hour)
                    writer.writerow(dict(timestamp_utc=z(at), source_window_end_utc=z(at+timedelta(hours=1)),
                                         spot_status="PASS", btc_open=100, btc_high=110, btc_low=90, btc_close=100,
                                         eth_open=200, eth_high=210, eth_low=190, eth_close=200))
            seq = {"spot_complete_hours": 168, "spot_flow_readback": {
                a: {"symbol": a+"USDT", "quote_unit": "USDT"} for a in ("BTC", "ETH")}}
            for a, anchor in (("btc", 100), ("eth", 200)):
                seq[a] = {"week_range": {"open": anchor, "close": anchor, "high": anchor+10, "low": anchor-10}}
            last = {"contract": "WEEKLY_RAW_CALIBRATION_PACK_v3", "iso_year": iso.year, "iso_week": iso.week,
                    "readiness": "READY", "generated_at_utc": z(start+timedelta(days=7)),
                    "hourly_gap_diagnostics": {"observed_hours": 168, "missing_hour_count": 0},
                    "hourly_sequence": seq, "enriched_hourly_path": f"weekly/{iso.year}/W{iso.week:02d}/WEEKLY_HOURLY_ENRICHED.csv"}
            stem.with_suffix(".json").write_text(json.dumps(last))
        return dict(year=2026, week=48, generated_unix=int((monday+timedelta(hours=10)).timestamp()),
                    completed_capture=last, range_forecast={"assets": {"BTC": {"anchor_price": 100}, "ETH": {"anchor_price": 200}}})

    def test_wilder_and_bands(self):
        bars = [(Decimal(100), Decimal(110), Decimal(90), Decimal(100))]*63
        self.assertEqual(benchmark(bars)["DUMB1.5"], {"low": 70, "high": 130})
        self.assertEqual(benchmark(bars)["DUMB2.0"], {"low": 60, "high": 140})
        self.assertEqual(benchmark(bars)["PREVWK"], {"low": 90.0, "high": 110.0})

    def test_source_binding_and_no_retroactive_write(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            kw = self.fixture(repo)
            snap = freeze_baselines(repo, **kw)
            self.assertEqual(snap["status"], "FROZEN_RETAINED_SNAPSHOT")
            self.assertEqual(len(snap["sources"]), 9)
            self.assertFalse(snap["scientific_admission"])
            self.assertEqual(snap["assets"]["ETH"]["DUMB1.5"], {"low": 170, "high": 230})
            freeze = {"btc_range_low": 80, "btc_range_high": 120}
            call = dict(public_issue_number=35, machine_issue_number=36, year=2026, week=48,
                        generated_unix=kw["generated_unix"], freeze=freeze)
            ledger = repo / "05_CYCLE_NAVIGATOR/forward_range_ledger/CN_FORWARD_RANGE_LEDGER_v2.jsonl"
            ledger.parent.mkdir(parents=True)
            ledger.write_text('{"public_issue_number":34,"forecast_week":"2026-W47","asset":"BTC","window":"weekly"}\n')
            before = ledger.read_bytes()
            append_forward_ranges(repo, **call, baseline_snapshot=snap)
            result = ledger.read_bytes()
            self.assertTrue(result.startswith(before))
            row = json.loads(result.splitlines()[-1])
            self.assertEqual(row["DUMB1.5"], {"low": 70, "high": 130})
            self.assertEqual(row["baseline_snapshot_sha256"], snap["snapshot_sha256"])
            append_forward_ranges(repo, **call, baseline_snapshot=None)
            self.assertEqual(ledger.read_bytes(), result)

    def test_wrong_anchor_and_late_freeze_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            kw = self.fixture(repo)
            self.assertEqual(freeze_baselines(repo, **dict(kw, generated_unix=kw["generated_unix"]+86400))["status"], "UNAVAILABLE")
            kw["range_forecast"]["assets"]["BTC"]["anchor_price"] = 101
            self.assertEqual(freeze_baselines(repo, **kw)["status"], "UNAVAILABLE")
            self.assertIsNone(row_benchmarks(None, "BTC", kw["generated_unix"])["DUMB1.5"])

    def test_missing_source_and_mismatching_snapshot(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            kw = self.fixture(repo)
            kw["completed_capture"]["readiness"] = "DEGRADED"
            self.assertEqual(freeze_baselines(repo, **kw)["status"], "UNAVAILABLE")
            kw["completed_capture"]["readiness"] = "READY"
            (repo/"03_DAILY_CAPTURE_LOGS/weekly/2026/W39/WEEKLY_HOURLY_ENRICHED.csv").unlink()
            self.assertEqual(freeze_baselines(repo, **kw)["status"], "UNAVAILABLE")

if __name__ == "__main__":
    unittest.main()
