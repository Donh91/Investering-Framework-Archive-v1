from __future__ import annotations
import importlib.util, json, tempfile, unittest, io, sys
from contextlib import redirect_stdout
from unittest import mock
from pathlib import Path

P = Path("scripts/data_governance/storage_health_gate.py")
S = importlib.util.spec_from_file_location("storage_health_gate", P)
M = importlib.util.module_from_spec(S)
assert S.loader
S.loader.exec_module(M)

DEFAULT_POLICY_ABS = Path("research/data_governance/STORAGE_HEALTH_POLICY_FREE_v1.json").resolve()
POLICY = json.loads(DEFAULT_POLICY_ABS.read_text())

class StorageHealthGateTests(unittest.TestCase):
    def test_small_text_repo_passes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "a.json").write_text("{}")
            r = M.scan(root, POLICY)
            self.assertEqual(r["status"], "PASS")
            self.assertEqual(r["level"], "GREEN")

    def test_large_file_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with (root / "huge.csv").open("wb") as f:
                f.truncate((POLICY["git_file_limits_mib"]["hard_block"] + 1) * 1024 * 1024)
            r = M.scan(root, POLICY)
            self.assertEqual(r["status"], "FAIL")
            self.assertTrue(any(x["reason"] == "FILE_OVER_HARD_LIMIT" for x in r["violations"]))

    def test_large_binary_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with (root / "raw.zip").open("wb") as f:
                f.truncate((POLICY["git_file_limits_mib"]["soft_warn"] + 1) * 1024 * 1024)
            r = M.scan(root, POLICY)
            self.assertEqual(r["status"], "FAIL")
            self.assertTrue(any(x["reason"] == "BULK_BINARY_IN_GIT" for x in r["violations"]))
    def test_growth_is_flagged_before_the_hard_limit_without_failing(self):
        """Archive #2152: a 26 MB hot manifest must have been visible long before it blocked every PR."""
        hard = POLICY["git_file_limits_mib"]["hard_block"] * 1024 * 1024
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with (root / "LATEST_EXPERIMENT_DISPATCH_MANIFEST.json").open("wb") as f:
                f.truncate(int(hard * 0.6))  # 60 % of the hard limit, also over the 5 MiB hot budget
            with (root / "history.json").open("wb") as f:
                f.truncate(int(hard * 0.55))  # not a hot file, but past the pre-limit line
            with (root / "LATEST_SMALL.json").open("wb") as f:
                f.truncate(1024)
            r = M.scan(root, POLICY)
            self.assertEqual(r["status"], "PASS")  # early warnings never block and never raise a limit
            reasons = {(x["path"], x["reason"]) for x in r["early_warnings"]}
            self.assertIn(("LATEST_EXPERIMENT_DISPATCH_MANIFEST.json", "PRE_LIMIT_GROWTH_RISK"), reasons)
            self.assertIn(("LATEST_EXPERIMENT_DISPATCH_MANIFEST.json", "HOT_ACTIVE_SET_OVER_BUDGET"), reasons)
            self.assertIn(("history.json", "PRE_LIMIT_GROWTH_RISK"), reasons)
            self.assertNotIn("LATEST_SMALL.json", {x["path"] for x in r["early_warnings"]})

    def test_hard_limit_still_blocks_and_is_not_an_early_warning(self):
        hard = POLICY["git_file_limits_mib"]["hard_block"] * 1024 * 1024
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with (root / "LATEST_BIG.json").open("wb") as f:
                f.truncate(hard + 1)
            r = M.scan(root, POLICY)
            self.assertEqual(r["status"], "FAIL")
            self.assertNotIn(("LATEST_BIG.json", "PRE_LIMIT_GROWTH_RISK"), {(x["path"], x["reason"]) for x in r["early_warnings"]})



    def test_warning_annotation_escapes_hostile_path(self):
        """A hostile PR file path must not inject a second GHA workflow command."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            hostile = root / "LATEST_x\n::stop-commands::tok"
            with hostile.open("wb") as f:
                f.truncate(5 * 1024 * 1024 + 1)
            capture = io.StringIO()
            argv = ["storage_health_gate.py", "--root", str(root), "--policy", str(DEFAULT_POLICY_ABS)]
            with mock.patch.object(sys, "argv", argv), redirect_stdout(capture):
                code = M.main()
            self.assertEqual(code, 0)
            command_lines, open_token = self._active_command_lines(capture.getvalue())
            self.assertIsNone(open_token)
            self.assertEqual(len(command_lines), 1, command_lines)
            self.assertTrue(command_lines[0].startswith("::warning "))
            self.assertIn("%0A", command_lines[0])
            self.assertNotIn("\n::stop-commands::", command_lines[0])

    def _run_main(self, root):
        capture = io.StringIO()
        argv = ["storage_health_gate.py", "--root", str(root), "--policy", str(DEFAULT_POLICY_ABS)]
        with mock.patch.object(sys, "argv", argv), redirect_stdout(capture):
            code = M.main()
        return code, capture.getvalue()

    def _active_command_lines(self, out):
        """Lines the runner would treat as commands: everything outside a stop-commands block."""
        active, token = [], None
        for line in out.splitlines():
            if token is not None:
                if line == f"::{token}::":
                    token = None
                continue
            if line.startswith("::stop-commands::"):
                token = line[len("::stop-commands::"):]
                continue
            if line.startswith("::") or "##[" in line:
                active.append(line)
        return active, token

    def test_lone_cr_percent_and_legacy_commands_cannot_inject(self):
        for name in ("LATEST_a\r::stop-commands::x", "LATEST_b%0A::error::forged", "LATEST_c##[stop-commands]tok",
                     "LATEST_d##[error title=forged]x"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                with (root / name).open("wb") as f:
                    f.truncate(5 * 1024 * 1024 + 1)
                code, out = self._run_main(root)
                self.assertEqual(code, 0)
                active, open_token = self._active_command_lines(out)
                self.assertIsNone(open_token)  # the JSON block is always resumed
                self.assertEqual(len(active), 1, active)
                self.assertTrue(active[0].startswith("::warning title=Storage early warning::"))
                self.assertNotIn("\r", active[0])
                if "%0A" in name:
                    self.assertIn("%250A", active[0])  # a literal %0A stays literal

    def test_hot_budget_boundary_and_prefix_only(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for name, size in (("LATEST_AT_BUDGET.json", 5 * 1024 * 1024), ("not_LATEST_big.json", 5 * 1024 * 1024 + 1)):
                with (root / name).open("wb") as f:
                    f.truncate(size)
            report = M.scan(root, POLICY)
            self.assertEqual(report["early_warnings"], [])  # exactly at the budget, and a non-prefix name, are not hot-set warnings

    def test_main_exit_code_early_warning_vs_hard_limit(self):
        """Early warnings never block, while the existing hard-limit remains fatal."""
        hard = POLICY["git_file_limits_mib"]["hard_block"] * 1024 * 1024
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with (root / "LATEST_GROWING.json").open("wb") as f:
                f.truncate(5 * 1024 * 1024 + 1)
            argv = ["storage_health_gate.py", "--root", str(root), "--policy", str(DEFAULT_POLICY_ABS)]
            with mock.patch.object(sys, "argv", argv), redirect_stdout(io.StringIO()):
                self.assertEqual(M.main(), 0)
            with (root / "VIOLATION.json").open("wb") as f:
                f.truncate(hard + 1)
            with mock.patch.object(sys, "argv", argv), redirect_stdout(io.StringIO()):
                self.assertEqual(M.main(), 2)

if __name__ == "__main__":
    unittest.main()
