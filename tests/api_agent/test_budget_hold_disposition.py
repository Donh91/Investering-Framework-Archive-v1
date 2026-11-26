import json
import subprocess
import unittest

from scripts.api_agent.budget_hold_disposition import classify, run_guards


def result(row, rc=0, stderr=""):
    return subprocess.CompletedProcess([], rc, json.dumps(row), stderr)


def monthly(remaining=3.956258, **kw):
    return dict(status="BLOCKED", fail_closed=True, cost_evidence_errors=[],
                malformed_cost_receipts=[], remaining_usd=remaining, reserve_usd=4.0,
                requested_hard_stop_usd=40, effective_hard_stop_usd=40,
                historical_pr_audit_only=False, paid_authority=False,
                owner_global_remaining_usd_after_risk=63.956258,
                owner_global_reserve_usd=4.0, **kw)


def lane(**kw):
    row = dict(status="PASS", fail_closed=True, cost_evidence_errors=[],
               task="RESEARCH_AUTOMATION", cap_usd=10.0, reserve_usd=0.25,
               remaining_usd=10.0)
    row.update(kw)
    return row


class BudgetHoldDispositionTest(unittest.TestCase):
    def test_exact_observed_reserve_hold(self):
        self.assertEqual(classify("monthly", result(monthly(), 1, "monthly_api_cost_guard_blocked\n"), "research")[0], "HOLD")

    def test_lane_hold_is_terminal(self):
        calls = []
        def runner(command, **_):
            calls.append(command)
            return result(lane(status="BLOCKED", remaining_usd=0.25), 1, "api_lane_budget_blocked")
        self.assertEqual(run_guards("research", runner)[0], "HOLD")
        self.assertEqual(len(calls), 1)

    def test_monthly_only_after_lane_pass(self):
        calls = []
        def runner(command, **_):
            calls.append(command)
            if len(calls) == 1:
                return result(lane())
            return result(monthly(), 1, "monthly_api_cost_guard_blocked")
        self.assertEqual(run_guards("research", runner)[0], "HOLD")
        self.assertEqual(len(calls), 2)
        self.assertNotIn("--pending-ledger-root", calls[1])

    def test_both_pass(self):
        row = monthly(remaining=5)
        row["status"] = "PASS"
        results = iter([result(lane()), result(row)])
        self.assertEqual(run_guards("research", lambda *a, **k: next(results))[0], "PASS")

    def test_unknown_or_malformed_never_hold_or_pass(self):
        cases = []
        for changes in [
            {"cost_evidence_errors": [{"reason": "UNKNOWN"}]},
            {"remaining_usd": True}, {"remaining_usd": float("nan")},
            {"fail_closed": 1}, {"reserve_usd": 0.0},
            {"malformed_cost_receipts": ["bad"]}, {"paid_authority": True},
            {"historical_pr_audit_only": True}, {"effective_hard_stop_usd": 100},
            {"remaining_usd": 5}, {"status": "PASS"},
        ]:
            row = monthly()
            row.update(changes)
            cases.append(result(row, 1, "monthly_api_cost_guard_blocked"))
        cases += [result(monthly(), 2, "monthly_api_cost_guard_blocked"),
                  result(monthly(), 1, "Traceback"),
                  result(monthly(), 0, ""),
                  subprocess.CompletedProcess([], 1, '{"status":"BLOCKED","status":"PASS"}', "monthly_api_cost_guard_blocked")]
        for item in cases:
            with self.subTest(item=item):
                self.assertEqual(classify("monthly", item, "research")[0], "ERROR")

    def test_director_retains_pending_root(self):
        calls = []
        def runner(command, **_):
            calls.append(command)
            if len(calls) == 1:
                return result(lane(task="DAILY_DIRECTOR_SHADOW", cap_usd=4.0, reserve_usd=0.05))
            return result(monthly(), 1, "monthly_api_cost_guard_blocked")
        self.assertEqual(run_guards("director", runner)[0], "HOLD")
        self.assertIn("--pending-ledger-root", calls[1])
        self.assertIn("runtime/api-cost-ledger", calls[1])
