"""Falsification fixtures never certify first-known or a predictive edge."""
import copy
import unittest

from r1_falsification import analyze, execute, frozen_read, EXPLORATORY, ADMISSION, EXPLORATORY_BLOB, ADMISSION_BLOB


class R1FalsificationTests(unittest.TestCase):
    def fixture(self):
        return frozen_read(EXPLORATORY, EXPLORATORY_BLOB), frozen_read(ADMISSION, ADMISSION_BLOB)

    def test_exact_original_replay_is_zero_incremental_skill(self):
        r = execute()
        self.assertEqual((r["attempts"], r["original_matured_outcomes"], r["original_first_known_admitted"]), (11, 9, 0))
        self.assertEqual(r["independent_market_families_certified"], 0)
        self.assertFalse(r["scientific_information_edge_admitted"])
        self.assertFalse(r["investor_action_edge_admitted"])
        for asset, expected in (("BTC", 4), ("ETH", 3)):
            row = r["by_asset"][asset]
            self.assertEqual(row["matched_directional_pairs"], 8)
            self.assertEqual(row["excluded_original_abstention"], 1)
            self.assertEqual(row["forecast_identical_to_momentum"], 8)
            self.assertEqual(row["forecast_correct"], expected)
            self.assertEqual(row["previous_packet_momentum_correct"], expected)
            self.assertEqual(row["forecast_only_correct"], 0)
            self.assertEqual(row["baseline_only_correct"], 0)

    def test_missing_original_outcome_cannot_be_silently_added(self):
        a, b = self.fixture()
        altered = copy.deepcopy(a)
        altered["measured_exploratory_population"]["source_rows"].pop()
        with self.assertRaisesRegex(ValueError, "ROSTER"):
            analyze(altered, b)

    def test_forged_pit_admission_is_rejected(self):
        a, b = self.fixture()
        changed = copy.deepcopy(b)
        changed["rows"][0]["admissibility"] = "ADMITTED"
        with self.assertRaisesRegex(ValueError, "PRETENDED_PIT"):
            analyze(a, changed)

    def test_original_git_blob_mismatch_rejected(self):
        a, b = self.fixture()
        changed = copy.deepcopy(a)
        changed["measured_exploratory_population"]["source_rows"][0]["original_forecast_git_blob"] = "fake"
        with self.assertRaisesRegex(ValueError, "UNBOUND"):
            analyze(changed, b)

    def test_abstain_cannot_become_hidden_success(self):
        a, b = self.fixture()
        changed = copy.deepcopy(a)
        mixed = next(r for r in changed["measured_exploratory_population"]["source_rows"]
                     if r["original_next_12h_direction"] == "MIXED")
        mixed["original_next_12h_direction"] = "WINNER"
        with self.assertRaisesRegex(ValueError, "ABSTENTION"):
            analyze(changed, b)


if __name__ == "__main__":
    unittest.main()
