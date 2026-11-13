"""No-network, source-bound financial risk range and future MAX preview tests."""
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/api_agent/check_monthly_cost_guard.py"


def risk_row(run, lower=0, upper=3, month="2026-11"):
    return {
        "run_id": str(run), "created_month_utc": month,
        "status": "POST_OUTCOME_UNKNOWN", "lower_usd": lower,
        "upper_usd": upper,
        "source": ("https://github.com/Donh91/"
                   "Investering-Framework-Archive-v1/actions/runs/" + str(run)),
        "basis": "Native original per-request governed USD3 ceiling, never retry old POST.",
    }


def run_guard(spent=0, cap=40, reserve=4, rows=None, extra=None,
              missing_ledger=False):
    with tempfile.TemporaryDirectory() as td:
        folder = Path(td)
        receipts = folder / "receipts"
        receipts.mkdir()
        receipt = {
            "contract": "SYNTHETIC_OWNER_COST_RECEIPT_v1",
            "response_id": "synthetic-owner-budget-test",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "estimated_cost_usd": spent,
        }
        (receipts / "receipt.json").write_text(json.dumps(receipt))
        ledger = folder / "risk.json"
        if not missing_ledger:
            content = {
                "contract": "API_PENDING_BILLING_RISK_V1",
                "no_retry_original_ids": True,
                "requires_reconciliation_before_releasing_reserve": True,
                "unresolved": rows if rows is not None else [
                    risk_row(41870364609), risk_row(41949497953),
                    risk_row(42204120988)],
            }
            ledger.write_text(json.dumps(content))
        cmd = [
            sys.executable, str(SCRIPT), "--receipt-root", str(receipts),
            "--hard-stop-usd", str(cap), "--reserve-usd", str(reserve),
            "--liability-ledger", str(ledger),
        ] + (extra or [])
        result = subprocess.run(cmd, capture_output=True, text=True,
                                check=False, timeout=25, cwd=ROOT)
        if not result.stdout.strip():
            if result.returncode != 0 and "caps/reserves must be finite nonnegative" in result.stderr:
                return result.returncode, {"status": "BLOCKED", "error": result.stderr}
            raise AssertionError(result.stderr)
        return result.returncode, json.loads(result.stdout)


