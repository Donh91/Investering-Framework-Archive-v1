import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/experiments"))
import compounding_learning_engine as clc
import compounding_learning_utils as clu
clc.validate_policy = clu.validate_policy
UTC = timezone.utc

POLICY = {
    "contract": "COMPOUNDING_LEARNING_POLICY_v1",
    "authority": "RESEARCH_ONLY_NON_CANONICAL",
    "canonical_effect": False,
    "portfolio_execution": False,
    "automatic_promotion": False,
    "automatic_canonical_write": False,
    "automatic_market_rule_change": False,
    "automatic_threshold_change": False,
    "automatic_weight_change": False,
    "automatic_child_registration": False,
    "fast_horizon_days_max": 7,
    "medium_horizon_days_max": 30,
    "max_checkpoint_candidates_per_run": 25,
    "confirmatory_candidate_ids": [],
    "profiles": {
        "FAST": {"day_checkpoints": [7, 14, 30], "matured_outcome_checkpoints": [3, 5, 10], "recurring_day_step_after_max": 30, "recurring_matured_step_after_max": 10},
        "MEDIUM": {"day_checkpoints": [30, 60, 90], "matured_outcome_checkpoints": [5, 10, 20], "recurring_day_step_after_max": 90, "recurring_matured_step_after_max": 20},
        "LONG": {"day_checkpoints": [60, 120, 180, 240], "matured_outcome_checkpoints": [5, 10, 25, 50], "recurring_day_step_after_max": 120, "recurring_matured_step_after_max": 50},
        "CONFIRMATORY": {"day_checkpoints": [30, 60, 90, 120, 180], "matured_outcome_checkpoints": [], "recurring_day_step_after_max": 0, "recurring_matured_step_after_max": 0, "interim_performance_inference_allowed": False},
    },
}


def registry(candidates):
    return {"contract": "EXPERIMENT_LIFECYCLE_REGISTRY_v1", "authority": "SHADOW_ONLY_NO_AUTOMATIC_PROMOTION", "candidates": candidates, "candidate_count": len(candidates)}


def admissions(rows):
    return {"contract": "EXPERIMENT_SCIENTIFIC_ADMISSION_REGISTRY_v1", "candidates": rows}


