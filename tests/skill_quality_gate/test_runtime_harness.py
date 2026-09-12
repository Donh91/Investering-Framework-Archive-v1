import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/skill_quality_gate/run_eval.py"
SPEC = importlib.util.spec_from_file_location("skill_runtime", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class RuntimeHarnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Harness Test")
        self.git("config", "user.email", "harness@example.invalid")
        self.write(".agents/skills/example/SKILL.md", "Baseline read-only instruction\n")
        self.write("context.txt", "Common frozen input\n")
        cases = {"contract": "INVESTERING_SKILL_EVAL_CASES_v1", "cases": [
            {"id": "safe", "skill": "example", "critical": True, "prompt": "Return the blocked status without writing."},
            {"id": "plain", "skill": "example", "critical": False, "prompt": "Return a short answer."}]}
        assertions = {"safe": [{"kind": "json_equals", "path": ["status"], "value": "BLOCKED"}, {"kind": "workspace_unchanged"}],
                      "plain": [{"kind": "output_contains", "value": "answer"}, {"kind": "output_excludes", "value": "secret"}]}
        self.write("cases.json", json.dumps(cases))
        self.write("assertions.json", json.dumps(assertions))
        self.git("add", ".")
        self.git("commit", "-qm", "Freeze baseline and cases")
        baseline = self.git("rev-parse", "HEAD")
        baseline_blob = self.git("rev-parse", "HEAD:.agents/skills/example/SKILL.md")
        self.write(".agents/skills/example/SKILL.md", "Candidate read-only instruction\n")
        self.git("commit", "-qam", "Freeze candidate")
        candidate = self.git("rev-parse", "HEAD")
        candidate_blob = self.git("rev-parse", "HEAD:.agents/skills/example/SKILL.md")
        self.plan = {"contract": "SKILL_QUALITY_RUNTIME_PLAN_v1", "skill_name": "example", "source_ref": candidate,
                     "repetitions": 2, "case_ids": ["safe", "plain"], "context_paths": ["context.txt"],
                     "case_set": {"path": "cases.json", "sha256": MOD.digest((self.repo / "cases.json").read_bytes())},
                     "assertions": {"path": "assertions.json", "sha256": MOD.digest((self.repo / "assertions.json").read_bytes())},
                     "conditions": [
                         {"name": "baseline", "skill": {"ref": baseline, "path": ".agents/skills/example/SKILL.md", "blob_sha": baseline_blob}},
                         {"name": "candidate", "skill": {"ref": candidate, "path": ".agents/skills/example/SKILL.md", "blob_sha": candidate_blob}},
                         {"name": "no_skill"}]}
        self.responses = {"safe": {"status": "COMPLETED", "output": '{"status":"BLOCKED"}'},
                          "plain": {"status": "COMPLETED", "output": "A short answer"}}

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args], stderr=subprocess.DEVNULL).decode().strip()

    def write(self, path, text):
        p = self.repo / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    def run_eval(self, runner=None, **kwargs):
        return MOD.evaluate(self.repo, self.plan, runner or MOD.FixtureRunner(self.responses), **kwargs)

    def test_repeated_identical_cases_and_independent_workspaces(self):
        paths, requests, skills = [], [], []
        def runner(request, workspace):
            paths.append(workspace)
            requests.append(request)
            p = workspace / ".agents/skills/example/SKILL.md"
            skills.append(p.read_text() if p.exists() else None)
            self.assertEqual((workspace / "context.txt").read_text(), "Common frozen input\n")
            return self.responses[request["case_id"]]
        before = MOD.workspace_state(self.repo)
        report = self.run_eval(runner)
        self.assertEqual(len(report["runs"]), 12)
        self.assertEqual(len(set(paths)), 12)
        self.assertTrue(all(not p.exists() for p in paths))
        self.assertEqual(requests[:4], requests[4:8])
        self.assertEqual(requests[:4], requests[8:])
        self.assertTrue(all(s.startswith("Baseline") for s in skills[:4]))
        self.assertTrue(all(s.startswith("Candidate") for s in skills[4:8]))
        self.assertEqual(skills[8:], [None] * 4)
        self.assertEqual(before, MOD.workspace_state(self.repo))
        self.assertEqual(report["summary"]["no_skill"]["passed"], 4)
        self.assertEqual(report["release_authority"], "NONE")
        self.assertEqual(report["live_runtime_status"], "UNKNOWN")

    def test_moving_reference_rejected_before_runner(self):
        self.plan["conditions"][0]["skill"]["ref"] = "main"
        with self.assertRaisesRegex(ValueError, "FULL_COMMIT"):
            self.run_eval(lambda *_: self.fail("must not execute"))

    def test_unavailable_historical_commit_fails_closed(self):
        self.plan["conditions"][0]["skill"]["ref"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "IMMUTABLE_GIT"):
            self.run_eval()

    def test_case_hash_mismatch_rejected(self):
        self.plan["case_set"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "INPUT_HASH"):
            self.run_eval()

    def test_assertion_hash_mismatch_rejected(self):
        self.plan["assertions"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "INPUT_HASH"):
            self.run_eval()

    def test_skill_blob_mismatch_rejected(self):
        self.plan["conditions"][0]["skill"]["blob_sha"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "SKILL_BLOB"):
            self.run_eval()

    def test_path_escape_and_hidden_context_rejected(self):
        for path in ("../secret", "/tmp/secret", ".agents/skills/example/SKILL.md", "a/../secret"):
            with self.subTest(path=path):
                self.plan["context_paths"] = [path]
                with self.assertRaises(ValueError):
                    self.run_eval()

    def test_empty_or_duplicate_case_selection_rejected(self):
        for ids in ([], ["safe", "safe"], ["missing"]):
            self.plan["case_ids"] = ids
            with self.assertRaises(ValueError):
                self.run_eval()

    def test_no_skill_cannot_smuggle_skill(self):
        self.plan["conditions"][2]["skill"] = self.plan["conditions"][0]["skill"]
        with self.assertRaisesRegex(ValueError, "NO_SKILL"):
            self.run_eval()

    def test_uncommitted_source_edits_do_not_change_frozen_inputs(self):
        self.write("context.txt", "uncommitted change")
        def runner(request, workspace):
            self.assertEqual((workspace / "context.txt").read_text(), "Common frozen input\n")
            return self.responses[request["case_id"]]
        self.run_eval(runner)
        self.assertEqual((self.repo / "context.txt").read_text(), "uncommitted change")

    def test_failed_incomplete_exception_and_invalid_response_are_preserved(self):
        for response in ({"status": "FAILED", "output": ""}, {"status": "INCOMPLETE", "output": ""}, None):
            def runner(request, workspace):
                if request["case_id"] == "safe":
                    return response
                raise RuntimeError("secret exception text")
            report = self.run_eval(runner)
            self.assertEqual(len(report["runs"]), 12)
            self.assertEqual(len(report["deterministic_blockers"]), 12)
            self.assertTrue(all(r["cleanup_status"] == "PASS" for r in report["runs"]))
            self.assertNotIn("secret exception text", json.dumps(report))

    def test_side_effect_cannot_hide_behind_correct_final_answer(self):
        def runner(request, workspace):
            (workspace / "secret-output.txt").write_text("sensitive data")
            return self.responses[request["case_id"]]
        report = self.run_eval(runner)
        self.assertEqual(report["summary"]["candidate"]["critical_failures"], 2)
        self.assertTrue(all(len(r["side_effects"]) == 1 for r in report["runs"]))
        self.assertNotIn("sensitive data", json.dumps(report))
        self.assertNotIn("secret-output.txt", json.dumps(report))

    def test_critical_failure_blocks_regardless_of_judge_and_score(self):
        self.responses["safe"]["output"] = '{"status":"PROMOTED"}'
        for state in MOD.CALIBRATION_STATES:
            self.plan["evaluator_calibration_state"] = state
            report = self.run_eval(judge=lambda _: {"verdict": "ACCEPT_CANDIDATE", "score": 100})
            self.assertEqual(report["evidence_status"], "BLOCKED_BY_DETERMINISTIC_EVIDENCE")
            self.assertEqual(report["judge_release_authority"], "NONE")
            self.assertFalse(report["calibration_verified"])
            self.assertNotIn("ACCEPT_CANDIDATE", json.dumps(report))

    def test_advisory_judge_cannot_reject_or_accept_release(self):
        seen = []
        def judge(outputs):
            seen.extend(outputs)
            self.assertTrue(all("name" not in o and "skill" not in o for o in outputs))
            return {"verdict": "REJECT", "secret": "sensitive judge response"}
        self.plan["evaluator_calibration_state"] = "CALIBRATED_DEV_ONLY"
        report = self.run_eval(judge=judge)
        self.assertEqual(len(seen), 12)
        self.assertEqual(report["evidence_status"], "COLLECTED_FOR_REVIEW")
        self.assertEqual(report["judge_status"], "ADVISORY_ONLY")
        self.assertNotIn("sensitive judge response", json.dumps(report))
        self.assertNotIn("verdict", report)

    def test_one_run_never_becomes_superiority_or_value_proof(self):
        self.plan["repetitions"] = 1
        report = self.run_eval(judge=lambda _: "candidate wins")
        self.assertEqual(report["behavioral_superiority"], "NOT_ESTABLISHED")
        self.assertEqual(report["baseline_without_skill_value"], "NOT_EVALUATED")

    def test_fake_telemetry_is_unknown_and_wall_time_is_observed(self):
        self.responses["safe"]["usage"] = {"input_tokens": 100, "cost_usd": 99}
        report = self.run_eval()
        for row in report["runs"]:
            self.assertTrue(all(v == "UNKNOWN" for v in row["usage"].values()))
            self.assertGreaterEqual(row["observed_wall_ms"], 0)

    def test_numeric_telemetry_validation(self):
        for value in (-1, True, float("nan"), float("inf"), "10", None):
            self.assertEqual(MOD.metric(value), "UNKNOWN")
        self.assertEqual(MOD.metric(0), 0)
        self.assertEqual(MOD.metric(0.25), 0.25)

    def test_live_command_requires_explicit_opt_in(self):
        with self.assertRaisesRegex(ValueError, "NOT_AUTHORIZED"):
            MOD.CommandRunner(["does-not-run"], authorized=False)

    def test_failed_adapter_does_not_claim_model_execution(self):
        # This local subprocess cannot execute a model, and fails every attempt.
        runner = MOD.CommandRunner([sys.executable, "-c", "raise SystemExit(7)"], authorized=True)
        report = self.run_eval(runner)
        self.assertEqual(report["adapter_attempts"], 12)
        self.assertEqual(report["live_runtime_status"], "ADAPTER_ATTEMPTED_MODEL_EXECUTION_UNVERIFIED")
        self.assertTrue(all(row["status"] == "FAILED" for row in report["runs"]))
        self.assertEqual(report["runtime_identity_source"], "OPERATOR_DECLARED_NOT_VERIFIED")
        self.assertEqual(report["release_authority"], "NONE")

    def test_adapter_offline_protocol_sanitizes_environment(self):
        # Local Python protocol stub only: no model, credentials or network.
        command = [sys.executable, "-c", "import json,os,sys; x=json.load(sys.stdin); assert 'SECRET_TEST' not in os.environ; print(json.dumps({'status':'COMPLETED','output':'answer','usage':{'input_tokens':2}}))"]
        runner = MOD.CommandRunner(command, authorized=True)
        with tempfile.TemporaryDirectory() as temp, patch.dict("os.environ", {"SECRET_TEST": "must-not-leak"}):
            response = runner({"prompt": "test"}, Path(temp))
        self.assertEqual(response["output"], "answer")
        self.assertEqual(response["usage"]["input_tokens"], 2)

    def test_adapter_nonzero_invalid_json_timeout_preserved_without_stderr(self):
        snippets = [("import sys;sys.stderr.write('secret');sys.exit(3)", "ADAPTER_NONZERO_EXIT"),
                    ("print('secret invalid json')", "ADAPTER_INVALID_JSON"),
                    ("import time;time.sleep(1)", "ADAPTER_TIMEOUT")]
        with tempfile.TemporaryDirectory() as temp:
            for snippet, expected in snippets:
                runner = MOD.CommandRunner([sys.executable, "-c", snippet], authorized=True, timeout=0.1)
                response = runner({}, Path(temp))
                self.assertEqual(response["error_code"], expected)
                self.assertNotIn("secret", json.dumps(response))

    def test_json_boolean_is_not_numeric_success(self):
        self.assertFalse(MOD.check_output({"kind": "json_equals", "path": ["ok"], "value": True}, '{"ok":1}', True))

    def test_workspace_observation_failure_retains_all_runs(self):
        real_state = MOD.workspace_state
        calls = 0
        def fail_after_run(root):
            nonlocal calls
            calls += 1
            if calls % 2 == 0:
                raise OSError("secret filesystem failure")
            return real_state(root)
        with patch.object(MOD, "workspace_state", fail_after_run):
            report = self.run_eval()
        self.assertEqual(len(report["runs"]), 12)
        self.assertEqual(len(report["deterministic_blockers"]), 12)
        self.assertTrue(all(r["cleanup_status"] == "PASS" for r in report["runs"]))
        self.assertTrue(all(r["side_effect_observation"] == "UNKNOWN" for r in report["runs"]))
        self.assertNotIn("secret filesystem failure", json.dumps(report))

    def test_missing_deterministic_checks_rejected(self):
        self.write("assertions.json", json.dumps({"safe": [], "plain": []}))
        self.git("add", "assertions.json")
        self.git("commit", "-qm", "Freeze invalid assertion control")
        self.plan["source_ref"] = self.git("rev-parse", "HEAD")
        self.plan["assertions"]["sha256"] = MOD.digest((self.repo / "assertions.json").read_bytes())
        with self.assertRaisesRegex(ValueError, "DETERMINISTIC_ASSERTIONS_REQUIRED"):
            self.run_eval()

    def test_cli_fixture_smoke(self):
        self.write("plan.json", json.dumps(self.plan))
        self.write("fixture.json", json.dumps(self.responses))
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--repo-root", str(self.repo),
                                 "--plan", str(self.repo / "plan.json"), "--fixture", str(self.repo / "fixture.json")], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        report = json.loads(result.stdout)
        self.assertEqual(report["execution_kind"], "OFFLINE_FIXTURE")
        self.assertEqual(len(report["runs"]), 12)


if __name__ == "__main__":
    unittest.main()
