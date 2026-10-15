"""Offline regression of optional Cycle Navigator long-horizon paid API cost path."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[2] / "scripts/cycle_navigator/build_internal_precision.py"
SPEC = importlib.util.spec_from_file_location("cn_internal_precision_budget", SRC)
assert SPEC and SPEC.loader
cn = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cn)


class Response:
    def __init__(self, data):
        self.body = json.dumps(data).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.body


class CNLongHorizonApiBudgetTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root = Path(self.t.name)
        policy = self.root / "research/api_agent/API_INTELLIGENCE_POLICY_v2.json"
        policy.parent.mkdir(parents=True)
        policy.write_text(json.dumps({
            "status": "ACTIVE_SHADOW_ONLY",
            "monthly_hard_stop_usd": 40,
            "global_reserve_usd": 4,
        }))
        (self.root / "research/api_agent/outputs").mkdir(parents=True)
        self.claims = [{"claim_id": "CN29-test-frozen-2w"}]
        self.evidence = [{"week": "2026-W41", "status": "FINAL"}]
        self.good = {
            "id": "resp_cn_budget_test",
            "status": "completed",
            "usage": {"input_tokens": 600, "output_tokens": 200},
            "output_text": json.dumps({
                "scores": [{"claim_id": self.claims[0]["claim_id"], "status": "SUPPORTED",
                            "score": 100, "evidence": "synthetic",
                            "self_critique": "not a market assertion"}]
            }),
        }

    def call(self, **kwargs):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-not-real"}, clear=False):
            return cn.score_long_horizon_via_api(
                "gpt-5.6-terra", self.claims, self.evidence,
                kwargs.get("limit", 5000), repo=self.root
            )

    def receipt(self):
        return cn._cn_cost_receipt_path(self.root, self.claims)

    def test_no_due_claims_is_strictly_no_spend(self):
        with patch("urllib.request.urlopen") as http:
            self.assertEqual(cn.score_long_horizon_via_api(
                "gpt-5.6-terra", [], [], 5000, repo=self.root), [])
            http.assert_not_called()

    def test_no_repo_authority_must_not_call_http(self):
        with patch("urllib.request.urlopen") as http:
            with self.assertRaisesRegex(RuntimeError, "CN_API_REPO_ROOT_REQUIRED"):
                cn.score_long_horizon_via_api("gpt-5.6-terra", self.claims, self.evidence, 5000)
            http.assert_not_called()

    def test_preflight_blocks_unaffordable_without_http(self):
        with patch("subprocess.run", return_value=subprocess.CompletedProcess([], 1)), \
             patch("urllib.request.urlopen") as http:
            with self.assertRaisesRegex(RuntimeError, "CN_API_GLOBAL_BUDGET_BLOCKED"):
                self.call()
            http.assert_not_called()
            self.assertFalse(self.receipt().exists())

    def test_source_budget_policy_must_match_governed_contract(self):
        path = self.root / "research/api_agent/API_INTELLIGENCE_POLICY_v2.json"
        policy = json.loads(path.read_text())
        policy["monthly_hard_stop_usd"] = 80
        path.write_text(json.dumps(policy))
        with patch("urllib.request.urlopen") as http:
            with self.assertRaisesRegex(RuntimeError, "CN_API_POLICY_UNVERIFIED"):
                self.call()
            http.assert_not_called()

    def test_missing_budget_policy_is_no_spend_and_weekly_can_continue(self):
        (self.root / "research/api_agent/API_INTELLIGENCE_POLICY_v2.json").unlink()
        with patch("urllib.request.urlopen") as http:
            with self.assertRaisesRegex(RuntimeError, "CN_API_POLICY_UNREADABLE_NO_SPEND"):
                self.call()
            http.assert_not_called()
            self.assertFalse(self.receipt().exists())

    def test_policy_list_is_no_spend(self):
        (self.root / "research/api_agent/API_INTELLIGENCE_POLICY_v2.json").write_text("[]")
        with patch("urllib.request.urlopen") as http:
            with self.assertRaisesRegex(RuntimeError, "CN_API_POLICY_INVALID_SHAPE_NO_SPEND"):
                self.call()
            http.assert_not_called()

    def test_malformed_policy_is_no_spend(self):
        (self.root / "research/api_agent/API_INTELLIGENCE_POLICY_v2.json").write_text("{broken")
        with patch("urllib.request.urlopen") as http:
            with self.assertRaisesRegex(RuntimeError, "CN_API_POLICY_UNREADABLE_NO_SPEND"):
                self.call()
            http.assert_not_called()

    def test_valid_call_has_exact_receipt_and_cannot_repeat(self):
        with patch("subprocess.run", return_value=subprocess.CompletedProcess([], 0)) as guard, \
             patch("urllib.request.urlopen", return_value=Response(self.good)) as http:
            rows = self.call()
            self.assertEqual(rows[0]["score"], 100)
            receipt = json.loads(self.receipt().read_text())
            self.assertEqual(receipt["status"], "PASS")
            self.assertEqual(receipt["contract"], "API_AGENT_RECEIPT_v3")
            self.assertEqual(receipt["task"], "CN_INTERNAL_LONG_HORIZON_SCORER")
            self.assertEqual(receipt["response_id"], "resp_cn_budget_test")
            self.assertEqual(receipt["input_tokens"], 600)
            self.assertEqual(receipt["output_tokens"], 200)
            self.assertGreater(receipt["estimated_cost_usd"], 0)
            command = guard.call_args.args[0]
            self.assertIn("check_monthly_cost_guard.py", " ".join(command))
            self.assertIn("--pending-ledger-root", command)
            self.assertIn("--reserve-usd", command)
            with self.assertRaisesRegex(RuntimeError, "COHORT_ALREADY_ATTEMPTED"):
                self.call()
            http.assert_called_once()

    def test_missing_usage_after_http_is_cost_unknown_and_blocks_reuse(self):
        no_usage = {**self.good}
        no_usage.pop("usage")
        with patch("subprocess.run", return_value=subprocess.CompletedProcess([], 0)), \
             patch("urllib.request.urlopen", return_value=Response(no_usage)) as http:
            with self.assertRaisesRegex(RuntimeError, "CN_API_COST_USAGE_UNKNOWN"):
                self.call()
            receipt = json.loads(self.receipt().read_text())
            self.assertNotIn("estimated_cost_usd", receipt)
            self.assertTrue(receipt["usage_reconciliation_required"])
            self.assertEqual(receipt["status"], "API_OUTPUT_INVALID")
            with self.assertRaisesRegex(RuntimeError, "COHORT_ALREADY_ATTEMPTED"):
                self.call()
            http.assert_called_once()

    def test_paid_claim_in_changed_cohort_must_not_pay_again(self):
        failed = {**self.good, "output_text": json.dumps({"scores": []})}
        first_id = self.claims[0]["claim_id"]
        with patch("subprocess.run", return_value=subprocess.CompletedProcess([], 0)), \
             patch("urllib.request.urlopen", return_value=Response(failed)) as http:
            with self.assertRaisesRegex(RuntimeError, "INVALID_STRUCTURED_OUTPUT"):
                self.call()
            self.assertTrue(self.receipt().exists())
            self.claims = [{"claim_id": first_id}, {"claim_id": "CN-next-due"}]
            new_due = cn._fresh_unattempted_long_claims(self.root, self.claims)
            self.assertEqual([claim["claim_id"] for claim in new_due], ["CN-next-due"])
            with self.assertRaisesRegex(RuntimeError, "CN_API_CLAIM_ALREADY_ATTEMPTED"):
                self.call()
            http.assert_called_once()

        self.claims = [{"claim_id": "CN-next-due"}]
        second = {**self.good, "id": "resp_other_only"}
        second["output_text"] = json.dumps({"scores": [{
            "claim_id": "CN-next-due", "status": "SUPPORTED", "score": 100,
            "evidence": "synthetic only", "self_critique": "not a historical prediction"}]})
        with patch("subprocess.run", return_value=subprocess.CompletedProcess([], 0)), \
             patch("urllib.request.urlopen", return_value=Response(second)) as http:
            self.assertEqual(self.call()[0]["claim_id"], "CN-next-due")
            http.assert_called_once()

    def test_malformed_previous_paid_receipt_blocks_new_cohort_no_http(self):
        older = self.root / "research/api_agent/outputs/cn_internal_precision" / "synthetic-old"
        older.mkdir(parents=True)
        (older / "receipt.json").write_text("{broken")
        with patch("urllib.request.urlopen") as http:
            with self.assertRaisesRegex(RuntimeError, "CN_API_PREVIOUS_RECEIPT_UNREADABLE"):
                cn._fresh_unattempted_long_claims(self.root, self.claims)
            with self.assertRaisesRegex(RuntimeError, "CN_API_PREVIOUS_RECEIPT_UNREADABLE"):
                self.call()
            http.assert_not_called()

    def test_invalid_model_output_retains_charge_and_skips_scoring(self):
        invalid = {**self.good, "output_text": json.dumps({"scores": []})}
        with patch("subprocess.run", return_value=subprocess.CompletedProcess([], 0)), \
             patch("urllib.request.urlopen", return_value=Response(invalid)):
            with self.assertRaisesRegex(RuntimeError, "INVALID_STRUCTURED_OUTPUT"):
                self.call()
            receipt = json.loads(self.receipt().read_text())
            self.assertEqual(receipt["status"], "API_OUTPUT_INVALID")
            self.assertGreater(receipt["estimated_cost_usd"], 0)

    def test_post_timeout_unknown_usage_not_silently_free(self):
        from urllib.error import URLError
        with patch("subprocess.run", return_value=subprocess.CompletedProcess([], 0)), \
             patch("urllib.request.urlopen", side_effect=URLError("test timeout")):
            with self.assertRaisesRegex(RuntimeError, "CN_API_COST_USAGE_UNKNOWN"):
                self.call()
            self.assertTrue(json.loads(self.receipt().read_text())["usage_reconciliation_required"])

    def test_invalid_output_token_limit_does_not_call_http(self):
        with patch("urllib.request.urlopen") as http:
            with self.assertRaisesRegex(RuntimeError, "CN_API_MODEL_OR_OUTPUT_LIMIT_NOT_APPROVED"):
                self.call(limit=10000)
            http.assert_not_called()


if __name__ == "__main__":
    unittest.main()
