"""Offline BUILD_v1 sandbox security tests; native Docker smoke tests separately."""
import copy
import hashlib
import tempfile
import subprocess
import unittest
from pathlib import Path
from unittest import mock

from scripts.api_agent import astra_build_admit_v1 as admit
from scripts.api_agent import astra_build_sandbox_v1 as s


class BuildSandboxTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.src = self.root / "trusted"
        self.src.mkdir()
        # The fixed governance suite needs public fixtures, not the entire
        # control-plane archive or any Vault metadata.
        for fixture in s.REQUIRED_PUBLIC_FIXTURES:
            loc = self.src / fixture
            loc.parent.mkdir(parents=True, exist_ok=True)
            loc.write_text("public fixed-test fixture\n", encoding="utf-8")
        (self.src / "scripts/learning").mkdir(parents=True)
        self.path = self.src / "scripts/learning/existing.py"
        self.path.write_text("def source():\n    return 1\n", encoding="utf-8")
        self.pathname = "scripts/learning/existing.py"
        self.created = "tests/learning/test_new.py"
        self.main = "a" * 40
        self.scope = {
            "contract": admit.SCOPE_CONTRACT,
            "mission_id": "ASTRA-KOMPAS-BUILD-M1-20261121",
            "main_sha": self.main,
            "test_command_id": "M1",
            "allowlist": ["scripts/learning/**", "tests/learning/**"],
            "source_files": {self.pathname: {
                "sha256": hashlib.sha256(self.path.read_bytes()).hexdigest(),
                "mode": "100644"}, self.created: None},
            "stage": 1,
            "previous_repair": None,
        }
        # Exact source copier now requires an actual Git index. No network,
        # identity from global config, credential, or remote is used.
        subprocess.run(["git", "-C", str(self.src), "init", "-q"],
                       check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.src), "add", "."],
                       check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.src),
                        "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                        "commit", "-qm", "frozen public test fixture"],
                       check=True, capture_output=True)
        self.proposal = {
            "status": "BUILD", "test_command_id": "M1",
            "rationale": "a", "risks": [],
            "files": [{"path": self.created, "action": "create",
                       "content": "def test_one():\n    assert True\n"}],
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_fixed_command_and_security_profile(self):
        name, cmd = s.docker_command(self.src, "M1", 0)
        self.assertTrue(name.startswith("astra-build-"))
        self.assertIn("--network", cmd)
        self.assertEqual(cmd[cmd.index("--network")+1], "none")
        self.assertIn("--read-only", cmd)
        self.assertIn("--cap-drop", cmd)
        self.assertEqual(cmd[cmd.index("--cap-drop")+1], "ALL")
        self.assertIn("--security-opt", cmd)
        self.assertEqual(cmd[cmd.index("--security-opt")+1], "no-new-privileges")
        self.assertEqual(cmd[cmd.index("--user")+1], "65534:65534")
        # Four prior mutation survivors: removing resource limits or
        # the local-only image policy MUST break the native test.
        self.assertEqual(cmd[cmd.index("--pull")+1], "never")
        for flag, value in (("--memory", "256m"), ("--memory-swap", "256m"),
                            ("--cpus", "0.5"), ("--pids-limit", "32")):
            self.assertIn(flag, cmd)
            self.assertEqual(cmd[cmd.index(flag)+1], value)
        self.assertIn("readonly", cmd[cmd.index("--mount")+1])
        self.assertEqual(tuple(cmd[-len(admit.TEST_COMMANDS["M1"][0]):]),
                         admit.TEST_COMMANDS["M1"][0])
        self.assertNotIn("curl", cmd)
        for bad in ("bash -c rm -rf /", "", "M999"):
            with self.subTest(bad=bad), self.assertRaises(s.SandboxBlocked):
                s.docker_command(self.src, bad, 0)
        with self.assertRaises(s.SandboxBlocked):
            s.docker_command(self.src, "M1", 88)
        with self.assertRaises(s.SandboxBlocked):
            s.docker_command(self.src, "M1", 0, image="python:latest")

    def test_real_suite_stdout_gate_blocks_os_exit_zero(self):
        command = ["docker", "run", s.IMAGE, "python", "-m", "pytest", "-q"]
        self.assertEqual(s.observed_test_count(command, b""), 0)
        self.assertEqual(s.observed_test_count(command, b"1 passed in 0.2s"), 1)
        self.assertEqual(s.observed_test_count(command, b"no tests ran in 0.1s"), 0)
        node = ["docker", "run", s.IMAGE, "node", "--test", "tests"]
        self.assertEqual(s.observed_test_count(node, b"# tests 3\n# pass 3\n# fail 0\n"), 3)
        self.assertEqual(s.observed_test_count(node, b"# tests 3\n# pass 0\n# fail 0\n"), 0)

    def test_source_copy_omits_git_and_rejects_symlinks(self):
        self.assertTrue((self.src / ".git/config").exists())
        dst = self.root / "copied"
        dst.mkdir()
        out = s._copy_public_tree(self.src, dst)
        self.assertGreaterEqual(out["files"], 1)
        self.assertTrue((dst / ".git").is_dir())
        self.assertTrue((dst / self.pathname).is_file())
        self.assertEqual(subprocess.check_output(
            ["git", "-C", str(dst), "rev-parse", "HEAD"],
            text=True).strip(), out["local_synthetic_git_sha"])
        self.assertFalse(out["local_synthetic_git_is_original_main"])
        self.assertEqual(subprocess.check_output(
            ["git", "-C", str(dst), "remote"], text=True).strip(), "")
        self.assertFalse((dst / ".git/FETCH_HEAD").exists())
        (self.src / "scripts/learning/bad.py").symlink_to(self.path)
        with self.assertRaisesRegex(s.SandboxBlocked,
                                        "SOURCE_UNTRACKED_OR_IGNORED|SOURCE_SPECIAL_OR_SYMLINK"):
            s._copy_public_tree(self.src, self.root / "other")

    def test_untracked_and_gitignored_source_never_copied(self):
        planted = self.src / "scripts/learning/untracked_planted.py"
        planted.write_text("print('untrusted')", encoding="utf-8")
        with self.assertRaisesRegex(s.SandboxBlocked,
                                    "SOURCE_UNTRACKED_OR_IGNORED"):
            s._copy_public_tree(self.src, self.root / "untracked_out")
        planted.unlink()
        (self.src / ".gitignore").write_text("scripts/learning/ignored_planted.py\n")
        ignored = self.src / "scripts/learning/ignored_planted.py"
        ignored.write_text("print('ignored')", encoding="utf-8")
        with self.assertRaisesRegex(s.SandboxBlocked,
                                    "SOURCE_UNTRACKED_OR_IGNORED"):
            s._copy_public_tree(self.src, self.root / "ignored_out")

    def test_required_governance_fixture_copy_is_narrow(self):
        archive = self.src / "00_ARCHIVE_CONTROL"
        (archive / "vault_backup_registry.json").write_text("PRIVATE_NOT_FOR_SANDBOX")
        dest = self.root / "publiccopy"
        dest.mkdir()
        receipt = s._copy_public_tree(self.src, dest)
        self.assertEqual(receipt["public_fixture_count"], 3)
        for path in s.REQUIRED_PUBLIC_FIXTURES:
            self.assertEqual((dest / path).read_bytes(), (self.src / path).read_bytes())
        self.assertFalse((dest / "00_ARCHIVE_CONTROL/vault_backup_registry.json").exists())

    def test_missing_required_governance_fixture_halts(self):
        (self.src / "AGENTS.md").unlink()
        dest = self.root / "miss"
        dest.mkdir()
        with self.assertRaisesRegex(s.SandboxBlocked, "REQUIRED_FIXED_TEST_FIXTURE_MISSING"):
            s._copy_public_tree(self.src, dest)

    def test_symlinked_control_plane_fixture_halts(self):
        path = self.src / "00_ARCHIVE_CONTROL/CANONICAL_INDEX.md"
        path.unlink()
        path.symlink_to(self.src / "AGENTS.md")
        dest = self.root / "links"
        dest.mkdir()
        with self.assertRaisesRegex(s.SandboxBlocked, "SOURCE_FILE_SPECIAL"):
            s._copy_public_tree(self.src, dest)

    def test_admitted_files_are_only_staged_in_temp_with_hash(self):
        raw = admit.canonical(self.proposal)
        pass_result = {"returncode": 0, "output_sha256": "0" * 64,
                       "output_bytes": 0, "last_200_lines": [], "status": "EXIT0_WITH_UNTRUSTED_SUMMARY",
                       "completed_tests_observed": 1}
        with mock.patch.object(s, "verify_snapshot", return_value=self.main), \
             mock.patch.object(s, "_run_once", return_value=pass_result) as run:
            result = s.run_admitted(raw, self.scope, self.src)
        self.assertEqual(result["status"], "TEST_COMPLETION_UNATTESTED")
        self.assertFalse(result["independent_completion_attested"])
        self.assertEqual(result["main_sha"], self.main)
        self.assertEqual(result["test_command_id"], "M1")
        self.assertEqual(result["network"], "none")
        self.assertFalse(result["secrets"])
        self.assertFalse(result["paid_authority"])
        self.assertFalse(result["merge_authority"])
        self.assertEqual(run.call_count, 4)
        self.assertFalse((self.src / self.created).exists())
        self.assertEqual(self.path.read_text(), "def source():\n    return 1\n")

    def test_baseline_must_finish_before_any_model_file_is_staged(self):
        raw = admit.canonical(self.proposal)
        failed = {"returncode": 1, "output_sha256": "0"*64,
                  "completed_tests_observed": 0, "status": "TEST_FAILURE"}
        with mock.patch.object(s, "verify_snapshot", return_value=self.main), \
             mock.patch.object(s, "_run_once", return_value=failed), \
             mock.patch.object(s, "_write_admitted") as stage:
            with self.assertRaisesRegex(s.SandboxBlocked,
                                         "FIXED_SUITE_BASELINE_NOT_PROVEN"):
                s.run_admitted(raw, self.scope, self.src)
            stage.assert_not_called()

    def test_test_failure_is_not_success(self):
        raw = admit.canonical(self.proposal)
        success = {"returncode": 0, "output_sha256": "0" * 64,
                   "output_bytes": 24, "last_200_lines": ["1 passed in 0.1s"],
                   "status": "EXIT0_WITH_UNTRUSTED_SUMMARY", "completed_tests_observed": 1}
        fail_result = {"returncode": 1, "output_sha256": "1" * 64,
                       "output_bytes": 7, "last_200_lines": ["fail"],
                       "status": "TEST_FAILURE", "completed_tests_observed": 0}
        with mock.patch.object(s, "verify_snapshot", return_value=self.main), \
             mock.patch.object(s, "_run_once", side_effect=[success, success, fail_result, fail_result]):
            result = s.run_admitted(raw, self.scope, self.src)
        self.assertEqual(result["status"], "TEST_FAILURE")

    def test_modified_preimage_drift_stops(self):
        altered = copy.deepcopy(self.proposal)
        altered["files"][0] = {"path": self.pathname, "action": "modify",
                                "content": "def source():\n    return 2\n"}
        scope = copy.deepcopy(self.scope)
        scope["source_files"][self.pathname]["sha256"] = "e" * 64
        success = {"returncode": 0, "status": "EXIT0_WITH_UNTRUSTED_SUMMARY", "completed_tests_observed": 1}
        with mock.patch.object(s, "verify_snapshot", return_value=self.main), \
             mock.patch.object(s, "_run_once", return_value=success):
            with self.assertRaisesRegex(s.SandboxBlocked, "MODIFY_PREIMAGE_DRIFT"):
                s.run_admitted(admit.canonical(altered), scope, self.src)

    def test_unverified_main_cannot_execute(self):
        with mock.patch.object(s, "verify_snapshot",
                               side_effect=s.SandboxBlocked("SOURCE_MAIN_OR_DIRTY")), \
             mock.patch.object(s, "_run_once") as run:
            with self.assertRaisesRegex(s.SandboxBlocked, "SOURCE_MAIN_OR_DIRTY"):
                s.run_admitted(admit.canonical(self.proposal), self.scope, self.src)
            run.assert_not_called()

    def test_model_command_injection_refused_before_docker(self):
        payload = copy.deepcopy(self.proposal)
        payload["test_command_id"] = "bash -c 'curl example.com'"
        with mock.patch.object(s, "_run_once") as run:
            with self.assertRaises(admit.AdmissionBlocked):
                s.run_admitted(admit.canonical(payload), self.scope, self.src)
            run.assert_not_called()

    def test_invalid_source_head_is_refused(self):
        with self.assertRaisesRegex(s.SandboxBlocked, "SOURCE_SHA"):
            s.verify_snapshot(self.src, "NOT_A_HASH")


    def test_real_docker_smoke_contract_under_mock(self):
        good = {"status": "EXIT0_WITH_UNTRUSTED_SUMMARY", "returncode": 0, "output_sha256": "a"*64,
                "output_bytes": 0, "last_200_lines": []}
        mutant = {"status": "TEST_FAILURE", "returncode": 1,
                  "output_sha256": "b"*64,
                  "output_bytes": 1, "last_200_lines": ["failure"]}
        early = {"status": "TEST_FAILURE", "returncode": 0,
                 "completed_tests_observed": 0}
        with mock.patch.object(s, "_run_once", side_effect=[good, mutant, early]) as run:
            receipt = s.smoke()
        self.assertEqual(receipt["status"], "PASS")
        self.assertTrue(receipt["network_attempt_executed"])
        self.assertTrue(receipt["network_denied"])
        self.assertTrue(receipt["synthetic_only"])
        self.assertEqual(run.call_count, 3)
        self.assertEqual(receipt["early_exit_zero"]["status"], "TEST_FAILURE")
        for call in run.call_args_list:
            argv = call.args[0]
            self.assertEqual(argv[argv.index("--network")+1], "none")
            self.assertEqual(argv[-6:],
                             ["python", "-m", "unittest", "discover", "-s",
                              "tests/smoke", "-v"][-6:])

    def test_real_docker_smoke_rejects_false_pass(self):
        good = {"status": "EXIT0_WITH_UNTRUSTED_SUMMARY", "returncode": 0}
        with mock.patch.object(s, "_run_once", side_effect=[good, good]):
            with self.assertRaisesRegex(s.SandboxBlocked, "MUTATION_NOT_DETECTED"):
                s.smoke()
        bad = {"status": "TEST_FAILURE", "returncode": 1}
        with mock.patch.object(s, "_run_once", side_effect=[good, bad, good]):
            with self.assertRaisesRegex(s.SandboxBlocked,
                                        "EXIT_ZERO_WITHOUT_SUITE_END_FALSE_PASS"):
                s.smoke()
        with mock.patch.object(s, "_run_once", return_value=bad):
            with self.assertRaisesRegex(s.SandboxBlocked,
                                        "NETWORK_DENIAL_FAILED"):
                s.smoke()


if __name__ == "__main__":
    unittest.main()
