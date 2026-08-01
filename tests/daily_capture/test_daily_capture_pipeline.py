import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class DailyCapturePipelineTests(unittest.TestCase):
    def test_capture_index_is_compact_and_non_authoritative(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            owner = root / "binance-spot-owner-output"
            owner.mkdir()
            (owner / "receipt.json").write_text(json.dumps({"status": "PASS", "run_id": "r1", "rows": 12}))
            status = root / "status.json"
            status.write_text(json.dumps({
                "fred_macro": 1,
                "binance_spot": 0,
                "binance_microstructure": 1,
                "okx_swap": 1,
                "top100_breadth": 1,
            }))
            output = root / "03_DAILY_CAPTURE_LOGS" / "captures"
            subprocess.run([
                sys.executable,
                "scripts/daily_capture/build_capture_index.py",
                "--root", str(root),
                "--status-file", str(status),
                "--output-root", str(output),
                "--run-id", "test-run",
                "--trigger", "test",
            ], check=True)
            packets = [p for p in output.rglob("*.json") if p.name != "LATEST.json"]
            self.assertEqual(len(packets), 1)
            packet = json.loads(packets[0].read_text())
            self.assertEqual(packet["status"], "PARTIAL")
            self.assertFalse(packet["canonical_data_ping"])
            self.assertFalse(packet["framework_state_change"])
            self.assertFalse(packet["portfolio_action"])
            self.assertEqual(packet["owners_passed"], 1)

    def test_weekly_pack_requires_real_capture_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            captures = root / "captures" / "2026" / "08" / "01"
            captures.mkdir(parents=True)
            for i in range(3):
                (captures / f"0{i}0000_run{i}.json").write_text(json.dumps({
                    "captured_at_utc": f"2026-08-01T0{i}:00:00Z",
                    "status": "COMPLETE",
                    "weekly_calibration_eligible": True,
                    "owners": [{"owner_id": "binance_spot", "status": "PASS"}],
                }))
            weekly = root / "weekly"
            subprocess.run([
                sys.executable,
                "scripts/daily_capture/build_weekly_calibration.py",
                "--input-root", str(root / "captures"),
                "--output-root", str(weekly),
                "--iso-year", "2026",
                "--iso-week", "31",
            ], check=True)
            pack = json.loads((weekly / "2026" / "W31.json").read_text())
            self.assertEqual(pack["capture_count"], 3)
            self.assertEqual(pack["readiness"], "DEGRADED")
            self.assertFalse(pack["forecast_evaluation_performed"])
            self.assertFalse(pack["framework_state_change"])
            self.assertFalse(pack["portfolio_action"])
            self.assertIn("MASTER_MONDAY_PREP", pack["handoff_targets"])


if __name__ == "__main__":
    unittest.main()
