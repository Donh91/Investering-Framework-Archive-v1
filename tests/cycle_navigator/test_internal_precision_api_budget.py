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
            "lane_caps_usd": {"CN_INTERNAL_LONG_HORIZON_SCORER": 1},
        }))
        (self.root / "research/api_agent/outputs").mkdir(parents=True)
        self.claims = [{"claim_id": "CN29-test-frozen-2w"}]
        self.evidence = [{"week": "2026-W41", "status": "FINAL"}]
        # Existing scorer tests target API response and independent budget
        # admission. GitHub persistence is tested explicitly below instead
        # of accidentally causing real remote writes in these offline cases.
        self.reservation_patcher = patch.object(cn, "_reserve_cn_api_attempt_before_post")
        self.reservation_call = self.reservation_patcher.start()
        self.addCleanup(self.reservation_patcher.stop)
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

    def test_oversized_first_claim_does_not_starve_later_due_claim(self):
        claims = [{"claim_id": "big"}, {"claim_id": "small"}]
        accepted = [{"claim_id": "small", "status": "SUPPORTED", "score": 100,
                     "evidence": "synthetic", "self_critique": "synthetic"}]
        with patch.object(cn, "evidence_for_long_claims", return_value=[{"status": "AVAILABLE"}]), \
             patch.object(cn, "score_long_horizon_via_api", side_effect=[
                 RuntimeError("CN_API_CONTEXT_SIZE_OUT_OF_BOUNDS"), accepted,
             ]) as paid:
            scores, blocked = cn.score_matured_claims_bounded(self.root, claims, "gpt-5.6-terra", 5000)
            self.assertEqual(scores, accepted)
            self.assertEqual(blocked, ["big"])
            self.assertEqual(paid.call_count, 2)
            self.assertEqual(paid.call_args_list[0].args[1], [claims[0]])
            self.assertEqual(paid.call_args_list[1].args[1], [claims[1]])

    def test_paid_or_ambiguous_failure_stops_before_following_claim(self):
        claims = [{"claim_id": "first"}, {"claim_id": "second"}]
        with patch.object(cn, "evidence_for_long_claims", return_value=[{"status": "AVAILABLE"}]), \
             patch.object(cn, "score_long_horizon_via_api", side_effect=RuntimeError("CN_API_COST_USAGE_UNKNOWN")) as paid:
            scores, blocked = cn.score_matured_claims_bounded(self.root, claims, "gpt-5.6-terra", 5000)
            self.assertEqual((scores, blocked), ([], []))
            paid.assert_called_once()

    def test_one_successful_paid_call_maximum_per_run(self):
        claims = [{"claim_id": "a"}, {"claim_id": "b"}]
        result = [{"claim_id": "a", "status": "MIXED", "score": 50,
                   "evidence": "synthetic", "self_critique": "synthetic"}]
        with patch.object(cn, "evidence_for_long_claims", return_value=[{"status": "AVAILABLE"}]), \
             patch.object(cn, "score_long_horizon_via_api", return_value=result) as paid:
            scores, blocked = cn.score_matured_claims_bounded(self.root, claims, "gpt-5.6-terra", 5000)
            self.assertEqual(scores, result)
            self.assertFalse(blocked)
            paid.assert_called_once()

    def test_missing_final_week_is_not_evaluable_without_payment(self):
        claim = {"claim_id": "missing"}
        with patch.object(cn, "evidence_for_long_claims", return_value=[{"status": "MISSING"}]), \
             patch.object(cn, "score_long_horizon_via_api") as paid:
            scores, blocked = cn.score_matured_claims_bounded(self.root, [claim], "gpt-5.6-terra", 5000)
            self.assertEqual(scores[0]["status"], "NOT_EVALUABLE")
            self.assertIsNone(scores[0]["score"])
            self.assertFalse(blocked)
            paid.assert_not_called()

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

    def test_missing_specific_lane_cap_fails_closed_before_payment(self):
        path = self.root / "research/api_agent/API_INTELLIGENCE_POLICY_v2.json"
        policy = json.loads(path.read_text())
        policy["lane_caps_usd"].pop("CN_INTERNAL_LONG_HORIZON_SCORER")
        path.write_text(json.dumps(policy))
        with patch("subprocess.run") as guard, patch("urllib.request.urlopen") as http:
            with self.assertRaisesRegex(RuntimeError, "CN_API_LANE_CAP_UNVERIFIED_NO_SPEND"):
                self.call()
            guard.assert_not_called()
            http.assert_not_called()

    def test_lane_budget_denial_fails_before_post_without_receipt(self):
        with patch("subprocess.run", side_effect=[
            subprocess.CompletedProcess([], 0),
            subprocess.CompletedProcess([], 1),
        ]) as guard, patch("urllib.request.urlopen") as http:
            with self.assertRaisesRegex(RuntimeError, "CN_API_LANE_BUDGET_BLOCKED"):
                self.call()
            self.assertEqual(guard.call_count, 2)
            http.assert_not_called()
            self.assertFalse(self.receipt().exists())

    def test_lane_budget_unavailable_fails_closed(self):
        with patch("subprocess.run", side_effect=[
            subprocess.CompletedProcess([], 0),
            OSError("lane validator unavailable"),
        ]) as guard, patch("urllib.request.urlopen") as http:
            with self.assertRaisesRegex(RuntimeError, "CN_API_LANE_BUDGET_CHECK_UNAVAILABLE"):
                self.call()
            self.assertEqual(guard.call_count, 2)
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

    def test_durable_reservation_requires_existing_github_actions_context(self):
        self.reservation_patcher.stop()
        with patch.dict(os.environ, {
                "OPENAI_API_KEY": "fake-not-a-secret", "GH_TOKEN": "",
                "GITHUB_ACTIONS": "false", "GITHUB_REPOSITORY": cn.CN_REPOSITORY}, clear=False), \
             patch("subprocess.run", return_value=subprocess.CompletedProcess([], 0)), \
             patch("urllib.request.urlopen") as http:
            with self.assertRaisesRegex(RuntimeError, "CN_API_DURABLE_RESERVATION_AUTH_REQUIRED_NO_SPEND"):
                self.call()
            http.assert_not_called()
            self.assertFalse(self.receipt().exists())

    def test_reservation_requires_remote_write_and_matching_main_readback(self):
        self.reservation_patcher.stop()
        with patch.dict(os.environ, {
                "GH_TOKEN": "offline-test-only", "GITHUB_ACTIONS": "true",
                "GITHUB_REPOSITORY": cn.CN_REPOSITORY}, clear=False):
            calls = []
            written = []
            def fake_api(path, *, fields=None, allow_not_found=False):
                calls.append((path, fields))
                if fields:
                    written.append(fields)
                    return {"content": {"sha": "test"}}
                return None
            with patch.object(cn, "_cn_gh_api", side_effect=fake_api), \
                 patch.object(cn, "_cn_gh_file", return_value=None):
                with self.assertRaisesRegex(RuntimeError, "CN_API_RESERVATION_MAIN_READBACK_FAILED_NO_SPEND"):
                    cn._reserve_cn_api_attempt_before_post(
                        self.root, ["frozen-A"], "a" * 64, "gpt-5.6-terra", 0.10)
            self.assertEqual(len(written), 1)
            self.assertEqual(written[0]["branch"], "main")
            self.assertTrue(any("contents/" in path for path, fields in calls if fields))

    def test_reservation_persists_counted_cost_and_verifies_main_bytes(self):
        import base64
        self.reservation_patcher.stop()
        stored = {}
        def fake_api(path, *, fields=None, allow_not_found=False):
            if fields is not None:
                self.assertEqual(fields["branch"], "main")
                stored["file_path"] = path
                stored["body"] = base64.b64decode(fields["content"])
                return {"commit": {"sha": "test"}} 
            if path == f"contents/{cn.CN_RESERVATION_ROOT}?ref=main":
                return None  # no historical reservations before this PUT
            if "contents/" in path and path.endswith("?ref=main"):
                return {"encoding": "base64",
                        "content": base64.b64encode(stored["body"]).decode()}
            return None
        with patch.dict(os.environ, {
                "GH_TOKEN": "offline-test-only", "GITHUB_ACTIONS": "true",
                "GITHUB_REPOSITORY": cn.CN_REPOSITORY}, clear=False), \
             patch.object(cn, "_cn_gh_api", side_effect=fake_api):
            cn._reserve_cn_api_attempt_before_post(
                self.root, ["frozen-A"], "a" * 64, "gpt-5.6-terra", 0.10)
        row = json.loads(stored["body"])
        self.assertEqual(row["contract"], "CN_PAID_API_PREPOST_RESERVATION_v1")
        self.assertEqual(row["estimated_cost_usd"], 0.10)
        self.assertTrue(type(row["created_unix"]) is int and row["created_unix"] > 0)
        self.assertTrue(row["no_automatic_paid_retry"])
        self.assertEqual(row["claim_ids"], ["frozen-A"])

    def test_reservation_rejects_invalid_max_cost_before_github(self):
        self.reservation_patcher.stop()
        with patch.dict(os.environ, {
                "GH_TOKEN": "offline-test-only", "GITHUB_ACTIONS": "true",
                "GITHUB_REPOSITORY": cn.CN_REPOSITORY}, clear=False), \
             patch.object(cn, "_cn_gh_api") as gh:
            with self.assertRaisesRegex(RuntimeError, "CN_API_DURABLE_RESERVATION_COST_INVALID"):
                cn._reserve_cn_api_attempt_before_post(
                    self.root, ["frozen-A"], "a" * 64, "gpt-5.6-terra", float("nan"))
            gh.assert_not_called()

    def test_unresolved_previous_reservation_blocks_paid_retry(self):
        self.reservation_patcher.stop()
        old_digest = "b" * 64
        old_path = f"{cn.CN_RESERVATION_ROOT}/{old_digest}.json"
        previous = {"contract": "CN_PAID_API_PREPOST_RESERVATION_v1",
                    "task": "CN_INTERNAL_LONG_HORIZON_SCORER",
                    "claim_ids": ["prior-A"],
                    "receipt_path": "research/api_agent/outputs/cn_internal_precision/" + ("c" * 64) + "/receipt.json"}
        with patch.dict(os.environ, {
                "GH_TOKEN": "offline-test-only", "GITHUB_ACTIONS": "true",
                "GITHUB_REPOSITORY": cn.CN_REPOSITORY}, clear=False), \
             patch.object(cn, "_cn_gh_api", return_value=[{
                 "name": old_digest + ".json", "path": old_path, "type": "file"}]), \
             patch.object(cn, "_cn_gh_file", side_effect=[
                 cn.canonical_bytes(previous), None]) as source:
            with self.assertRaisesRegex(RuntimeError, "CN_API_PREVIOUS_UNRECONCILED_PAID_ATTEMPT"):
                cn._reserve_cn_api_attempt_before_post(
                    self.root, ["new-B"], "a" * 64, "gpt-5.6-terra", 0.10)
            self.assertEqual(source.call_count, 2)

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
            self.assertEqual(guard.call_count, 2, "both the global and task-specific gates must run")
            monthly_command = guard.call_args_list[0].args[0]
            lane_command = guard.call_args_list[1].args[0]
            self.assertIn("check_monthly_cost_guard.py", " ".join(monthly_command))
            self.assertIn("--pending-ledger-root", monthly_command)
            self.assertIn("--reserve-usd", monthly_command)
            self.assertIn("check_api_lane_budget.py", " ".join(lane_command))
            self.assertEqual(lane_command[lane_command.index("--task") + 1], "CN_INTERNAL_LONG_HORIZON_SCORER")
            self.assertEqual(lane_command[lane_command.index("--cap-usd") + 1], "1")
            self.assertIn("--reserve-usd", lane_command)
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

    def test_duplicate_model_rows_cannot_reduce_pending_count_or_double_score(self):
        one = json.loads(self.good["output_text"])["scores"][0]
        duplicated = {**self.good, "output_text": json.dumps({"scores": [one, one]})}
        with patch("subprocess.run", return_value=subprocess.CompletedProcess([], 0)), \
             patch("urllib.request.urlopen", return_value=Response(duplicated)) as paid:
            with self.assertRaisesRegex(RuntimeError, "INVALID_STRUCTURED_OUTPUT"):
                self.call()
            receipt = json.loads(self.receipt().read_text())
            self.assertEqual(receipt["status"], "API_OUTPUT_INVALID")
            self.assertEqual(receipt["claim_ids"], [self.claims[0]["claim_id"]])
            with self.assertRaisesRegex(RuntimeError, "COHORT_ALREADY_ATTEMPTED"):
                self.call()
            paid.assert_called_once()

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