class OwnerGlobalBudgetTests(unittest.TestCase):
    def test_known_cost_plus_three_upper_unknown_is_never_zero(self):
        rc, state = run_guard(17)
        self.assertEqual(rc, 0, state)
        self.assertEqual(state["status"], "PASS")
        self.assertEqual(state["owner_normal_target_usd"], 50)
        self.assertEqual(state["effective_hard_stop_usd"], 40)
        self.assertEqual(state["pending_liability_count"], 3)
        self.assertEqual(state["pending_liability_lower_usd"], 0)
        self.assertEqual(state["pending_liability_upper_usd"], 9)
        self.assertEqual(state["exposure_range_min_usd"], 17)
        self.assertEqual(state["exposure_range_max_usd"], 26)
        self.assertEqual(state["normal_remaining_usd"], 24)

    def test_routine_zero_reserve_argument_does_not_remove_four_dollar_buffer(self):
        rc, state = run_guard(26, cap=40, reserve=0)
        self.assertEqual(rc, 0, state)
        self.assertEqual(state["reserve_usd"], 4)
        rc, state = run_guard(27.01, cap=40, reserve=0)
        self.assertNotEqual(rc, 0, state)
        self.assertEqual(state["status"], "BLOCKED")

    def test_owner_50_total_with_four_reserve_and_unchanged_old_caller_caps(self):
        # An original caller passing 40 still has its own stricter ceiling.
        rc, state = run_guard(26, cap=40, reserve=0)
        self.assertEqual(rc, 0, state)
        self.assertEqual(state["effective_hard_stop_usd"], 40)
        self.assertEqual(state["reserve_usd"], 4)
        # If an existing caller requests 45, the same protected four applies.
        rc, state = run_guard(26, cap=45, reserve=0,
                              extra=["--new-request-upper-usd","3"])
        self.assertEqual(rc, 0, state)
        self.assertEqual(state["reserve_usd"], 4)
        self.assertEqual(state["exposure_range_max_usd"], 38)
        # The new total cap is 50, NOT 50 plus a separate exceptional 5.
        rc, state = run_guard(33, cap=50, reserve=0,
                              extra=["--new-request-upper-usd","3"])
        self.assertEqual(rc, 0, state)
        self.assertEqual(state["effective_hard_stop_usd"], 50)
        self.assertEqual(state["reserve_usd"], 4)
        self.assertEqual(state["exposure_range_max_usd"], 45)
        self.assertEqual(state["remaining_usd"], 5)
        rc, state = run_guard(36.01, cap=50, reserve=0,
                              extra=["--new-request-upper-usd","3"])
        self.assertNotEqual(rc, 0)
        self.assertEqual(state["status"],"BLOCKED")
        self.assertLess(state["remaining_usd"],4)
        # A client cannot increase the globally authorized amount via CLI.
        rc, state = run_guard(1, cap=50.01, reserve=0)
        self.assertNotEqual(rc, 0)
        self.assertIn("OWNER_GLOBAL_50_USD_CAP_EXCEEDED",
                      str(state["cost_evidence_errors"]))

    def test_existing_small_lane_reserve_does_not_override_global_four_dollars(self):
        # Regression for the native CN 9.4/0.1 partial-spend lane. Its
        # source-bound local reserve remains 0.1; global USD4 still binds.
        rc, state = run_guard(0.12, cap=9.4, reserve=0.1)
        self.assertEqual(rc, 0, state)
        self.assertEqual(state["pending_liability_upper_usd"], 9)
        self.assertEqual(state["exposure_range_max_usd"], 9.12)
        self.assertEqual(state["reserve_usd"], 0.1)
        self.assertGreaterEqual(state["owner_global_remaining_usd_after_risk"], 4)
        rc, state = run_guard(0.12, cap=9.2, reserve=0.1)
        self.assertNotEqual(rc, 0)
        self.assertEqual(state["status"], "BLOCKED")

    def test_one_request_usd3_limit_remains_even_under_new_50_global_cap(self):
        for value in ("3.01","4","10"):
            rc, state=run_guard(1,cap=50,reserve=4,
                                extra=["--new-request-upper-usd",value])
            self.assertNotEqual(rc,0)
            self.assertEqual(state["status"],"BLOCKED")

    def test_mismatched_explicit_owner_ledger_ceiling_is_blocked(self):
        from scripts.api_agent.check_monthly_cost_guard import pending_risk
        with tempfile.TemporaryDirectory() as td:
            original=json.loads((ROOT/"research/api_agent/coordination/API_PENDING_BILLING_RISK_V1.json").read_text())
            self.assertEqual(original["normal_budget_usd"],50)
            self.assertEqual(original["absolute_budget_usd"],50)
            p=Path(td)/"ledger.json"
            for key,value in (("normal_budget_usd",40),("absolute_budget_usd",45)):
                bad={**original,key:value}
                p.write_text(json.dumps(bad))
                with self.assertRaisesRegex(ValueError,"LIABILITY_LEDGER_CONTRACT_INVALID"):
                    pending_risk(p)

    def test_stricter_original_caller_reserve_and_lane_still_bind(self):
        rc, state = run_guard(17, cap=30, reserve=12)
        self.assertNotEqual(rc, 0)
        self.assertEqual(state["effective_hard_stop_usd"], 30)
        self.assertEqual(state["reserve_usd"], 12)
        rc, state = run_guard(8, cap=30, reserve=12)
        self.assertEqual(rc, 0, state)
        rc, state = run_guard(8, cap=10, reserve=1)
        self.assertNotEqual(rc, 0)
        self.assertEqual(state["effective_hard_stop_usd"], 10)

    def test_no_free_spend_for_missing_malformed_or_duplicate_liability(self):
        rc, state = run_guard(1, missing_ledger=True)
        self.assertNotEqual(rc, 0)
        self.assertIn("LIABILITY_EVIDENCE_UNAVAILABLE",
                      str(state["cost_evidence_errors"]))
        for rows in (
            [],
            [risk_row(41870364609)],
            [risk_row(41949497953)],
            [risk_row(41870364609), risk_row(41949497953)],
            [risk_row(41870364609), risk_row(41949497953), risk_row(42204120988, upper=2.99)],
            [risk_row(41870364609, upper=2.99), risk_row(41949497953)],
            [risk_row(41870364609), risk_row(41949497953, upper=2.99)],
            [risk_row(41870364609), risk_row(41870364609)],
            [risk_row(41870364609, upper=4)],
            [risk_row(41870364609, upper=0)],
            [risk_row(41870364609, upper=-1)],
            [risk_row(41870364609, lower=2, upper=1)],
            [risk_row(41870364609, upper=float("nan"))],
            [{**risk_row(41870364609), "source": "forged"}],
        ):
            rc, state = run_guard(0, rows=rows)
            self.assertNotEqual(rc, 0, state)
            self.assertEqual(state["status"], "BLOCKED")

    def test_pending_past_month_stays_reserved_until_reconciled(self):
        rc, state = run_guard(26, cap=40, reserve=0,
                              rows=[risk_row(41870364609, month="2026-10"),
                                    risk_row(41949497953, month="2026-11"),
                                    risk_row(42204120988, month="2026-11")])
        self.assertEqual(rc, 0)
        self.assertEqual(state["exposure_range_max_usd"], 35)

    def test_max_quote_current_model_one_time_no_payment(self):
        params = [
            "--model", "gpt-6.1-sol", "--task", "SENIOR_REPAIR_AUDIT",
            "--effort", "max", "--owner-work-id", "S1-MAX-20261106-NEW",
            "--input-token-upper", "300000", "--output-token-upper", "45000",
        ]
        rc, state = run_guard(24, cap=40, reserve=4, extra=params)
        self.assertEqual(rc, 0, state)
        self.assertEqual(state["approval_quote"]["status"],
                         "QUOTE_ONLY_NATIVE_OWNER_CLAIM_REQUIRED")
        self.assertEqual(state["approval_quote"]["token_price_upper_usd"], 1.05)
        self.assertEqual(state["new_request_reserved_upper_usd"], 1.05)
        self.assertEqual(state["exposure_range_max_usd"], 34.05)

    def test_future_model_unknown_price_or_unapproved_route_fails_closed(self):
        params = [
            "--model", "gpt-6.2-sol", "--task", "SENIOR_REPAIR_AUDIT",
            "--effort", "max", "--owner-work-id", "S1-MAX-20261106-NEW",
            "--input-token-upper", "300000", "--output-token-upper", "45000",
        ]
        rc, state = run_guard(1, extra=params)
        self.assertNotEqual(rc, 0)
        self.assertIn("MAX_MODEL_NOT_CURRENTLY_PRICED_AND_ADMITTED",
                      str(state["cost_evidence_errors"]))
        params[params.index("gpt-6.2-sol")] = "gpt-6.1-sol"
        params[params.index("max")] = "high"
        rc, state = run_guard(1, extra=params)
        self.assertNotEqual(rc, 0)
        self.assertIn("MAX_APPROVAL_ID_OR_EFFORT_INVALID",
                      str(state["cost_evidence_errors"]))

    def test_no_unbounded_or_nan_new_api_reservation(self):
        for value in ("4", "-1", "NaN", "Infinity"):
            with self.subTest(value=value):
                rc, state = run_guard(1, extra=[
                    "--new-request-upper-usd", value])
                self.assertNotEqual(rc, 0)
                self.assertEqual(state["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
