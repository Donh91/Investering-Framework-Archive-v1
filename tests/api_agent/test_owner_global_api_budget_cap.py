"""No-network proof legacy budget arguments cannot bypass owner global API cap."""
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/api_agent/check_monthly_cost_guard.py"


def run_guard(spent: float, cap: float = 40, reserve: float = 4):
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        receipt = {
            "contract": "SYNTHETIC_OWNER_COST_RECEIPT_v1",
            "response_id": "synthetic-owner-budget-test",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "estimated_cost_usd": spent,
        }
        (p / "receipt.json").write_text(json.dumps(receipt))
        result = subprocess.run([
            sys.executable, str(SCRIPT), "--receipt-root", str(p),
            "--hard-stop-usd", str(cap), "--reserve-usd", str(reserve),
        ], capture_output=True, text=True, check=False, timeout=25)
        return result.returncode, json.loads(result.stdout)


class OwnerGlobalBudgetTests(unittest.TestCase):
    def test_legacy_40_and_4_is_clamped_to_owner_30_and_12(self):
        rc, state = run_guard(17)
        self.assertEqual(rc, 0, state)
        self.assertEqual(state["status"], "PASS")
        self.assertEqual(state["requested_hard_stop_usd"], 40)
        self.assertEqual(state["effective_hard_stop_usd"], 30)
        self.assertEqual(state["reserve_usd"], 12)
        self.assertEqual(state["owner_remaining_usd"], 13)
        rc, state = run_guard(19)
        self.assertNotEqual(rc, 0)
        self.assertEqual(state["status"], "BLOCKED")
        self.assertEqual(state["remaining_usd"], 11)
        self.assertEqual(state["owner_remaining_usd"], 11)

    def test_stricter_legacy_lane_remains_enforced_with_global_shadow(self):
        rc, state = run_guard(8, cap=10, reserve=1)
        self.assertEqual(rc, 0, state)
        self.assertEqual(state["effective_hard_stop_usd"], 10)
        self.assertEqual(state["reserve_usd"], 1)
        rc, state = run_guard(9, cap=10, reserve=1)
        self.assertNotEqual(rc, 0)
        self.assertEqual(state["status"], "BLOCKED")
        self.assertEqual(state["remaining_usd"], 1)

    def test_lane_stricter_than_owner_cannot_bypass_owner_reserve(self):
        rc, state = run_guard(18.5, cap=20, reserve=1)
        self.assertNotEqual(rc, 0)
        self.assertEqual(state["status"], "BLOCKED")
        self.assertEqual(state["remaining_usd"], 1.5)
        self.assertEqual(state["owner_remaining_usd"], 11.5)

    def test_no_actual_spend_and_no_relaxation_from_large_claim(self):
        rc, state = run_guard(0, cap=5000, reserve=0)
        self.assertEqual(rc, 0)
        self.assertEqual(state["effective_hard_stop_usd"], 30)
        self.assertEqual(state["reserve_usd"], 12)
        self.assertEqual(state["owner_global_reserve_usd"], 12)


if __name__ == "__main__":
    unittest.main()
