import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[2]
SCRIPT = ROOT / "scripts" / "experiments" / "factor_test_admission.py"
E1 = ROOT / "04_RESEARCH_LAB" / "auto_trading" / "experiments" / "E1_LEAKAGE_VALIDATION_RESULT_v1.json"


def load_module():
    spec = importlib.util.spec_from_file_location("factor_test_admission", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def factor_spec():
    return {
        "title": "AT-HYP-0019 rolling normalization factor comparison",
        "hypothesis": "Rolling normalization may produce more stable predictive information than raw sentiment levels.",
        "falsifier": "Independent OOS evidence fails the frozen positive sign-stability gate versus RAW.",
        "horizon_days": 1,
        "regime_dependency": "REGIME_AGNOSTIC_RESEARCH",
        "novelty_reason": "AUTO_TRADING_AT_HYP_0019",
        "revisit_conditions": ["Independent point-in-time dataset becomes available"],
        "evidence_basis": ["04_RESEARCH_LAB/auto_trading/THEORY_LEDGER.md#AT-HYP-0019"],
        "factor_design": {
            "theory_id": "AT-HYP-0019",
            "feature_field": "score",
            "label_field": "future_real_price_return_24h",
            "source_repository": "Donh91/secrets",
            "source_path": "RESTRICTED_SOURCE_BOUND_AT_TRIAL_TIME",
            "source_commit": "PINNED_AT_TRIAL_TIME",
            "source_sha256": "PINNED_AT_TRIAL_TIME",
            "rolling_window_hours": 24,
            "forward_horizon_hours": 24,
            "transforms": ["RAW", "ROLLING_PERCENTILE", "ZSCORE", "DISTANCE_FROM_EXTREMA"],
            "primary_metric": "OOS_ORIENTED_SPEARMAN_IC",
            "support_rule": {
                "combined_oos_ic_positive": True,
                "btc_oos_ic_positive": True,
                "eth_oos_ic_positive": True,
                "combined_quartile_spread_positive": True,
                "cross_symbol_non_degradation_vs_raw": True,
                "min_combined_ic_improvement_over_raw": 0.02,
            },
            "proposal_trial_n": 4,
            "monotonic_trial_n_required": True,
            "failed_and_abandoned_attempts_remain_counted": True,
            "point_in_time_required": True,
            "independent_evidence_required_for_promotion": True,
        },
    }


class FactorTestAdmissionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()
        cls.e1 = json.loads(E1.read_text())

    def test_factor_test_gets_truthful_existing_owner_candidate_and_admission(self):
        candidate, admission = self.mod.build_records(factor_spec(), self.e1, "2026-09-13T00:10:00Z")
        self.assertEqual(candidate["contract"], "EXPERIMENT_CANDIDATE_v1")
        self.assertEqual(candidate["spec"]["kind"], "FACTOR_TEST")
        self.assertEqual(admission["contract"], "EXPERIMENT_SCIENTIFIC_ADMISSION_v1")
        self.assertEqual(admission["status"], "QUALIFIED_FOR_FORWARD_TEST")
        self.assertFalse(admission["authority"]["portfolio_execution"])
        self.assertFalse(admission["authority"]["automatic_promotion"])
        self.assertEqual(admission["plan"]["baseline"][0], "RAW_FEATURE_LEVEL")

    def test_identity_changes_when_factor_design_changes(self):
        candidate_a, _ = self.mod.build_records(factor_spec(), self.e1, "2026-09-13T00:10:00Z")
        changed = factor_spec()
        changed["factor_design"]["rolling_window_hours"] = 48
        candidate_b, _ = self.mod.build_records(changed, self.e1, "2026-09-13T00:10:00Z")
        self.assertNotEqual(candidate_a["candidate_id"], candidate_b["candidate_id"])

    def test_e1_pass_is_hard_gate(self):
        failed = dict(self.e1)
        failed["verdict"] = "FAIL"
        with self.assertRaisesRegex(ValueError, "E1_PASS_REQUIRED"):
            self.mod.build_records(factor_spec(), failed, "2026-09-13T00:10:00Z")

    def test_invalid_transform_or_trial_accounting_fails_closed(self):
        bad = factor_spec()
        bad["factor_design"]["transforms"] = ["RAW", "MAGIC"]
        with self.assertRaisesRegex(ValueError, "invalid_factor_transforms"):
            self.mod.build_records(bad, self.e1, "2026-09-13T00:10:00Z")
        bad = factor_spec()
        bad["factor_design"]["proposal_trial_n"] = 0
        with self.assertRaisesRegex(ValueError, "proposal_trial_n_required"):
            self.mod.build_records(bad, self.e1, "2026-09-13T00:10:00Z")

    def test_writes_into_existing_roots_and_refuses_rewrite(self):
        candidate, admission = self.mod.build_records(factor_spec(), self.e1, "2026-09-13T00:10:00Z")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            candidate_path, admission_path = self.mod.write_records(root / "research/experiment_lifecycle/candidates", root / "research/experiment_lifecycle/admission", candidate, admission)
            self.assertTrue(candidate_path.exists())
            self.assertTrue(admission_path.exists())
            with self.assertRaises(FileExistsError):
                self.mod.write_records(root / "research/experiment_lifecycle/candidates", root / "research/experiment_lifecycle/admission", candidate, admission)

    def test_base_kind_set_is_not_mutated_by_extension(self):
        original = set(self.mod.base.KINDS)
        self.mod.normalize_spec(factor_spec())
        self.assertEqual(original, set(self.mod.base.KINDS))
        self.assertNotIn("FACTOR_TEST", self.mod.base.KINDS)


if __name__ == "__main__":
    unittest.main()
