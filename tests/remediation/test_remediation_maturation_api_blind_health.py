from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "build_remediation_maturation",
    ROOT / "scripts/remediation/build_remediation_maturation.py",
)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(module)


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def prior_queue():
    return {
        "contract": "REMEDIATION_MATURATION_ENGINE_v1",
        "contract_revision": "1.1",
        "generated_at_utc": "2026-09-22T00:00:00Z",
        "items": [
            {
                "signature": "old-red",
                "workflow": "a.yml",
                "finding": "LATEST_RUN_FAILED",
                "state": "POST_FIX_OBSERVATION",
                "post_fix_successes": 1,
            }
        ],
        "codex_ready_tasks": [],
        "needs_more_evidence": [],
        "active_remediation": [
            {
                "signature": "old-red",
                "workflow": "a.yml",
                "finding": "LATEST_RUN_FAILED",
                "state": "POST_FIX_OBSERVATION",
                "post_fix_successes": 1,
            }
        ],
        "summary": {"total": 1, "codex_ready": 0, "needs_more_evidence": 0, "active_remediation": 1},
    }


class RemediationMaturationApiBlindHealthTests(unittest.TestCase):
    def run_build(self, health, prior=None):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_json(repo / "research/architecture_health/LATEST_AUTOMATION_HEALTH.json", health)
            write_json(repo / "research/remediation/LATEST_REMEDIATION_QUEUE.json", prior or prior_queue())
            return module.build(repo)

    def test_api_error_carries_prior_without_post_fix_credit_or_new_signature(self):
        prior = prior_queue()
        health = {
            "generated_at_utc": "2026-09-23T00:00:00Z",
            "api_error": "HTTPError:403",
            "scheduled_workflow_count": 10,
            "registered_workflow_count": 0,
            "workflows": [
                {
                    "workflow": "blind.yml",
                    "scheduled": True,
                    "findings": ["WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE", "NO_RUN_HISTORY"],
                    "live": None,
                }
            ],
        }
        result = self.run_build(health, prior)
        self.assertEqual(result["items"], prior["items"])
        self.assertEqual(result["items"][0]["post_fix_successes"], 1)
        self.assertNotIn("blind.yml", json.dumps(result["items"]))
        self.assertEqual(result["maturation_refusal"]["reason"], "AUTOMATION_HEALTH_API_ERROR")
        self.assertFalse(result["maturation_refusal"]["post_fix_successes_incremented"])
        self.assertFalse(result["maturation_refusal"]["new_health_signatures_created"])

    def test_majority_missing_live_rows_fails_closed_even_without_api_error(self):
        health = {
            "generated_at_utc": "2026-09-23T00:00:00Z",
            "api_error": None,
            "scheduled_workflow_count": 4,
            "registered_workflow_count": 1,
            "workflows": [
                {"workflow": "a.yml", "scheduled": True, "live": {"state": "active"}, "findings": []},
                {"workflow": "b.yml", "scheduled": True, "live": None, "findings": ["NO_RUN_HISTORY"]},
                {"workflow": "c.yml", "scheduled": True, "live": None, "findings": ["NO_RUN_HISTORY"]},
                {"workflow": "d.yml", "scheduled": True, "live": None, "findings": ["NO_RUN_HISTORY"]},
            ],
        }
        result = self.run_build(health)
        self.assertEqual(result["maturation_refusal"]["reason"], "AUTOMATION_HEALTH_LIVE_COVERAGE_INSUFFICIENT")

    def test_half_or_more_scheduled_live_rows_is_usable(self):
        health = {
            "generated_at_utc": "2026-09-23T00:00:00Z",
            "api_error": None,
            "scheduled_workflow_count": 2,
            "registered_workflow_count": 2,
            "workflows": [
                {
                    "workflow": "a.yml",
                    "scheduled": True,
                    "cron_count": 1,
                    "lifecycle_state": "ACTIVE",
                    "live": {"state": "active", "failure_streak": 1, "success_streak": 0, "latest_run": {"id": 1, "conclusion": "failure"}},
                    "findings": ["LATEST_RUN_FAILED"],
                },
                {
                    "workflow": "b.yml",
                    "scheduled": True,
                    "cron_count": 1,
                    "lifecycle_state": "ACTIVE",
                    "live": {"state": "active", "failure_streak": 0, "success_streak": 1, "latest_run": {"id": 2, "conclusion": "success"}},
                    "findings": [],
                },
            ],
        }
        result = self.run_build(health, {"items": []})
        self.assertNotIn("maturation_refusal", result)
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0]["workflow"], "a.yml")

    def test_prior_object_is_not_mutated(self):
        prior = prior_queue()
        expected = copy.deepcopy(prior)
        health = {"api_error": "offline", "scheduled_workflow_count": 1, "registered_workflow_count": 0, "workflows": []}
        self.run_build(health, prior)
        self.assertEqual(prior, expected)


if __name__ == "__main__":
    unittest.main()
