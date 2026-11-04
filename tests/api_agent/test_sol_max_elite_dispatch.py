"""No-network native owner-run and GET-only Sol MAX dispatch tests."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.api_agent import sol_max_elite_dispatch as d
from scripts.api_agent import sol_max_elite_transport as t
from tests.api_agent.test_sol_max_elite_transport import sample, HEAD, MISSION, RUN

ENV = {
    "GITHUB_EVENT_NAME": "issue_comment",
    "GITHUB_ACTOR": "Donh91",
    "GITHUB_REPOSITORY": t.REPO,
    "GITHUB_SHA": HEAD,
    "GITHUB_RUN_ATTEMPT": "1",
    "GITHUB_RUN_ID": RUN,
    "GH_TOKEN": "test-token",
}


def event(path: Path, marker: str, association="OWNER", actor="Donh91"):
    obj = {
        "issue": {"number": 1156},
        "comment": {"id": 111, "body": marker, "author_association": association,
                    "user": {"login": actor}},
    }
    path.write_text(json.dumps(obj))
    return path


class NativeSolDispatchTests(unittest.TestCase):
    def test_exact_owner_comment_only(self):
        with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, ENV):
            p = Path(td) / "event.json"
            event(p, f"[S1_SOL_MAX_ELITE] mission={MISSION}")
            self.assertEqual(d.owner_event(p, mode="submit")[0], MISSION)
            event(p, f"[S1_SOL_MAX_ELITE_COLLECT] run={RUN}")
            self.assertEqual(d.owner_event(p, mode="collect")[0], RUN)
            event(p, f"[S1_SOL_MAX_ELITE] mission={MISSION}", association="NONE")
            with self.assertRaisesRegex(ValueError, "NOT_OWNER_ISSUE_COMMENT"):
                d.owner_event(p, mode="submit")
            event(p, f"[S1_SOL_MAX_ELITE] mission={MISSION}", actor="attacker")
            with self.assertRaisesRegex(ValueError, "NOT_OWNER_ISSUE_COMMENT"):
                d.owner_event(p, mode="submit")
            event(p, "[S1_SOL_MAX_ELITE] mission=evil\nrm -rf /")
            with self.assertRaisesRegex(ValueError, "COMMENT_MARKER_INVALID"):
                d.owner_event(p, mode="submit")

    def test_actual_runner_module_cli_loads_without_pythonpath_hack(self):
        result = subprocess.run(
            [sys.executable, "-m", "scripts.api_agent.sol_max_elite_dispatch", "--help"],
            capture_output=True, text=True, check=False, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("preflight", result.stdout)
        self.assertIn("collect", result.stdout)

    def test_native_main_sha_mismatch_blocks_preflight(self):
        with patch.object(d.subprocess, "check_output", return_value=HEAD + "\n"), \
             patch.dict(os.environ, ENV), \
             patch.object(d, "api", return_value={"object": {"sha": "b" * 40}}):
            with self.assertRaisesRegex(ValueError, "STALE_MAIN"):
                d.current_checkout(Path("."))

    def test_staged_mission_is_visible_but_no_paid_admission(self):
        with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, ENV):
            root = Path(td)
            sample(root)
            ef = event(root / "event.json", f"[S1_SOL_MAX_ELITE] mission={MISSION}")
            out = root / "out"
            with patch.object(d, "current_checkout", return_value=HEAD):
                r = d.preflight(root, out, ef)
            self.assertFalse(r["paid_allowed"])
            self.assertEqual(r["state"], "GATED")
            self.assertEqual(r["mission"], MISSION)
            self.assertTrue((out / "source.json").exists())
            self.assertTrue((out / "request.json").exists())
            with patch.object(d, "gh", side_effect=AssertionError("no claim expected")):
                with self.assertRaisesRegex(ValueError, "STILL_GATED"):
                    d.reserve(root, out, ef)

    def test_bad_native_claim_census_never_retries_a_paid_mission(self):
        with patch.object(d, "gh", return_value=json.dumps([[
                {"body": f"{t.CLAIM_PREFIX} garbage", "user": {"login": "github-actions[bot]"}}]])):
            with self.assertRaisesRegex(ValueError, "SCHEMA_OR_ACTOR"):
                d.all_native_claims()
        valid = t.claim_body(MISSION, HEAD, "c" * 64)
        with patch.object(d, "gh", return_value=json.dumps([[
                {"body": valid, "user": {"login": "github-actions[bot]"}, "id": 6}]])):
            self.assertEqual(len(d.all_native_claims()), 1)
        with self.assertRaisesRegex(ValueError, "ALREADY_CLAIMED_NO_REPOST"):
            t.check_unspent_claim(
                [{"body": valid, "user": {"login": "github-actions[bot]"}}], MISSION)

    def test_account_wide_cost_guard_and_native_claim_capacity(self):
        with tempfile.TemporaryDirectory() as td:
            ready = SimpleNamespace(returncode=0, stdout=json.dumps({
                "status": "PASS", "remaining_usd": 29.0}) + "\n")
            with patch.object(d.subprocess, "run", return_value=ready):
                self.assertEqual(d.check_budget(Path(td), [])["remaining"], 29.0)
                with self.assertRaisesRegex(ValueError, "BUDGET_OR_CLAIM_LIMIT"):
                    d.check_budget(Path(td), [{} for _ in range(5)])
            missing = SimpleNamespace(returncode=1, stdout="")
            with patch.object(d.subprocess, "run", return_value=missing):
                with self.assertRaisesRegex(ValueError, "MONTHLY_BUDGET_GUARD"):
                    d.check_budget(Path(td), [])

    def test_rerun_or_different_actor_never_claims(self):
        with patch.dict(os.environ, ENV):
            with patch.object(d, "api", return_value={
                "id": int(RUN), "head_sha": HEAD, "event": "issue_comment",
                "name": "Framework Learning Supervisor",
                "actor": {"login": "Donh91"}}):
                self.assertEqual(d.require_original_owner_run(HEAD)["head_sha"], HEAD)
            with patch.dict(os.environ, {"GITHUB_RUN_ATTEMPT": "2"}):
                with self.assertRaisesRegex(ValueError, "RERUN"):
                    d.require_original_owner_run(HEAD)

    def test_reserved_submission_remains_pinned_if_unrelated_main_advances(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "out"
            out.mkdir()
            (out / "request.json").write_text("{}")
            (out / "reservation.json").write_text(json.dumps({
                "mission": MISSION, "source_head": HEAD}))
            with patch.object(d, "owner_event", return_value=(MISSION, {})), \
                 patch.object(d.t, "read_registration", return_value={}), \
                 patch.object(d.subprocess, "check_output", return_value=HEAD), \
                 patch.object(d, "current_checkout", side_effect=AssertionError("do not reread moving main")), \
                 patch.object(d.t, "submit_one", return_value={"status": "PENDING_COLLECT"}) as api:
                result = d.submit(root, out, root / "event.json")
            self.assertEqual(result["status"], "PENDING_COLLECT")
            self.assertEqual(api.call_count, 1)

    def test_collect_is_only_get_and_never_writer(self):
        with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, ENV):
            root = Path(td)
            packet = {
                "contract": "S1_SOL_ELITE_SOURCE_PACKET_v1", "repo": t.REPO,
                "mission_id": MISSION, "source_head": HEAD, "source_files": {},
            }
            req = t.checked_request(packet)
            claim = {
                "id": 42, "mission": MISSION, "source_head": HEAD,
                "origin_run_id": RUN, "body": t.claim_body(MISSION, HEAD, t.digest(t.canonical(req))),
            }
            origin = root / "origin"
            (origin / "post").mkdir(parents=True)
            (origin / "source.json").write_text(json.dumps(packet))
            (origin / "request.json").write_text(json.dumps(req))
            (origin / "reservation.json").write_text(json.dumps(claim))
            (origin / "post/response_handle.json").write_text(json.dumps({
                "response_id": "resp_good123", "claim_id": 42, "claim_body": claim["body"]}))
            ef = event(root / "event.json", f"[S1_SOL_MAX_ELITE_COLLECT] run={RUN}")
            def native(path):
                if path.startswith("actions/runs/"):
                    return {"name": "Framework Learning Supervisor",
                            "event": "issue_comment", "head_sha": HEAD,
                            "actor": {"login": "Donh91"}}
                if path.startswith("issues/comments/"):
                    return {"body": claim["body"], "user": {"login": "github-actions[bot]"}}
                raise AssertionError("invalid native request")
            with patch.object(d, "api", side_effect=native), \
                 patch.object(d.t, "collect_one", return_value=(200, {
                    "id": "resp_good123", "status": "completed",
                    "usage": {"input_tokens": 12, "output_tokens": 24}})) as getter:
                result = d.collect(root / "collected", origin, ef)
            self.assertEqual(result["status"], "COMPLETED")
            self.assertFalse(result["new_paid_post"])
            self.assertFalse(result["source_applied"])
            self.assertFalse(result["merge_authorized"])
            self.assertEqual(getter.call_count, 1)

    def test_existing_workflow_owns_paired_submit_and_get_only(self):
        workflow = Path(".github/workflows/framework-learning-supervisor.yml").read_text()
        self.assertIn("sol-max-elite-submit:", workflow)
        self.assertIn("sol-max-elite-collect:", workflow)
        self.assertIn("github.event.comment.author_association == 'OWNER'", workflow)
        collect = workflow.split("  sol-max-elite-collect:", 1)[1].split(
            "  sol-max-implementation-patch:", 1)[0]
        command = "python -m scripts.api_agent.sol_max_elite_dispatch "
        self.assertEqual(workflow.count(command), 4)
        self.assertIn(command + "collect", collect)
        self.assertNotIn(command + "submit", collect)
        self.assertNotIn("python scripts/api_agent/sol_max_elite_dispatch.py", workflow)
        self.assertNotIn("api_gateway.py", collect)
        self.assertIn("if: always()", collect)
        self.assertIn("s1-sol-elite-attempt-", workflow)

    def test_real_p0_transport_sources_fit_public_cost_bounds(self):
        packet = t.render_source(Path("."), "S1-API-RESILIENCE-20261104", HEAD)
        self.assertEqual(packet["file_count"], 6)
        self.assertLess(packet["cost_ceiling_usd"], 3)
        self.assertGreater(len(t.canonical(packet["packet"])), 100_000)
        self.assertFalse(packet["dispatch_enabled"])

    def test_unmerged_original_forecast_branch_is_not_faked_as_main(self):
        # Original #1879 source ownership is NOT interchangeable with main.
        with self.assertRaisesRegex(ValueError, "ELITE_PUBLIC_SOURCE_UNAVAILABLE"):
            t.render_source(Path("."), "S1-FORECAST-UNLOCK-20261104", HEAD)

    def test_origin_artifact_attack_rejected_before_provider(self):
        with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, ENV):
            root = Path(td)
            (root / "post").mkdir()
            (root / "source.json").write_text("{}")
            (root / "request.json").write_text("{}")
            (root / "reservation.json").write_text("{}")
            (root / "post/response_handle.json").write_text("{}")
            ef = event(root / "event.json", f"[S1_SOL_MAX_ELITE_COLLECT] run={RUN}")
            with patch.object(d.t, "collect_one", side_effect=AssertionError("no GET")):
                with self.assertRaisesRegex(ValueError, "ORIGIN_ARTIFACT_DRIFT"):
                    d.collect(root / "out", root, ef)


if __name__ == "__main__":
    unittest.main()
