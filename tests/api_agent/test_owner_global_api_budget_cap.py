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
            self.assertEqual(original["absolute_budget_usd"],100)
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
        # Settled canonical items do not create a permanent floor. Fresh
        # synthetic unresolved liabilities still reject malformed exposures.
        for rows in (
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

    def test_canonical_ledger_keeps_existing_40_4_lanes_live(self):
        # Run against REAL canonical receipts and canonical persistent ledger.
        # Synthetic fixtures hid the rejected-P1 USD10 reservation regression.
        cmd = [
            sys.executable, str(SCRIPT),
            "--receipt-root", str(ROOT / "research/api_agent/outputs"),
            "--liability-ledger", str(ROOT / "research/api_agent/coordination/API_PENDING_BILLING_RISK_V1.json"),
            "--hard-stop-usd", "40", "--reserve-usd", "4",
            "--new-request-upper-usd", "0",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True,
                                check=False, timeout=25, cwd=ROOT)
        self.assertTrue(result.stdout.strip(), result.stderr)
        state = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, state)
        self.assertEqual(state["status"], "PASS", state)
        # Native POSTs are settled; retain consumed USD3+10 and distinct USD10
        # owner-approved (not yet consumed) public research reservation.
        self.assertEqual(state["pending_liability_upper_usd"], 46.0)   # the four Astra mission rows (#1156): USD20 R2 (consumed) + USD3 Alpha-on-Sol + USD3 Sol A/B (consumed) + USD20 Navigator One
        self.assertEqual(state["pending_liability_count"], 4)
        self.assertEqual(state["owner_global_hard_stop_usd"], 100.0)
        self.assertGreaterEqual(state["remaining_usd"], 4.0)
        self.assertEqual(state["effective_hard_stop_usd"], 40.0)

    def test_canonical_provider_settlement_is_evidence_bound_and_private(self):
        from scripts.api_agent.check_monthly_cost_guard import (
            pending_risk, UNRESOLVED_NATIVE_POST_FLOOR_USD,
        )
        p = ROOT / "research/api_agent/coordination/API_PENDING_BILLING_RISK_V1.json"
        ledger = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(UNRESOLVED_NATIVE_POST_FLOOR_USD, {})
        self.assertEqual(ledger["unresolved"], [])
        self.assertEqual(
            sorted(r["work_id"] for r in ledger["owner_reservations"]),
            ["ASTRA-HIGH-ALPHA-LAB-PAPER-EDGE-20261116-ONE","ASTRA-HIGH-COMPASS-EARLY-WARNING-CYCLE-20261116-ONE","ASTRA-HIGH-COMPASS-EDGE-SCIENCE-20261116-ONE","ASTRA-HIGH-COMPASS-TOTAL-AUDIT-20261116-ONE","ASTRA-HIGH-MAEVE-TASK2-PREP-20261117-ONE","ASTRA-HIGH-S1-VNEXT-ARCHITECTURE-20261116-ONE","ASTRA-HIGH-TASK2-ALL-CN-HISTORICAL-20261113-ONE","ASTRA-HIGH-TASK2-PUBLIC-W46W47-20261116-ONE","ASTRA-HIGH-TASK2-SCIENTIFIC-20261113-ONE"])
        self.assertEqual(pending_risk(p), (0.0, 46.0, 4))   # canonical USD20 R2 (consumed) + USD3 Alpha-on-Sol + USD3 Sol A/B (consumed) + USD20 Navigator One mission rows
        self.assertEqual(len(ledger["settled"]), 3)
        self.assertEqual({r["kind"] for r in ledger["settled"]}, {"NATIVE_POST"})
        self.assertEqual(ledger["provider_settlement_evidence"]["sha256"],
                         "fb6ba8b50b356a9a48c05915578e77fc16cca3af08694436cc57f4f4335598c8")
        self.assertTrue(ledger["provider_settlement_evidence"]["path"].startswith(
            "reports/claude/automated/2026/11/CLAUDE-API-BUDGET-PROVIDER-RECONCILIATION-"))
        for row in ledger["settled"]:
            for name in ("lower_usd", "upper_usd", "amount_usd", "billed_usd"):
                self.assertNotIn(name, row)
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "settlement.json"
            for mutation in ("missing_evidence", "wrong_commit", "wrong_bytes", "dropped_entry", "duplicate_unresolved"):
                bad = json.loads(json.dumps(ledger))
                if mutation == "missing_evidence":
                    bad["provider_settlement_evidence"]["sha256"] = "forged"
                elif mutation == "wrong_commit":
                    bad["provider_settlement_evidence"]["commit_sha"] = "0" * 40
                elif mutation == "wrong_bytes":
                    bad["provider_settlement_evidence"]["bytes"] = 0
                elif mutation == "dropped_entry":
                    bad["settled"].pop()
                else:
                    bad["unresolved"] = [risk_row(41870364609)]
                f.write_text(json.dumps(bad), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "PROVIDER_SETTLE"):
                    pending_risk(f)
            # The consumed Astra reservations can neither be settled by this
            # aggregate evidence nor silently dropped from the ledger.
            for mutation, code in (("astra_settled", "PROVIDER_SETTLED_SET_INVALID"),
                                   ("astra_dropped", "ASTRA_PROVIDER_GROUP_EVIDENCE_INVALID")):
                bad = json.loads(json.dumps(ledger))
                astra = bad["owner_reservations"].pop(0)
                if mutation == "astra_settled":
                    bad["settled"].append({"kind": "ASTRA_PREHTTP_RESERVATION",
                                           "work_id": astra["work_id"],
                                           "created_month_utc": "2026-11",
                                           "status": "PROVIDER_PERIOD_RECONCILED",
                                           "source": astra["source"], "no_retry": True})
                f.write_text(json.dumps(bad), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, code):
                    pending_risk(f)

    def test_consumed_group_counted_once_and_tampering_denied(self):
        from scripts.api_agent import check_monthly_cost_guard as g
        p = g.CANONICAL_LIABILITY_LEDGER
        original = json.loads(p.read_text())
        self.assertEqual(g.pending_risk(p), (0.0, 46.0, 4))   # canonical USD20 R2 (consumed) + USD3 Alpha-on-Sol + USD3 Sol A/B (consumed) + USD20 Navigator One mission rows
        self.assertEqual(g.settled_owner_cost_upper(p, datetime(2026, 11, 18, tzinfo=timezone.utc)), 12.60981)
        self.assertEqual(g.settled_owner_cost_upper(p, datetime(2026, 12, 1, tzinfo=timezone.utc)), 0.0)
        self.assertEqual(original["owner_astra_provider_period_settlement"]["provider_period_spend_usd"], 5.41)
        self.assertEqual(original["owner_astra_provider_period_settlement"]["settled_total_usd"], 5.41)
        self.assertEqual(original["owner_astra_provider_period_settlement"]["source"], "owner OpenAI usage dashboard + CSV export 2026-11-18")
        with tempfile.TemporaryDirectory() as td:
            probe = Path(td) / "ledger.json"
            for change in ("wrong_run", "wrong_amount", "replay", "invented_release", "drop"):
                bad = json.loads(json.dumps(original))
                row = bad["owner_reservations"][0]
                if change == "wrong_run":
                    row["native_settlement_evidence"]["run_id"] = "0"
                elif change == "wrong_amount":
                    bad["owner_astra_provider_period_settlement"]["provider_period_spend_usd"] = 0
                elif change == "replay":
                    row["status"] = g.ACTIVE_RESERVATION_STATUS
                    row["reconciliation_required"] = True
                elif change == "invented_release":
                    row["status"] = g.RELEASED_STATUS
                else:
                    bad["owner_reservations"].pop()
                probe.write_text(json.dumps(bad))
                with self.assertRaises(ValueError):
                    g.pending_risk(probe)
            # A separate future reservation still contributes exactly its full ceiling.
            new = {"work_id": "ASTRA-HIGH-TASK2-REALDATA-V2-20261113-ONE",
                   "created_month_utc": "2026-11", "status": g.ACTIVE_RESERVATION_STATUS,
                   "lower_usd": 0, "upper_usd": 10,
                   "source": "https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596",
                   "one_paid_post_max": 1, "reconciliation_required": True}
            original["owner_reservations"].append(new)
            probe.write_text(json.dumps(original))
            self.assertEqual(g.pending_risk(probe), (0.0, 56.0, 5))   # plus the canonical USD20 R2 (consumed) + USD3 Alpha-on-Sol + USD3 Sol A/B (consumed) + USD20 Navigator One mission rows
            # Reviewed native never-triggered evidence, not a claim about any current row.
            from unittest.mock import patch
            proof = {"trigger_comment": None, "workflow_run": None, "census": "synthetic"}
            new.update(status=g.RELEASED_STATUS, reconciliation_required=False,
                       no_retry=True, native_settlement_evidence=proof)
            probe.write_text(json.dumps(original))
            with patch.dict(g.OWNER_NEVER_TRIGGERED_EVIDENCE, {new["work_id"]: proof}):
                self.assertEqual(g.pending_risk(probe), (0.0, 46.0, 4))   # the canonical USD20 R2 (consumed) + USD3 Alpha-on-Sol + USD3 Sol A/B (consumed) + USD20 Navigator One mission rows stay counted

    def test_maeve_consumed_pr_preflight_never_returns_paid_pass(self):
        import os
        work = "ASTRA-HIGH-MAEVE-TASK2-PREP-20261117-ONE"
        cmd = [sys.executable, str(SCRIPT), "--receipt-root", str(ROOT / "research/api_agent/outputs"),
               "--hard-stop-usd", "100", "--reserve-usd", "4",
               "--new-request-upper-usd", "0", "--owner-astra-program-work-id", work]
        for event, ref, expected in [
            ("pull_request", "refs/pull/2222/merge", "CONSUMED_NO_POST"),
            ("issue_comment", "refs/heads/main", "BLOCKED"),
            ("pull_request", "refs/heads/main", "BLOCKED"),
        ]:
            env = dict(os.environ, GITHUB_ACTIONS="true", GITHUB_EVENT_NAME=event, GITHUB_REF=ref)
            proc = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=25)
            state = json.loads(proc.stdout)
            self.assertEqual(state["status"], expected, state)
            self.assertFalse(state["paid_authority"])
            self.assertEqual(proc.returncode == 0, expected == "CONSUMED_NO_POST")

    def test_native_caller_caps_above_40_only_in_hard_disabled_astra_v2_job(self):
        import re
        workflow = ROOT / ".github/workflows/owner-bound-daily-director-manual.yml"
        source = workflow.read_text(encoding="utf-8")
        marker = "\n  astra-realdata-task2-v2:\n"
        self.assertEqual(source.count(marker), 1)
        astra_job = source.split(marker, 1)[1]
        self.assertRegex(astra_job, r"(?m)^    if: >-\s*\n      false &&\s*$")
        candidates = list(ROOT.glob(".github/workflows/*.yml")) + list(ROOT.glob("scripts/**/*.py"))
        high_values = []
        for path in candidates:
            data = path.read_text(encoding="utf-8")
            for match in re.finditer(r"--hard-stop-usd\s+(\d+(?:\.\d+)?)", data):
                amount = float(match.group(1))
                if amount > 40:
                    high_values.append((path.relative_to(ROOT).as_posix(), amount, match.start()))
        # 1 old DISABLED 50USD code-interpreter lane plus exactly 5 new
        # owner-bound Astra 100USD exceptional routes, no general caller.
        legacy = [x for x in high_values if x[0] == workflow.relative_to(ROOT).as_posix()]
        exceptional = [x for x in high_values if x[0] ==
            ".github/workflows/owner-astra-research-program-20261116.yml"]
        self.assertEqual(len(legacy), 1, high_values)
        self.assertEqual(legacy[0][1], 50.0)
        self.assertGreater(legacy[0][2], source.index(marker))
        self.assertEqual(len(exceptional), 5, high_values)
        self.assertTrue(all(row[1] == 100.0 for row in exceptional))
        maeve = [x for x in high_values if x[0] == ".github/workflows/owner-astra-maeve-task2-20261117.yml"]
        self.assertEqual(len(maeve), 1, high_values)
        self.assertEqual(maeve[0][1], 100.0)
        self.assertEqual(len(high_values), 7, high_values)
        # Removing the false && on the only elevated-cap job must fail tests.
        self.assertFalse(json.loads((ROOT / "research/api_agent/coordination/ASTRA_TASK2_REALDATA_V2_ADMISSION_V1.json").read_text())["authorized_paid_dispatch"])

    def test_no_unbounded_or_nan_new_api_reservation(self):
        for value in ("4", "-1", "NaN", "Infinity"):
            with self.subTest(value=value):
                rc, state = run_guard(1, extra=[
                    "--new-request-upper-usd", value])
                self.assertNotEqual(rc, 0)
                self.assertEqual(state["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
