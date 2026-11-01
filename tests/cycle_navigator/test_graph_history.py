"""Source-bound graph-history acceptance and adversarial regression checks."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.cycle_navigator.build_graph_history import (
    archive, canonical, digest, load_original, observed, publish, ROOT, WEEKLY
)

W45 = date(2026, 11, 2)
W46 = date(2026, 11, 9)


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(value))


def source(root, monday=W45, *, status="PUBLISHED", issued="2026-11-02T09:06:00Z"):
    year, week, _ = monday.isocalendar()
    label = f"{year}-W{week:02d}"
    folder = root / WEEKLY / str(year) / f"W{week:02d}"
    points = [{"day": i, "expected_close": 80000+i*15,
               "low": 78000, "high": 83000} for i in range(1, 8)]
    daily = {"contract": "CN_FROZEN_DAILY_PRICE_PATH_v1", "forecast_week": label,
             "BTC": {"status": status, "reason": "coherent conditional base case" if status == "PUBLISHED" else "source abstained",
                     "points": points if status == "PUBLISHED" else []},
             "ETH": {"status": "UNAVAILABLE", "reason": "ETH evidence insufficient", "points": []}}
    freeze = {"btc_range_low": 76000, "btc_range_high": 86000,
              "eth_range_low": 2000, "eth_range_high": 2600,
              "daily_price_path": daily}
    put(folder / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json", freeze)
    sha = digest((folder / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json").read_bytes())
    put(folder / "CYCLE_NAVIGATOR_DELIVERY_POINTER.json",
        {"forecast_freeze_sha256": sha, "iso_year": year, "iso_week": week, "public_issue_number": 32})
    epoch = int(datetime.fromisoformat(issued.replace("Z", "+00:00")).timestamp())
    put(folder / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json",
        {"generated_unix": epoch, "public_issue_number": 32})
    next_hour = datetime.fromtimestamp(epoch, timezone.utc).replace(minute=0, second=0) + timedelta(hours=1)
    put(folder / "CYCLE_NAVIGATOR_SITE_PUBLIC_FREEZE_RECEIPT.json",
        {"forecast_week": label, "source_forecast_freeze_sha256": sha,
         "public_issue_number": 32, "scoring_valid_from_utc": next_hour.isoformat().replace("+00:00", "Z")})
    return folder


def hour(root, at, *, btc="80200", eth="2350", spot="PASS"):
    path = root / "03_DAILY_CAPTURE_LOGS/hourly" / str(at.year) / f"{at.month:02d}" / f"{at.date().isoformat()}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {"timestamp_utc": at.isoformat().replace("+00:00", "Z"), "btc_close": btc,
           "eth_close": eth, "spot_status": spot}
    mode = "a" if path.exists() else "w"
    with path.open(mode, newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(row))
        if mode == "w":
            writer.writeheader()
        writer.writerow(row)


class GraphHistoryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_start_boundary_and_no_preissuance_backfill(self):
        self.assertEqual(archive(self.root, date(2026, 10, 26))["weeks"], [])
        source(self.root)
        result = archive(self.root, W45)
        self.assertEqual(len(result["weeks"]), 1)
        row = json.loads((self.root / ROOT / "weeks/2026/W45/forecast-reference.json").read_text())
        self.assertEqual(row["BTC"]["status"], "PUBLISHED")
        self.assertEqual(len(row["BTC"]["points"]), 7)
        self.assertEqual(row["ETH"]["points"], [])
        self.assertFalse((self.root / ROOT / "weeks/2026/W45/actual-series.json").exists())
        self.assertGreater(row["first_eligible_utc"], row["issued_at_utc"])
        self.assertEqual(archive(self.root, W45), result)

    def test_no_fabricated_daily_path_and_source_week_gap_is_explicit(self):
        source(self.root, status="UNAVAILABLE")
        result = archive(self.root, W46)
        self.assertEqual([r["status"] for r in result["weeks"]], ["RECORDED", "MISSING_FREEZE"])
        payload = publish(self.root)
        self.assertEqual(len(payload["weeks"]), 2)
        self.assertEqual(payload["weeks"][0]["forecast"], [])
        self.assertEqual(payload["weeks"][0]["forecast_status"], "UNAVAILABLE")
        self.assertEqual(payload["weeks"][1]["forecast_status"], "UNAVAILABLE")
        self.assertEqual(payload["actual"], [])

    def test_immutable_original_hash_and_no_late_prospective_promotion(self):
        folder = source(self.root, issued="2026-11-03T02:00:00Z")
        self.assertEqual(load_original(self.root, W45)["BTC"]["status"], "UNAVAILABLE")
        archive(self.root, W45)
        freeze = json.loads((folder / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json").read_text())
        freeze["btc_range_high"] = 87000
        put(folder / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json", freeze)
        with self.assertRaisesRegex(ValueError, "ORIGINAL_FREEZE_BINDING_MISMATCH"):
            archive(self.root, W45)

    def test_closed_week_hourly_gaps_are_not_interpolated_and_can_fill_later(self):
        source(self.root)
        hour(self.root, datetime(2026, 11, 2, 0, tzinfo=timezone.utc))
        hour(self.root, datetime(2026, 11, 2, 2, tzinfo=timezone.utc))
        one = archive(self.root, W46)
        actual_file = self.root / ROOT / "weeks/2026/W45/actual-series.json"
        a = json.loads(actual_file.read_text())
        self.assertEqual(a["observed_hours"], 2)
        self.assertEqual(a["status"], "PARTIAL")
        self.assertEqual([row["observed_at_utc"] for row in a["points"]],
                         ["2026-11-02T01:00:00Z", "2026-11-02T03:00:00Z"])
        hour(self.root, datetime(2026, 11, 2, 1, tzinfo=timezone.utc))
        two = archive(self.root, W46)
        self.assertEqual(two["weeks"][0]["source_sha256"], one["weeks"][0]["source_sha256"])
        self.assertEqual(len(json.loads(actual_file.read_text())["points"]), 3)

    def test_historical_mutations_and_conflicting_duplicates_stop(self):
        source(self.root)
        at = datetime(2026, 11, 2, 0, tzinfo=timezone.utc)
        hour(self.root, at)
        archive(self.root, W46)
        path = self.root / "03_DAILY_CAPTURE_LOGS/hourly/2026/11/2026-11-02.csv"
        path.write_text(path.read_text().replace("80200", "80301"))
        with self.assertRaisesRegex(ValueError, "ACTUAL_MUTATION_OR_LOST_HOUR"):
            archive(self.root, W46)
        hour(self.root, at, btc="80777")
        with self.assertRaisesRegex(ValueError, "CONFLICTING_SOURCE_HOUR"):
            observed(self.root, W45)

    def test_reject_future_wrong_week_bad_spot_and_invalid_quote(self):
        source(self.root)
        hour(self.root, datetime(2026, 11, 2, 0, tzinfo=timezone.utc), spot="FAIL")
        hour(self.root, datetime(2026, 11, 2, 1, tzinfo=timezone.utc), btc="-9")
        hour(self.root, datetime(2026, 11, 9, 0, tzinfo=timezone.utc))
        self.assertEqual(observed(self.root, W45)["points"], [])

    def test_public_uses_live_source_only_and_keeps_unit_boundary(self):
        source(self.root)
        archive(self.root, W45)
        latest = self.root / "05_CYCLE_NAVIGATOR/site/dist/data/latest.json"
        put(latest, {"public_live_precision": {
            "contract": "CN_PUBLIC_LIVE_PRICE_PRECISION_v1", "forecast_week": "2026-W45", "public_issue_number": 32,
            "hourly_price_path": {"contract": "CN_PUBLIC_HOURLY_PRICE_PATH_v1",
                                  "source": "HOURLY_SPOT_PASS_ONLY", "forecast_week": "2026-W45", "public_issue_number": 32,
                                  "observed_through_utc": "2026-11-02T11:00:00Z",
                                  "BTC": [{"observed_at_utc": "2026-11-02T11:00:00Z", "close": 80500}],
                                  "ETH": []}}})
        x = publish(self.root)
        self.assertEqual(x["actual"][0]["close"], 80500)
        self.assertFalse(x["comparison_precision_eligible"])
        self.assertEqual(x["weeks"][0]["actual_status"], "LIVE")
        put(latest, {"public_live_precision": {
            "contract": "CN_PUBLIC_LIVE_PRICE_PRECISION_v1", "forecast_week": "2026-W46",
            "hourly_price_path": {"contract": "CN_PUBLIC_HOURLY_PRICE_PATH_v1",
                                  "source": "HOURLY_SPOT_PASS_ONLY", "forecast_week": "2026-W46",
                                  "BTC": [{"observed_at_utc": "2026-11-02T11:00:00Z", "close": 80500}]}}})
        self.assertEqual(publish(self.root)["actual"], [])

    def test_live_wrong_issue_and_future_hour_cannot_poison_history(self):
        source(self.root)
        archive(self.root, W45)
        latest = self.root / "05_CYCLE_NAVIGATOR/site/dist/data/latest.json"
        good = {"contract": "CN_PUBLIC_LIVE_PRICE_PRECISION_v1", "forecast_week": "2026-W45",
                "public_issue_number": 32, "hourly_price_path": {
                    "contract": "CN_PUBLIC_HOURLY_PRICE_PATH_v1", "forecast_week": "2026-W45",
                    "public_issue_number": 32, "source": "HOURLY_SPOT_PASS_ONLY",
                    "observed_through_utc": "2026-11-02T11:00:00Z",
                    "BTC": [{"observed_at_utc": "2026-11-02T12:00:00Z", "close": 80000},
                            {"observed_at_utc": "2026-11-09T01:00:00Z", "close": 80000}],
                    "ETH": []}}
        put(latest, {"public_live_precision": good})
        self.assertEqual(publish(self.root)["actual"], [])
        good["hourly_price_path"]["BTC"].append({"observed_at_utc": "2026-11-02T10:00:00Z", "close": 80500})
        good["public_issue_number"] = 31
        put(latest, {"public_live_precision": good})
        self.assertEqual(publish(self.root)["actual"], [])


if __name__ == "__main__":
    unittest.main()
