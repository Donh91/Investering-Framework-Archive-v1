import unittest
from copy import deepcopy
from scripts.api_agent.model_routing_shadow_audit_v1 import policy_diagnostics, receipt_census


def row(**changes):
    r = dict(contract="API_AGENT_RECEIPT_v3", task="T", model="m", reasoning_effort="high",
             response_ids=["r1"], response_id="r1", attempt_count=1, output_hash="a" * 64,
             input_tokens=10, output_tokens=2, created_unix=100, estimated_cost_usd=0.2, status="PASS")
    r.update(changes)
    return r


class ShadowAuditTests(unittest.TestCase):
    def test_scope_drift_is_not_runtime_failure(self):
        r = dict(contract="CAPABILITY_ROUTING_POLICY_v1", models={"old": {}})
        t = dict(contract="API_TASK_REGISTRY_v1", tasks={"RESEARCH_LAB_SOL_ANALYSIS": {"model": "old"}, "X": {"model": "other"}})
        s = dict(contract="SOL_MAX_SHARED_MODEL_POLICY_V1", required_new_max_model="new")
        x = policy_diagnostics(r, t, s)
        self.assertEqual(x["registry_models_missing_from_router"], [["X", "other"]])
        self.assertFalse(x["new_sol_max_listed_in_general_router"])
        self.assertFalse(any(x["authority"].values()))
        self.assertRaises(ValueError, policy_diagnostics, {}, t, s)

    def test_cost_retains_failed_attempts_without_claiming_resolution(self):
        failed = row(response_id="r2", response_ids=["r2"], status="API_OUTPUT_INVALID", estimated_cost_usd=0.1)
        x = receipt_census([row(), failed])["cohorts"][0]
        self.assertEqual(x["recorded_estimate_usd"], "0.3")
        self.assertEqual(x["estimate_per_gateway_pass_usd"], "0.3")
        self.assertEqual(x["receipt_count"], 2)
        self.assertIsNone(x["cost_per_independently_resolved_work_usd"])

    def test_duplicate_and_overlap(self):
        self.assertEqual(receipt_census([row(), deepcopy(row())])["duplicate_rows"], 1)
        for other in (row(estimated_cost_usd=0.3), row(response_ids=["r1", "r2"], response_id="r2", attempt_count=2)):
            with self.subTest(other=other):
                self.assertRaises(ValueError, receipt_census, [row(), other])

    def test_invalid_inputs_fail_closed(self):
        for changes in ({"estimated_cost_usd": v} for v in (float("nan"), float("inf"), -1, True, "0.1")):
            self.assertRaises(ValueError, receipt_census, [row(**changes)])
        for changes in ({"attempt_count": 2}, {"response_id": "wrong"}, {"output_hash": "bad"},
                        {"output_tokens": True}, {"status": "UNKNOWN"}, {"task": ""}):
            self.assertRaises(ValueError, receipt_census, [row(**changes)])

    def test_zero_pass_and_separate_efforts(self):
        x = receipt_census([row(status="COST_EXCEEDED"), row(response_id="r2", response_ids=["r2"], reasoning_effort="low")])
        self.assertEqual(len(x["cohorts"]), 2)
        self.assertIsNone(x["cohorts"][0]["estimate_per_gateway_pass_usd"])
        self.assertIsNone(x["routing_recommendation"])
        self.assertFalse(any(x["authority"].values()))


if __name__ == "__main__":
    unittest.main()
