from __future__ import annotations

import unittest
from datetime import timedelta

from scripts.experiments import pdlt_discovery as discovery
from scripts.experiments import pdlt_v1_1 as prereg


class PDLTMethodsHardeningTests(unittest.TestCase):
    def test_discovery_family_is_full_120_rule_search(self):
        self.assertEqual(discovery.DISCOVERY_FAMILY_SIZE, 120)
        self.assertEqual(prereg.DISCOVERY_METHODS["enumerated_rule_count"], 120)
        self.assertEqual(prereg.DISCOVERY_METHODS["single_rules"], 30)
        self.assertEqual(prereg.DISCOVERY_METHODS["pair_rules"], 90)

    def test_fixed_split_has_full_14d_purge_and_is_not_row_fraction(self):
        train_end = discovery.ts(discovery.TRAIN_END_UTC)
        holdout_start = discovery.ts(discovery.HOLDOUT_START_UTC)
        self.assertEqual((holdout_start - train_end), timedelta(hours=336))
        self.assertEqual(discovery.PURGE_HOURS, 336)
        self.assertEqual(prereg.DISCOVERY_METHODS["purge_hours"], 336)

    def test_holdout_uses_frozen_training_probability_and_can_be_worse_than_baseline(self):
        rows = []
        # Eight fired rows contain a 50/50 outcome mix. A training-derived 0.90
        # probability is therefore worse than the 0.50 baseline on this holdout.
        for i, event in enumerate([0, 1, 0, 1, 0, 1, 0, 1, 0, 1]):
            rows.append({
                "deltas": {"score": -1.0 if i < 8 else 1.0},
                "event72": event,
                "event7d": 0,
                "event14d": 0,
            })
        baseline = {
            "p_pullback_72h": 0.50,
            "p_heavy_pullback_7d": 0.10,
            "p_persistent_distribution_14d": 0.10,
        }
        conditions = [{"field": "score", "threshold": 0.0}]
        fixed = {
            "p_pullback_72h": 0.90,
            "p_heavy_pullback_7d": 0.10,
            "p_persistent_distribution_14d": 0.10,
        }
        value = discovery.candidate_metrics(rows, conditions, baseline, fixed_probabilities=fixed)
        self.assertEqual(value["fires"], 8)
        self.assertEqual(value["probability_source"], "FIXED_TRAIN_DERIVED")
        self.assertLess(value["brier_improvement72"], 0.0)

    def test_same_sample_empirical_probability_is_explicitly_discovery_only(self):
        rows = [
            {"deltas": {"score": -1.0}, "event72": event, "event7d": 0, "event14d": 0}
            for event in [0, 1, 0, 1, 0, 1, 0, 1]
        ]
        baseline = {
            "p_pullback_72h": 0.25,
            "p_heavy_pullback_7d": 0.10,
            "p_persistent_distribution_14d": 0.10,
        }
        value = discovery.candidate_metrics(rows, [{"field": "score", "threshold": 0.0}], baseline)
        self.assertEqual(value["probability_source"], "EMPIRICAL_SAME_SAMPLE_DISCOVERY_ONLY")

    def test_manifest_serializes_phase2_method_fields(self):
        cfg = prereg.load(prereg.Path("research/experiments/pdlt_v1_1/PDLT_CONFIG_v1_1.json"))
        manifest = prereg.make_manifest(cfg)
        self.assertEqual(manifest["manifest_schema_revision"], 2)
        self.assertEqual(manifest["secondary_contrasts"], cfg["secondary_contrasts"])
        self.assertEqual(manifest["evidence_gates"], cfg["evidence_gates"])
        self.assertEqual(manifest["candidate_caps"], cfg["candidate_caps"])
        self.assertEqual(manifest["discovery_methods"]["minimum_holdout_fires"], 8)
        self.assertEqual(manifest["discovery_methods"]["historical_holdout_role"], "PRE_PROSPECTIVE_SCREEN_ONLY_NOT_EVIDENCE")


if __name__ == "__main__":
    unittest.main()
