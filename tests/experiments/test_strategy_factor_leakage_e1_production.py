"""Regression tests for the E1X production temporal-integrity harness.

Offline and deterministic: repository data only, no network, no git history.
"""
import importlib.util
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parents[2]
SCRIPT = ROOT / "scripts" / "experiments" / "strategy_factor_leakage_e1_production.py"


def load_module():
    spec = importlib.util.spec_from_file_location("strategy_factor_leakage_e1_production", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["strategy_factor_leakage_e1_production"] = module
    spec.loader.exec_module(module)
    return module


class E1XHarnessControlsTest(unittest.TestCase):
    """The detector must be proven before any production verdict is trusted."""

    @classmethod
    def setUpClass(cls):
        cls.x = load_module()
        rows, _ = cls.x.load_hourly_rows()
        cls.rows = rows[-320:]
        cls.cg_rows, _ = cls.x.load_cg_monthly()

    def test_known_clean_causal_feature_passes_on_real_data(self):
        result = self.x.run_right_truncation(self.x.control_clean_trailing_mean(self.rows))
        self.assertEqual(result["observed"], "PASS")
        self.assertEqual(result["classifications"], ["NO_ISSUE"])
        self.assertGreater(result["output_comparisons"], 10)

    def test_seeded_future_leak_through_production_function_fails_with_one_record_suffix(self):
        result = self.x.run_right_truncation(self.x.control_seeded_negative_shift(self.rows))
        self.assertEqual(result["observed"], "FAIL")
        self.assertEqual(result["classifications"], ["TRUE_FUTURE_LEAKAGE"])
        minimized = [m["minimization"] for m in result["mismatches"] if m["minimization"].get("status") == "MINIMIZED"]
        self.assertTrue(minimized)
        self.assertTrue(all(m["minimal_future_suffix_records"] == 1 for m in minimized))

    def test_seeded_full_sample_normalization_fails(self):
        result = self.x.run_right_truncation(self.x.control_seeded_full_sample_zscore(self.cg_rows))
        self.assertTrue(result["expectation_met"])

    def test_seeded_recursive_indicator_is_not_called_leakage(self):
        right = self.x.run_right_truncation(self.x.control_seeded_ema_right(self.rows))
        self.assertEqual(right["observed"], "PASS")

    def test_seeded_warmup_drift_is_detected_and_classified_by_production_history(self):
        rows, _ = self.x.load_hourly_rows()
        short = self.x.run_warmup(self.x.control_seeded_ema_warmup(rows, 150))
        long = self.x.run_warmup(self.x.control_seeded_ema_warmup(rows, 1000))
        self.assertEqual(short["observed"], "DRIFT_DETECTED")
        self.assertEqual(short["classification"], "INSUFFICIENT_WARMUP")
        self.assertEqual(long["classification"], "RECURSIVE_CONVERGENCE_DRIFT")
        self.assertTrue(150 < short["worst_case_converged_from_warmup_records"] <= 1000)

    def test_nondeterminism_is_not_reported_as_leakage(self):
        result = self.x.run_right_truncation(self.x.control_seeded_nondeterminism(self.rows))
        self.assertEqual(result["classifications"], ["NONDETERMINISM"])

    def test_source_revision_is_classified_as_vintage_risk(self):
        result = self.x.run_right_truncation(self.x.control_source_revision(self.cg_rows))
        self.assertEqual(result["observed"], "FAIL")
        self.assertEqual(result["classifications"], ["SOURCE_VINTAGE_RISK"])

    def test_membership_difference_is_separated_from_survivorship_leak(self):
        obs, _ = self.x.load_pullback_observations()
        live = self.x.run_right_truncation(self.x.control_membership(obs, True))
        recomputed = self.x.run_right_truncation(self.x.control_membership(obs, False))
        late = self.x.run_right_truncation(self.x.control_late_listing(obs))
        self.assertEqual(live["classifications"], ["EXPECTED_CROSS_SECTIONAL_DIFFERENCE"])
        self.assertEqual(recomputed["classifications"], ["TRUE_FUTURE_LEAKAGE"])
        self.assertEqual(late["observed"], "PASS")


class E1XProductionFindingsTest(unittest.TestCase):
    """Mechanical reproductions of the audited findings on production code."""

    @classmethod
    def setUpClass(cls):
        cls.x = load_module()

    def test_pdlt_discovery_production_anchor_passes_after_completed_candle_fix(self):
        # PR #1214 anchors discovery on the last completed 4h candle.
        for variant in ("PRODUCTION", "ALIGNED_TIMESTAMPS"):
            with self.subTest(variant=variant):
                result = self.x.run_right_truncation(self.x.case_pdlt(variant))
                self.assertEqual(result["observed"], "PASS")
                self.assertEqual(result["classifications"], ["NO_ISSUE"])
                self.assertGreater(result["output_comparisons"], 10)

    def test_pdlt_seeded_legacy_open_time_anchor_is_still_detected(self):
        result = self.x.run_right_truncation(self.x.case_pdlt("SEEDED_LEGACY_OPEN_TIME_ANCHOR"))
        self.assertEqual(result["observed"], "FAIL")
        self.assertEqual(result["classifications"], ["TRUE_FUTURE_LEAKAGE"])
        fields = {d["field"] for m in result["mismatches"] for d in m["field_differences"]}
        self.assertTrue(fields)
        self.assertTrue(fields <= {"72h.start", "7d.start", "14d.start"})
        lead = result["contaminating_lead_seconds"]
        self.assertTrue(0 < lead["min"] <= lead["max"] <= 4 * 3600)

    def test_pdlt_label_time_truncation_is_blind_and_completed_candle_anchor_passes(self):
        blind = self.x.run_right_truncation(self.x.case_pdlt("LABEL_TIME_TRUNCATION_CONTROL"))
        repaired = self.x.run_right_truncation(self.x.case_pdlt("REPAIR_CANDIDATE_COMPLETED_CANDLE"))
        self.assertEqual(blind["observed"], "PASS")
        self.assertEqual(blind["classifications"], ["NO_ISSUE"])
        self.assertGreater(blind["output_comparisons"], 0)
        self.assertEqual(repaired["observed"], "PASS")
        self.assertEqual(repaired["classifications"], ["NO_ISSUE"])
        self.assertGreater(repaired["output_comparisons"], 0)

    def test_pdlt_repaired_production_is_not_reemitted_as_current_finding(self):
        current = self.x.run_right_truncation(self.x.case_pdlt("PRODUCTION"))
        findings = self.x.build_findings({
            "right_truncation": [current],
            "warmup": [],
            "source_vintage_probes": {},
            "audited_main_sha": "TEST",
        })
        self.assertFalse(any(row["finding_id"] == "E1X-F02" for row in findings))
        self.assertNotIn("RT-A07-AT-PDLT-DISCOVERY-PRODUCTION", self.x.ADJUDICATION)
        self.assertNotIn("RT-A07-AT-PDLT-DISCOVERY-SEEDED_LEGACY_OPEN_TIME_ANCHOR", self.x.ADJUDICATION)

    def test_copper_gold_event_study_respects_publication_knowledge_after_repair(self):
        knowledge, rule = self.x.cg_knowledge_time_factory()
        self.assertGreater(rule["minimum_observed_lag_seconds"], 0)
        start = date(2010, 7, 18)
        btc = [(start + timedelta(days=i), 100.0 + 0.01 * i) for i in range((date(2026, 9, 1) - start).days)]
        features = ROOT / self.x.CG_FEATURES
        peaks = [date(2021, 11, 8), date(2024, 3, 13)]
        claimed = self.x.run_right_truncation(self.x.case_event_study(features, btc, peaks, knowledge, rule, {}, True))
        published = self.x.run_right_truncation(self.x.case_event_study(features, btc, peaks, knowledge, rule, {}, False))
        self.assertEqual(claimed["observed"], "PASS")
        self.assertEqual(published["observed"], "PASS")
        self.assertEqual(published["classifications"], [])
        self.assertGreater(published["output_comparisons"], 0)

    def test_etf_trailing_documented_farside_timing(self):
        btc_rows, _ = self.x.load_etf_pack("btc")
        eth_rows, _ = self.x.load_etf_pack("eth")
        case = self.x.case_backtest_etf_trailing_documented_publication({"BTC": btc_rows, "ETH": eth_rows}, {})
        result = self.x.run_right_truncation(case)
        by_target = {m["target_utc"]: m["classification"] for m in result["mismatches"]}
        self.assertEqual(by_target.get("2026-07-16T20:00:00Z"), "TRUE_FUTURE_LEAKAGE")
        self.assertEqual(by_target.get("2026-07-17T05:00:00Z"), "SOURCE_VINTAGE_RISK")
        self.assertNotIn("2026-07-17T12:00:00Z", by_target)

    def test_clean_production_owners_pass(self):
        rows, hb = self.x.load_hourly_rows()
        cg_rows, cgb = self.x.load_cg_monthly()
        for case in (self.x.case_backtest_daily_utc(rows, hb), self.x.case_copper_gold_owner(cg_rows, cgb),
                     self.x.case_e2_features(rows, hb), self.x.case_intraday(rows, hb), self.x.case_n5("CAPTURE_TIME"), self.x.case_spar()):
            with self.subTest(case=case.case_id):
                self.assertEqual(self.x.run_right_truncation(case)["observed"], "PASS")

    def test_harness_never_reports_unexecuted_as_pass(self):
        result = self.x.run_right_truncation(self.x.RightTruncationCase(
            "EMPTY", "test", "none", "none", "no outputs", [], lambda recs: {}, expected=None))
        self.assertEqual(result["output_comparisons"], 0)
        self.assertEqual(result["observed"], "NOT_RUN")
        self.assertEqual(result["classifications"], ["UNKNOWN"])


if __name__ == "__main__":
    unittest.main()