import csv
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class DailyCapturePipelineTests(unittest.TestCase):
    def run_script(self, relative_path: str, *args: str) -> None:
        subprocess.run([sys.executable, str(REPO_ROOT / relative_path), *args], check=True)

    def test_live_anchor_index_is_compact_and_non_authoritative(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for owner_dir in ("binance-spot-microstructure-output", "okx-swap-owner-output"):
                d = root / owner_dir
                d.mkdir()
                (d / "receipt.json").write_text(json.dumps({"status": "PASS", "run_id": owner_dir}))
            status = root / "status.json"
            status.write_text(json.dumps({
                "fred_macro": 78,
                "binance_spot": 78,
                "binance_microstructure": 0,
                "okx_swap": 0,
                "top100_breadth": 1,
                "cfgi_sentiment": 78,
            }))
            output = root / "03_DAILY_CAPTURE_LOGS" / "captures"
            self.run_script(
                "scripts/daily_capture/build_capture_index.py",
                "--root", str(root),
                "--status-file", str(status),
                "--output-root", str(output),
                "--run-id", "test-run",
                "--trigger", "test",
            )
            packets = [p for p in output.rglob("*.json") if p.name != "LATEST.json"]
            self.assertEqual(len(packets), 1)
            packet = json.loads(packets[0].read_text())
            self.assertEqual(packet["contract"], "DAILY_LIVE_ANCHOR_INDEX_v3")
            self.assertEqual(packet["capture_lane"], "LIVE_POINT_IN_TIME_ANCHOR")
            self.assertEqual(packet["status"], "PARTIAL")
            self.assertEqual(packet["anchor_core_passed"], 2)
            self.assertEqual(packet["anchor_core_planned"], 3)
            self.assertTrue(packet["weekly_calibration_eligible"])
            self.assertFalse(packet["canonical_data_ping"])
            self.assertFalse(packet["framework_state_change"])
            self.assertFalse(packet["portfolio_action"])
            self.assertIn("BTCUSDT_1H_OHLCV", packet["hourly_sequence_owned_fields"])

    def test_hourly_sequence_merges_without_interpolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = root / "fixture"
            fixture.mkdir()
            retrieval = datetime(2026, 8, 8, 20, 55, tzinfo=timezone.utc)
            end = retrieval.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
            start = end - timedelta(hours=13)
            for symbol, price in (("BTCUSDT", 65000.0), ("ETHUSDT", 1900.0), ("ETHBTC", 0.0292)):
                rows = []
                for i in range(14):
                    stamp = start + timedelta(hours=i)
                    open_ = price * (1 + i * 0.001)
                    close = open_ * (0.9995 if i % 3 == 0 else 1.0005)
                    high = max(open_, close) * 1.001
                    low = min(open_, close) * 0.999
                    rows.append([
                        int(stamp.timestamp() * 1000), str(open_), str(high), str(low), str(close), "100",
                        int((stamp + timedelta(hours=1)).timestamp() * 1000) - 1, "0", 10, "0", "0", "0",
                    ])
                (fixture / f"{symbol}_spot.json").write_text(json.dumps(rows))
            for symbol, oi0 in (("BTCUSDT", 100000.0), ("ETHUSDT", 200000.0)):
                oi_rows = []
                ls_rows = []
                for i in range(14):
                    stamp = start + timedelta(hours=i)
                    ts = int(stamp.timestamp() * 1000)
                    oi_rows.append({"ts": str(ts), "oiCcy": str(oi0 + i * 100), "oiUsd": str((oi0 + i * 100) * 10)})
                    ls_rows.append([str(ts), str(1.1 + i * 0.001)])
                (fixture / f"{symbol}_oi_okx.json").write_text(json.dumps({"code": "0", "msg": "", "data": oi_rows}))
                (fixture / f"{symbol}_long_short_okx.json").write_text(json.dumps({"code": "0", "msg": "", "data": ls_rows}))
                (fixture / f"{symbol}_funding_okx.json").write_text(json.dumps({"code": "0", "msg": "", "data": [{
                    "instId": "BTC-USDT-SWAP" if symbol == "BTCUSDT" else "ETH-USDT-SWAP",
                    "fundingRate": "0.0001",
                    "realizedRate": "0.00009",
                    "fundingTime": str(int((start + timedelta(hours=8)).timestamp() * 1000)),
                }]}))

            output = root / "hourly"
            raw = root / "raw"
            self.run_script(
                "scripts/daily_capture/build_hourly_sequence.py",
                "--output-root", str(output),
                "--raw-output", str(raw),
                "--lookback-hours", "14",
                "--retrieval-timestamp", retrieval.isoformat().replace("+00:00", "Z"),
                "--fixture-dir", str(fixture),
            )
            csv_paths = list(output.glob("2026/08/*.csv"))
            self.assertTrue(csv_paths)
            rows = []
            for path in csv_paths:
                with path.open(newline="") as handle:
                    rows.extend(csv.DictReader(handle))
            self.assertEqual(len(rows), 14)
            self.assertTrue(all(row["btc_close"] for row in rows))
            self.assertTrue(all(row["eth_close"] for row in rows))
            self.assertTrue(all(row["ethbtc_close"] for row in rows))
            self.assertTrue(all(row["btc_open_interest_source"] == "OKX_CONTRACT_OI_HISTORY" for row in rows))
            self.assertTrue(all(row["btc_long_short_source"] == "OKX_GLOBAL_ACCOUNT_RATIO" for row in rows))
            self.assertEqual(rows[0]["btc_oi_change_1h_pct"], "")
            self.assertEqual(rows[0]["btc_price_oi_state"], "UNAVAILABLE")
            self.assertIn("PRICE_DOWN_OI_UP", {row["btc_price_oi_state"] for row in rows})
            manifest_paths = list((output / "runs").rglob("*.json"))
            manifest = json.loads(manifest_paths[0].read_text())
            self.assertFalse(manifest["interpolation"])
            self.assertFalse(manifest["forward_fill"])
            self.assertEqual(manifest["spot_complete_hours"], 14)
            self.assertEqual(manifest["derivatives_oi_complete_hours"], 14)
            self.assertEqual(manifest["long_short_complete_hours"], 14)
            self.assertEqual(manifest["derivatives_venue"], "OKX")

    def test_weekly_pack_combines_anchor_and_hourly_sequence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            captures = root / "captures" / "2026" / "08" / "01"
            captures.mkdir(parents=True)
            for i in range(3):
                (captures / f"0{i}0000_run{i}.json").write_text(json.dumps({
                    "captured_at_utc": f"2026-08-01T0{i}:00:00Z",
                    "status": "COMPLETE",
                    "weekly_calibration_eligible": True,
                    "owners": [{"owner_id": "okx_swap", "status": "PASS"}],
                }))
            hourly_dir = root / "hourly" / "2026" / "08"
            hourly_dir.mkdir(parents=True)
            hourly_file = hourly_dir / "2026-08-01.csv"
            fields = [
                "timestamp_utc", "btc_close", "eth_close", "ethbtc_close",
                "btc_open_interest", "eth_open_interest", "btc_long_short_ratio", "eth_long_short_ratio",
                "btc_return_1h_pct", "eth_return_1h_pct", "ethbtc_return_1h_pct",
                "btc_range_1h_pct", "eth_range_1h_pct", "btc_price_oi_state", "eth_price_oi_state",
            ]
            with hourly_file.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                for i in range(6):
                    writer.writerow({
                        "timestamp_utc": f"2026-08-01T0{i}:00:00Z",
                        "btc_close": "65000", "eth_close": "1900", "ethbtc_close": "0.029",
                        "btc_open_interest": "100", "eth_open_interest": "200",
                        "btc_long_short_ratio": "1.1", "eth_long_short_ratio": "1.2",
                        "btc_return_1h_pct": "-0.2" if i % 2 else "0.1",
                        "eth_return_1h_pct": "-0.3" if i % 2 else "0.2",
                        "ethbtc_return_1h_pct": "-0.1",
                        "btc_range_1h_pct": "0.4", "eth_range_1h_pct": "0.5",
                        "btc_price_oi_state": "PRICE_DOWN_OI_UP" if i % 2 else "PRICE_UP_OI_UP",
                        "eth_price_oi_state": "PRICE_DOWN_OI_UP" if i % 2 else "PRICE_UP_OI_UP",
                    })
            weekly = root / "weekly"
            self.run_script(
                "scripts/daily_capture/build_weekly_calibration.py",
                "--input-root", str(root / "captures"),
                "--hourly-root", str(root / "hourly"),
                "--output-root", str(weekly),
                "--iso-year", "2026",
                "--iso-week", "31",
            )
            pack = json.loads((weekly / "2026" / "W31.json").read_text())
            self.assertEqual(pack["contract"], "WEEKLY_RAW_CALIBRATION_PACK_v2")
            self.assertEqual(pack["capture_count"], 3)
            self.assertEqual(pack["hourly_sequence"]["observed_hourly_rows"], 6)
            self.assertEqual(pack["hourly_sequence"]["btc"]["price_oi_state_counts"]["PRICE_DOWN_OI_UP"], 3)
            self.assertEqual(pack["readiness"], "DEGRADED")
            self.assertTrue(pack["sequence_evidence_built"])
            self.assertFalse(pack["forecast_evaluation_performed"])
            self.assertFalse(pack["framework_state_change"])
            self.assertFalse(pack["portfolio_action"])
            self.assertIn("PULLBACK_SEQUENCE_REPLAY", pack["handoff_targets"])


if __name__ == "__main__":
    unittest.main()
