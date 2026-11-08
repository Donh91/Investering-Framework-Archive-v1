"""Synthetic-only leakage regressions for the existing public Trenches G2/G3 lifecycle ablation.

Not a wallet-profit study, source availability proof, licensed training approval,
chronological holdout or executable microcap sellability claim.
"""
from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from research.api_agent.meme_alpha.experiments import trenches_point_in_time_ablation_v1 as exp


def synthetic_panel(n: int = 150) -> tuple[pd.DataFrame, dict]:
    rows = []
    for cohort in ("tr", "te"):
        for i in range(n):
            rows.append({
                "mint": f"{cohort}-{i:04d}",
                "path_completed": int(i % 2 == 0),
                # Legitimate train-observed G2 field with varied numeric values.
                "holder_count": float(i + 1) if cohort == "tr" else str(i + 10),
                # Test-only positive observations MUST NOT select a feature.
                "smart_degen_count": np.nan if cohort == "tr" else float(i + 1),
                "fresh_wallet_rate": np.nan if cohort == "tr" else float(i) / n,
            })
    panel = pd.DataFrame(rows)
    split = {
        "in_sample": [f"tr-{i:04d}" for i in range(n)],
        "out_of_sample": [f"te-{i:04d}" for i in range(n)],
    }
    return panel, split


class TrenchesTrainOnlySplitTests(unittest.TestCase):
    def test_test_only_source_annotations_never_select_train_features(self):
        panel, split = synthetic_panel()
        # Previous selection on the FULL panel would select G3 using TEST rows.
        leaked = panel.copy()
        self.assertIn("smart_degen_count", exp.numericize(leaked, exp.SOURCE_G3_FIELDS))
        train, test, g2, g3 = exp.train_only_split_and_features(panel, split)
        self.assertEqual(len(train), 150)
        self.assertEqual(len(test), 150)
        self.assertIn("holder_count", g2)
        self.assertNotIn("fresh_wallet_rate", g2)
        self.assertNotIn("smart_degen_count", g3)

    def test_training_feature_not_dropped_using_invalid_test_distribution(self):
        panel, split = synthetic_panel()
        panel.loc[panel["mint"].str.startswith("te-"), "holder_count"] = "not-a-number"
        train, test, g2, _ = exp.train_only_split_and_features(panel, split)
        self.assertIn("holder_count", g2)
        self.assertEqual(int(train["holder_count"].notna().sum()), 150)
        self.assertTrue(test["holder_count"].isna().all())

    def test_identical_token_in_both_cohorts_fail_closed(self):
        panel, split = synthetic_panel()
        split["out_of_sample"].append(split["in_sample"][0])
        with self.assertRaisesRegex(RuntimeError, "TRAIN_TEST_MINT_OVERLAP"):
            exp.train_only_split_and_features(panel, split)

    def test_missing_or_malformed_cohort_definition_fail_closed(self):
        panel, split = synthetic_panel()
        for bad in (
            {"in_sample": split["in_sample"]},
            {"in_sample": "tr-0000", "out_of_sample": split["out_of_sample"]},
            {"in_sample": [None], "out_of_sample": split["out_of_sample"]},
            {"in_sample": [], "out_of_sample": split["out_of_sample"]},
        ):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(RuntimeError, "INVALID_TOKEN_SPLIT"):
                    exp.train_only_split_and_features(panel, bad)


if __name__ == "__main__":
    unittest.main()
