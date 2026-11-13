"""act-free tests for the native S1_DIFF_SCAN_V1 producer step (gate job).

Each case builds a throwaway git repository with a real PR-style merge commit and a
synthetic pull_request event payload, then runs the step script as CI would.
Restricted markers are assembled at runtime so this file itself stays scanner-clean.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.governance import s1_native_privacy_scan_step_v1 as step

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "governance" / "s1_native_privacy_scan_step_v1.py"
WORKFLOW = ROOT / ".github" / "workflows" / "data-architecture-gate.yml"
REPO = "Donh91/Investering-Framework-Archive-v1"
MARKER = "OWNER" + "_" + "ONLY"
STEP_NAME = "S1 native privacy scan of the PR diff (S1_DIFF_SCAN_V1, exact head blobs)"


def git(repo, *args):
    cmd = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
           "-c", "commit.gpgsign=false", "-c", "protocol.file.allow=always", *args]
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout.strip()


class Fixture:
    """base commit on main, one PR commit, one --no-ff merge commit checked out."""

    def __init__(self, tmp, pr_changes, base_files=None, title="Update public notes",
                 body="Public documentation fix.", main_changes=None):
        self.repo = Path(tmp) / "origin"
        self.repo.mkdir()
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "uploadpack.allowAnySHA1InWant", "true")
        base = {"README.md": "Public notes.\n", "docs/old.md": "Old public page.\n" * 20,
                "docs/gone.md": "Public page to delete.\n"}
        for rel in step.SCAN_CODE_PATHS:  # scan code present and identical on base
            base[rel] = (ROOT / rel).read_bytes()
        base.update(base_files or {})
        self._write(base)
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "base")
        self.base = git(self.repo, "rev-parse", "HEAD")
        git(self.repo, "checkout", "-q", "-b", "pr")
        pr_changes(self)
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "pr change")
        self.head = git(self.repo, "rev-parse", "HEAD")
        git(self.repo, "checkout", "-q", "main")
        if main_changes is not None:
            main_changes(self)
            git(self.repo, "add", "-A")
            git(self.repo, "commit", "-q", "-m", "independent main change")
            self.base = git(self.repo, "rev-parse", "HEAD")
        original_base = git(self.repo, "merge-base", self.base, self.head)
        git(self.repo, "merge", "-q", "--no-ff", "-m", "merge pr", "pr")
        self.merge = git(self.repo, "rev-parse", "HEAD")
        # GitHub PR changed_files counts original three-dot diff, not merge output.
        files = git(self.repo, "diff", "--name-status", "-M", original_base, self.head).splitlines()
        self.event = {"number": 7, "pull_request": {
            "number": 7, "title": title, "body": body, "changed_files": len(files),
            "head": {"sha": self.head}, "base": {"sha": self.base}}}
        self.event_path = Path(tmp) / "event.json"
        self.write_event()

    def _write(self, files):
        for rel, data in files.items():
            p = self.repo / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))

    def write(self, rel, data):
        self._write({rel: data})

    def write_event(self):
        self.event_path.write_text(json.dumps(self.event), encoding="utf-8")

    def env(self, **extra):
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GITHUB_", "S1_"))}
        env.update({"GITHUB_EVENT_NAME": "pull_request", "GITHUB_EVENT_PATH": str(self.event_path),
                    "GITHUB_REPOSITORY": REPO, "GITHUB_RUN_ID": "1", "GITHUB_RUN_ATTEMPT": "1"})
        env.update(extra)
        return env

    def cli(self, repo=None, **extra):
        p = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(repo or self.repo)],
                           capture_output=True, text=True, env=self.env(**extra))
        payload = json.loads(p.stdout[:p.stdout.rindex("}") + 1])
        return p.returncode, payload, p.stdout + p.stderr


def clean_change(fx):
    fx.write("README.md", "Public notes, second edition.\n")
    fx.write("docs/new.md", "A new public page.\n")


class NativePrivacyScanStep(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="s1scanstep-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_clean_diff_is_no_restricted_content_and_exit_zero(self):
        fx = Fixture(self.tmp, clean_change)
        code, out, _ = fx.cli()
        self.assertEqual((code, out["result"], out["wrapper_reasons"]), (0, "NO_RESTRICTED_CONTENT", []), out)
        self.assertEqual(out["head_sha"], fx.head)
        self.assertEqual(out["merge_sha"], fx.merge)
        self.assertEqual(out["merge_base_parent_sha"], fx.base)
        self.assertEqual(out["files_count"], 2)
        self.assertTrue(out["scan_code"]["identical_to_base_parent"])
        self.assertEqual(out["scanner_result"]["head"], fx.head)

    def test_every_scanned_file_is_bound_to_the_native_head_blob(self):
        fx = Fixture(self.tmp, clean_change)
        _, out, _ = fx.cli()
        want = {step._path_ref(p): git(fx.repo, "rev-parse", f"{fx.head}:{p}")
                for p in ("README.md", "docs/new.md")}
        self.assertEqual({r["path_sha256_16"]: r["head_blob_sha"] for r in out["files"]}, want)
        blob = (fx.repo / "docs/new.md").read_bytes()
        self.assertEqual(step.git_blob_sha(blob), want[step._path_ref("docs/new.md")])
        scanner_blob = git(fx.repo, "rev-parse", f"{fx.merge}:scripts/governance/s1_diff_scan_v1.py")
        self.assertEqual(out["scan_code"]["files"]["scripts/governance/s1_diff_scan_v1.py"]["merge_blob_sha"],
                         scanner_blob)

    def test_restricted_content_fails_and_is_not_echoed(self):
        fx = Fixture(self.tmp, lambda f: f.write("docs/plan_note.md", f"Draft. {MARKER} design.\n"),
                     title="Add note")
        code, out, text = fx.cli()
        self.assertEqual((code, out["result"]), (1, "RESTRICTED_CONTENT"), out)
        self.assertNotIn(MARKER, text)
        self.assertNotIn("plan_note", text)

    def test_restricted_title_or_body_fails_and_is_not_echoed(self):
        fx = Fixture(self.tmp, clean_change, body=f"See the {MARKER} thread.")
        code, out, text = fx.cli()
        self.assertEqual((code, out["result"]), (1, "RESTRICTED_CONTENT"), out)
        self.assertNotIn(MARKER, text)

    def test_blocked_governance_path_fails(self):
        fx = Fixture(self.tmp, lambda f: f.write("00_FMOS/NOTE.md", "Harmless text.\n"))
        code, out, _ = fx.cli()
        self.assertEqual((code, out["result"]), (1, "RESTRICTED_CONTENT"), out)

    def test_shadow_mode_reports_but_does_not_fail(self):
        fx = Fixture(self.tmp, lambda f: f.write("00_FMOS/NOTE.md", "Harmless text.\n"))
        code, out, _ = fx.cli(S1_PRIVACY_SCAN_MODE="shadow")
        self.assertEqual((code, out["result"], out["mode"]), (0, "RESTRICTED_CONTENT", "shadow"), out)
        code, out, _ = fx.cli(S1_PRIVACY_SCAN_MODE="anything-else")
        self.assertEqual((code, out["mode"]), (1, "enforce"), out)

    def test_blob_mismatch_fails_closed(self):
        fx = Fixture(self.tmp, clean_change)

        def tampered(g, head, path):
            data = step.read_head_blob(g, head, path)
            return data + b"x" if path == "docs/new.md" else data

        out = step.run_step(str(fx.repo), fx.env(), reader=tampered)
        self.assertEqual(out["result"], "UNKNOWN", out)
        self.assertIn("SCANNED_TEXT_NOT_BOUND_TO_HEAD_BLOB", out["wrapper_reasons"])
        self.assertEqual(step.exit_code(out["result"], "enforce"), 1)
        row = [r for r in out["files"] if r["path_sha256_16"] == step._path_ref("docs/new.md")][0]
        self.assertIsNone(row["head_blob_sha"])

    def test_non_pull_request_event_skips_cleanly(self):
        fx = Fixture(self.tmp, clean_change)
        for name in ("workflow_dispatch", "push", "schedule"):
            code, out, _ = fx.cli(GITHUB_EVENT_NAME=name)
            self.assertEqual((code, out["result"]), (0, "SKIPPED_NOT_PR"), out)

    def test_pull_request_event_without_payload_fails_closed(self):
        fx = Fixture(self.tmp, clean_change)
        code, out, _ = fx.cli(GITHUB_EVENT_PATH=str(Path(self.tmp) / "absent.json"))
        self.assertEqual((code, out["result"]), (1, "UNKNOWN"), out)
        self.assertEqual(out["wrapper_reasons"], ["PULL_REQUEST_EVENT_PAYLOAD_UNAVAILABLE"])

    def _shallow(self, fx):
        clone = Path(self.tmp) / "runner"
        git(self.tmp, "clone", "-q", "--depth=1", "--no-tags", fx.repo.as_uri(), str(clone))
        self.assertEqual(git(clone, "rev-parse", "HEAD"), fx.merge)
        self.assertNotEqual(subprocess.run(["git", "-C", str(clone), "rev-parse", "-q", "--verify", "HEAD^2"],
                                           capture_output=True).returncode, 0)
        return clone

    def test_depth_one_checkout_is_deepened_to_the_merge_parents(self):
        fx = Fixture(self.tmp, clean_change)
        clone = self._shallow(fx)
        git(clone, "config", "protocol.file.allow", "always")
        code, out, _ = fx.cli(repo=clone)
        self.assertEqual((code, out["result"]), (0, "NO_RESTRICTED_CONTENT"), out)
        self.assertEqual(out["merge_base_parent_sha"], fx.base)

    def test_missing_base_fails_closed(self):
        fx = Fixture(self.tmp, clean_change)
        clone = self._shallow(fx)
        git(clone, "remote", "remove", "origin")
        code, out, _ = fx.cli(repo=clone)
        self.assertEqual((code, out["result"]), (1, "UNKNOWN"), out)
        self.assertEqual(out["wrapper_reasons"], ["MERGE_PARENTS_UNAVAILABLE"])

    def test_event_head_must_be_the_merged_head(self):
        fx = Fixture(self.tmp, clean_change)
        fx.event["pull_request"]["head"]["sha"] = fx.base
        fx.write_event()
        code, out, _ = fx.cli()
        self.assertEqual((code, out["result"]), (1, "UNKNOWN"), out)
        self.assertEqual(out["wrapper_reasons"], ["CHECKOUT_IS_NOT_MERGE_OF_EVENT_HEAD"])

    def test_file_census_must_equal_the_event_count(self):
        fx = Fixture(self.tmp, clean_change)
        fx.event["pull_request"]["changed_files"] += 1
        fx.write_event()
        code, out, _ = fx.cli()
        self.assertEqual((code, out["result"]), (1, "UNKNOWN"), out)
        self.assertIn("FILE_CENSUS_MISMATCH_WITH_EVENT", out["wrapper_reasons"])

    def test_rename_and_delete_are_scanned_with_native_statuses(self):
        def change(f):
            git(f.repo, "mv", "docs/old.md", "docs/renamed.md")
            git(f.repo, "rm", "-q", "docs/gone.md")
        fx = Fixture(self.tmp, change)
        code, out, _ = fx.cli()
        self.assertEqual((code, out["result"]), (0, "NO_RESTRICTED_CONTENT"), out)
        self.assertEqual(sorted(r["status"] for r in out["files"]), ["removed", "renamed"])

    def test_rename_out_of_a_blocked_path_fails(self):
        fx = Fixture(self.tmp, lambda f: git(f.repo, "mv", "00_FMOS/RULE.md", "docs/rule.md"),
                     base_files={"00_FMOS/RULE.md": "A public rule text.\n" * 20})
        code, out, _ = fx.cli()
        self.assertEqual((code, out["result"]), (1, "RESTRICTED_CONTENT"), out)

    def test_literal_git_pathspec_filename_cannot_hide_deleted_private_marker(self):
        magic = ":(exclude)*.md"
        fx = Fixture(
            self.tmp,
            lambda f: git(f.repo, "rm", "-q", "--", magic),
            base_files={magic: "Private " + MARKER + " evidence.\\n"},
        )
        code, out, details = fx.cli()
        self.assertEqual((code, out["result"]), (1, "RESTRICTED_CONTENT"), details)
        self.assertEqual(out["files_count"], 1)
        self.assertEqual(out["wrapper_reasons"], [])

    def test_original_pr_three_dot_patch_is_scanned_after_parallel_main_edit(self):
        def remove_marker_and_add_public_note(f):
            f.write("README.md", "Header\\nFooter\\nPublic note\\n")

        def main_also_removes_marker(f):
            f.write("README.md", "Header\\nFooter\\n")

        fx = Fixture(
            self.tmp, remove_marker_and_add_public_note,
            base_files={"README.md": "Header\\n" + MARKER + "\\nFooter\\n"},
            main_changes=main_also_removes_marker,
        )
        self.assertNotEqual(fx.base, git(fx.repo, "merge-base", fx.base, fx.head))
        code, out, details = fx.cli()
        self.assertEqual((code, out["result"]), (1, "RESTRICTED_CONTENT"), details)
        self.assertEqual(out["files_count"], 1)
        self.assertEqual(out["wrapper_reasons"], [])
        self.assertEqual(out["original_pr_merge_base_sha"],
                         git(fx.repo, "merge-base", fx.base, fx.head))

    def test_binary_or_symlink_is_never_green(self):
        fx = Fixture(self.tmp, lambda f: f.write("docs/pic.md", b"\x00\x01\x02\xff binary"))
        code, out, _ = fx.cli()
        self.assertEqual((code, out["result"]), (1, "UNKNOWN"), out)
        tmp2 = tempfile.mkdtemp(prefix="s1scanstep-")
        self.addCleanup(shutil.rmtree, tmp2, ignore_errors=True)
        fx = Fixture(tmp2, lambda f: os.symlink("README.md", f.repo / "docs" / "link.md"))
        code, out, _ = fx.cli()
        self.assertEqual((code, out["result"]), (1, "UNKNOWN"), out)

    def test_a_pr_that_changes_the_scan_code_is_never_green(self):
        rel = "scripts/governance/s1_diff_scan_v1.py"
        fx = Fixture(self.tmp, lambda f: f.write(rel, (ROOT / rel).read_text() + "\n# edited\n"))
        code, out, _ = fx.cli()
        self.assertEqual(code, 1, out)
        self.assertIn("SCAN_CODE_CHANGED_BY_PR_OR_ABSENT_ON_BASE", out["wrapper_reasons"])
        self.assertFalse(out["scan_code"]["identical_to_base_parent"])

    def test_wrong_repository_name_is_not_green(self):
        fx = Fixture(self.tmp, clean_change)
        code, out, _ = fx.cli(GITHUB_REPOSITORY="someone/fork")
        self.assertEqual((code, out["result"]), (1, "UNKNOWN"), out)


class GateWorkflowWiring(unittest.TestCase):
    """Text-level checks (no PyYAML in the CI test job)."""

    def setUp(self):
        self.text = WORKFLOW.read_text(encoding="utf-8")
        self.lines = self.text.splitlines()

    def _step_block(self):
        start = [i for i, l in enumerate(self.lines) if l.strip() == f"- name: {STEP_NAME}"]
        self.assertEqual(len(start), 1, "the scan step must exist exactly once")
        block = [self.lines[start[0]]]
        for line in self.lines[start[0] + 1:]:
            if line.startswith("      - "):
                break
            block.append(line)
        return start[0], block

    def test_step_is_in_the_existing_gate_job_and_no_job_was_added(self):
        jobs_at = self.lines.index("jobs:")
        job_ids = [l.strip()[:-1] for l in self.lines[jobs_at + 1:] if re.fullmatch(r"  [A-Za-z0-9_-]+:", l)]
        self.assertEqual(job_ids, ["gate"])
        at, block = self._step_block()
        self.assertGreater(at, self.lines.index("  gate:"))
        self.assertIn("        run: python scripts/governance/s1_native_privacy_scan_step_v1.py", block)
        self.assertIn("        if: github.event_name == 'pull_request'", block)
        self.assertIn("          S1_PRIVACY_SCAN_MODE: shadow", block)

    def test_step_uses_no_secret_and_no_inline_expression_in_run(self):
        _, block = self._step_block()
        joined = "\n".join(block)
        self.assertNotIn("secrets.", joined)
        self.assertNotIn("github.token", joined.lower())
        self.assertNotIn("GITHUB_TOKEN", joined)
        self.assertNotIn("continue-on-error", joined)
        run_lines = [l for l in block if l.strip().startswith("run:")]
        self.assertEqual(len(run_lines), 1)
        self.assertNotIn("${{", run_lines[0])

    def test_permissions_and_triggers_did_not_widen(self):
        self.assertEqual(len(re.findall(r"^\s*permissions:", self.text, re.M)), 1)
        at = self.lines.index("permissions:")
        self.assertEqual(self.lines[at + 1], "  contents: read")
        self.assertEqual(self.lines[at + 2], "jobs:")
        self.assertEqual(self.lines[1:4], ["on:", "  pull_request:", "  workflow_dispatch:"])
        self.assertNotIn("pull_request_target", self.text)
        self.assertNotIn("secrets.", self.text)

    def test_only_this_workflow_runs_the_step_script(self):
        users = sorted(p.name for p in WORKFLOW.parent.glob("*.y*ml")
                       if "s1_native_privacy_scan_step_v1" in p.read_text(encoding="utf-8"))
        self.assertEqual(users, ["data-architecture-gate.yml"])


if __name__ == "__main__":
    unittest.main()
