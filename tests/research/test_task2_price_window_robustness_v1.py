"""Window-unit scientific denominator tests for ex-post price-only mechanics."""
import copy
import unittest
from datetime import datetime, timezone
from scripts.research import task2_price_window_robustness_v1 as m
from scripts.research import task2_archive_price_only_stress_v1 as prior
from scripts.research import task2_matched_windows_v1 as matched

T=int(datetime(2020,9,1,tzinfo=timezone.utc).timestamp()*1000)
def sample(prices=None):
    if prices is None:prices=[100.]*384
    return {"era":matched.ERA_NAMES[0],"source_segment":0,
            "score_start_utc":"2020-09-03T00:00:00+00:00",
            "score_end_utc":"2020-09-16T23:00:00+00:00",
            "tape":[(T+i*matched.HOUR_MS,float(p)) for i,p in enumerate(prices)]}

def fake_row(costmeans):
    return {"cost_arms":{f"{c:.3f}":{"mean_delta_pct_initial":v,
                                     "settings_with_sale":1}
                         for c,v in zip(prior.COSTS,costmeans)}}

class Task2WindowUnitRobustnessTests(unittest.TestCase):
    def test_flat_window_is_one_window_not_144_independent_trials(self):
        out=m.window_aggregates([sample()],prior.fixture_grid())
        self.assertEqual(len(out),1)
        self.assertEqual(out[0]["cost_arms"]["0.000"]["candidate_settings"],144)
        self.assertEqual(out[0]["cost_arms"]["0.000"]["settings_without_sale"],144)
        ag=m.aggregate_window_units(out)
        self.assertEqual(ag["0.000"]["window_unit_count"],1)
        self.assertEqual(ag["0.000"]["nominal_correlated_setting_window_cells"],144)
        self.assertEqual(ag["0.000"]["windows_mean_tied"],1)
        self.assertFalse(ag["0.000"]["scientific_independence_claim"])
    def test_small_window_frozen_576_all_costs(self):
        out=m.window_aggregates([sample()],prior.fixture_grid())
        for cost in prior.COSTS:self.assertEqual(sum(out[0]["cost_arms"][f"{cost:.3f}"][k] for k in
            ("positive_settings","negative_settings","ties")),144)
    def test_price_fall_can_create_one_sided_protection_not_prediction(self):
        x=[100.]*384;x[48]=93.;x[49]=88.;x[50:]=[70.]*(384-50)
        out=m.window_aggregates([sample(x)],prior.fixture_grid())[0]
        self.assertGreater(out["cost_arms"]["0.000"]["settings_with_sale"],0)
        self.assertGreater(out["cost_arms"]["0.000"]["positive_settings"],0)
    def test_very_high_cost_no_fabricated_skill(self):
        x=[100.]*384;x[48]=93.;x[49]=88.;x[50:]=[70.]*(384-50)
        out=m.window_aggregates([sample(x)],prior.fixture_grid())[0]
        ag=out["cost_arms"]
        self.assertLessEqual(sum(
            matched.evaluate_window(sample(x)["tape"],49,.25,24,.02)["delta_vs_hold_pct_initial"]
            for _ in range(1)),sum(
            matched.evaluate_window(sample(x)["tape"],49,.25,24,0)["delta_vs_hold_pct_initial"]
            for _ in range(1)))
        self.assertLessEqual(ag["0.020"]["positive_settings"],ag["0.000"]["positive_settings"])
    def test_paired_one_unit_per_window_not_config_count(self):
        items=[fake_row((5,4,3,2)),fake_row((-1,-2,-3,-4)),fake_row((0,0,0,0))]
        ag=m.aggregate_window_units(items)
        self.assertEqual(ag["0.000"]["window_unit_count"],3)
        self.assertEqual(ag["0.000"]["windows_mean_positive"],1)
        self.assertEqual(ag["0.000"]["windows_mean_negative"],1)
        self.assertEqual(ag["0.000"]["windows_mean_tied"],1)
        self.assertEqual(ag["0.000"]["leave_one_window_out_total"],3)
    def test_leave_one_out_detects_fragile_single_winner(self):
        items=[fake_row((5,5,5,5)),fake_row((-2,-2,-2,-2)),fake_row((-2,-2,-2,-2))]
        s=m.aggregate_window_units(items)["0.000"]
        self.assertEqual(s["leave_one_window_out_total"],3)
        self.assertEqual(s["leave_one_window_out_negative_means"],1)
        self.assertEqual(s["leave_one_window_out_positive_means"],2)
    def test_no_cost_first_arm_is_not_optimized_winner(self):
        self.assertFalse(m.AUTHORITY["original_forecasts_scored"])
        self.assertFalse(m.AUTHORITY["cfgi_tested"])
        self.assertFalse(m.AUTHORITY["out_of_sample"])
    def test_empty_window_cohort_rejected(self):
        with self.assertRaisesRegex(ValueError,"NO_WINDOW_COHORT"):
            m.aggregate_window_units([])
    def test_truncated_parameter_grid_rejected(self):
        with self.assertRaisesRegex(ValueError,"FROZEN_576_CONFIGS_REQUIRED"):
            m.window_aggregates([sample()],prior.fixture_grid()[:10])
    def test_settings_equal_nominal_sample_does_not_create_144_shock_families(self):
        self.assertEqual(m.CONFIRMED_SHOCK_FAMILIES,0)
    def test_full_original_archive_replay_if_available(self):
        if prior.PRICE.exists():
            full=m.execute()
            self.assertEqual(full["window_unit_count"],71)
            self.assertEqual(full["by_era"][matched.ERA_NAMES[0]]["windows"],30)
            self.assertEqual(full["by_era"][matched.ERA_NAMES[1]]["windows"],41)
            self.assertEqual(full["known_independent_shock_family_count"],0)
            self.assertFalse(full["hypothesis_freeze_before_outcomes"])
            self.assertIsNone(full["p_value"])
            self.assertIsNone(full["confidence_interval"])
            self.assertFalse(full["original_compass_or_cfgi_tested"])
            for era in matched.ERA_NAMES:
                for costdata in full["by_era"][era]["by_cost"].values():
                    n=costdata["window_unit_count"]
                    self.assertEqual(costdata["nominal_correlated_setting_window_cells"],n*144)
                    self.assertEqual(costdata["windows_mean_positive"]+
                        costdata["windows_mean_negative"]+costdata["windows_mean_tied"],n)
if __name__=="__main__":unittest.main()
