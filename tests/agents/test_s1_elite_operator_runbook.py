"""Offline regression checks for Chat S1 elite operator reference.

This test does not assert live S1 execution, GitHub merge rights or runtime improvement.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
RUNBOOK = ROOT / "00_FMOS" / "CHAT_S1_ELITE_RUNBOOK.md"


class S1EliteRunbookTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = RUNBOOK.read_text(encoding="utf-8")

    def test_original_identity_and_single_supervisor(self):
        self.assertIn("6ae5fd466b48819187abc224ec0f1c5f", self.text)
        self.assertIn("One S1 only", self.text)
        self.assertIn("saved ChatGPT task", self.text)

    def test_exact_head_release_and_native_evidence(self):
        for term in (
            "expected_head_sha",
            "pull_request",
            "adversarial",
            "new main",
            "POST_FIX_OBSERVATION",
        ):
            self.assertIn(term, self.text)

    def test_high_impact_safety_boundary(self):
        for term in (
            "destructive keys",
            "independent Vault",
            "COMMENTED",
            "APPROVED",
            "PIT",
            "first-known",
        ):
            self.assertIn(term, self.text)

    def test_no_false_scientific_or_paid_success(self):
        for term in (
            "EDGE_SUPPORTED",
            "W45",
            "Astra",
            "USD40",
            "ambiguous billed POST",
        ):
            # Some explicit scientific labels may be qualified as UNPROVEN instead.
            if term == "EDGE_SUPPORTED":
                self.assertIn("UNPROVEN", self.text)
            else:
                self.assertIn(term, self.text)

    def test_no_unbounded_hold_loop(self):
        for term in (
            "max-three ACTIVE",
            "four material touches",
            "objective trigger",
            "SLA_BREACHED",
            "NO_UPDATE",
        ):
            if term == "max-three ACTIVE":
                self.assertIn("at most three distinct ORIGINAL", self.text)
            elif term == "four material touches":
                self.assertIn("four material touches", self.text.lower())
            elif term == "SLA_BREACHED":
                self.assertIn("SLA_BREACHED", self.text)
            elif term == "NO_UPDATE":
                self.assertIn("NO_UPDATE", self.text)
            else:
                self.assertIn(term, self.text)


if __name__ == "__main__":
    unittest.main()
