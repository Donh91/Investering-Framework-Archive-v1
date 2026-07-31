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

if __name__ == "__main__":
    unittest.main()
