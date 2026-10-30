"""Unit tests for read-only Supervisor vNEXT main writer discovery."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from scripts.governance.supervisor_main_writer_inventory import census


class MainWriterInventoryTests(unittest.TestCase):
    def check(self, fixtures: dict[str, str]) -> dict:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            d = root / ".github" / "workflows"
            d.mkdir(parents=True)
            for name, content in fixtures.items():
                dest = d / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(content, encoding="utf-8")
            return census(root)

    def test_detects_direct_head_to_main(self):
        result = self.check({"hourly-sequence-capture.yml": """concurrency:
  group: framework-market-owner-writer
permissions:
  contents: write
jobs:
  capture:
    steps:
      - run: |
          git pull --rebase origin main
          git push origin HEAD:main
"""})
        self.assertEqual(result["obvious_direct_main_writer_workflows"], 1)
        row = result["writers"][0]
        self.assertEqual(row["direct_main_write_evidence"][0]["line"], 10)
        self.assertTrue(row["critical_publication_or_supervision"])
        self.assertTrue(row["contents_write_declared"])
        self.assertEqual(row["concurrency_groups_seen"], ["framework-market-owner-writer"])
        self.assertEqual(row["principal"], "UNVERIFIED_RUNTIME")

    def test_detects_main_ref_push(self):
        result = self.check({"test.yaml": "git push origin HEAD:refs/heads/main\n"})
        self.assertEqual(result["obvious_direct_main_writer_workflows"], 1)

    def test_detects_plain_origin_main(self):
        result = self.check({"test.yml": "git push origin main\n"})
        self.assertEqual(result["obvious_direct_main_writer_workflows"], 1)

    def test_detects_rest_ref_write(self):
        result = self.check({"test.yml": "gh api -X PATCH repos/x/y/git/refs/heads/main\n"})
        self.assertEqual(result["obvious_direct_main_writer_workflows"], 1)

    def test_does_not_count_comments_or_main_reads(self):
        result = self.check({"test.yml": "# git push origin HEAD:main\ngit pull --rebase origin main\n"})
        self.assertEqual(result["obvious_direct_main_writer_workflows"], 0)

    def test_different_concurrency_groups_are_visible(self):
        result = self.check({"framework-learning-supervisor.yml": "concurrency:\n  group: framework-main-writer\ngit push origin HEAD:main\n",
                             "hourly-sequence-capture.yml": "concurrency:\n  group: framework-market-owner-writer\ngit push origin HEAD:main\n"})
        self.assertEqual(result["obvious_direct_main_writer_workflows"], 2)
        self.assertEqual(len({x for w in result["writers"] for x in w["concurrency_groups_seen"]}), 2)

    def test_python_assertion_merely_quoting_git_push_is_not_writer(self):
        # Exact failure mode from forecast-skill-study-v132-gate.yml.
        result = self.check({"forecast-skill-study-v132-gate.yml": """jobs:
  audit:
    steps:
      - run: |
          python - <<'PY'
          assert 'git push origin HEAD:main' in barrier
          PY
"""})
        self.assertEqual(result["obvious_direct_main_writer_workflows"], 0)

    def test_echo_command_literal_is_not_confirmed_writer(self):
        result = self.check({"test.yml": "echo 'git push origin HEAD:main'\n"})
        self.assertEqual(result["obvious_direct_main_writer_workflows"], 0)

    def test_actual_shell_if_chain_still_counts_writer(self):
        result = self.check({"test.yml":
            "if git pull --rebase origin main && git push origin HEAD:main; then echo ok; fi\n"})
        self.assertEqual(result["obvious_direct_main_writer_workflows"], 1)

    def test_no_release_permission_even_if_no_writers(self):
        result = self.check({"test.yml": "name: test\n"})
        self.assertFalse(result["merge_release_authority"])
        self.assertEqual(result["platform_enforced_serialization"], "NOT_ASSESSED")
        self.assertEqual(result["coverage"], "BOUNDED_REGEX_EVIDENCE_NOT_EXHAUSTIVE")
        self.assertTrue(result["critical_writers_not_detected"])

    def test_env_group_must_not_masquerade_as_concurrency(self):
        result = self.check({"test.yml": """jobs:
  publish:
    env:
      group: unrelated-release-context
    steps:
      - run: git push origin HEAD:main
"""})
        self.assertEqual(result["obvious_direct_main_writer_workflows"], 1)
        self.assertEqual(result["writers"][0]["concurrency_groups_seen"], [])

    def test_job_scoped_concurrency_group_excludes_env_decoy(self):
        result = self.check({"test.yml": """jobs:
  publish:
    concurrency:
      group: real-job-lock
    env:
      group: unrelated-release-context
    steps:
      - run: git push origin HEAD:main
"""})
        self.assertEqual(result["writers"][0]["concurrency_groups_seen"], ["real-job-lock"])

    def test_workflow_and_job_concurrency_scopes_are_distinct(self):
        result = self.check({"test.yml": """concurrency:
  group: workflow-main-lock
jobs:
  publish:
    concurrency:
      group: real-job-lock
    steps:
      - run: |
          printf "group: shell-text-is-not-a-lock"
          git push origin HEAD:main
"""})
        self.assertEqual(result["writers"][0]["concurrency_groups_seen"],
                         ["real-job-lock", "workflow-main-lock"])

    def test_env_contents_write_is_not_permission_grant(self):
        result = self.check({"test.yml": """jobs:
  publish:
    env:
      contents: write
    steps:
      - run: git push origin HEAD:main
"""})
        self.assertFalse(result["writers"][0]["contents_write_declared"])

    def test_workflow_and_job_permissions_contents_write_are_detected(self):
        for permissions_yaml in (
            "permissions:\n  contents: write\n",
            "jobs:\n  publish:\n    permissions:\n      contents: write # explicit job permission\n",
        ):
            with self.subTest(permissions_yaml=permissions_yaml):
                result = self.check({"test.yml": permissions_yaml + "git push origin HEAD:main\n"})
                self.assertTrue(result["writers"][0]["contents_write_declared"])

    def test_missing_checkout_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(FileNotFoundError):
                census(Path(td))


if __name__ == "__main__":
    unittest.main()
