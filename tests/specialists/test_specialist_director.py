import json
import unittest
from pathlib import Path

from scripts.specialists.specialist_director import synthesize, validate_specialist

REGISTRY_PATH = Path("research/specialists/SPECIALIST_REGISTRY_v1.json")


def payload(specialist_id: str, direction: str = "UP", freshness: str = "PASS", confidence: int = 70):
    return {
        "specialist_id": specialist_id,
        "run_id": f"run-{specialist_id}",
        "as_of_utc": "2026-08-01T05:30:00Z",
        "owner_inputs": ["owner-row"],
        "owner_receipts": ["sha256:test"],
        "freshness_status": freshness,
        "state": {
            "MACRO_SPECIALIST_v1": "TAILWIND",
            "SPOT_STRUCTURE_SPECIALIST_v1": "EXPANSION",
            "DERIVATIVES_SPECIALIST_v1": "NEUTRAL",
            "BREADTH_SPECIALIST_v1": "EXPANDING",
            "CYCLE_SPECIALIST_v1": "TRANSITION",
        }[specialist_id],
        "direction": direction,
        "confidence_0_100": confidence,
        "persistence_status": "BUILDING",
        "evidence_for": ["a"],
        "evidence_against": ["b"],
        "missing_required_inputs": [],
        "conflicts": [],
        "no_action_reason": "shadow_only",
        "authority": {
            "creates_truth": False,
            "framework_state_change": False,
            "model_weight_change": False,
            "portfolio_action": False,
        },
    }


class SpecialistDirectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text())

    def test_three_distinct_families_are_ready(self):
        result = synthesize([
            payload("MACRO_SPECIALIST_v1"),
            payload("SPOT_STRUCTURE_SPECIALIST_v1"),
            payload("BREADTH_SPECIALIST_v1"),
        ], self.registry)
        self.assertEqual(result["status"], "READY")
        self.assertFalse(result["market_truth_created"])
        self.assertFalse(result["portfolio_action"])

    def test_disagreement_is_preserved(self):
        result = synthesize([
            payload("MACRO_SPECIALIST_v1", "UP"),
            payload("SPOT_STRUCTURE_SPECIALIST_v1", "DOWN"),
            payload("BREADTH_SPECIALIST_v1", "DOWN"),
        ], self.registry)
        self.assertTrue(result["disagreement_preserved"])
        self.assertEqual(result["directions_present"], ["DOWN", "UP"])

    def test_stale_high_confidence_is_rejected(self):
        item = payload("MACRO_SPECIALIST_v1", freshness="STALE", confidence=80)
        result = validate_specialist(item, self.registry)
        self.assertFalse(result.valid)
        self.assertIn("stale_confidence_above_50", result.errors)

    def test_forbidden_authority_is_rejected(self):
        item = payload("SPOT_STRUCTURE_SPECIALIST_v1")
        item["authority"]["portfolio_action"] = True
        result = validate_specialist(item, self.registry)
        self.assertFalse(result.valid)
        self.assertIn("forbidden_authority:portfolio_action", result.errors)

    def test_unknown_is_not_converted_to_neutral(self):
        item = payload("MACRO_SPECIALIST_v1", direction="UNKNOWN", confidence=40)
        item["state"] = "UNKNOWN"
        result = synthesize([item], self.registry)
        self.assertEqual(result["directions_present"], [])
        self.assertEqual(result["status"], "DEGRADED")


if __name__ == "__main__":
    unittest.main()
