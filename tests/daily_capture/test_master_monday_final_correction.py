import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


class MasterMondayFinalCorrectionTests(unittest.TestCase):
    def run_script(self, relative_path: str, *args: str) -> None:
        subprocess.run([sys.executable, str(REPO_ROOT / relative_path), *args], check=True)

    def test_farside_parser_accepts_td_header_and_preserves_accounted_dash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = root / "fixture"
            fixture.mkdir()
            btc = """
            <table><tr><td>Date</td><td>IBIT</td><td>EZBC</td><td>Total</td></tr>
            <tr><td>06 Aug 2026</td><td>137.6</td><td>0.0</td><td>137.6</td></tr>
            <tr><td>07 Aug 2026</td><td>101.7</td><td>-</td><td>101.7</td></tr></table>
            """
            eth = """
            <table><tr><td>Date</td><td>ETHA</td><td>FETH</td><td>Total</td></tr>
            <tr><td>06 Aug 2026</td><td>80.0</td><td>12.1</td><td>92.1</td></tr>
            <tr><td>07 Aug 2026</td><td>38.1</td><td>11.5</td><td>49.6</td></tr></table>
            """
            (fixture / "btc.html").write_text(btc)
            (fixture / "eth.html").write_text(eth)
            out = root / "out"
            self.run_script(
                "scripts/data_terminal/farside_etf_owner.py",
                "--output-dir", str(out),
                "--fixture-dir", str(fixture),
                "--now-utc", "2026-08-10T06:00:00Z",
                "--history-limit", "10",
            )
            snapshot = json.loads((out / "owner_snapshot.json").read_text())
            self.assertEqual(snapshot["status"], "PASS")
            self.assertTrue(snapshot["unknown_cells_are_not_imputed"])
            btc_latest = next(row for row in snapshot["rows"] if row["asset"] == "BTC")
            self.assertEqual(btc_latest["date"], "2026-08-07")
            self.assertEqual(btc_latest["unknown_fund_cell_count"], 1)
            self.assertIsNone(btc_latest["fund_values"][1])
            self.assertTrue(btc_latest["unknown_cells_fully_accounted_by_reported_total"])
            self.assertTrue(btc_latest["total_parity"])
            self.assertEqual(len(snapshot["history_rows"]["BTC"]), 2)
            self.assertEqual(len(snapshot["history_rows"]["ETH"]), 2)

    def test_weekly_orchestration_accepts_final_close_pointer_v3(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            capture = root / "03_DAILY_CAPTURE_LOGS"
            close_dir = capture / "weekly_close" / "2026" / "W32"
            close_dir.mkdir(parents=True)
            weekly_dir = capture / "weekly"
            weekly_dir.mkdir(parents=True)
            accepted = root / "accepted"
            accepted.mkdir()

            package = {
                "contract": "WEEKLY_MARKET_CLOSE_PACKAGE_v3",
                "final": True,
                "close_mode": "FINAL_COMPLETED_ISO_WEEK",
                "completeness": "COMPLETE",
                "iso_year": 2026,
                "iso_week": 32,
                "window_end_utc": "2026-08-10T00:00:00Z",
            }
            package_path = close_dir / "WEEKLY_MARKET_CLOSE_PACKAGE.json"
            package_path.write_bytes(canonical(package))
            package_hash = hashlib.sha256(canonical(package)).hexdigest()
            pointer = {
                "contract": "WEEKLY_MARKET_CLOSE_POINTER_v3",
                "path": "weekly_close/2026/W32/WEEKLY_MARKET_CLOSE_PACKAGE.json",
                "final": True,
                "close_mode": "FINAL_COMPLETED_ISO_WEEK",
                "completeness": "COMPLETE",
                "iso_year": 2026,
                "iso_week": 32,
                "window_end_utc": "2026-08-10T00:00:00Z",
                "sha256": package_hash,
            }
            (capture / "weekly_close" / "LATEST_WEEKLY_MARKET_CLOSE.json").write_bytes(canonical(pointer))
            (weekly_dir / "LATEST_WEEKLY_CALIBRATION.json").write_text(json.dumps({"iso_year": 2026, "iso_week": 32}) + "\n")

            output = root / "freeze.json"
            self.run_script(
                "scripts/orchestration/weekly_orchestration_controller.py",
                "--capture-root", str(capture),
                "--accepted-data-ping-root", str(accepted),
                "--output", str(output),
                "--now-utc", "2026-08-10T02:40:00Z",
            )
            freeze = json.loads(output.read_text())
            self.assertEqual(freeze["status"], "READY")
            self.assertEqual(freeze["final_week_close"]["pointer_contract"], "WEEKLY_MARKET_CLOSE_POINTER_v3")
            self.assertEqual(freeze["iso_week"], 32)


if __name__ == "__main__":
    unittest.main()
