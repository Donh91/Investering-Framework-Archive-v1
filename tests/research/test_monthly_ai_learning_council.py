from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.research.monthly_ai_learning_council import build_context, choose_primary_action, deterministic_claims, finalize

UTC = timezone.utc


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def seed_repo(root: Path, *, prior_month=None, prior_outcomes=0, current_outcomes=0, escalation=None) -> None:
    dump(root / "research/monthly_learning_council/MONTHLY_AI_LEARNING_COUNCIL_POLICY_v1.json", {
        "monthly_review_day": 3,
        "quarterly_review_months": [1, 4, 7, 10],
        "matured_outcome_delta_trigger": 25,
        "minimum_matured_outcomes_for_learning_claim": 25,
        "max_ai_research_candidates": 5,
        "max_escalation_candidates_in_context": 25,
    })
    dump(root / "research/monthly_learning_council/STATE.json", {
        "last_completed_month": prior_month,
        "last_matured_outcomes_total": prior_outcomes,
        "last_escalation_fingerprint": "",
    })
    dump(root / "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json", {"contract": "EXPERIMENT_LIFECYCLE_REGISTRY_v1", "candidates": []})
    dump(root / "research/experiment_lifecycle/weekly_adjudication/LATEST.json", {"summary": {}, "escalation_queue": escalation or []})
    dump(root / "04_MARKET_LEARNING/shadow_registry/LATEST.json", {"contract": "SHADOW", "summary": {}})
    dump(root / "06_RESEARCH_LAB/shared_row_model_tournament_v1/weekly/LATEST.json", {"contract": "SHARED", "status": "COLLECTING"})
    for i in range(current_outcomes):
        dump(root / f"research/framework_memory/outcome_memory/a/{i}.json", {"i": i})


class MonthlyAILearningCouncilTests(unittest.TestCase):
    def test_monthly_review_becomes_due_on_day_three(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            seed_repo(root, prior_month="2026-08")
            ctx = build_context(root, datetime(2026, 9, 3, 6, 0, tzinfo=UTC))
            self.assertTrue(ctx["eligibility"]["monthly_due"])
            self.assertTrue(ctx["eligibility"]["run_review"])
            self.assertEqual(ctx["review_kind"], "MONTHLY")

    def test_evidence_milestone_can_run_before_monthly_date(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            seed_repo(root, prior_month="2026-09", prior_outcomes=10, current_outcomes=35)
            ctx = build_context(root, datetime(2026, 9, 10, 6, 0, tzinfo=UTC))
            self.assertFalse(ctx["eligibility"]["monthly_due"])
            self.assertTrue(ctx["eligibility"]["maturation_trigger"])
            self.assertEqual(ctx["review_kind"], "EVIDENCE_MILESTONE")

    def test_deterministic_escalation_outranks_ai_hypothesis(self) -> None:
        ctx = {"evidence_census": {"weekly_escalation_queue": [{"candidate_id": "C1", "selected_action": "RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW"}]}}
        action, target, _, queue = choose_primary_action(ctx, {"status": "READY", "hypotheses": ["test me"]})
        self.assertEqual(action, "RUN_INCREMENTAL_VALUE_TEST")
        self.assertEqual(target, "C1")
        self.assertEqual(queue, [])

    def test_ai_hypothesis_is_research_only_candidate(self) -> None:
        action, target, reason, queue = choose_primary_action({"evidence_census": {"weekly_escalation_queue": []}}, {"status": "READY", "hypotheses": ["Breadth survival adds incremental value; falsify if it does not beat the baseline."]})
        self.assertEqual(action, "RESEARCH_NEW_HYPOTHESIS")
        self.assertTrue(target.startswith("MLC-HYP-"))
        self.assertFalse(queue[0]["canonical_effect"])
        self.assertIn("falsify", reason.lower())

    def test_learning_claim_requires_floor(self) -> None:
        ctx = {"evidence_census": {"experiment_registry": {"matured_candidates": [
            {"candidate_id": "A", "state": "MATURED_SUPPORTED", "matured_outcome_count": 24},
            {"candidate_id": "B", "state": "MATURED_SUPPORTED", "matured_outcome_count": 25},
            {"candidate_id": "C", "state": "MATURED_NOT_SUPPORTED", "matured_outcome_count": 30},
        ]}}}
        learned, challenged = deterministic_claims(ctx, 25)
        self.assertEqual([x["candidate_id"] for x in learned], ["B"])
        self.assertEqual([x["candidate_id"] for x in challenged], ["C"])

    def test_finalize_preserves_firewall_when_ai_missing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            seed_repo(root, prior_month="2026-08")
            runtime = root / "runtime"
            runtime.mkdir()
            ctx = build_context(root, datetime(2026, 9, 3, 6, 0, tzinfo=UTC))
            dump(runtime / "context.json", ctx)
            state = finalize(root, runtime, datetime(2026, 9, 3, 6, 1, tzinfo=UTC))
            self.assertFalse(state["canonical_effect"])
            self.assertFalse(state["portfolio_execution"])
            self.assertFalse(state["paid_data_authorized"])
            self.assertEqual(state["last_completed_month"], "2026-09")


if __name__ == "__main__":
    unittest.main()
