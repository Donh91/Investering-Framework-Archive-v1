"""Offline BUILD_v1 sandbox security tests; native Docker smoke tests separately."""
import copy
import hashlib
import tempfile
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

    def test_source_copy_omits_git_and_rejects_symlinks(self):
        (self.src / ".git").mkdir()
        (self.src / ".git/config").write_text("secret")
        dst = self.root / "copied"
        dst.mkdir()
        out = s._copy_public_tree(self.src, dst)
        self.assertGreaterEqual(out["files"], 1)
        self.assertFalse((dst / ".git").exists())
        self.assertTrue((dst / self.pathname).is_file())
        (self.src / "scripts/learning/bad.py").symlink_to(self.path)
        with self.assertRaisesRegex(s.SandboxBlocked, "SOURCE_SPECIAL_OR_SYMLINK"):
            s._copy_public_tree(self.src, self.root / "other")

    def test_admitted_files_are_only_staged_in_temp_with_hash(self):
        raw = admit.canonical(self.proposal)
        pass_result = {"returncode": 0, "output_sha256": "0" * 64,
                       "output_bytes": 0, "last_200_lines": [], "status": "PASS"}
        with mock.patch.object(s, "verify_snapshot", return_value=self.main), \
             mock.patch.object(s, "_run_once", return_value=pass_result) as run:
            result = s.run_admitted(raw, self.scope, self.src)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["main_sha"], self.main)
        self.assertEqual(result["test_command_id"], "M1")
        self.assertEqual(result["network"], "none")
        self.assertFalse(result["secrets"])
        self.assertFalse(result["paid_authority"])
        self.assertFalse(result["merge_authority"])
        self.assertEqual(run.call_count, 2)
        self.assertFalse((self.src / self.created).exists())
        self.assertEqual(self.path.read_text(), "def source():\n    return 1\n")

    def test_test_failure_is_not_success(self):
        raw = admit.canonical(self.proposal)
        fail_result = {"returncode": 1, "output_sha256": "1" * 64,
                       "output_bytes": 7, "last_200_lines": ["fail"],
                       "status": "TEST_FAILURE"}
        with mock.patch.object(s, "verify_snapshot", return_value=self.main), \
             mock.patch.object(s, "_run_once", return_value=fail_result):
            result = s.run_admitted(raw, self.scope, self.src)
        self.assertEqual(result["status"], "TEST_FAILURE")

    def test_modified_preimage_drift_stops(self):
        altered = copy.deepcopy(self.proposal)
        altered["files"][0] = {"path": self.pathname, "action": "modify",
                                "content": "def source():\n    return 2\n"}
        scope = copy.deepcopy(self.scope)
        scope["source_files"][self.pathname]["sha256"] = "e" * 64
        with mock.patch.object(s, "verify_snapshot", return_value=self.main):
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
        good = {"status": "PASS", "returncode": 0, "output_sha256": "a"*64,
                "output_bytes": 0, "last_200_lines": []}
        mutant = {"status": "TEST_FAILURE", "returncode": 1,
                  "output_sha256": "b"*64,
                  "output_bytes": 1, "last_200_lines": ["failure"]}
        with mock.patch.object(s, "_run_once", side_effect=[good, mutant]) as run:
            receipt = s.smoke()
        self.assertEqual(receipt["status"], "PASS")
        self.assertTrue(receipt["network_attempt_executed"])
        self.assertTrue(receipt["network_denied"])
        self.assertTrue(receipt["synthetic_only"])
        self.assertEqual(run.call_count, 2)
        for call in run.call_args_list:
            argv = call.args[0]
            self.assertEqual(argv[argv.index("--network")+1], "none")
            self.assertEqual(argv[-6:],
                             ["python", "-m", "unittest", "discover", "-s",
                              "tests/smoke", "-v"][-6:])

    def test_real_docker_smoke_rejects_false_pass(self):
        good = {"status": "PASS", "returncode": 0}
        with mock.patch.object(s, "_run_once", side_effect=[good, good]):
            with self.assertRaisesRegex(s.SandboxBlocked, "MUTATION_NOT_DETECTED"):
                s.smoke()
        bad = {"status": "TEST_FAILURE", "returncode": 1}
        with mock.patch.object(s, "_run_once", return_value=bad):
            with self.assertRaisesRegex(s.SandboxBlocked,
                                        "NETWORK_DENIAL_FAILED"):
                s.smoke()


if __name__ == "__main__":
    unittest.main()
