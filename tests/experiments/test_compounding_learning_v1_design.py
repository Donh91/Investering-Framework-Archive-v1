import sys
import tempfile
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
        "max_next_best_tests_per_run": 1,
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


def c(cid="EC-1", **kw):
    row = {"candidate_id": cid, "title": "Prospective X", "kind": "FORECAST_TEST", "created_at_utc": "2026-01-01T00:00:00Z", "state": "INCUBATING", "matured_outcome_count": 0, "observation_count": 1, "scientific_admission_status": "QUALIFIED_FOR_FORWARD_TEST"}
    row.update(kw); return row


def registry(*rows):
    return {"contract": "EXPERIMENT_LIFECYCLE_REGISTRY_v1", "candidate_count": len(rows), "candidates": list(rows)}


def admissions(*rows):
    return {"contract": "EXPERIMENT_SCIENTIFIC_ADMISSION_REGISTRY_v1", "candidate_count": len(rows), "candidates": list(rows)}


def a(cid="EC-1", fingerprint="abc", **kw):
    row = {"candidate_id": cid, "status": "QUALIFIED_FOR_FORWARD_TEST", "historical_candidate_requalification": False, "semantic_fingerprint": fingerprint}
    row.update(kw); return row


def ar(cid, action, state, matured):
    return {"candidate_id": cid, "lifecycle_state": state, "matured_outcome_count": matured, "scientific_admission_status": "QUALIFIED_FOR_FORWARD_TEST", "selected_action": action, "reason": "test", "canonical_effect": False, "portfolio_execution": False}


def adjudication(*rows):
    return {"contract": "UNIFIED_EXPERIMENTAL_LIFECYCLE_ADJUDICATION_v1", "authority": "RESEARCH_ONLY_NON_CANONICAL", "canonical_effect": False, "portfolio_execution": False, "automatic_threshold_change": False, "automatic_weight_change": False, "automatic_market_rule_change": False, "generated_at_utc": "2026-01-08T00:00:00Z", "candidate_actions": list(rows)}


