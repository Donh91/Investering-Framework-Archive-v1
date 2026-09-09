from __future__ import annotations

import unittest
from datetime import datetime, timezone

from scripts.health.provider_budget_status import build, cfgi_status


class ProviderBudgetStatusTests(unittest.TestCase):
    def test_cfgi_pass_preserves_provider_reported_credits(self) -> None:
        receipt = {
            "status": "PASS",
            "retrieved_at_utc": "2026-09-08T19:25:38Z",
            "billing": {"credits_used": 30, "credits_remaining": 500, "expected_credits": 30},
        }
        row = cfgi_status(receipt)
        self.assertEqual(row["status"], "PASS")
        self.assertEqual(row["credits_remaining"], 500)
        self.assertEqual(row["current_standard_call_expected_credits"], 30)

    def test_cfgi_low_and_exhausted_are_degraded(self) -> None:
        low = build(
            {"status": "PASS", "billing": {"credits_remaining": 10, "expected_credits": 30}},
            "gh-1",
            now=datetime(2026, 9, 8, tzinfo=timezone.utc),
        )
        self.assertEqual(low["status"], "DEGRADED")
        self.assertEqual(low["providers"]["CFGI"]["status"], "LOW_INSUFFICIENT_FOR_NEXT_STANDARD_CALL")
        exhausted = build(
            {"status": "PASS", "billing": {"credits_remaining": 0, "expected_credits": 30}},
            "gh-2",
            now=datetime(2026, 9, 8, tzinfo=timezone.utc),
        )
        self.assertEqual(exhausted["status"], "DEGRADED")
        self.assertEqual(exhausted["providers"]["CFGI"]["status"], "EXHAUSTED")

    def test_absent_credit_header_is_unknown_not_zero(self) -> None:
        packet = build(
            {"status": "PASS", "billing": {"credits_remaining": None, "expected_credits": 30}},
            "gh-3",
            now=datetime(2026, 9, 8, tzinfo=timezone.utc),
        )
        self.assertEqual(packet["status"], "UNKNOWN")
        self.assertEqual(packet["providers"]["CFGI"]["status"], "UNKNOWN_CREDIT_HEADER_ABSENT")
        self.assertIsNone(packet["providers"]["CFGI"]["credits_remaining"])
        self.assertFalse(packet["authority"]["portfolio_execution"])


if __name__ == "__main__":
    unittest.main()
