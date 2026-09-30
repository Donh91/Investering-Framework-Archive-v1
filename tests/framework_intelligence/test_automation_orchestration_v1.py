import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path("scripts/framework_intelligence/automation_orchestration_v1.py")
spec = importlib.util.spec_from_file_location("automation_orchestration_v1", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def workflow(name, *, findings=None, head="abc", streak=1):
    return {
        "workflow": name,
        "status": "RED",
        "findings": list(findings or ["LATEST_RUN_FAILED"]),
        "scheduled": True,
        "openai_enabled": False,
        "write_target_class": "DIRECT_MAIN",
        "writer_group": "framework-main-writer",
        "live": {
            "failure_streak": streak,
            "recent_failure_count": streak,
            "latest_run": {
                "id": 123,
                "html_url": "https://example.invalid/run/123",
                "head_sha": head,
            },
        },
    }


class AutomationOrchestrationV1Test(unittest.TestCase):
    def write_fixture(self, root: Path, workflows, remediation=None, codex=None):
        health = {
            "contract": "AUTOMATION_PRODUCTION_HEALTH_v1",
            "generated_at_utc": "2026-09-30T09:51:50Z",
            "status": "RED",
            "workflow_count": len(workflows),
            "scheduled_workflow_count": len(workflows),
            "writer_count": len(workflows),
            "green_count": 0,
            "amber_count": 0,
            "red_count": len(workflows),
            "workflows": workflows,
        }
        hp = root / "research/architecture_health/LATEST_AUTOMATION_HEALTH.json"
        hp.parent.mkdir(parents=True, exist_ok=True)
        hp.write_text(json.dumps(health))
        rp = root / "research/remediation/LATEST_REMEDIATION_QUEUE.json"
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps(remediation or {"items": []}))
        cp = root / "research/remediation/LATEST_CODEX_READY_TASKS.json"
        cp.write_text(json.dumps(codex or {"tasks": []}))

    def test_existing_remediation_prevents_duplicate_agent_work(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_fixture(
                root,
                [workflow("broken.yml")],
                remediation={
                    "items": [
                        {
                            "workflow": "broken.yml",
                            "state": "CODEX_READY",
                            "signature": "sig1",
                            "finding": "LATEST_RUN_FAILED",
                            "route": "CODEX_PR",
                        }
                    ]
                },
            )
            out = root / "out"
            plan = mod.build_plan(root, out)
            self.assertEqual(plan["items"][0]["route"], "FOLLOW_EXISTING_REMEDIATION")
            self.assertEqual(plan["routing_summary"]["existing_remediation_count"], 1)
            self.assertEqual(plan["routing_summary"]["luna_triage_count"], 0)
            self.assertEqual(plan["routing_summary"]["sol_6_1_diagnosis_count"], 0)

    def test_three_failures_on_same_head_are_batched_to_sol(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_fixture(
                root,
                [
                    workflow("a.yml", head="same-head"),
                    workflow("b.yml", head="same-head"),
                    workflow("c.yml", head="same-head"),
                ],
            )
            plan = mod.build_plan(root, root / "out")
            self.assertEqual(plan["routing_summary"]["shared_head_cluster_count"], 1)
            self.assertEqual(plan["routing_summary"]["sol_6_1_diagnosis_count"], 3)
            self.assertTrue(plan["agent_calls"]["sol_6_1_required"])
            self.assertFalse(plan["agent_calls"]["astra_required"])

    def test_isolated_first_failure_uses_luna(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_fixture(root, [workflow("solo.yml", head="solo-head", streak=1)])
            plan = mod.build_plan(root, root / "out")
            self.assertEqual(plan["items"][0]["route"], "LUNA_TRIAGE")
            self.assertEqual(plan["routing_summary"]["luna_triage_count"], 1)
            self.assertTrue(plan["agent_calls"]["luna_required"])

    def test_repeated_failure_uses_sol(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_fixture(
                root,
                [workflow("repeat.yml", findings=["REPEATED_CONSECUTIVE_FAILURES"], head="repeat", streak=3)],
            )
            plan = mod.build_plan(root, root / "out")
            self.assertEqual(plan["items"][0]["route"], "SOL_DIAGNOSIS")
            self.assertTrue(plan["agent_calls"]["sol_6_1_required"])

    def test_same_fingerprint_does_not_burn_models_twice(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_fixture(root, [workflow("solo.yml", head="same", streak=1)])
            out = root / "out"
            first = mod.build_plan(root, out)
            second = mod.build_plan(root, out)
            self.assertTrue(first["material_delta"])
            self.assertFalse(second["material_delta"])
            self.assertFalse(second["agent_calls"]["luna_required"])
            self.assertFalse(second["agent_calls"]["sol_6_1_required"])

    def test_finalize_preserves_advisory_authority(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_fixture(root, [workflow("solo.yml")])
            out = root / "out"
            mod.build_plan(root, out)
            luna = root / "luna.json"
            luna.write_text(json.dumps({"status": "READY", "summary": "triage"}))
            result = mod.finalize(out, luna, None)
            self.assertEqual(result["authority"], "ADVISORY_ORCHESTRATION_ONLY")
            self.assertIn("sole CODEX_READY authority", result["note"])


if __name__ == "__main__":
    unittest.main()
