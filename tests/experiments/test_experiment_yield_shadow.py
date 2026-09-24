import unittest

from scripts.experiments.build_experiment_yield_shadow import build_shadow


class ExperimentYieldShadowTests(unittest.TestCase):
    def test_shadow_classifies_without_production_authority(self):
        registry = {"rows": [
            {"experiment_id": "blocked", "state": "WAITING_FOR_DATA"},
            {"experiment_id": "dup", "state": "PROPOSED", "duplicate_of": "x"},
            {"experiment_id": "quiet", "state": "MATURED_INCONCLUSIVE", "observation_count": 0},
            {"experiment_id": "base", "state": "MATURED_SUPPORTED"},
        ]}
        result = build_shadow(registry, {"rows": []})
        rows = {r["experiment_id"]: r for r in result["rows"]}
        self.assertEqual(rows["blocked"]["shadow_state"], "OBSERVE")
        self.assertEqual(rows["dup"]["shadow_state"], "OBSERVE")
        self.assertEqual(rows["quiet"]["shadow_state"], "OBSERVE")
        self.assertEqual(rows["base"]["shadow_state"], "SHADOW_BASELINE")
        self.assertEqual(result["mode"], "SHADOW_OBSERVE_ONLY")
        self.assertTrue(result["promotion_policy"]["natural_observation_window_required"])
        self.assertFalse(result["promotion_policy"]["automatic_retirement_allowed"])
        self.assertFalse(result["authority"]["production_suppression"])


if __name__ == "__main__":
    unittest.main()
