import json
import unittest
from pathlib import Path

from scripts.api_agent.shadow_admission_ai_decider import (
    apply_ai_decision,
    dry_run_decision,
    initial_state,
    validate_decision,
)

ROOT = Path(".")
POLICY = json.loads((ROOT / "research/api_agent/SHADOW_ADMISSION_AI_POLICY_v1.json").read_text())
REGISTRY = json.loads((ROOT / "06_RESEARCH_LAB/buildwithclaude_shadow_round1_v1/ROUND1_CANDIDATES.json").read_text())
CANDIDATE_IDS = [row["id"] for row in REGISTRY["candidates"]]


class ShadowAdmissionAIDeciderTests(unittest.TestCase):
    def test_policy_delegates_without_human_confirmation(self):
        self.assertEqual(POLICY["decision_authority"], "OPENAI_API_AUTONOMOUS")
        self.assertFalse(POLICY["human_confirmation_required"])
        self.assertEqual(POLICY["authority_ceiling"], "OPERATIONAL_HELPER")
        self.assertFalse(POLICY["deterministic_validator_may_override_substantive_decision"])

    def test_dry_run_keeps_every_candidate_shadow(self):
        value = dry_run_decision(REGISTRY)
        validate_decision(value, CANDIDATE_IDS, POLICY["allowed_decisions"])
        self.assertEqual(len(value["candidate_decisions"]), 4)
        self.assertTrue(all(row["decision"] == "KEEP_SHADOW" for row in value["candidate_decisions"]))

    def test_decision_state_mismatch_is_rejected(self):
        value = dry_run_decision(REGISTRY)
        value["candidate_decisions"][0]["decision"] = "PROMOTE_OPERATIONAL_HELPER"
        with self.assertRaisesRegex(ValueError, "decision_state_mismatch"):
            validate_decision(value, CANDIDATE_IDS, POLICY["allowed_decisions"])

    def test_duplicate_candidate_is_rejected(self):
        value = dry_run_decision(REGISTRY)
        value["candidate_decisions"][1]["candidate_id"] = value["candidate_decisions"][0]["candidate_id"]
        with self.assertRaisesRegex(ValueError, "candidate_identity_invalid_or_duplicate"):
            validate_decision(value, CANDIDATE_IDS, POLICY["allowed_decisions"])

    def test_promotion_enables_only_operational_helper_state(self):
        value = dry_run_decision(REGISTRY)
        row = value["candidate_decisions"][0]
        row.update(
            decision="PROMOTE_OPERATIONAL_HELPER",
            resulting_state="OPERATIONAL_HELPER",
            evidence_sufficiency="SUFFICIENT",
            implementation_status="ENABLE_AUTOMATICALLY",
            incremental_value_assessment="Adds measurable protection.",
            complexity_tax_assessment="Benefit exceeds low cost.",
            rationale="Frozen promotion gate is satisfied.",
            rollback_path="Disable helper and restore shadow state.",
            master_monday_note="Promoted autonomously.",
        )
        validate_decision(value, CANDIDATE_IDS, POLICY["allowed_decisions"])
        state = apply_ai_decision(initial_state(REGISTRY), value, "abc123", REGISTRY)
        promoted = state["candidates"][row["candidate_id"]]
        self.assertEqual(promoted["state"], "OPERATIONAL_HELPER")
        self.assertTrue(promoted["operational_enabled"])
        self.assertEqual(promoted["authority_ceiling"], "OPERATIONAL_HELPER")
        self.assertFalse(state["human_confirmation_required"])

    def test_archive_disables_candidate(self):
        value = dry_run_decision(REGISTRY)
        row = value["candidate_decisions"][0]
        row.update(
            decision="ARCHIVE_ONLY",
            resulting_state="ARCHIVE_ONLY",
            implementation_status="DISABLE_AUTOMATICALLY",
        )
        validate_decision(value, CANDIDATE_IDS, POLICY["allowed_decisions"])
        state = apply_ai_decision(initial_state(REGISTRY), value, "def456", REGISTRY)
        self.assertFalse(state["candidates"][row["candidate_id"]]["operational_enabled"])


if __name__ == "__main__":
    unittest.main()