class DesignTest(unittest.TestCase):
    def test_every_profile_has_full_descriptive_schedule(self):
        for profile in ("FAST", "STANDARD", "LONG", "CONFIRMATORY"):
            self.assertEqual(controller.PROFILE_DEFAULTS[profile]["day_checkpoints"], [7,14,30,60,90,120,180,240])

    def test_support_and_failure_same_semantic_family_becomes_contested(self):
        reg = registry(c("S", state="MATURED_SUPPORTED", matured_outcome_count=10, observation_count=20), c("F", state="MATURED_NOT_SUPPORTED", matured_outcome_count=10, observation_count=20))
        adm = admissions(a("S", "same"), a("F", "same"))
        adj = adjudication(ar("S", "RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW", "MATURED_SUPPORTED", 10), ar("F", "RUN_FAILURE_AND_RETIREMENT_REVIEW", "MATURED_NOT_SUPPORTED", 10))
        families = controller.build_hypothesis_families(reg, adm, adj)
        self.assertEqual(families[0]["current_evidence_status"], "CONTESTED")
        self.assertEqual(controller.generate_candidate_tests(families)[0]["test_type"], "CONTRADICTION_DISCRIMINATION_TEST")

    def test_next_test_has_uncertainty_falsifier_and_information_gain(self):
        reg = registry(c(state="MATURED_SUPPORTED", matured_outcome_count=10, observation_count=20))
        adm = admissions(a())
        adj = adjudication(ar("EC-1", "RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW", "MATURED_SUPPORTED", 10))
        state, proposal, backlog, event = controller._build_products(reg, adm, adj, policy(), {}, {}, datetime(2026,1,8,tzinfo=UTC))
        for key in ("problem_uncertainty", "hypothesis", "explicit_baseline", "explicit_falsifier", "what_would_change_our_view", "expected_information_gain", "required_data_lineage", "negative_controls", "revisit_condition"):
            self.assertTrue(proposal.get(key), key)
        self.assertEqual(proposal["expected_information_gain"]["score_interpretation"], "TRANSPARENT_HEURISTIC_FOR_RANKING_NOT_AN_EMPIRICAL_PROBABILITY")
        self.assertTrue(proposal["requires_scientific_admission"])
        self.assertFalse(proposal["automatic_execution"])
        self.assertFalse(proposal["canonical_effect"])
        self.assertEqual(backlog["contract"], "LEARNING_BACKLOG_v1")
        self.assertIsNotNone(event)
        self.assertEqual(state["run_disposition"], "MATERIAL_LEARNING_DELTA")

    def test_more_observations_without_new_mature_evidence_is_not_material_learning(self):
        adm = admissions(a())
        adj = adjudication(ar("EC-1", "RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW", "MATURED_SUPPORTED", 10))
        first, _, _, event1 = controller._build_products(registry(c(state="MATURED_SUPPORTED", matured_outcome_count=10, observation_count=10)), adm, adj, policy(), {}, {}, datetime(2026,1,8,tzinfo=UTC))
        self.assertIsNotNone(event1)
        _, _, _, event2 = controller._build_products(registry(c(state="MATURED_SUPPORTED", matured_outcome_count=10, observation_count=99)), adm, adj, policy(), first, {}, datetime(2026,1,9,tzinfo=UTC))
        self.assertIsNone(event2)

    def test_new_mature_outcomes_are_material(self):
        adm = admissions(a())
        adj1 = adjudication(ar("EC-1", "RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW", "MATURED_SUPPORTED", 10))
        first, _, _, _ = controller._build_products(registry(c(state="MATURED_SUPPORTED", matured_outcome_count=10)), adm, adj1, policy(), {}, {}, datetime(2026,1,8,tzinfo=UTC))
        adj2 = adjudication(ar("EC-1", "RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW", "MATURED_SUPPORTED", 20))
        _, _, _, event2 = controller._build_products(registry(c(state="MATURED_SUPPORTED", matured_outcome_count=20)), adm, adj2, policy(), first, {}, datetime(2026,1,9,tzinfo=UTC))
        self.assertIsNotNone(event2)

    def test_backlog_retains_disappeared_idea(self):
        family = {"semantic_identity":"x", "current_evidence_status":"SUPPORTED_NEEDS_INCREMENTAL_VALUE", "unresolved_uncertainty":"u", "supporting_evidence_refs":["A"], "contradicting_evidence_refs":[], "candidate_ids":["A"], "kinds":["FORECAST_TEST"], "learning_profiles":["STANDARD"], "known_regime_dependence":["ALL"], "redundancy_collinearity_warning":False, "complexity_burden":"LOW", "max_candidate_observation_count":20}
        tests = controller.generate_candidate_tests([family]); proposal, _ = controller.select_bounded_next_best_test(tests)
        first = controller.build_learning_backlog({}, tests, proposal, datetime(2026,1,1,tzinfo=UTC))
        empty, _ = controller.select_bounded_next_best_test([])
        second = controller.build_learning_backlog(first, [], empty, datetime(2026,1,2,tzinfo=UTC))
        self.assertEqual(second["entries"][0]["status"], "HISTORICAL_RETAINED")

    def test_confirmatory_checkpoints_never_allow_interim_skill_inference(self):
        activation = {"study_id":"T13", "cohort_start_utc":"2026-01-01T00:00:00Z", "cohort_end_utc_exclusive":"2026-09-01T00:00:00Z", "freeze_accrual_window_days":240, "forecast_skill_status":"UNPROVEN", "outcome_data_read":False}
        def fake_load(path, default=None):
            if path == controller.T13_ACTIVATION: return activation
            if path == controller.T13_STATUS: return {"forecast_skill_status":"UNPROVEN", "outcome_data_read":False}
            return default
        with patch.object(controller, "load_json", side_effect=fake_load):
            result = controller._t13_status(datetime(2026,9,1,tzinfo=UTC))
        self.assertEqual(result["operational_checkpoint_days_reached"], [7,14,30,60,90,120,180,240])
        self.assertFalse(result["interim_performance_inference_allowed"])
        self.assertFalse(result["automatic_child_experiment_allowed"])

    def test_learning_event_is_append_only(self):
        event = {"contract":"LEARNING_EVENT_v1", "event_id":"LE-X", "generated_at_utc":"2026-01-01T00:00:00Z", "x":1}
        with tempfile.TemporaryDirectory() as td:
            with patch.object(controller, "EVENT_ROOT", Path(td)):
                self.assertTrue(controller._persist_event_append_only(event))
                self.assertFalse(controller._persist_event_append_only({**event, "generated_at_utc":"2026-01-02T00:00:00Z"}))
                with self.assertRaises(RuntimeError): controller._persist_event_append_only({**event, "x":2})


if __name__ == "__main__":
    unittest.main()
