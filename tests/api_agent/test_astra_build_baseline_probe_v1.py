"""Trusted pristine baseline and model-copy separation, all synthetic fixtures."""
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.api_agent import astra_build_baseline_probe_v1 as probe
from scripts.api_agent import astra_build_admit_v1 as admit
from scripts.api_agent import astra_build_sandbox_v1 as sandbox


class BaselineTrustBoundaryTests(unittest.TestCase):
    def test_full_pristine_suite_does_not_test_restricted_candidate_copy(self):
        sha = "a" * 40
        image_id = "sha256:" + "b" * 64
        seen_roots = []
        def command(root, scope, ordinal, *, profile="trusted_full_main"):
            seen_roots.append((root, scope, ordinal, profile))
            fixed = (admit.PREFILTER_COMMANDS if profile == "restricted_candidate"
                     else admit.TEST_COMMANDS)[scope][ordinal]
            return "fixed-job", ["docker", "run", sandbox.IMAGE, *fixed]
        positive = {
            "status": "EXIT0_WITH_UNTRUSTED_SUMMARY", "returncode": 0,
            "completed_tests_observed": 5, "output_sha256": "f" * 64,
            "last_200_lines": [], "failure_diagnostics_untrusted": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            pristine = Path(tmp) / "pristine"
            pristine.mkdir()
            with mock.patch.object(probe.subprocess, "check_output",
                                   return_value=image_id + "\n"), \
                 mock.patch.object(probe, "native_pristine_source", return_value=sha), \
                 mock.patch.object(sandbox, "_copy_public_tree",
                                   return_value={"files": 10, "bytes": 100}), \
                 mock.patch.object(sandbox, "docker_command", side_effect=command), \
                 mock.patch.object(sandbox, "_run_once",
                                   return_value=positive) as run:
                result = probe.probe(pristine, sha, image_id)
            self.assertEqual(result["probe_result"], "CANDIDATE_BASELINES_LOOK_COMPLETE")
            self.assertEqual(len(seen_roots), 6)
            self.assertEqual(sum(row[3] == "restricted_candidate" for row in seen_roots), 3)
            self.assertTrue(all(row[0] != pristine.resolve() for row in seen_roots[:3]))
            self.assertTrue(all(row[0] == pristine.resolve() for row in seen_roots[3:]))
            self.assertEqual(result["baseline_workspace"],
                             "TRUSTED_PRISTINE_MAIN_READONLY_NO_MODEL")
            self.assertEqual(result["candidate_workspace"], "RESTRICTED_PUBLIC_COPY")
            self.assertEqual(run.call_count, 6)
            self.assertEqual(len(result["prefilter_results"]), 3)
            self.assertEqual(len(result["results"]), 3)
            self.assertFalse(result["candidate_test_completion_attested"])
            self.assertFalse(result["build_hold_lifted"])
            self.assertFalse(result["paid_or_merge_authority"])

    def test_failed_full_main_baseline_still_blocks(self):
        sha = "a" * 40
        image_id = "sha256:" + "b" * 64
        failed = {
            "status": "TEST_FAILURE", "returncode": 1,
            "completed_tests_observed": 0, "output_sha256": "f" * 64,
            "last_200_lines": ["test failure"],
        }
        with tempfile.TemporaryDirectory() as tmp:
            pristine = Path(tmp)
            def command(root, scope, ordinal, *, profile="trusted_full_main"):
                fixed = (admit.PREFILTER_COMMANDS if profile == "restricted_candidate"
                         else admit.TEST_COMMANDS)[scope][ordinal]
                return "fixed-job", ["docker", "run", sandbox.IMAGE, *fixed]
            with mock.patch.object(probe.subprocess, "check_output",
                                   return_value=image_id + "\n"), \
                 mock.patch.object(probe, "native_pristine_source", return_value=sha), \
                 mock.patch.object(sandbox, "_copy_public_tree",
                                   return_value={"files": 1}), \
                 mock.patch.object(sandbox, "docker_command", side_effect=command), \
                 mock.patch.object(sandbox, "_run_once", return_value=failed):
                result = probe.probe(pristine, sha, image_id)
            self.assertEqual(result["probe_result"], "BASELINES_FAIL_OR_INCOMPLETE")
            self.assertFalse(result["build_hold_lifted"])

    def test_bad_pristine_prefilter_fails_before_large_full_suite(self):
        sha = "a" * 40
        image_id = "sha256:" + "b" * 64
        failed = {"status": "TEST_FAILURE", "returncode": 1,
                  "completed_tests_observed": 0, "output_sha256": "f"*64,
                  "last_200_lines": ["missing fixture"]}
        with tempfile.TemporaryDirectory() as tmp:
            pristine=Path(tmp)
            def command(root,scope,ordinal,*,profile="trusted_full_main"):
                fixed=(admit.PREFILTER_COMMANDS if profile=="restricted_candidate"
                       else admit.TEST_COMMANDS)[scope][ordinal]
                return "fixed",["docker","run",sandbox.IMAGE,*fixed]
            with mock.patch.object(probe.subprocess,"check_output",
                                   return_value=image_id+"\n"), \
                 mock.patch.object(probe,"native_pristine_source",return_value=sha), \
                 mock.patch.object(sandbox,"_copy_public_tree",
                                   return_value={"files":1}), \
                 mock.patch.object(sandbox,"docker_command",side_effect=command), \
                 mock.patch.object(sandbox,"_run_once",return_value=failed) as run:
                receipt=probe.probe(pristine,sha,image_id)
            self.assertEqual(receipt["probe_result"],"BASELINES_FAIL_OR_INCOMPLETE")
            self.assertEqual(len(receipt["prefilter_results"]),3)
            self.assertEqual(receipt["results"],[])
            self.assertEqual(run.call_count,3)
            self.assertFalse(receipt["build_hold_lifted"])



if __name__ == "__main__":
    unittest.main()
