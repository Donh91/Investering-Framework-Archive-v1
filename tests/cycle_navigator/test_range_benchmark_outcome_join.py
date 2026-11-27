import csv
import hashlib
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from scripts.cycle_navigator.range_benchmark_outcome_join import join_diagnostics, _join


class OutcomeJoin(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 30, 12, tzinfo=timezone.utc)
        self.row = {"contract":"CN_FORWARD_RANGE_FREEZE_v2","asset":"BTC","window":"day_3_4",
                    "forecast_week":"2026-W48","generated_unix":1795427178,
                    "public_issue_number":35,"machine_issue_number":36,"status":"FROZEN_PROSPECTIVE",
                    "baseline_status":"FROZEN_RETAINED_SNAPSHOT"}

    def test_no_historical_backfill_or_duplicate(self):
        r = dict(self.row, baseline_status=None)
        with TemporaryDirectory() as tmp, patch("scripts.cycle_navigator.range_benchmark_outcome_join._join") as join:
            out = join_diagnostics(Path(tmp), [r], self.now)
            self.assertEqual(out["excluded"], {"NO_ORIGINAL_FROZEN_BENCHMARK":1})
            out = join_diagnostics(Path(tmp), [self.row,self.row], self.now)
            self.assertEqual(out["excluded"], {"DUPLICATE_FREEZE_IDENTITY":2})
            join.assert_not_called()
            self.assertEqual(out["scientifically_eligible_rows"],0)

    def test_unmatured_late_and_missing_sources(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp)
            with self.assertRaisesRegex(ValueError,"WEEK_NOT_MATURE"):
                _join(p,self.row,datetime(2026,11,27,12,tzinfo=timezone.utc))
            with self.assertRaisesRegex(ValueError,"NOT_FULL_WINDOW_PROSPECTIVE"):
                _join(p,dict(self.row,window="day_1_2"),self.now)
            out=join_diagnostics(p,[self.row],self.now)
            self.assertEqual(out["joined_rows"],0)
            self.assertEqual(out["scientifically_eligible_rows"],0)

    def test_full_retained_source_join_and_tamper(self):
        def write(repo, rel, value):
            p = repo / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
            p.write_bytes(raw)
            return hashlib.sha256(raw).hexdigest()

        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            folder = Path("05_CYCLE_NAVIGATOR/weekly/2026/W48")
            actual = Path("03_DAILY_CAPTURE_LOGS/weekly/2026/W48.json")
            actual_csv = actual.with_suffix("") / "WEEKLY_HOURLY_ENRICHED.csv"
            score_path = Path("05_CYCLE_NAVIGATOR/public_scorecards/2026/W48/CN35_PUBLIC_SCORECARD.json")
            freeze = {"price_quote":{"BTC":"USDT"},"intraday_map":{"day_3_4":"BTC $90–$110"}}
            freeze_path = folder/"CYCLE_NAVIGATOR_FORECAST_FREEZE.json"
            freeze_hash = write(repo,freeze_path,freeze)
            bands = {"DUMB1.5":{"low":85,"high":115},"DUMB2.0":{"low":80,"high":120},
                     "PREVWK":{"low":90,"high":110}}
            clock = self.row["generated_unix"]
            snapshot = {"contract":"CN_RANGE_BENCHMARK_FREEZE_v1","status":"FROZEN_RETAINED_SNAPSHOT",
                        "scientific_admission":False,"generated_unix":clock,"quote_unit":"USDT",
                        "history_days":63,"assets":{"BTC":bands}}
            snapshot_hash = hashlib.sha256(json.dumps(snapshot,sort_keys=True,separators=(",",":")).encode()).hexdigest()
            snapshot["snapshot_sha256"] = snapshot_hash
            manifest = {"contract":"CYCLE_NAVIGATOR_SOURCE_MANIFEST_v1","issue_number":36,"public_issue_number":35,
                        "target_iso_year":2026,"target_iso_week":48,"range_benchmark_freeze":snapshot}
            manifest_hash = write(repo,folder/"CYCLE_NAVIGATOR_SOURCE_MANIFEST.json",manifest)
            write(repo,folder/"CYCLE_NAVIGATOR_MACHINE_PACKAGE.json",{
                "contract":"CYCLE_NAVIGATOR_MACHINE_PACKAGE_v1","issue_number":36,"public_issue_number":35,
                "generated_unix":clock,"source_manifest_sha256":manifest_hash,"forecast_freeze":freeze})
            binding_path = folder/"CYCLE_NAVIGATOR_PUBLIC_SERIES_BINDING.json"
            write(repo,binding_path,{"contract":"CN_PUBLIC_SERIES_BINDING_v1","forecast_week":"2026-W48",
                                    "public_issue_number":35,"machine_issue_number":36})
            receipt_path = folder/"CYCLE_NAVIGATOR_SITE_PUBLIC_FREEZE_RECEIPT.json"
            policy = "FIRST_COMPLETE_UTC_HOUR_AT_OR_AFTER_FREEZE_v1"
            formula = "70pct_containment_plus_30pct_jaccard"
            valid_from = "2026-11-23T10:00:00Z"
            write(repo,receipt_path,{"contract":"CN_SITE_PUBLIC_FREEZE_RECEIPT_v1","status":"SITE_FROZEN_SOURCE_OF_RECORD",
                                    "forecast_week":"2026-W48","frozen_unix":clock,"public_issue_number":35,
                                    "machine_issue_number":36,"source_forecast_freeze_path":freeze_path.as_posix(),
                                    "source_forecast_freeze_sha256":freeze_hash,"source_binding_path":binding_path.as_posix(),
                                    "source_manifest_sha256":manifest_hash,"range_benchmark_snapshot_sha256":snapshot_hash,
                                    "score_formula":formula,"score_window_policy":policy,"scoring_valid_from_utc":valid_from})
            write(repo,actual,{"contract":"WEEKLY_RAW_CALIBRATION_PACK_v3","readiness":"READY","iso_year":2026,"iso_week":48,
                               "generated_at_utc":"2026-11-30T08:00:00Z",
                               "hourly_gap_diagnostics":{"observed_hours":168,"missing_hour_count":0},
                               "hourly_sequence":{"spot_complete_hours":168,"spot_flow_readback":{"BTC":{"symbol":"BTCUSDT","quote_unit":"USDT"}},
                                                  "btc":{"week_range":{"open":100,"high":110,"low":90,"close":100}}},
                               "enriched_hourly_path":actual_csv.relative_to("03_DAILY_CAPTURE_LOGS").as_posix()})
            p=repo/actual_csv
            p.parent.mkdir(parents=True,exist_ok=True)
            monday=datetime(2026,11,23,tzinfo=timezone.utc)
            with p.open("w",newline="") as handle:
                fields=["timestamp_utc","source_window_end_utc","spot_status","btc_open","btc_high","btc_low","btc_close"]
                w=csv.DictWriter(handle,fieldnames=fields)
                w.writeheader()
                for i in range(168):
                    at=monday+timedelta(hours=i)
                    w.writerow(dict(timestamp_utc=at.isoformat().replace("+00:00","Z"),
                                    source_window_end_utc=(at+timedelta(hours=1)).isoformat().replace("+00:00","Z"),
                                    spot_status="PASS",btc_open=100,btc_high=110,btc_low=90,btc_close=100))
            write(repo,score_path,{"contract":"CN_PUBLIC_WEEKLY_SCORECARD_v1","status":"FINAL_DUAL_TRACK",
                "forecast_week":"2026-W48","outcome_week":"2026-W48","public_issue_number":35,
                "lineage":{"machine_issue_number":36,"public_proof":{"channel":"SITE_SOURCE_OF_RECORD",
                           "freeze_sha256":freeze_hash,"receipt":receipt_path.as_posix()}},
                "price_range_precision":{"source":"05_CYCLE_NAVIGATOR/forward_range_ledger/CN_FORWARD_RANGE_LEDGER_v2.jsonl",
                    "actuals":actual.as_posix(),"actuals_hourly_coverage":168,"formula":formula,
                    "score_window_policy":policy,"scoring_valid_from_utc":valid_from,
                    "rows":[{"asset":"BTC","window":"day_3_4","forecast_low":90,"forecast_high":110,
                             "actual_low":90,"actual_high":110,"score":100.0,"score_window_policy":policy}]}})
            row=dict(self.row,**bands,forecast_low=90,forecast_high=110,baseline_snapshot_sha256=snapshot_hash,
                     baseline_quote_unit="USDT")
            out=join_diagnostics(repo,[row],self.now)
            self.assertEqual(out["joined_rows"],1,out)
            self.assertEqual(out["rows"][0]["CN"],100.0)
            self.assertEqual(out["rows"][0]["benchmarks"],{"DUMB1.5":90.0,"DUMB2.0":85.0,"PREVWK":100.0})
            self.assertEqual(out["scientifically_eligible_rows"],0)
            forged=dict(row,**{"DUMB1.5":{"low":90,"high":110}})
            self.assertEqual(join_diagnostics(repo,[forged],self.now)["excluded"],{"BASELINE_VALUES_MISMATCH":1})
            manifest["range_benchmark_freeze"]["history_days"]=64
            write(repo,folder/"CYCLE_NAVIGATOR_SOURCE_MANIFEST.json",manifest)
            self.assertEqual(join_diagnostics(repo,[row],self.now)["excluded"],{"FREEZE_RECEIPT_MISMATCH":1})

    def test_diagnostic_result_never_admits(self):
        with TemporaryDirectory() as tmp, patch("scripts.cycle_navigator.range_benchmark_outcome_join._join",return_value={"CN":100}) as join:
            out=join_diagnostics(Path(tmp),[self.row],self.now)
            join.assert_called_once()
            self.assertEqual(out["joined_rows"],1)
            self.assertEqual(out["scientifically_eligible_rows"],0)
            self.assertFalse(out["independence_attested"])

if __name__=="__main__":
    unittest.main()
