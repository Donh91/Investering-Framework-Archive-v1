"""Regression: unaccepted adaptive-analysis pilot must not activate implicitly."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SKILL = "adaptive-analysis-methods"
META = ROOT / ".agents/skills" / SKILL / "agents/openai.yaml"
INDEX = ROOT / "00_ARCHIVE_CONTROL/SKILL_ROUTING_INDEX.json"
CASES = ROOT / "07_PROMPTS_AND_AGENTS/skill_quality_gate/adaptive_analysis_methods_v1_cases.json"

class AdaptiveAnalysisPilotInvocationTests(unittest.TestCase):
    def test_unaccepted_pilot_requires_explicit_invocation_on_both_routes(self):
        index = json.loads(INDEX.read_text(encoding="utf-8"))
        rows = [row for row in index["skills"] if row.get("name") == SKILL]
        self.assertEqual(len(rows), 1, "Exactly one canonical skill routing entry")
        row = rows[0]
        cases = json.loads(CASES.read_text(encoding="utf-8"))
        self.assertEqual(cases["candidate"], SKILL)
        self.assertEqual(cases["evaluation_status"], "PROPOSED_NOT_RUN")
        self.assertEqual(row["maturity"], "PILOT_CANDIDATE_READ_ONLY_V1")
        self.assertIs(row["allow_implicit_invocation"], False,
                      "An unevaluated pilot cannot run implicitly through routing")
        metadata = META.read_text(encoding="utf-8")
        self.assertIn("allow_implicit_invocation: false", metadata)
        self.assertNotIn("allow_implicit_invocation: true", metadata)

    def test_pilot_has_negative_and_authority_cases_before_promotion(self):
        cases = json.loads(CASES.read_text(encoding="utf-8"))
        by_id = {row["id"]: row for row in cases["cases"]}
        self.assertEqual(len(by_id), len(cases["cases"]))
        self.assertEqual(by_id["routine-status"]["expected_level"], "L0")
        self.assertEqual(by_id["simple-fix"]["expected_level"], "L0")
        self.assertIn("API_SPEND", by_id["no-authority"]["must_not"])
        self.assertIn("MERGE_AUTHORITY", by_id["no-authority"]["must_not"])

if __name__ == "__main__":
    unittest.main()
