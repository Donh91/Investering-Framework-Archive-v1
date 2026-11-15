from __future__ import annotations
import importlib.util, json, tempfile, unittest
from pathlib import Path

P = Path("scripts/data_governance/storage_health_gate.py")
S = importlib.util.spec_from_file_location("storage_health_gate", P)
M = importlib.util.module_from_spec(S)
assert S.loader
S.loader.exec_module(M)

POLICY = json.loads(Path("research/data_governance/STORAGE_HEALTH_POLICY_FREE_v1.json").read_text())

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


if __name__ == "__main__":
    unittest.main()
