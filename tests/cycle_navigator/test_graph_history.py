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
    archive, canonical, digest, load_original, observed, publish, publish_w45_research_preview, ROOT, WEEKLY
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

    def test_missing_forecast_week_never_backfills_but_keeps_actual_curve(self):
        source(self.root, W46, issued="2026-11-09T07:00:00Z")
        at = datetime(2026, 11, 2, 0, tzinfo=timezone.utc)
        hour(self.root, at)
        one = archive(self.root, W46)
        self.assertEqual(one["weeks"][0]["status"], "MISSING_FREEZE")
        self.assertIsNone(one["weeks"][0]["forecast_path"])
        actual_file = self.root / ROOT / "weeks/2026/W45/actual-series.json"
        self.assertEqual(json.loads(actual_file.read_text())["observed_hours"], 1)
        self.assertEqual(len(publish(self.root)["actual"]), 1)
        source(self.root, W45, issued="2026-11-02T07:00:00Z")
        two = archive(self.root, W46)
        self.assertEqual(two["weeks"][0]["status"], "MISSING_FREEZE")
        self.assertEqual(two["weeks"][0]["chain_digest"], one["weeks"][0]["chain_digest"])
        self.assertFalse((self.root / ROOT / "weeks/2026/W45/forecast-reference.json").exists())
        self.assertEqual(publish(self.root)["weeks"][0]["forecast"], [])
        # Missing a forecast must not weaken the original hourly immutability gate.
        path = self.root / "03_DAILY_CAPTURE_LOGS/hourly/2026/11/2026-11-02.csv"
        path.write_text(path.read_text().replace("80200", "80301"))
        with self.assertRaisesRegex(ValueError, "ACTUAL_MUTATION_OR_LOST_HOUR"):
            archive(self.root, W46)

    def test_deleted_index_cannot_rebootstrap_over_recorded_forecast(self):
        source(self.root)
        original = archive(self.root, W46)
        self.assertEqual(original["weeks"][0]["status"], "RECORDED")
        recorded = self.root / ROOT / "weeks/2026/W45/forecast-reference.json"
        self.assertTrue(recorded.is_file())
        (self.root / ROOT / "index.json").unlink()
        with self.assertRaisesRegex(ValueError, "HISTORY_INDEX_MISSING_WITH_EXISTING_RECORDS"):
            archive(self.root, W46)
        with self.assertRaisesRegex(ValueError, "HISTORY_INDEX_MISSING_WITH_EXISTING_RECORDS"):
            publish(self.root)
        self.assertTrue(recorded.is_file())

    def test_deleted_index_cannot_rebootstrap_over_actuals_only(self):
        original = archive(self.root, W46)
        self.assertEqual(original["weeks"][0]["status"], "MISSING_FREEZE")
        self.assertTrue((self.root / ROOT / "weeks/2026/W45/actual-series.json").is_file())
        (self.root / ROOT / "index.json").unlink()
        with self.assertRaisesRegex(ValueError, "HISTORY_INDEX_MISSING_WITH_EXISTING_RECORDS"):
            archive(self.root, W46)
        with self.assertRaisesRegex(ValueError, "HISTORY_INDEX_MISSING_WITH_EXISTING_RECORDS"):
            publish(self.root)

    def test_interrupted_index_write_cannot_be_silently_accepted(self):
        index_tmp = self.root / ROOT / "index.json.tmp"
        index_tmp.parent.mkdir(parents=True, exist_ok=True)
        index_tmp.write_text("partial-write")
        with self.assertRaisesRegex(ValueError, "HISTORY_INDEX_MISSING_WITH_EXISTING_RECORDS"):
            archive(self.root, W45)
        with self.assertRaisesRegex(ValueError, "HISTORY_INDEX_MISSING_WITH_EXISTING_RECORDS"):
            publish(self.root)

    def test_recorded_forecast_cannot_disappear_on_later_archive(self):
        folder = source(self.root)
        original = archive(self.root, W45)
        (folder / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json").unlink()
        with self.assertRaisesRegex(ValueError, "INDEX_HISTORY_REWRITE"):
            archive(self.root, W45)
        self.assertEqual(json.loads((self.root / ROOT / "index.json").read_text()), original)

    def test_prior_chain_tampering_cannot_be_rehashed_to_a_new_history(self):
        source(self.root)
        archive(self.root, W45)
        path = self.root / ROOT / "index.json"
        old = json.loads(path.read_text())
        old["weeks"][0]["chain_digest"] = "0" * 64
        put(path, old)
        with self.assertRaisesRegex(ValueError, "INVALID_HISTORY_INDEX_CHAIN"):
            archive(self.root, W45)
        # Public-only Pages builds must also fail closed without a fresh archive pass.
        with self.assertRaisesRegex(ValueError, "INVALID_HISTORY_INDEX_CHAIN"):
            publish(self.root)

    def test_durable_actual_is_not_hidden_by_null_index_path(self):
        source(self.root)
        hour(self.root, datetime(2026, 11, 2, 0, tzinfo=timezone.utc))
        original = archive(self.root, W46)
        actual = self.root / ROOT / "weeks/2026/W45/actual-series.json"
        self.assertTrue(actual.is_file())
        self.assertEqual(len(publish(self.root)["actual"]), 1)
        index_path = self.root / ROOT / "index.json"
        altered = json.loads(json.dumps(original))
        altered["weeks"][0]["actual_path"] = None
        put(index_path, altered)
        with self.assertRaisesRegex(ValueError, "INDEX_DISK_ACTUAL_OMITTED:2026-W45"):
            publish(self.root)
        with self.assertRaisesRegex(ValueError, "INDEX_DISK_ACTUAL_OMITTED:2026-W45"):
            archive(self.root, W46)
        self.assertTrue(actual.is_file())
        put(index_path, original)
        self.assertEqual(len(publish(self.root)["actual"]), 1)

    def test_durable_suffix_cannot_be_hidden_by_valid_rechained_prefix(self):
        source(self.root, W45)
        source(self.root, W46, issued="2026-11-09T08:00:00Z")
        w47 = W46 + timedelta(days=7)
        source(self.root, w47, issued="2026-11-16T08:00:00Z")
        original = archive(self.root, w47)
        self.assertEqual(len(original["weeks"]), 3)
        preserved = self.root / ROOT / "weeks/2026/W46/forecast-reference.json"
        self.assertTrue(preserved.is_file())
        index_path = self.root / ROOT / "index.json"
        truncated = json.loads(json.dumps(original))
        truncated["weeks"] = truncated["weeks"][:1]
        truncated["chain_tip"] = truncated["weeks"][0]["chain_digest"]
        put(index_path, truncated)
        with self.assertRaisesRegex(ValueError, "INDEX_DISK_UNINDEXED_HISTORY"):
            publish(self.root)
        with self.assertRaisesRegex(ValueError, "INDEX_DISK_UNINDEXED_HISTORY"):
            archive(self.root, w47)
        self.assertTrue(preserved.is_file())
        put(index_path, original)
        self.assertEqual(len(publish(self.root)["weeks"]), 3)

    def test_true_absent_actual_path_and_unavailable_forecast_are_allowed(self):
        first = archive(self.root, W45)
        self.assertEqual(first["weeks"][0]["status"], "MISSING_FREEZE")
        self.assertIsNone(first["weeks"][0]["actual_path"])
        self.assertEqual(len(publish(self.root)["weeks"]), 1)
        second = archive(self.root, W46)
        self.assertEqual(second["weeks"][0]["status"], "MISSING_FREEZE")
        self.assertEqual(len(publish(self.root)["weeks"]), 2)
        self.assertTrue((self.root / ROOT / "weeks/2026/W45/actual-series.json").is_file())

    def test_public_only_rejects_forged_missing_forecast_and_index_truncation(self):
        source(self.root)
        archive(self.root, W46)
        path = self.root / ROOT / "index.json"
        original = json.loads(path.read_text())
        forged = json.loads(json.dumps(original))
        forged["weeks"][0].update(status="MISSING_FREEZE", source_sha256=None, forecast_path=None)
        put(path, forged)
        with self.assertRaisesRegex(ValueError, "INVALID_HISTORY_INDEX_CHAIN"):
            publish(self.root)
        truncated = json.loads(json.dumps(original))
        truncated["weeks"].pop(0)
        put(path, truncated)
        with self.assertRaisesRegex(ValueError, "INVALID_HISTORY_INDEX_SEQUENCE"):
            publish(self.root)
        forged_path = json.loads(json.dumps(original))
        forged_path["weeks"][0]["forecast_path"] = None
        put(path, forged_path)
        with self.assertRaisesRegex(ValueError, "INVALID_HISTORY_INDEX_PATH"):
            publish(self.root)
        forged_actual = json.loads(json.dumps(original))
        forged_actual["weeks"][0]["actual_path"] = "../../untrusted-actuals.json"
        put(path, forged_actual)
        with self.assertRaisesRegex(ValueError, "INVALID_HISTORY_INDEX_PATH"):
            publish(self.root)
        put(path, original)
        self.assertEqual(len(publish(self.root)["weeks"]), 2)

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

    def test_missing_forecast_current_week_preserves_only_verified_live_actuals(self):
        # The source-only green curve is independent of a missing blue forecast.
        result = archive(self.root, W45)
        self.assertEqual(result["weeks"][0]["status"], "MISSING_FREEZE")
        latest = self.root / "05_CYCLE_NAVIGATOR/site/dist/data/latest.json"
        good = {"public_live_precision": {
            "contract": "CN_PUBLIC_LIVE_PRICE_PRECISION_v1",
            "forecast_week": "2026-W45", "public_issue_number": 32,
            "hourly_price_path": {
                "contract": "CN_PUBLIC_HOURLY_PRICE_PATH_v1",
                "source": "HOURLY_SPOT_PASS_ONLY",
                "forecast_week": "2026-W45", "public_issue_number": 32,
                "observed_through_utc": "2026-11-02T11:00:00Z",
                "BTC": [{"observed_at_utc": "2026-11-02T11:00:00Z", "close": 80500}],
                "ETH": []}}}
        put(latest, good)
        valid = publish(self.root)
        self.assertEqual(valid["weeks"][0]["forecast"], [])
        self.assertEqual(valid["weeks"][0]["forecast_status"], "UNAVAILABLE")
        self.assertEqual(valid["weeks"][0]["actual_status"], "LIVE")
        self.assertEqual(valid["actual"], [{"time": "2026-11-02T11:00:00Z", "close": 80500}])

        def rejected(mutator):
            case = json.loads(json.dumps(good))
            mutator(case["public_live_precision"])
            put(latest, case)
            self.assertEqual(publish(self.root)["actual"], [])

        rejected(lambda live: live["hourly_price_path"].update(public_issue_number=33))
        rejected(lambda live: live.update(public_issue_number=None))
        rejected(lambda live: live.update(public_issue_number=0))
        rejected(lambda live: live.update(forecast_week="2026-W46"))
        rejected(lambda live: live["hourly_price_path"].update(source="UNVERIFIED"))
        rejected(lambda live: live["hourly_price_path"]["BTC"][0].update(
            observed_at_utc="2026-11-02T12:00:00Z"))

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


    def test_rechained_forecast_withdrawal_fails_against_immutable_disk_record(self):
        # Adversarial: chain/tip recomputed, so hash-only verification passes.
        source(self.root)
        archive(self.root, W46)
        index_file = self.root / ROOT / "index.json"
        original_index = json.loads(index_file.read_text())
        self.assertEqual(publish(self.root)["weeks"][0]["status"], "RECORDED")
        chain = "0" * 64
        altered = json.loads(json.dumps(original_index))
        for row in altered["weeks"]:
            if row["forecast_week"] == "2026-W45":
                row.update(status="MISSING_FREEZE", source_sha256=None, forecast_path=None)
            chain = digest(canonical({"previous": chain, "week": row["forecast_week"],
                                      "source_sha256": row["source_sha256"], "status": row["status"]}))
            row["chain_digest"] = chain
        altered["chain_tip"] = chain
        put(index_file, altered)
        with self.assertRaisesRegex(ValueError, "INDEX_DISK_RECORD_CONFLICT:2026-W45"):
            publish(self.root)
        with self.assertRaisesRegex(ValueError, "INDEX_DISK_RECORD_CONFLICT:2026-W45"):
            archive(self.root, W46)
        put(index_file, original_index)
        self.assertEqual(publish(self.root)["weeks"][0]["status"], "RECORDED")
        self.assertEqual(archive(self.root, W46), original_index)

    def test_rechained_forecast_sha_substitution_fails_against_disk(self):
        source(self.root)
        archive(self.root, W45)
        index_file = self.root / ROOT / "index.json"
        forged = json.loads(index_file.read_text())
        forged["weeks"][0]["source_sha256"] = "f" * 64
        row = forged["weeks"][0]
        forged["chain_tip"] = digest(canonical({"previous": "0" * 64,
            "week": row["forecast_week"], "source_sha256": row["source_sha256"],
            "status": row["status"]}))
        row["chain_digest"] = forged["chain_tip"]
        put(index_file, forged)
        with self.assertRaisesRegex(ValueError, "INDEX_DISK_RECORD_CONFLICT"):
            publish(self.root)
        with self.assertRaisesRegex(ValueError, "INDEX_DISK_RECORD_CONFLICT"):
            archive(self.root, W45)


    def test_historical_forecast_quote_is_only_original_source_declared(self):
        # W45 lacks a typed original price_quote; a dollar sign is NOT proof.
        first_folder = source(self.root)
        second_folder = source(self.root, W46, issued="2026-11-09T07:00:00Z")
        original = json.loads((second_folder / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json").read_text())
        original["price_quote"] = {"BTC": "USDT", "ETH": "USDT"}
        put(second_folder / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json", original)
        source_hash = digest((second_folder / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json").read_bytes())
        pointer_file = second_folder / "CYCLE_NAVIGATOR_DELIVERY_POINTER.json"
        pointer = json.loads(pointer_file.read_text())
        pointer["forecast_freeze_sha256"] = source_hash
        put(pointer_file, pointer)
        receipt_file = second_folder / "CYCLE_NAVIGATOR_SITE_PUBLIC_FREEZE_RECEIPT.json"
        receipt = json.loads(receipt_file.read_text())
        receipt["source_forecast_freeze_sha256"] = source_hash
        put(receipt_file, receipt)
        archive(self.root, W46)
        original_history = (self.root / ROOT / "weeks/2026/W45/forecast-reference.json")
        w46_history = (self.root / ROOT / "weeks/2026/W46/forecast-reference.json")
        self.assertEqual(json.loads(original_history.read_text())["forecast_quote_unit"], "UNAVAILABLE")
        self.assertEqual(json.loads(w46_history.read_text())["forecast_quote_unit"], "USDT")
        display = publish(self.root)
        self.assertEqual(display["forecast_unit"], "PER_WEEK_DECLARED_OR_UNAVAILABLE")
        self.assertEqual(display["actual_unit"], "USDT")
        self.assertFalse(display["comparison_precision_eligible"])
        self.assertEqual([w["forecast_model_declared_quote"] for w in display["weeks"]],
                         ["UNAVAILABLE", "USDT"])
        # Tamper with original typed quote while preserving source-reference bytes.
        altered = json.loads((second_folder / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json").read_text())
        altered["price_quote"]["BTC"] = "USD"
        put(second_folder / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json", altered)
        with self.assertRaisesRegex(ValueError, "HISTORY_ORIGINAL_QUOTE_SOURCE_MISMATCH"):
            publish(self.root)


    def test_historical_w45_legacy_usd_tag_survives_replay_while_public_quote_stays_unavailable(self):
        # Simulate a real previously archived W45 forecast-reference from the
        # old code, without altering a freeze, timestamp or portfolio signal.
        source(self.root, status="UNAVAILABLE")
        archive(self.root, W45)
        ref = self.root / ROOT / "weeks/2026/W45/forecast-reference.json"
        historical = json.loads(ref.read_text())
        self.assertEqual(historical["forecast_quote_unit"], "UNAVAILABLE")
        historical["forecast_quote_unit"] = "USD"
        put(ref, historical)
        exact_bytes = ref.read_bytes()
        archive(self.root, W46)
        self.assertEqual(ref.read_bytes(), exact_bytes)
        self.assertEqual(publish(self.root)["weeks"][0]["forecast_model_declared_quote"], "UNAVAILABLE")
        self.assertEqual(json.loads(ref.read_text())["forecast_quote_unit"], "USD")
        # The exception only permits the single historical quote-label bug.
        # A changed frozen forecast field still triggers immutable conflict.
        historical["BTC"]["reason"] = "UNAUTHORIZED_RETROACTIVE_CHANGE"
        put(ref, historical)
        with self.assertRaisesRegex(ValueError, "IMMUTABLE_HISTORY_CONFLICT"):
            archive(self.root, W46)

    def test_untyped_original_btc_quote_never_borrows_eth_or_native_spot_usdt(self):
        folder = source(self.root)
        frozen = json.loads((folder / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json").read_text())
        frozen["price_quote"] = {"BTC": "UNAVAILABLE", "ETH": "USDT"}
        put(folder / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json", frozen)
        hashed = digest((folder / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json").read_bytes())
        pointer = folder / "CYCLE_NAVIGATOR_DELIVERY_POINTER.json"
        pointer_data = json.loads(pointer.read_text())
        pointer_data["forecast_freeze_sha256"] = hashed
        put(pointer, pointer_data)
        receipt = folder / "CYCLE_NAVIGATOR_SITE_PUBLIC_FREEZE_RECEIPT.json"
        receipt_data = json.loads(receipt.read_text())
        receipt_data["source_forecast_freeze_sha256"] = hashed
        put(receipt, receipt_data)
        original = load_original(self.root, W45)
        self.assertEqual(original["forecast_quote_unit"], "UNAVAILABLE")
        self.assertEqual(original["BTC"]["status"], "PUBLISHED")
        self.assertEqual(original["ETH"]["status"], "UNAVAILABLE")

    def test_time_machine_premium_view_preserves_data_provenance(self):
        """Visual-only upgrade must keep historical blue/green admission separate."""
        html = (Path(__file__).resolve().parents[2] /
                "05_CYCLE_NAVIGATOR/site/graph-history/index.html").read_text()
        for required in (
                "#071320", "#31d0a0", "#79aaff",
                "class=\"panel panel-primary\"", "prefers-reduced-motion",
                "Kildeudstedt dagsprognose · 7/7",
                "w?.forecast_status==='PUBLISHED'",
                "w?.forecast_model_declared_quote==='USDT'",
                "data?.actual_unit==='USDT'",
                "issued<first&&issued<monday+DAY",
                "w.forecast.length===7",
                "comparableOriginal(w)",
                "path(eligible,xf,yf,HOUR*1.5)",
                "forecast_model_declared_quote",
                "Seneste registrerede timeluk",
                "data.actual_unit==='USDT'?'USDT':'UNAVAILABLE'",
                "Ingen automatisk USD/USDT-omregning",
                "Ingen prognosekurve konstrueres uden syv originale",
        ):
            self.assertIn(required, html)
        self.assertNotIn("Frosne prognoser er i USD", html)


    def test_optional_source_locked_w45_research_route_is_isolated_from_original_graph(self):
        root = Path(__file__).resolve().parents[2]
        src = root / "06_RESEARCH_LAB/mission_packets/2026-11-05__W45_MIDWEEK_PROSPECTIVE_BENCHMARK_v1.json"
        page = root / "05_CYCLE_NAVIGATOR/site/research-w45/index.html"
        self.assertTrue(src.is_file())
        self.assertTrue(page.is_file())
        dst_src = self.root / src.relative_to(root)
        dst_page = self.root / page.relative_to(root)
        dst_src.parent.mkdir(parents=True, exist_ok=True)
        dst_page.parent.mkdir(parents=True, exist_ok=True)
        dst_src.write_bytes(src.read_bytes())
        dst_page.write_bytes(page.read_bytes())
        result = publish_w45_research_preview(self.root)
        self.assertEqual(result, "RESEARCH_ONLY_PUBLISHED")
        exposed = self.root / "05_CYCLE_NAVIGATOR/site/dist/data/research-w45-shadow.json"
        delivered = self.root / "05_CYCLE_NAVIGATOR/site/dist/research-w45/index.html"
        self.assertEqual(exposed.read_bytes(), src.read_bytes())
        self.assertEqual(delivered.read_bytes(), page.read_bytes())
        self.assertIn(b"noindex,nofollow", delivered.read_bytes())
        self.assertNotIn(b"BUYSIGNAL", delivered.read_bytes())
        original = json.loads(exposed.read_text())
        self.assertFalse(original["forecast"]["site_blue_original_forecast_eligible"])
        self.assertEqual(original["original_W45_daily_price_path_status"],
                         {"BTC": "UNAVAILABLE", "ETH": "UNAVAILABLE"})

        # Research authority must never be able to become original CN.
        original["forecast"]["site_blue_original_forecast_eligible"] = True
        put(dst_src, original)
        self.assertEqual(publish_w45_research_preview(self.root), "RESEARCH_QUARANTINED")
        self.assertFalse(exposed.exists())
        self.assertFalse(delivered.exists())
        # Retaining the research page cannot change canonical source state.
        self.assertFalse((self.root / ROOT / "index.json").exists())

        dst_src.write_bytes(src.read_bytes())
        tampered = page.read_text().replace("noindex,nofollow", "index,follow")
        dst_page.write_text(tampered)
        self.assertEqual(publish_w45_research_preview(self.root), "RESEARCH_QUARANTINED")
        self.assertFalse(exposed.exists())
        self.assertFalse(delivered.exists())

    def test_optional_thursday_forecast_scoring_does_not_promote_or_break_original_research(self):
        root = Path(__file__).resolve().parents[2]
        required = (
            "06_RESEARCH_LAB/mission_packets/2026-11-05__W45_MIDWEEK_PROSPECTIVE_BENCHMARK_v1.json",
            "06_RESEARCH_LAB/mission_packets/2026-11-05__W45_THURSDAY_SELFTEST_v1.json",
            "05_CYCLE_NAVIGATOR/site/research-w45/index.html",
        )
        for rel in required:
            src, dst = root / rel, self.root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())
        self.assertEqual(publish_w45_research_preview(self.root), "RESEARCH_ONLY_PUBLISHED")
        outcome_file = self.root / "05_CYCLE_NAVIGATOR/site/dist/data/research-w45-thursday-outcomes.json"
        original_file = self.root / "05_CYCLE_NAVIGATOR/site/dist/data/research-w45-outcomes.json"
        self.assertTrue(outcome_file.is_file())
        self.assertTrue(original_file.is_file())
        outcome = json.loads(outcome_file.read_text())
        self.assertEqual(outcome["contract"], "RESEARCH_W45_THURSDAY_SELFTEST_OUTCOMES_v1")
        self.assertEqual(outcome["original_monday_daily_issued"], {"BTC": 0, "ETH": 0})
        self.assertEqual(outcome["matured_observations"], 0)
        self.assertFalse(outcome["official_scoring_eligible"])
        self.assertFalse(outcome["portfolio_action_authority"])
        # A malicious rewrite of Thursday's locked initial issue must
        # quarantine ONLY this independent additional JSON endpoint.
        freeze = self.root / required[1]
        changed = json.loads(freeze.read_text())
        changed["first_public_issue_utc"] = "2026-11-05T18:00:00Z"
        put(freeze, changed)
        self.assertEqual(publish_w45_research_preview(self.root), "RESEARCH_ONLY_PUBLISHED")
        self.assertFalse(outcome_file.exists())
        self.assertTrue(original_file.exists())
        # The primary graph never consumes any research self-test bytes.
        self.assertFalse((self.root / ROOT / "index.json").exists())

    def test_honest_midweek_w45_is_first_prospective_forecast_not_original_blue(self):
        real = Path(__file__).resolve().parents[2]
        files = (
            "06_RESEARCH_LAB/mission_packets/2026-11-05__W45_THURSDAY_SELFTEST_v1.json",
            "03_DAILY_CAPTURE_LOGS/hourly/2026/11/2026-11-04.csv",
            "03_DAILY_CAPTURE_LOGS/hourly/2026/11/2026-11-05.csv",
        )
        for rel in files:
            dst = self.root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes((real / rel).read_bytes())
        source(self.root, status="UNAVAILABLE")
        archive(self.root, W45)
        result = publish(self.root)
        overlay = result["first_honest_midweek_research"]
        self.assertEqual(overlay["contract"], "CN_GRAPH_HISTORY_FIRST_HONEST_MIDWEEK_RESEARCH_v1")
        self.assertEqual(overlay["issued_at_utc"], "2026-11-05T20:11:38Z")
        self.assertEqual(overlay["input_cutoff_utc"], "2026-11-05T18:00:00Z")
        self.assertEqual(len(overlay["BTC"]), 4)
        self.assertEqual(len(overlay["ETH"]), 4)
        self.assertEqual(overlay["BTC"][0]["target_at_utc"], "2026-11-06T00:00:00Z")
        self.assertEqual(overlay["BTC"][0]["expected_close"], 75573.64)
        self.assertTrue(overlay["research_only"])
        self.assertFalse(overlay["original_monday_issuance"])
        self.assertFalse(overlay["official_scoring_eligible"])
        self.assertEqual(result["weeks"][0]["forecast_status"], "UNAVAILABLE")
        self.assertEqual(result["weeks"][0]["forecast"], [])
        self.assertEqual(
            json.loads((self.root / "05_CYCLE_NAVIGATOR/site/dist/data/graph-history/timeline.json").read_text())
            ["first_honest_midweek_research"]["frozen_packet_sha256"],
            overlay["frozen_packet_sha256"])

        # On each attempted mutation, research overlay disappears. Frozen
        # Monday original stays unavailable and actual source remains separate.
        packet = self.root / files[0]
        original = packet.read_bytes()
        mutated = json.loads(original)
        mutated["first_public_issue_utc"] = "2026-11-05T18:00:00Z"
        put(packet, mutated)
        self.assertIsNone(publish(self.root)["first_honest_midweek_research"])
        self.assertEqual(publish(self.root)["weeks"][0]["forecast"], [])
        packet.write_bytes(original)
        changed = json.loads(original)
        changed["assets"]["BTC"]["forecasts"][0]["B1_conditional_close"] += 500
        put(packet, changed)
        self.assertIsNone(publish(self.root)["first_honest_midweek_research"])
        packet.write_bytes(original)
        w45 = self.root / files[2]
        before = w45.read_text()
        w45.write_text(before.replace("75952.45", "79952.45"))
        self.assertIsNone(publish(self.root)["first_honest_midweek_research"])

    def test_midweek_overlay_never_claims_seven_original_when_w45_valid_monday_source(self):
        source(self.root, status="PUBLISHED")
        archive(self.root, W45)
        # No original owner-issued Thursday packet in this fixture.
        result = publish(self.root)
        self.assertIsNone(result["first_honest_midweek_research"])
        self.assertEqual(result["weeks"][0]["forecast_status"], "PUBLISHED")

    def test_missing_research_preview_never_blocks_canonical_site(self):
        self.assertEqual(publish_w45_research_preview(self.root), "NOT_AVAILABLE")
        self.assertEqual(archive(self.root, W45)["weeks"][0]["status"], "MISSING_FREEZE")
        self.assertEqual(publish(self.root)["weeks"][0]["forecast_status"], "UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
