from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "audit_runner", ROOT / "scripts/api_agent/fmos_mission_loop_audit_runner.py"
)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MOD)

class FmosMissionLoopAuditTests(unittest.TestCase):
    def test_registry_binding_and_zero_authority(self):
        reg = MOD.load_registry(ROOT / "research/api_agent/API_TASK_REGISTRY_v1.json")
        cfg = reg["tasks"][MOD.TASK]
        self.assertEqual(cfg["model"], "gpt-6-sol")
        self.assertEqual(cfg["reasoning_effort"], "high")
        self.assertEqual(cfg["invocation_mode"], "OWNER_GATED_ONE_OFF")
        self.assertTrue(cfg["advisory_only"])
        self.assertFalse(cfg["automatic_code_write"])
        self.assertFalse(cfg["automatic_merge"])
        self.assertFalse(cfg["canonical_effect"])
        self.assertFalse(cfg["portfolio_action"])

    def test_policy_preserves_global_budget(self):
        policy = json.loads((ROOT / "research/api_agent/API_INTELLIGENCE_POLICY_v2.json").read_text())
        self.assertEqual(policy["monthly_hard_stop_usd"], 40)
        self.assertEqual(policy["global_reserve_usd"], 4)
        self.assertEqual(policy["lane_caps_usd"][MOD.TASK], 6)
        audit = policy["fmos_autonomous_mission_loop_audit"]
        self.assertFalse(audit["periodic_schedule"])
        self.assertEqual(audit["output_authority"], "ADVISORY_READ_ONLY")

    def test_required_schema_keys_exist(self):
        schema = json.loads((ROOT / "research/architecture_audits/fmos_autonomous_mission_loop_v1/AUDIT_OUTPUT_SCHEMA.json").read_text())
        required = set(schema.get("required") or [])
        self.assertTrue(MOD.REQUIRED_TOP_LEVEL.issubset(required))

    def test_pass_instructions_are_distinct(self):
        self.assertIn("RECONSTRUCTION", MOD.pass_instruction(1))
        self.assertIn("ADVERSARIAL", MOD.pass_instruction(2))
        self.assertIn("FINAL SYNTHESIS", MOD.pass_instruction(3))

if __name__ == "__main__":
    unittest.main()
