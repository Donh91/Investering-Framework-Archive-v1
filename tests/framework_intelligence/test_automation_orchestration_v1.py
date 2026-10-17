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


    def test_exact_identity_blocks_cross_workflow_collision_and_prose(self):
        positive = [
            ("ETF.yml", "etf.yaml"),
            (".github/workflows/ETf.YML", "etf.yml"),
            ("alpha.yml", "alpha"),
            ("solo.yaml", ".github/workflows/solo.yml"),
        ]
        for row_name, health_name in positive:
            with self.subTest(row_name=row_name):
                self.assertTrue(mod.row_matches_workflow({"workflow": row_name}, health_name))
        negatives = [
            ({"workflow": "etf.yml", "state": "CODEX_READY"}, "daily-settled-etf-calibration.yml"),
            ({"workflow": "alpha.yml", "state": "IN_REMEDIATION"}, "alpha-backup.yml"),
            ({"workflow": "other.yml", "objective": "Fix ci.yml", "candidate_id": "ci",
              "finding": "ci.yml failed", "candidate_path": "ci.yml"}, "ci.yml"),
            ({"objective": "Fix ci.yml", "candidate_id": "ci"}, "ci.yml"),
            ({"workflow": "research-intake/ci-fix", "candidate_id": "ci-fix"}, "ci.yml"),
            ({"workflow": "etf.yml"}, ".github/workflows/other/etf.yml"),
        ]
        for row, name in negatives:
            with self.subTest(row=row, target=name):
                self.assertFalse(mod.row_matches_workflow(row, name))

    def test_wrong_remediation_cannot_hide_red_workflow_or_paid_lane(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_fixture(root, [workflow("daily-settled-etf-calibration.yml")],
                               remediation={"items": [{
                                   "workflow": "etf.yml", "state": "CODEX_READY",
                                   "finding": "daily-settled-etf-calibration.yml", "signature": "other"
                               }]})
            plan = mod.build_plan(root, root / "out")
            self.assertEqual(plan["items"][0]["route"], "LUNA_TRIAGE")
            self.assertTrue(plan["agent_calls"]["luna_required"])
            self.assertEqual(plan["routing_summary"]["existing_remediation_count"], 0)

    def test_exact_in_remediation_keeps_no_duplicate_model_calls(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_fixture(root, [workflow("ALPHA.yml", streak=3)],
                               remediation={"items": [{
                                   "workflow": ".github/workflows/alpha.yaml",
                                   "state": "IN_REMEDIATION", "signature": "same"
                               }]})
            plan = mod.build_plan(root, root / "out")
            self.assertEqual(plan["items"][0]["route"], "FOLLOW_EXISTING_REMEDIATION")
            self.assertFalse(plan["agent_calls"]["sol_6_1_required"])
            self.assertFalse(plan["agent_calls"]["luna_required"])

    def test_verified_situation_room_intake_keeps_existing_dedup(self):
        import hashlib
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cid = "codex-situation-room-daily-static-root-cause-v1"
            relative = f"research/codex/intake/2026/08/{cid}.json"
            candidate = {"contract": "CODEX_RESEARCH_CANDIDATE_v1",
                         "candidate_id": cid, "status": "SUBMITTED",
                         "primary_target": ".github/workflows/situation-room-daily-static.yml",
                         "allowed_change_scope": [
                             ".github/workflows/situation-room-daily-static.yml",
                             ".github/workflows/situation-room-owner-live-gate.yml"]}
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(candidate))
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            link = {"workflow": f"research-intake/{cid}", "candidate_id": cid,
                    "candidate_path": relative, "candidate_sha256": digest,
                    "state": "POST_FIX_OBSERVATION", "signature": "observed"}
            self.assertEqual(mod.verified_intake_target(root, link),
                             ".github/workflows/situation-room-daily-static.yml")
            self.write_fixture(root, [workflow("situation-room-daily-static.yml", streak=2)],
                               remediation={"items": [link]})
            plan = mod.build_plan(root, root / "out")
            self.assertEqual(plan["items"][0]["route"], "FOLLOW_EXISTING_REMEDIATION")
            self.assertFalse(plan["agent_calls"]["sol_6_1_required"])
            # Multi-workflow scope is NOT permission to deduplicate the other gate.
            self.write_fixture(root, [workflow("situation-room-owner-live-gate.yml")],
                               remediation={"items": [link]})
            other = mod.build_plan(root, root / "out2")
            self.assertEqual(other["items"][0]["route"], "LUNA_TRIAGE")
            # Tampered candidate, even with the same name, must not be trusted.
            path.write_text(json.dumps({**candidate, "primary_target": ".github/workflows/etf.yml"}))
            self.assertIsNone(mod.verified_intake_target(root, link))
            self.write_fixture(root, [workflow("situation-room-daily-static.yml")],
                               remediation={"items": [link]})
            bad = mod.build_plan(root, root / "out3")
            self.assertEqual(bad["items"][0]["route"], "LUNA_TRIAGE")

    def test_negative_identity_fails_under_legacy_substring_mutation(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_fixture(root, [workflow("daily-settled-etf-calibration.yml")],
                               remediation={"items": [{
                                   "workflow": "etf.yml", "state": "CODEX_READY",
                                   "signature": "alien"
                               }]})
            def assert_negative_guard():
                plan = mod.build_plan(root, root / "mutant")
                self.assertEqual(plan["items"][0]["route"], "LUNA_TRIAGE")
            assert_negative_guard()
            def old_substring(row, target, **kwargs):
                left = mod.workflow_key(row.get("workflow"))
                right = mod.workflow_key(target)
                return bool(left and right and (left in right or right in left))
            with patch.object(mod, "row_matches_workflow", old_substring):
                with self.assertRaises(AssertionError):
                    assert_negative_guard()


if __name__ == "__main__":
    unittest.main()
