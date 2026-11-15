"""One paid Master Monday calibration and one publication per frozen ISO week (Metronome ACTIVE safety)."""
import subprocess
import sys
import tempfile
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "master_monday" / "weekly_publication_idempotency.py"
WORKFLOW = ROOT / ".github" / "workflows" / "weekly-api-calibration-shadow.yml"
sys.path.insert(0, str(SCRIPT.parent))
import weekly_publication_idempotency as I  # noqa: E402

WEEK = "research/master_monday_preflight/frozen/2026/W46"


def publish(root: Path, week: str = "W46") -> None:
    p = root / "research/api_agent/outputs/weekly/2026" / week / "MASTER_MONDAY_DELIVERY_POINTER.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{}")


class IdempotencyDecisionTest(unittest.TestCase):
    def test_first_run_for_the_week_proceeds(self):
        with tempfile.TemporaryDirectory() as td:
            publish(Path(td), "W45")  # last week's publication does not block this week
            self.assertEqual(I.decide(Path(td), WEEK, False)["reason"], "FIRST_PUBLICATION_FOR_WEEK")
            self.assertFalse(I.decide(Path(td), WEEK, False)["skip"])

    def test_second_run_for_a_published_week_skips_paid_call_and_republication(self):
        with tempfile.TemporaryDirectory() as td:
            publish(Path(td))
            d = I.decide(Path(td), WEEK + "/", False)
            self.assertEqual((d["skip"], d["reason"]), (True, "WEEK_ALREADY_PUBLISHED"))

    def test_only_an_explicit_owner_reissue_overrides(self):
        with tempfile.TemporaryDirectory() as td:
            publish(Path(td))
            d = I.decide(Path(td), WEEK, True)
            self.assertEqual((d["skip"], d["reason"]), (False, "OWNER_FORCE_REISSUE"))

    def test_unknown_week_layout_fails_closed_and_visibly(self):
        with tempfile.TemporaryDirectory() as td:
            for bad in ("", "research/other/2026/W46", "research/master_monday_preflight/frozen/2026/46",
                        "research/master_monday_preflight/frozen/../2026/W46"):
                with self.assertRaises(ValueError):
                    I.decide(Path(td), bad, False)

    def test_cli_prints_github_outputs(self):
        with tempfile.TemporaryDirectory() as td:
            publish(Path(td))
            out = subprocess.run([sys.executable, str(SCRIPT), "--repo-root", td, "--week-dir", WEEK],
                                 check=True, capture_output=True, text=True).stdout.splitlines()
            self.assertEqual(out, ["skip=true", "reason=WEEK_ALREADY_PUBLISHED"])
            out = subprocess.run([sys.executable, str(SCRIPT), "--repo-root", td, "--week-dir", WEEK, "--force-reissue", "true"],
                                 check=True, capture_output=True, text=True).stdout.splitlines()
            self.assertEqual(out, ["skip=false", "reason=OWNER_FORCE_REISSUE"])


class WorkflowWiringTest(unittest.TestCase):
    """Standard-library text checks (the gate installs no YAML parser)."""

    def setUp(self):
        self.text = WORKFLOW.read_text(encoding="utf-8")

    def test_force_reissue_is_an_owner_dispatch_input_defaulting_false(self):
        block = re.search(r"workflow_dispatch:\n    inputs:\n      force_reissue:\n(?:        .*\n)+", self.text)
        self.assertIsNotNone(block)
        self.assertIn("type: boolean", block.group(0))
        self.assertIn("default: false", block.group(0))

    def test_guard_runs_before_the_freeze_commit_and_gates_every_paid_or_publishing_step(self):
        self.assertLess(self.text.index("id: idempotency"), self.text.index("id: commit"))
        self.assertIn("skip: ${{ steps.idempotency.outputs.skip }}", self.text)
        commit = self.text[self.text.index("id: commit"):self.text.index("run:", self.text.index("id: commit"))]
        self.assertIn("if: steps.idempotency.outputs.skip == 'false'", commit)
        for job in ("  calibration:\n", "  publish:\n"):
            head = self.text[self.text.index(job):self.text.index("runs-on:", self.text.index(job))]
            self.assertIn("needs.freeze.outputs.skip == 'false'", head)
        self.assertIn("weekly_publication_idempotency.py", self.text)

    def test_guard_step_fails_closed_and_no_gate_uses_a_negative_skip_check(self):
        step = self.text[self.text.index("id: idempotency"):self.text.index("- name:", self.text.index("id: idempotency"))]
        self.assertIn("shell: bash", step)          # bash -eo pipefail: a guard crash fails the step
        self.assertIn("set -euo pipefail", step)
        self.assertNotIn("${{ inputs.force_reissue", step.split("run:")[1])  # passed via env, never inlined
        self.assertIn("github.actor == github.repository_owner", step)
        self.assertNotIn("skip != 'true'", self.text)  # an empty/missing skip must never mean "proceed"

    def test_crashing_guard_under_the_step_shell_fails_and_writes_no_skip(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out"
            cmd = (f'set -euo pipefail; "{sys.executable}" "{SCRIPT}" --repo-root "{td}" '
                   f'--week-dir research/master_monday_preflight/frozen/2026/46 --force-reissue false | tee -a "{out}"')
            proc = subprocess.run(["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", cmd],
                                  capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertNotIn("skip=", out.read_text() if out.exists() else "")
            with self.assertRaises(ValueError):
                I.decide(Path(td), "research/master_monday_preflight/frozen/\u0662\u0660\u0662\u0666/W46", False)


if __name__ == "__main__":
    unittest.main()