def adjudication(rows):
    return {"contract": "UNIFIED_EXPERIMENTAL_LIFECYCLE_ADJUDICATION_v1", "candidate_actions": rows}


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.as_of = datetime(2026, 9, 10, tzinfo=UTC)

    def test_bootstrap_never_replays_historical_checkpoints(self):
        cand = {"candidate_id": "C1", "created_at_utc": "2026-07-01T00:00:00Z", "kind": "FORECAST_TEST", "horizon_days": 7, "state": "MATURED_SUPPORTED", "matured_outcome_count": 15, "observation_count": 50}
        state, nxt, changed = clc.build_state(registry([cand]), admissions([{"candidate_id": "C1", "status": "QUALIFIED_FOR_FORWARD_TEST"}]), adjudication([{"candidate_id": "C1", "selected_action": "RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW"}]), {}, POLICY, {}, self.as_of)
        self.assertTrue(changed)
        self.assertEqual(state["status"], "ACTIVE_BOOTSTRAPPED_NO_RETROACTIVE_CHECKPOINTS")
        self.assertEqual(state["new_checkpoint_candidate_count"], 0)
        self.assertEqual(nxt["proposal_status"], "BOOTSTRAP_NO_RETROACTIVE_PROPOSAL")
        self.assertGreater(len(state["checkpoint_keys_seen"]), 0)

    def test_new_post_activation_crossing_routes_support_to_incremental_value_not_promotion(self):
        cand0 = {"candidate_id": "C1", "created_at_utc": "2026-09-01T00:00:00Z", "kind": "FORECAST_TEST", "horizon_days": 7, "state": "WAITING_FOR_MATURITY", "matured_outcome_count": 2, "observation_count": 8}
        base, _, _ = clc.build_state(registry([cand0]), admissions([{"candidate_id": "C1", "status": "QUALIFIED_FOR_FORWARD_TEST"}]), adjudication([]), {}, POLICY, {}, datetime(2026, 9, 6, tzinfo=UTC))
        cand1 = dict(cand0, state="MATURED_SUPPORTED", matured_outcome_count=3, observation_count=10)
        state, nxt, _ = clc.build_state(registry([cand1]), admissions([{"candidate_id": "C1", "status": "QUALIFIED_FOR_FORWARD_TEST"}]), adjudication([{"candidate_id": "C1", "selected_action": "RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW"}]), {}, POLICY, base, datetime(2026, 9, 8, tzinfo=UTC))
        self.assertEqual(state["primary_action"], "RUN_INCREMENTAL_VALUE_TEST")
        self.assertEqual(state["checkpoint_queue"][0]["learning_verdict"], "PROMISING")
        self.assertEqual(nxt["proposal_kind"], "INCREMENTAL_VALUE_CHILD")
        self.assertFalse(nxt["automatic_candidate_registration"])
        self.assertFalse(nxt["automatic_promotion"])

    def test_duplicate_cannot_spawn_child(self):
        cand0 = {"candidate_id": "D1", "created_at_utc": "2026-09-01T00:00:00Z", "kind": "SENSOR_COMBINATION", "horizon_days": 7, "state": "INCUBATING", "matured_outcome_count": 2, "observation_count": 5}
        base, _, _ = clc.build_state(registry([cand0]), admissions([{"candidate_id": "D1", "status": "SEMANTIC_DUPLICATE_KEEP_SHADOW"}]), adjudication([]), {}, POLICY, {}, datetime(2026, 9, 6, tzinfo=UTC))
        cand1 = dict(cand0, matured_outcome_count=3)
        state, nxt, _ = clc.build_state(registry([cand1]), admissions([{"candidate_id": "D1", "status": "SEMANTIC_DUPLICATE_KEEP_SHADOW"}]), adjudication([{"candidate_id": "D1", "selected_action": "ARCHIVE_ONLY_DUPLICATE"}]), {}, POLICY, base, datetime(2026, 9, 8, tzinfo=UTC))
        self.assertEqual(state["checkpoint_queue"][0]["learning_verdict"], "REDUNDANT")
        self.assertEqual(nxt["proposal_status"], "NO_CHILD_REQUIRED")
        self.assertEqual(state["primary_action"], "DEPRIORITIZE")

    def test_matured_state_without_adjudication_cannot_be_called_edge(self):
        cand0 = {"candidate_id": "M1", "created_at_utc": "2026-09-01T00:00:00Z", "kind": "FORECAST_TEST", "horizon_days": 7, "state": "WAITING_FOR_MATURITY", "matured_outcome_count": 2, "observation_count": 5}
        base, _, _ = clc.build_state(registry([cand0]), admissions([{"candidate_id": "M1", "status": "QUALIFIED_FOR_FORWARD_TEST"}]), adjudication([]), {}, POLICY, {}, datetime(2026, 9, 6, tzinfo=UTC))
        cand1 = dict(cand0, state="MATURED_SUPPORTED", matured_outcome_count=3)
        state, _, _ = clc.build_state(registry([cand1]), admissions([{"candidate_id": "M1", "status": "QUALIFIED_FOR_FORWARD_TEST"}]), adjudication([]), {}, POLICY, base, datetime(2026, 9, 8, tzinfo=UTC))
        self.assertEqual(state["checkpoint_queue"][0]["learning_verdict"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(state["primary_action"], "CONTINUE_OBSERVING")

    def test_confirmatory_profile_is_health_only(self):
        policy = {**POLICY, "confirmatory_candidate_ids": ["TCONF"]}
        cand0 = {"candidate_id": "TCONF", "created_at_utc": "2026-07-01T00:00:00Z", "kind": "FORECAST_TEST", "horizon_days": 240, "state": "MATURED_SUPPORTED", "matured_outcome_count": 50, "observation_count": 100}
        base, _, _ = clc.build_state(registry([cand0]), admissions([{"candidate_id": "TCONF", "status": "QUALIFIED_FOR_FORWARD_TEST"}]), adjudication([{"candidate_id": "TCONF", "selected_action": "RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW"}]), {}, policy, {}, datetime(2026, 8, 1, tzinfo=UTC))
        state, nxt, _ = clc.build_state(registry([cand0]), admissions([{"candidate_id": "TCONF", "status": "QUALIFIED_FOR_FORWARD_TEST"}]), adjudication([{"candidate_id": "TCONF", "selected_action": "RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW"}]), {}, policy, base, datetime(2026, 9, 1, tzinfo=UTC))
        self.assertEqual(state["checkpoint_queue"][0]["learning_profile"], "CONFIRMATORY")
        self.assertEqual(state["checkpoint_queue"][0]["learning_verdict"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(state["primary_action"], "CONTINUE_OBSERVING")
        self.assertEqual(nxt["proposal_status"], "NO_CHILD_REQUIRED")

    def test_policy_firewall_rejects_auto_promotion(self):
        bad = dict(POLICY)
        bad["automatic_promotion"] = True
        with self.assertRaises(ValueError):
            clc.validate_policy(bad)

    def test_second_identical_schedule_run_is_byte_stable_noop(self):
        cand = {"candidate_id": "N1", "created_at_utc": "2026-09-01T00:00:00Z", "kind": "FORECAST_TEST", "horizon_days": 7, "state": "INCUBATING", "matured_outcome_count": 0, "observation_count": 5}
        base, _, _ = clc.build_state(registry([cand]), admissions([{"candidate_id": "N1", "status": "QUALIFIED_FOR_FORWARD_TEST"}]), adjudication([]), {}, POLICY, {}, datetime(2026, 9, 4, tzinfo=UTC))
        same, _, changed = clc.build_state(registry([cand]), admissions([{"candidate_id": "N1", "status": "QUALIFIED_FOR_FORWARD_TEST"}]), adjudication([]), {}, POLICY, base, datetime(2026, 9, 4, 0, 15, tzinfo=UTC))
        self.assertFalse(changed)
        self.assertEqual(same, base)

    def test_t13_is_not_a_runtime_input(self):
        source = (ROOT / "scripts/experiments/compounding_learning_engine.py").read_text() + (ROOT / "scripts/experiments/compounding_learning_utils.py").read_text() + (ROOT / "scripts/experiments/compounding_learning_controller.py").read_text()
        self.assertNotIn("COHORT_ACTIVATION_v1", source)
        self.assertNotIn("LATEST_STUDY_STATUS", source)
        self.assertIn('"t13_read_or_mutated_by_controller": False', source)


if __name__ == "__main__":
    unittest.main()
