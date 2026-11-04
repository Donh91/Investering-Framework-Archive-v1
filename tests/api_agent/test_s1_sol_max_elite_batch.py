"""Offline, non-paid checks for the owner-bound Sol MAX implementation batch."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "research/api_agent/coordination/S1_SOL_MAX_ELITE_BOUNDED_BATCH_20261104.json"

class TestEliteBatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = json.loads(PATH.read_text())

    def test_contract_and_no_paid_dispatch(self):
        b = self.batch
        self.assertEqual(b["contract"], "S1_SOL_MAX_ELITE_BOUNDED_BATCH_v1")
        self.assertEqual(b["repo"], "Donh91/Investering-Framework-Archive-v1")
        self.assertEqual((b["model"], b["reasoning_effort"]), ("gpt-6.1-sol", "max"))
        self.assertEqual(b["state"], "REGISTERED_NOT_EXECUTING")
        self.assertIs(b["dispatch_enabled"], False)
        self.assertEqual(b["max_concurrent_paid_missions"], 1)
        self.assertIs(b["forbid_new_scheduler_agent_or_writer"], True)
        self.assertEqual(b["billing_liability_for_run_41870364609"], "UNKNOWN")
        self.assertIs(b["payment_policy"]["do_not_retry_unresolved_paid_post"], True)
        self.assertEqual(b["payment_policy"]["per_call_max_usd"], 3)

    def test_all_five_are_unique_existing_owner_missions(self):
        rows = self.batch["definitions"]
        self.assertEqual(len(rows), 5)
        self.assertEqual([x["rank"] for x in rows], [1, 2, 3, 4, 5])
        ids = {x["id"] for x in rows}
        self.assertEqual(len(ids), len(rows))
        for row in rows:
            self.assertIn(row["owner_issue"], (1156, 1157, 1516))
            self.assertTrue(row["defect"] and row["deliverable"] and row["tests"] and row["kill"])
            self.assertTrue(set(row["depends_on"]).issubset(ids))
            self.assertTrue(row["phase"].startswith("STAGED"))
            self.assertIn(row["priority"], ("P0", "P1"))

    def test_forecast_original_owner_and_immutable_w45(self):
        row = self.batch["definitions"][2]
        self.assertEqual(row["original_pr"], 1879)
        self.assertEqual(row["owner_issue"], 1516)
        self.assertIn("W45 immutably remains 0/7", row["deliverable"])
        self.assertTrue(self.batch["security"]["no_historical_forecast_rewrite"])

    def test_no_silent_paid_fallback(self):
        p = self.batch["payment_policy"]
        self.assertEqual((p["owner_monthly_hard_stop_usd"], p["owner_global_reserve_usd"]), (30, 12))
        self.assertTrue(p["no_auto_paid_trigger_until_reconciled"])
        self.assertTrue(self.batch["security"]["no_model_git_credentials"])

if __name__ == "__main__":
    unittest.main()
