"""Native, offline adversarial tests for original CN frozen ranges and risk replay."""
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.research import task2_realdata_challenger_w39_w46_v1 as m

ROOT = Path(__file__).resolve().parents[2]


class OriginalCNRealdataTests(unittest.TestCase):
    def test_original_source_contract_and_eligible_real_dataset(self):
        summary, rows = m.forecast_study(ROOT)
        self.assertEqual(summary["contract"], m.CONTRACT)
        self.assertEqual(summary["eligible_independent_week_groups"], 7)
        self.assertEqual(summary["eligible_asset_week_window_groups"], 28)
        self.assertEqual(len(rows), 112)
        self.assertEqual(len([r for r in rows if r["model"] == "ORIGINAL_CN"]), 28)
        self.assertGreater(summary["exclusions"].get("WINDOW_BEGAN_BEFORE_ISSUANCE", 0), 0)
        self.assertEqual(summary["exclusions"].get("UNMATURED_W46"), 8)
        for row in rows:
            self.assertIn(row["window"], ("day_3_4","day_5_7"))
            self.assertLessEqual(int(row["forecast_week"].split("-W")[1]),45)
            self.assertIsNone(row["provider_first_published_at"])
            self.assertIsNone(row["user_first_delivered_at"])
            self.assertGreater(row["anchor_last_known"], 0)
            self.assertGreater(row["forecast_high"], row["forecast_low"])

    def test_range_coverage_correct_and_nonprobabilistic(self):
        r=m.range_score(95.,105.,100.,106.,100.)
        self.assertFalse(r["full_extreme_containment"])
        self.assertAlmostEqual(r["tail_breach_pct_anchor"],1)
        self.assertAlmostEqual(r["normalized_width_pct"],10)
        self.assertAlmostEqual(r["width_penalty_a10_diagnostic"],30)

    def test_wide_band_pays_width_penalty(self):
        x=m.range_score(50.,150.,95.,105.,100.)
        y=m.range_score(94.,106.,95.,105.,100.)
        self.assertTrue(x["full_extreme_containment"])
        self.assertTrue(y["full_extreme_containment"])
        self.assertGreater(x["width_penalty_a10_diagnostic"], y["width_penalty_a10_diagnostic"])

    def test_price_zero_nan_bool_rejected(self):
        for v in (0, -2, float("nan"), True):
            with self.assertRaises(ValueError):
                m.range_score(1.,2.,1.,2.,v)

    def test_utc_mandatory(self):
        for t in ("2026-11-09T11:00:00", "2026-11-09T11:00:00+01:00"):
            with self.assertRaises(ValueError):
                m.stamp(t)
        self.assertEqual(m.stamp("2026-11-09T11:00:00Z").utcoffset().total_seconds(),0)

    def test_conflicting_original_freeze_rejected(self):
        a={"contract":"CN_FORWARD_RANGE_FREEZE_v2","forecast_week":"2026-W44",
           "asset":"BTC","window":"day_3_4","forecast_low":100,"forecast_high":110,
           "generated_unix":1792997869,"status":"FROZEN_PROSPECTIVE"}
        b=dict(a,forecast_low=90)
        with self.assertRaisesRegex(ValueError, "CONFLICTING_ORIGINAL_FREEZE"):
            m.unique_freezes([a,b])
        rows,dupes=m.unique_freezes([a,dict(a)])
        self.assertEqual(len(rows),1)
        self.assertEqual(dupes,1)

    def test_window_clock_is_monday_to_sunday(self):
        monday,next_monday=m.week_bounds("2026-W45")
        self.assertEqual(monday.isoformat(),"2026-11-02T00:00:00+00:00")
        self.assertEqual(next_monday.isoformat(),"2026-11-09T00:00:00+00:00")

    def test_missing_historical_maturity_source_cannot_score(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            p=root/m.LEDGER
            p.parent.mkdir(parents=True)
            p.write_text(json.dumps({"contract":"CN_FORWARD_RANGE_FREEZE_v2",
                "forecast_week":"2026-W45","asset":"BTC","window":"day_3_4",
                "forecast_low":70000,"forecast_high":80000,
                "generated_unix":1793607548,"status":"FROZEN_PROSPECTIVE"})+"\n")
            summ, rows=m.forecast_study(root)
            self.assertEqual(rows,[])
            self.assertEqual(summ["exclusions"]["MISSING_SOURCE_WEEK"],1)

    def test_risk_replay_actual_archived_hourly_data(self):
        summary, rows = m.hourly_study(ROOT)
        self.assertEqual(summary["status"],"RETROSPECTIVE_RESEARCH_ONLY")
        self.assertEqual(summary["hours_in_qualified_tape"],1176)
        self.assertEqual(summary["independent_weeks"],7)
        self.assertTrue(rows)
        for row in rows:
            self.assertIn(row["rule"],m.RISK_RULES)
            self.assertLessEqual(row["lookback_source_utc"],row["decision_utc"])
            self.assertIsNone(row["provider_first_published_utc"])
            self.assertEqual(row["claim_class"],"RETROSPECTIVE_SOURCE_WINDOW_PROXY_NOT_ISSUED_COMPASS")
            self.assertNotIn("2026-11-16",row["decision_utc"])

    def test_risk_source_missing_stops_not_fills(self):
        with tempfile.TemporaryDirectory() as td:
            summ,rows=m.hourly_study(Path(td))
            self.assertEqual(summ["status"],"BLOCKED_SOURCE_MISSING")
            self.assertEqual(rows,[])
            self.assertEqual(len(summ["missing"]),7)

    def test_full_decision_denominators_consistent(self):
        summ,rows=m.hourly_study(ROOT)
        for key,x in summ["risk_candidates"].items():
            self.assertEqual(x["TP"]+x["FP"]+x["TN"]+x["FN"],x["n_daily_decisions_correlated"])
            self.assertLessEqual(x["independent_positive_event_clusters_upper_bound"],x["n_positive_origin_days_correlated"])

    def test_final_w46_is_not_scored_and_no_portfolio_authority(self):
        s,rows=m.forecast_study(ROOT)
        self.assertTrue(s["no_model_promotion"])
        self.assertTrue(s["no_api_or_wallet"])
        self.assertFalse(any(r["forecast_week"]=="2026-W46" for r in rows))
        q,rows=m.hourly_study(ROOT)
        self.assertTrue(q["no_wallet_execution"])
        self.assertTrue(q["no_model_promotion"])
        self.assertEqual(q["multiple_testing"],"EXPLORATORY_NO_SIGNIFICANCE_OR_SCORE_PROMOTION")


if __name__=="__main__":
    unittest.main()
