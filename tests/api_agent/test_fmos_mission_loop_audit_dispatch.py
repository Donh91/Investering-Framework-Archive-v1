import json
import tempfile
import unittest
from pathlib import Path

from scripts.api_agent import fmos_mission_loop_audit_dispatch as mod


class TestFmosMissionLoopAuditDispatch(unittest.TestCase):
    def test_extract_decision_accepts_allowed_value(self):
        self.assertEqual(
            mod.extract_decision({"summary": "DECISION=ADAPT_MINIMAL; MODEL_USED=gpt-6.1-sol; NO_AUTHORITY_CHANGE;"}),
            "ADAPT_MINIMAL",
        )

    def test_extract_decision_rejects_unknown_value(self):
        self.assertIsNone(mod.extract_decision({"summary": "DECISION=DO_WHATEVER;"}))

    def test_context_cap_covers_failed_owner_audit_packet(self):
        self.assertEqual(mod.MAX_CONTEXT_BYTES, 650000)
        self.assertGreater(mod.MAX_CONTEXT_BYTES, 318928)

    def test_clip_is_bounded(self):
        out = mod.clip("x" * 100, 10)
        self.assertTrue(out.startswith("x" * 10))
        self.assertIn("TRUNCATED_AT_BOUND", out)

    def test_validate_one_requires_empty_forecasts_and_model_binding(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "receipt.json").write_text(json.dumps({
                "status": "PASS",
                "model": "gpt-6.1-sol",
                "reasoning_effort": "high",
                "forecast_candidate_count": 0,
                "estimated_cost_usd": 0.1,
            }))
            (root / "output.json").write_text(json.dumps({
                "status": "READY",
                "summary": "PASS1 MODEL_USED=gpt-6.1-sol NO_AUTHORITY_CHANGE",
                "evidence_for": [],
                "evidence_against": [],
                "uncertainties": [],
                "hypotheses": [],
                "forecast_candidates": [],
            }))
            result = mod.validate_one(root, "pass1")
            self.assertEqual(result["receipt"]["model"], "gpt-6.1-sol")

    def test_pass3_requires_frozen_decision(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "receipt.json").write_text(json.dumps({
                "status": "PASS",
                "model": "gpt-6.1-sol",
                "reasoning_effort": "high",
                "forecast_candidate_count": 0,
                "estimated_cost_usd": 0.1,
            }))
            (root / "output.json").write_text(json.dumps({
                "status": "READY",
                "summary": "DECISION=ADAPT_SUBSTANTIAL; MODEL_USED=gpt-6.1-sol; NO_CODE_WRITE_PERFORMED; NO_AUTHORITY_CHANGE;",
                "evidence_for": [],
                "evidence_against": [],
                "uncertainties": [],
                "hypotheses": [],
                "forecast_candidates": [],
            }))
            result = mod.validate_one(root, "pass3")
            self.assertEqual(mod.extract_decision(result["output"]), "ADAPT_SUBSTANTIAL")


if __name__ == "__main__":
    unittest.main()
