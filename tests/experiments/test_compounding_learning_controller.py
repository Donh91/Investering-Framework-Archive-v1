import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[2] / "scripts" / "research"))
import compounding_learning_controller as controller

UTC = timezone.utc


def policy():
    return {
        "contract": "COMPOUNDING_LEARNING_CONTROLLER_POLICY_v1",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "default_profile": "STANDARD",
        "profiles": controller.PROFILE_DEFAULTS,
        "max_checkpoint_candidates_per_run": 25,
        "canonical_effect": False,
        "automatic_promotion": False,
        "automatic_canonical_write": False,
        "portfolio_execution": False,
        "model_weight_change": False,
        "automatic_threshold_change": False,
        "automatic_weight_change": False,
        "automatic_market_rule_change": False,
        "retrospective_rescore_allowed": False,
        "frozen_parent_rewrite_allowed": False,
    }


def candidate(**overrides):
    row = {
        "candidate_id": "EC-1",
        "title": "Prospective X",
        "kind": "FORECAST_TEST",
        "created_at_utc": "2026-01-01T00:00:00Z",
        "state": "INCUBATING",
        "matured_outcome_count": 0,
        "observation_count": 1,
        "scientific_admission_status": "QUALIFIED_FOR_FORWARD_TEST",
    }
    row.update(overrides)
    return row


def frozen_plan():
    return {
        "problem_to_solve": "Does X add decision information beyond the frozen baseline?",
        "incremental_value_claim": "X adds prospective incremental value.",
        "baseline": ["CURRENT_FRAMEWORK_WITHOUT_CANDIDATE", "ALWAYS_WAIT"],
        "negative_controls": ["DETERMINISTIC_PLACEBO", "BEST_SINGLE_COMPONENT_CONTROL"],
        "regime_dependency": "CURRENT_OBSERVED_REGIME",
        "success_criteria": [
            "candidate beats the relevant baseline on prospective independent windows",
            "negative controls do not reproduce the claimed edge",
        ],
        "failure_criteria": [
            "no incremental value versus baseline",
            "placebo or negative control performs similarly",
        ],
        "kill_criteria": [
            "persistent redundancy after prospective comparison",
            "complexity cost exceeds measured incremental value",
        ],
        "complexity_tax": {"maintenance": "MEASURE", "source_fragility": "MEASURE"},
    }


def admission(**overrides):
    row = {
        "candidate_id": "EC-1",
        "status": "QUALIFIED_FOR_FORWARD_TEST",
        "historical_candidate_requalification": False,
        "semantic_fingerprint": "abc",
        "plan": frozen_plan(),
    }
    row.update(overrides)
    return {
        "contract": "EXPERIMENT_SCIENTIFIC_ADMISSION_REGISTRY_v1",
        "candidate_count": 1,
        "candidates": [row],
    }


def registry(row):
    return {
        "contract": "EXPERIMENT_LIFECYCLE_REGISTRY_v1",
        "candidate_count": 1,
        "candidates": [row],
    }


def adjudication(
    action="WAIT_FOR_MORE_PROSPECTIVE_EVIDENCE",
    state="INCUBATING",
    matured=0,
    admission_status="QUALIFIED_FOR_FORWARD_TEST",
):
    return {
        "contract": "UNIFIED_EXPERIMENTAL_LIFECYCLE_ADJUDICATION_v1",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "canonical_effect": False,
        "portfolio_execution": False,
        "automatic_threshold_change": False,
        "automatic_weight_change": False,
        "automatic_market_rule_change": False,
        "generated_at_utc": "2026-01-08T00:00:00Z",
        "candidate_actions": [
            {
                "candidate_id": "EC-1",
                "lifecycle_state": state,
                "matured_outcome_count": matured,
                "scientific_admission_status": admission_status,
                "selected_action": action,
                "reason": "owner verdict reason",
                "canonical_effect": False,
                "portfolio_execution": False,
            }
        ],
    }


