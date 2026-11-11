"""Adversarial Task2 W46 original daily forecast scoring without promotion."""
from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.research import task2_cn_daily_path_score_v1 as mod

REPO = Path(__file__).resolve().parents[2]
STAMP = datetime(2026, 11, 10, 0, 1, tzinfo=timezone.utc)
MON = datetime(2026, 11, 9, tzinfo=timezone.utc)


def put_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")


def fixture(root: Path):
    d = root / "05_CYCLE_NAVIGATOR/weekly/2026/W46"
    d.mkdir(parents=True, exist_ok=True)
    prices = {"BTC": (110.0, 95.0, 130.0), "ETH": (11.0, 9.0, 14.0)}
    freeze = {
        "price_quote": {"BTC": "USDT", "ETH": "USDT"},
        "daily_price_path": {"contract": "CN_FROZEN_DAILY_PRICE_PATH_v1", "forecast_week": "2026-W46"},
        "daily_range_plan": {"contract": "CN_FROZEN_DAILY_RANGE_PLAN_v1"},
    }
    for a, (target, low, high) in prices.items():
        points = [{"day": i, "expected_close": target, "low": low, "high": high} for i in range(1, 8)]
        bands = [{"day": i, "low": low, "high": high} for i in range(1, 8)]
        freeze["daily_price_path"][a] = {"status": "PUBLISHED", "points": points}
        freeze["daily_range_plan"][a] = {"status": "PUBLISHED", "points": bands}
    fp = d / mod.FORECAST
    put_json(fp, freeze)
    receipt = {
        "contract": "CN_SITE_PUBLIC_FREEZE_RECEIPT_v1",
        "forecast_week": "2026-W46", "status": "SITE_FROZEN_SOURCE_OF_RECORD",
        "source_forecast_freeze_sha256": hashlib.sha256(fp.read_bytes()).hexdigest(),
        "public_issue_number": 33,
        "daily_product_acceptance": {"issued_at_utc": "2026-11-09T10:52:34.925867Z"},
        "scoring_valid_from_utc": "2026-11-09T11:00:00Z",
    }
    put_json(d / mod.RECEIPT, receipt)
    hourly = root / "03_DAILY_CAPTURE_LOGS/hourly/2026/11/2026-11-09.csv"
    hourly.parent.mkdir(parents=True, exist_ok=True)
    names = ["timestamp_utc", "spot_status",
             "btc_open", "btc_high", "btc_low", "btc_close",
             "eth_open", "eth_high", "eth_low", "eth_close", "source_window_end_utc"]
    with hourly.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=names)
        w.writeheader()
        for h in range(24):
            btc = 100 + h
            eth = 10 + h / 10
            w.writerow({
                "timestamp_utc": mod.iso(MON + timedelta(hours=h)),
                "spot_status": "PASS",
                "btc_open": btc, "btc_high": btc + 1, "btc_low": btc - 1, "btc_close": btc,
                "eth_open": eth, "eth_high": eth + 0.1, "eth_low": eth - 0.1, "eth_close": eth,
                "source_window_end_utc": mod.iso(MON + timedelta(hours=24)),
            })
    return d, hourly


