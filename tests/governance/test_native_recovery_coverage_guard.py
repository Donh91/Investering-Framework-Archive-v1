"""Guard recovery coverage for required unattended Auto Market State lanes."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.health.native_market_recovery import POLICY

REGISTRY = Path("02_DATA_PING/source_integrations/2026-09-02__auto-market-state-source-admission-v1_1.json")
WORKFLOW_ROOT = Path(".github/workflows")


class NativeRecoveryCoverageGuardTest(unittest.TestCase):
    def test_every_required_unattended_lane_has_exactly_one_recovery_policy_route(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        required = {
            row["manual_replacement_lane"]
            for row in registry["sources"]
            if row.get("decision_context_required") is True
            and row.get("unattended_git_owner") is True
            and isinstance(row.get("manual_replacement_lane"), str)
            and row["manual_replacement_lane"]
        }
        self.assertEqual(set(POLICY), required)

    def test_every_recovery_target_is_existing_manual_dispatch_owner(self):
        for lane, rule in POLICY.items():
            with self.subTest(lane=lane):
                workflow = WORKFLOW_ROOT / rule["workflow"]
                self.assertTrue(workflow.is_file(), f"missing recovery workflow for {lane}: {workflow}")
                text = workflow.read_text(encoding="utf-8")
                self.assertIn("workflow_dispatch:", text)
                self.assertGreaterEqual(int(rule["streak"]), 1)
                self.assertGreater(int(rule["cooldown_hours"]), 0)

    def test_known_shared_owner_routes_are_deduplicatable_by_workflow_identity(self):
        self.assertEqual(POLICY["hourly_market"]["workflow"], POLICY["derivatives"]["workflow"])
        daily = {
            POLICY[lane]["workflow"]
            for lane in ("live_anchor", "breadth", "sentiment", "altseason_context", "macro_risk")
        }
        self.assertEqual(daily, {"daily-raw-owner-capture.yml"})


if __name__ == "__main__":
    unittest.main()
