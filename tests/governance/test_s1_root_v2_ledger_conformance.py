"""Cross-implementation conformance for the runtime ledger consumer (synthetic vectors only)."""
import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "research", "s1_root_v2"))
import ledger_conformance as C
import ledger_screen as L

LABELS = {"EXACT_APPROVAL_ONLY": "ADMIT", "HOLD": "HOLD", "UNKNOWN": "UNKNOWN"}

class LedgerConformance(unittest.TestCase):
    def test_every_vector(self):
        names = [v[0] for v in C.vectors()]
        self.assertEqual(len(names), len(set(names)))
        for name, sb, lb, repo, pr, head, minimum, expected in C.vectors():
            with self.subTest(name):
                self.assertEqual(LABELS.get(L.screen(sb, lb, repo, pr, head, minimum)), expected)

    def test_only_one_admit_class(self):
        self.assertEqual({"approve_exact_head", "approve_newer_than_block", "other_repo_same_pr_ignored"},
                         {v[0] for v in C.vectors() if v[7] == "ADMIT"})

if __name__ == "__main__":
    unittest.main()
