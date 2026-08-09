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

    def _write_hourly_fixtures(self, fixture: Path, retrieval: datetime, hours: int = 26) -> None:
        end = retrieval.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
        start = end - timedelta(hours=hours - 1)
        for symbol, price in (("BTCUSDT", 65000.0), ("ETHUSDT", 1900.0), ("ETHBTC", 0.0292)):
            rows = []
            for i in range(hours):
                stamp = start + timedelta(hours=i)
                open_ = price * (1 + i * 0.001)
                close = open_ * (0.9995 if i % 3 == 0 else 1.0005)
                high = max(open_, close) * 1.001
                low = min(open_, close) * 0.999
                base_volume = 100.0 + i
                quote_volume = base_volume * close
                taker_buy_base = base_volume * 0.55
                taker_buy_quote = quote_volume * 0.55
                rows.append([
                    int(stamp.timestamp() * 1000), str(open_), str(high), str(low), str(close), str(base_volume),
                    int((stamp + timedelta(hours=1)).timestamp() * 1000) - 1,
                    str(quote_volume), 1000 + i, str(taker_buy_base), str(taker_buy_quote), "0",
                ])
            (fixture / f"{symbol}_spot.json").write_text(json.dumps(rows))
        for symbol, oi0 in (("BTCUSDT", 100000.0), ("ETHUSDT", 200000.0)):
            oi_rows = []
            ls_rows = []
            for i in range(hours):
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

    def test_hourly_sequence_materializes_26h_and_free_spot_flow_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = root / "fixture"
            fixture.mkdir()
            retrieval = datetime(2026, 8, 9, 10, 55, tzinfo=timezone.utc)
            self._write_hourly_fixtures(fixture, retrieval, 26)

            output = root / "hourly"
            raw = root / "raw"
            self.run_script(
                "scripts/daily_capture/build_hourly_sequence.py",
                "--output-root", str(output),
                "--raw-output", str(raw),
                "--lookback-hours", "26",
                "--retrieval-timestamp", retrieval.isoformat().replace("+00:00", "Z"),
                "--fixture-dir", str(fixture),
            )
            rows = []
            for path in output.glob("2026/08/*.csv"):
                with path.open(newline="") as handle:
                    rows.extend(csv.DictReader(handle))
            rows.sort(key=lambda row: row["timestamp_utc"])
            self.assertEqual(len(rows), 26)
            self.assertTrue(all(row["btc_quote_volume"] for row in rows))
            self.assertTrue(all(row["eth_quote_volume"] for row in rows))
            self.assertTrue(all(row["btc_trade_count"] for row in rows))
            self.assertTrue(all(row["eth_trade_count"] for row in rows))
            self.assertTrue(all(row["btc_taker_buy_quote_volume"] for row in rows))
            self.assertTrue(all(row["eth_taker_buy_quote_volume"] for row in rows))
            self.assertTrue(all(abs(float(row["btc_taker_buy_quote_share"]) - 0.55) < 1e-9 for row in rows))
            self.assertTrue(all(abs(float(row["eth_taker_buy_quote_share"]) - 0.55) < 1e-9 for row in rows))
            self.assertTrue(all(row["btc_open_interest_source"] == "OKX_CONTRACT_OI_HISTORY" for row in rows))
            self.assertTrue(all(row["btc_long_short_source"] == "OKX_GLOBAL_ACCOUNT_RATIO" for row in rows))
            self.assertEqual(rows[0]["btc_oi_change_1h_pct"], "")
            self.assertEqual(rows[0]["btc_price_oi_state"], "UNAVAILABLE")
            manifest_paths = list((output / "runs").rglob("*.json"))
            manifest = json.loads(manifest_paths[0].read_text())
            self.assertEqual(manifest["contract"], "HOURLY_SEQUENCE_CAPTURE_v2_2")
            self.assertFalse(manifest["interpolation"])
            self.assertFalse(manifest["forward_fill"])
            self.assertEqual(manifest["spot_complete_hours"], 26)
            self.assertEqual(manifest["spot_flow_complete_hours"], 26)
            self.assertEqual(manifest["derivatives_oi_complete_hours"], 26)
            self.assertEqual(manifest["long_short_complete_hours"], 26)

    def test_weekly_pack_materializes_enriched_csv_gaps_windows_and_etf(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            captures = root / "captures" / "2026" / "08" / "09"
            captures.mkdir(parents=True)
            for i in range(15):
                (captures / f"{i:02d}_run.json").write_text(json.dumps({
                    "captured_at_utc": "2026-08-09T10:00:00Z",
                    "status": "COMPLETE",
                    "weekly_calibration_eligible": True,
                    "owners": [{"owner_id": "okx_swap", "status": "PASS"}],
                }))

            fixture = root / "fixture"
            fixture.mkdir()
            retrieval = datetime(2026, 8, 9, 10, 55, tzinfo=timezone.utc)
            self._write_hourly_fixtures(fixture, retrieval, 26)
            hourly = root / "hourly"
            self.run_script(
                "scripts/daily_capture/build_hourly_sequence.py",
                "--output-root", str(hourly),
                "--raw-output", str(root / "raw"),
                "--lookback-hours", "26",
                "--retrieval-timestamp", retrieval.isoformat().replace("+00:00", "Z"),
                "--fixture-dir", str(fixture),
            )

            etf_dir = root / "etf" / "2026" / "08" / "08"
            etf_dir.mkdir(parents=True)
            (etf_dir / "080000_2026-08-07.json").write_text(json.dumps({
                "session_date": "2026-08-07",
                "retrieved_at_utc": "2026-08-08T06:00:00Z",
                "rows": [
                    {"asset": "BTC", "reported_total": 101.7},
                    {"asset": "ETH", "reported_total": 49.6},
                ],
            }))

            weekly = root / "weekly"
            self.run_script(
                "scripts/daily_capture/build_weekly_calibration.py",
                "--input-root", str(root / "captures"),
                "--hourly-root", str(hourly),
                "--etf-root", str(root / "etf"),
                "--output-root", str(weekly),
                "--iso-year", "2026",
                "--iso-week", "32",
                "--now-utc", "2026-08-09T12:00:00Z",
            )
            pack = json.loads((weekly / "2026" / "W32.json").read_text())
            self.assertEqual(pack["contract"], "WEEKLY_RAW_CALIBRATION_PACK_v3")
            self.assertEqual(pack["capture_count"], 15)
            self.assertEqual(pack["hourly_sequence"]["observed_hourly_rows"], 26)
            self.assertEqual(pack["settled_etf"]["week_total_reported_units"]["BTC"], 101.7)
            self.assertEqual(pack["settled_etf"]["week_total_reported_units"]["ETH"], 49.6)
            self.assertIn("missing_hour_count", pack["hourly_gap_diagnostics"])
            self.assertIn("DAY1_2", pack["day_window_actuals"]["windows"])
            self.assertIn("DAY3_4", pack["day_window_actuals"]["windows"])
            self.assertIn("DAY5_7", pack["day_window_actuals"]["windows"])
            enriched_path = root / pack["enriched_hourly_path"]
            facts_path = root / pack["sequence_facts_path"]
            self.assertTrue(enriched_path.exists())
            self.assertTrue(facts_path.exists())
            with enriched_path.open(newline="") as handle:
                enriched_rows = list(csv.DictReader(handle))
            self.assertEqual(len(enriched_rows), 26)
            self.assertTrue(enriched_rows[-1]["btc_return_24h_pct"])
            self.assertTrue(enriched_rows[-1]["eth_return_24h_pct"])
            self.assertIn("eth_minus_btc_return_24h_pct", enriched_rows[-1])
            self.assertIn("btc_oi_change_24h_pct", enriched_rows[-1])
            facts = json.loads(facts_path.read_text())
            self.assertFalse(facts["market_interpretation"])
            self.assertFalse(facts["forecast_evaluation_performed"])
            self.assertFalse(facts["interpolation"])
            self.assertFalse(facts["forward_fill"])

    def test_previous_week_flag_targets_completed_iso_week(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "captures").mkdir()
            (root / "hourly").mkdir()
            weekly = root / "weekly"
            self.run_script(
                "scripts/daily_capture/build_weekly_calibration.py",
                "--input-root", str(root / "captures"),
                "--hourly-root", str(root / "hourly"),
                "--output-root", str(weekly),
                "--previous-week",
                "--now-utc", "2026-08-10T00:25:00Z",
            )
            pointer = json.loads((weekly / "LATEST_WEEKLY_CALIBRATION.json").read_text())
            self.assertEqual(pointer["iso_year"], 2026)
            self.assertEqual(pointer["iso_week"], 32)


if __name__ == "__main__":
    unittest.main()