class Task2DailyPathEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.directory, self.hourly = fixture(self.root)

    def test_day1_matures_close_but_not_whole_day_extrema(self):
        out = mod.build(self.root, as_of=STAMP)
        self.assertEqual(out["contract"], mod.CONTRACT)
        self.assertEqual(len(out["rows"]), 14)
        self.assertEqual(out["maturity_counts"], {"MATURED_DESCRIPTIVE_ONLY": 2, "UNMATURED": 12})
        btc = out["rows"][0]
        self.assertEqual(btc["asset"], "BTC")
        self.assertEqual(btc["eligible_observed_hours"], 13)
        self.assertEqual(btc["expected_eligible_hours"], 13)
        self.assertEqual(btc["actual_close"], 123)
        self.assertEqual(btc["abs_error"], 13)
        self.assertEqual(btc["band_status"], "PARTIAL_DAY_UNSCORED")
        self.assertIsNone(btc["joint_band_contains_extrema"])
        self.assertFalse(btc["scientific_edge_admitted"])
        self.assertTrue(out["no_public_score"])

    def test_no_future_day_scored_and_no_synthetic_fill(self):
        out = mod.build(self.root, as_of=STAMP)
        self.assertTrue(all(r["status"] == "UNMATURED" for r in out["rows"] if r["day"] >= 2))
        future = mod.build(self.root, as_of=datetime(2026, 11, 11, 0, 1, tzinfo=timezone.utc))
        self.assertEqual(future["maturity_counts"]["SOURCE_GAP"], 2)
        self.assertIsNone(next(r for r in future["rows"] if r["asset"] == "BTC" and r["day"] == 2)["actual_close"])

    def test_source_gap_rejects_partial_and_duplicate_completed_candles(self):
        data = self.hourly.read_text().splitlines()
        self.hourly.write_text("\n".join([x for x in data if not x.startswith("2026-11-09T11:00:00Z")]) + "\n")
        out = mod.build(self.root, as_of=STAMP)
        self.assertEqual(out["maturity_counts"]["SOURCE_GAP"], 2)
        self.assertIsNone(out["rows"][0]["abs_error"])
        self.hourly.write_text("\n".join(data + [data[-1]]) + "\n")
        out = mod.build(self.root, as_of=STAMP)
        self.assertEqual(out["maturity_counts"]["SOURCE_GAP"], 2)

    def test_bad_forecast_hash_and_missing_receipt_fail_closed(self):
        fp = self.directory / mod.FORECAST
        fp.write_text(fp.read_text() + " ")
        with self.assertRaisesRegex(ValueError, "ORIGINAL_FORECAST_SHA256_MISMATCH"):
            mod.build(self.root, as_of=STAMP)
        self.directory.joinpath(mod.RECEIPT).unlink()
        with self.assertRaisesRegex(ValueError, "ORIGINAL_FREEZE_RECEIPT_REQUIRED"):
            mod.build(self.root, as_of=STAMP)

    def test_tampered_quote_and_misaligned_day_rejected(self):
        fp = self.directory / mod.FORECAST
        rp = self.directory / mod.RECEIPT
        forecast = json.loads(fp.read_text())
        forecast["price_quote"]["BTC"] = "USD"
        put_json(fp, forecast)
        receipt = json.loads(rp.read_text())
        receipt["source_forecast_freeze_sha256"] = hashlib.sha256(fp.read_bytes()).hexdigest()
        put_json(rp, receipt)
        with self.assertRaisesRegex(ValueError, "QUOTE_PARITY_NOT_DECLARED"):
            mod.build(self.root, as_of=STAMP)

    def test_naive_or_non_utc_as_of_rejected(self):
        with self.assertRaisesRegex(ValueError, "AS_OF_MUST_BE_UTC"):
            mod.build(self.root, as_of=datetime(2026, 11, 10))
        with self.assertRaisesRegex(ValueError, "UTC_Z_TIMESTAMP_REQUIRED"):
            mod.utc("2026-11-10T00:00:00+01:00")

    def test_real_w46_first_matured_close_receipt(self):
        if not (REPO / "05_CYCLE_NAVIGATOR/weekly/2026/W46" / mod.RECEIPT).is_file():
            self.skipTest("original repository W46 not mounted")
        x = mod.build(REPO, as_of=STAMP)
        btc = next(r for r in x["rows"] if r["asset"] == "BTC" and r["day"] == 1)
        eth = next(r for r in x["rows"] if r["asset"] == "ETH" and r["day"] == 1)
        self.assertEqual((btc["actual_close"], btc["abs_error"]), (75368.41, 851.57))
        self.assertEqual((eth["actual_close"], eth["abs_error"]), (2135.24, 21.60))
        self.assertEqual((btc["band_status"], eth["band_status"]), ("PARTIAL_DAY_UNSCORED", "PARTIAL_DAY_UNSCORED"))
        self.assertEqual(x["maturity_counts"], {"MATURED_DESCRIPTIVE_ONLY": 2, "UNMATURED": 12})


if __name__ == "__main__":
    unittest.main()