class CompoundingLearningControllerTest(unittest.TestCase):
    def test_week_checkpoint_is_descriptive_only(self):
        packets, keys = controller.evaluate_candidates(
            registry(candidate()),
            admission(),
            adjudication(),
            policy(),
            {},
            datetime(2026, 1, 8, tzinfo=UTC),
        )
        self.assertEqual(len(packets), 1)
        self.assertIn("EC-1:CHECKPOINT:DAY:7", keys)
        self.assertFalse(packets[0]["proposal_eligible"])
        self.assertEqual(packets[0]["recommended_action"], "CONTINUE_OBSERVING")
        self.assertEqual(
            packets[0]["what_we_learned"]["claim_limit"],
            "NO_NEW_SCIENTIFIC_VERDICT_BY_COMPOUNDING_CONTROLLER",
        )
        self.assertFalse(packets[0]["canonical_effect"])
        self.assertFalse(packets[0]["portfolio_execution"])

    def test_full_long_and_confirmatory_checkpoint_schedule_is_exposed(self):
        expected = [7, 14, 30, 60, 90, 120, 180, 240]
        self.assertEqual(controller.PROFILE_DEFAULTS["LONG"]["day_checkpoints"], expected)
        self.assertEqual(
            controller.PROFILE_DEFAULTS["CONFIRMATORY"]["day_checkpoints"], expected
        )
        controller._validate_policy(policy())

    def test_matured_checkpoint_is_event_driven(self):
        row = candidate(created_at_utc="2026-01-07T00:00:00Z", matured_outcome_count=10)
        packets, keys = controller.evaluate_candidates(
            registry(row),
            admission(),
            adjudication(matured=10),
            policy(),
            {},
            datetime(2026, 1, 8, tzinfo=UTC),
        )
        self.assertEqual(len(packets), 1)
        self.assertIn("EC-1:CHECKPOINT:MATURED:5", keys)
        self.assertIn("EC-1:CHECKPOINT:MATURED:10", keys)

    def test_stale_adjudication_cannot_reinterpret_newer_registry(self):
        row = candidate(state="MATURED_SUPPORTED", matured_outcome_count=10)
        stale = adjudication(
            action="RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW",
            state="INCUBATING",
            matured=5,
        )
        packets, _ = controller.evaluate_candidates(
            registry(row),
            admission(),
            stale,
            policy(),
            {},
            datetime(2026, 1, 8, tzinfo=UTC),
        )
        self.assertEqual(
            packets[0]["learning_state"], "WAIT_FOR_REFRESHED_UNIFIED_ADJUDICATION"
        )
        self.assertFalse(packets[0]["proposal_eligible"])
        self.assertIsNone(packets[0]["what_we_learned"]["owner_action"])

    def test_supported_fresh_escalation_creates_information_rich_child_proposal_only(self):
        row = candidate(state="MATURED_SUPPORTED", matured_outcome_count=10)
        fresh = adjudication(
            action="RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW",
            state="MATURED_SUPPORTED",
            matured=10,
        )
        state, proposal = controller.build_state(
            registry(row),
            admission(),
            fresh,
            policy(),
            {},
            datetime(2026, 1, 8, tzinfo=UTC),
        )
        self.assertEqual(state["primary_action"], "RUN_INCREMENTAL_VALUE_TEST")
        self.assertEqual(proposal["parent_candidate_id"], "EC-1")
        self.assertEqual(
            proposal["proposal_status"],
            "PRE_VOI_CANDIDATE_ROUTE_THROUGH_EXISTING_GOVERNANCE",
        )
        self.assertTrue(proposal["uncertainty"]["problem_to_solve"])
        self.assertEqual(
            proposal["falsifier"],
            [
                "no incremental value versus baseline",
                "placebo or negative control performs similarly",
            ],
        )
        self.assertTrue(proposal["what_would_change_view"]["toward_more_support"])
        self.assertTrue(proposal["why_information_rich"])
        self.assertEqual(
            proposal["selection_claim_limit"],
            "PRE_VOI_CANDIDATE_NOT_FINAL_SCIENTIFIC_OR_RESOURCE_PRIORITY",
        )
        self.assertFalse(proposal["child_may_mutate_parent"])
        self.assertFalse(proposal["new_test_automatically_admitted"])
        self.assertFalse(proposal["automatic_promotion"])

    def test_missing_admission_detail_does_not_invent_falsifier(self):
        bare = admission()
        bare["candidates"][0].pop("plan")
        with patch.object(
            controller,
            "_admission_detail",
            return_value=({}, "ADMISSION_DETAIL_UNAVAILABLE"),
        ):
            packets, _ = controller.evaluate_candidates(
                registry(candidate()),
                bare,
                adjudication(),
                policy(),
                {},
                datetime(2026, 1, 8, tzinfo=UTC),
            )
        self.assertEqual(packets[0]["falsifier"], [])
        self.assertEqual(
            packets[0]["admission_plan_status"], "ADMISSION_DETAIL_UNAVAILABLE"
        )
        self.assertIn("must not invent", packets[0]["why_information_rich"])

    def test_duplicate_never_spawns_child(self):
        duplicate_admission = admission(status="SEMANTIC_DUPLICATE_KEEP_SHADOW")
        duplicate_adjudication = adjudication(
            action="ARCHIVE_ONLY_DUPLICATE",
            admission_status="SEMANTIC_DUPLICATE_KEEP_SHADOW",
        )
        state, proposal = controller.build_state(
            registry(candidate(matured_outcome_count=10)),
            duplicate_admission,
            duplicate_adjudication,
            policy(),
            {},
            datetime(2026, 1, 8, tzinfo=UTC),
        )
        self.assertEqual(state["primary_action"], "CONTINUE_OBSERVING")
        self.assertEqual(
            proposal["proposal_status"], "NO_NEW_SCIENTIFICALLY_ELIGIBLE_CHILD_TEST"
        )

    def test_failure_review_can_only_propose_new_regime_stress_child(self):
        row = candidate(state="MATURED_NOT_SUPPORTED", matured_outcome_count=10)
        fresh = adjudication(
            action="RUN_FAILURE_AND_RETIREMENT_REVIEW",
            state="MATURED_NOT_SUPPORTED",
            matured=10,
        )
        state, proposal = controller.build_state(
            registry(row),
            admission(),
            fresh,
            policy(),
            {},
            datetime(2026, 1, 8, tzinfo=UTC),
        )
        self.assertEqual(state["primary_action"], "STRESS_TEST_REGIME_SPECIFICITY")
        self.assertIn("REGIME_SPECIFIC", proposal["next_falsifiable_question"])
        self.assertFalse(proposal["retrospective_rescore_allowed"])
        self.assertFalse(proposal["automatic_parameter_search"])
        self.assertFalse(proposal["child_may_mutate_parent"])

    def test_negative_learning_priority_precedes_supportive_replication(self):
        self.assertLess(
            controller.LEARNING_PRIORITY["NEGATIVE_EVIDENCE_NEEDS_FAILURE_REVIEW"],
            controller.LEARNING_PRIORITY["SUPPORTED_NEEDS_INCREMENTAL_VALUE"],
        )

    def test_historical_requalification_has_no_retrospective_day_clock(self):
        old = candidate(created_at_utc="2020-01-01T00:00:00Z")
        historical = admission(historical_candidate_requalification=True)
        packets, keys = controller.evaluate_candidates(
            registry(old),
            historical,
            adjudication(),
            policy(),
            {},
            datetime(2026, 1, 8, tzinfo=UTC),
        )
        self.assertEqual(packets, [])
        self.assertEqual(keys, [])

    def test_emitted_checkpoint_is_one_shot(self):
        previous = {"emitted_event_keys": ["EC-1:CHECKPOINT:DAY:7"]}
        packets, keys = controller.evaluate_candidates(
            registry(candidate()),
            admission(),
            adjudication(),
            policy(),
            previous,
            datetime(2026, 1, 8, tzinfo=UTC),
        )
        self.assertEqual(packets, [])
        self.assertEqual(keys, [])

    def test_t13_operational_checkpoints_include_240_but_never_emit_interim_skill_inference(self):
        activation = {
            "study_id": "FORECAST_SKILL_CONFIRMATORY_V1_3_1",
            "cohort_start_utc": "2026-09-05T00:00:00Z",
            "cohort_end_utc_exclusive": "2027-05-03T00:00:00Z",
            "freeze_accrual_window_days": 240,
            "forecast_skill_status": "UNPROVEN",
            "outcome_data_read": False,
        }
        study = {
            "forecast_skill_status": "UNPROVEN",
            "status": "NOT_STARTED_SCIENTIFIC_FIREWALL",
            "outcome_data_read": False,
        }

        def fake_load(path, default=None):
            if path == controller.T13_ACTIVATION:
                return activation
            if path == controller.T13_STATUS:
                return study
            return default

        with patch.object(controller, "load_json", side_effect=fake_load):
            pre = controller._t13_status(datetime(2026, 9, 4, 23, 5, tzinfo=UTC))
            day30 = controller._t13_status(datetime(2026, 10, 4, 12, tzinfo=UTC))
            closed = controller._t13_status(datetime(2027, 5, 3, 0, 0, tzinfo=UTC))

        self.assertEqual(pre["phase"], "PRE_START")
        self.assertIn(30, day30["operational_checkpoint_days_reached"])
        self.assertIn(240, closed["operational_checkpoint_days_reached"])
        self.assertEqual(
            closed["day_240_meaning"],
            "FINAL_EVALUATION_READINESS_ONLY_UNTIL_CONFIRMATORY_OWNER_RUNS",
        )
        for result in (pre, day30, closed):
            self.assertFalse(result["interim_performance_inference_allowed"])
            self.assertFalse(result["scientific_method_change_allowed"])
            self.assertFalse(result["automatic_child_experiment_allowed"])
            self.assertTrue(result.get("checkpoint_may_not_emit_skill_verdict", True))

    def test_policy_firewall_fails_closed(self):
        bad = policy()
        bad["automatic_promotion"] = True
        with self.assertRaises(RuntimeError):
            controller._validate_policy(bad)

    def test_policy_rejects_missing_long_checkpoint_schedule(self):
        bad = policy()
        bad["profiles"] = {k: dict(v) for k, v in controller.PROFILE_DEFAULTS.items()}
        bad["profiles"]["LONG"] = {
            "day_checkpoints": [30, 60, 90, 120, 180, 240],
            "matured_checkpoints": [10, 25, 50, 100],
        }
        with self.assertRaises(RuntimeError):
            controller._validate_policy(bad)


if __name__ == "__main__":
    unittest.main()
