"""CN weekly offline publication must not depend on cost guards or paid API access."""
from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest import mock

from scripts.cycle_navigator import build_weekly_cycle_navigator as B

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/cycle-navigator-weekly-publication.yml"
SOURCE = ROOT / "scripts/cycle_navigator/build_weekly_cycle_navigator.py"


class CNOfflineBudgetIsolationTests(unittest.TestCase):
    def test_workflow_does_not_gate_offline_publishing_on_paid_budget(self):
        workflow = WORKFLOW.read_text()
        self.assertNotIn("Enforce monthly API cost guard", workflow)
        self.assertNotIn("check_monthly_cost_guard.py", workflow)
        self.assertIn("CN_OFFLINE_ONLY: '1'", workflow)
        self.assertIn("python scripts/cycle_navigator/build_weekly_cycle_navigator.py", workflow)
        # Important negative guard: the offline issuer cannot inherit a provider key.
        self.assertNotIn("OPENAI_API_KEY:", workflow)

    def test_provider_post_fail_closed_in_offline_mode(self):
        with mock.patch.dict(os.environ, {"CN_OFFLINE_ONLY": "1", "OPENAI_API_KEY": "unused"}, clear=False):
            with self.assertRaisesRegex(RuntimeError, "CN_OFFLINE_ONLY_API_POST_FORBIDDEN"):
                B.call_openai("gpt-6-sol", "", {}, 16)

    def test_offline_producer_remains_the_only_weekly_issue_path(self):
        source = SOURCE.read_text()
        segment = source[source.index("def main()"):]
        self.assertIn("value = build_offline_value(", segment)
        self.assertIn('"api_request_performed": False', segment)
        # This is a source assertion, not a permission to skip pre-HTTP guards on paid lanes.
        self.assertNotIn("call_openai(", segment)


if __name__ == "__main__":
    unittest.main()
