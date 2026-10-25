"""Contract tests for source-integrity and nonpromotable historical controls."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "research"))
from cn_historical_location_baseline import build, _score, MATRIX_PATH


def write(root, path, obj):
    p = Path(root) / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, sort_keys=True) + "\n")
    raw = p.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


class RangeControlTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source_path = "05_CYCLE_NAVIGATOR/weekly/2026/W41/CYCLE_NAVIGATOR_FORECAST_FREEZE.json"
        self.week_path = "03_DAILY_CAPTURE_LOGS/weekly/2026/W41.json"
        self.prior_path = "03_DAILY_CAPTURE_LOGS/weekly/2026/W40.json"
        prior = {"iso_year": 2026, "iso_week": 40, "readiness":"READY", "generated_at_utc":"2026-10-05T06:09:56Z",
                 "hourly_gap_diagnostics":{"observed_hours":168},
                 "day_window_actuals":{"windows":{"DAY5_7":{"btc":{"close": 86530},"eth":{"close":2726.94}}}}}
        self.prior = prior
        self.matrixweek = {"forecast_week":"2026-W41","source_path":self.source_path,"source_git_blob_sha1":"",
          "freeze_recorded_at_utc":"2026-10-05T06:14:06Z","weekly_actuals_path":self.week_path,
          "weekly_actuals_git_blob_sha1":"","windows":[],"weekly_envelopes":[]}
        for window, n in (("DAY1_2",48),("DAY3_4",48),("DAY5_7",72)):
            for asset, low, high, actual_low, actual_high in (("BTC",82000,92000,80393.56,86999.11),("ETH",2560,2960,2406.11,2738)):
                self.matrixweek["windows"].append({"asset":asset,"window":window,"forecast_low":low,"forecast_high":high,
                    "actual_low":actual_low,"actual_high":actual_high,"joint_contained":False,"observed_hours":n})
        self.matrix = {"contract":"TASK2_CN_RETROSPECTIVE_ORIGINAL_TEXT_V1",
            "authority":"RESEARCH_ONLY_NOT_SOURCE_ADMITTED","summary":{"science_admitted_pairs":0},
            "weeks":[self.matrixweek]}
        self.write_all()

    def write_all(self):
        self.matrixweek["source_git_blob_sha1"] = write(self.root, self.source_path, {"original":"never_rewrite"})
        self.matrixweek["weekly_actuals_git_blob_sha1"] = write(self.root, self.week_path, {"observed":"immutable"})
        write(self.root, self.prior_path, self.prior)
        write(self.root, MATRIX_PATH, self.matrix)

    def test_basic_output_6_rows(self):
        v=build(self.root)
        self.assertEqual(v["summary"]["n_asset_windows"],6)
        self.assertEqual(v["summary"]["methods"]["cn_original"]["joint_contained"],0)
        self.assertEqual(v["scientifically_admitted_n"],0)
        self.assertEqual(v["rows"][0]["anchor"],86530)

    def test_issue_window_straddle_explicit(self):
        v=build(self.root)
        self.assertTrue(v["rows"][0]["full_iso_first_window_straddles_issue"])
        self.assertFalse(v["rows"][2]["full_iso_first_window_straddles_issue"])

    def test_exclude_degraded_previous_week_no_fake_baseline(self):
        self.prior["readiness"]="DEGRADED"
        self.write_all()
        v=build(self.root)
        self.assertEqual(v["summary"]["n_asset_windows"],0)
        self.assertEqual(v["excluded"][0]["reason"],"PREVIOUS_WEEK_NOT_FULLY_READY")

    def test_exclude_missing_candles(self):
        self.prior["hourly_gap_diagnostics"]["observed_hours"]=40
        self.write_all()
        self.assertEqual(build(self.root)["summary"]["n_asset_windows"],0)

    def test_detect_hindsight_prior_pack(self):
        self.prior["generated_at_utc"]="2026-10-05T08:10:00Z"
        self.write_all()
        with self.assertRaisesRegex(ValueError,"prior_pack_published_after_issue"):
            build(self.root)

    def test_detect_forecast_source_mutation(self):
        write(self.root, self.source_path, {"original":"tampered"})
        with self.assertRaisesRegex(ValueError,"forecast_origin_blob_mismatch"):
            build(self.root)

    def test_detect_actual_source_mutation(self):
        write(self.root, self.week_path, {"observed":"tampered"})
        with self.assertRaisesRegex(ValueError,"immutable_source_sha_mismatch"):
            build(self.root)

    def test_duplicate_row_rejected(self):
        self.matrixweek["windows"].append(copy.deepcopy(self.matrixweek["windows"][0]))
        self.write_all()
        with self.assertRaisesRegex(ValueError,"duplicate_original_forecast_row"):
            build(self.root)

    def test_tampered_original_containment_rejected(self):
        self.matrixweek["windows"][0]["joint_contained"]=True
        self.write_all()
        with self.assertRaisesRegex(ValueError,"original_containment_changed"):
            build(self.root)

    def test_invalid_bounds_rejected(self):
        self.matrixweek["windows"][0]["forecast_high"]=81000
        self.write_all()
        with self.assertRaisesRegex(ValueError,"inverted_range"):
            build(self.root)

    def test_naive_forecast_clock_rejected(self):
        self.matrixweek["freeze_recorded_at_utc"]="2026-10-05T06:14:06"
        self.write_all()
        with self.assertRaisesRegex(ValueError,"timezone_required"):
            build(self.root)

    def test_same_width_control_matched_and_wide_control_thirty_pct(self):
        v=build(self.root)
        for row in v["rows"]:
            self.assertAlmostEqual(row["same_width_prior_close"]["width_pct_of_previous_close"],row["cn_original"]["width_pct_of_previous_close"],places=5)
            self.assertAlmostEqual(row["fixed_15pct_prior_close"]["width_pct_of_previous_close"],30,places=5)

    def test_no_fake_proper_interval_score(self):
        v=build(self.root)
        self.assertNotIn("proper_interval_score",str(v))
        self.assertEqual(v["authority"],"RESEARCH_ONLY_DIAGNOSTIC_NOT_PIT_ADMITTED")

    def test_real_repo_regression_on_original_nine_week_panel(self):
        repo = Path(__file__).resolve().parents[2]
        if not (repo / MATRIX_PATH).is_file():
            self.skipTest("full GitHub checkout required for nine-week source-bound replay")
        v = build(repo)
        self.assertEqual(v["summary"]["n_asset_windows"], 48)
        self.assertEqual(v["summary"]["n_distinct_weeks"], 8)
        self.assertEqual(v["summary"]["methods"]["cn_original"]["joint_contained"], 27)
        self.assertEqual(v["summary"]["methods"]["same_width_prior_close"]["joint_contained"], 25)
        self.assertEqual(v["summary"]["methods"]["fixed_15pct_prior_close"]["joint_contained"], 44)
        self.assertEqual([x["week"] for x in v["excluded"]], ["2026-W33"])
        self.assertEqual(v["scientifically_admitted_n"], 0)

    def test_deterministic(self):
        self.assertEqual(build(self.root),build(self.root))

if __name__=="__main__":
    unittest.main()
