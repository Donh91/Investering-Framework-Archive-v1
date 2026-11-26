"""Offline mission-specific BUILD cost constraints, including attempted bypasses."""
import unittest
from unittest import mock
from scripts.api_agent import astra_build_cost_v1 as c


class BuildCostTest(unittest.TestCase):
    def quote(self, mission="M1", stage=1, **other):
        kwargs=dict(work_id=f"ASTRA-BUILD-{mission}-20261121-S{stage}",
                    mission=mission, stage=stage, model=c.MODEL,
                    reasoning_effort=c.EFFORT, request_bytes=30_000,
                    max_output_tokens=10_000,
                    prior=(None if stage == 1 else {
                        "work_id": f"ASTRA-BUILD-{mission}-20261121-S1",
                        "stage": 1, "status": "VERIFIED_SANDBOX_TEST_FAILURE",
                        "sandbox_receipt_sha256": "a" * 64,
                        "native_run_id": 123, "attempt_terminal": True}))
        kwargs.update(other)
        return c.quote(**kwargs)

    def assert_hold(self, reason, **kwargs):
        with self.assertRaisesRegex(c.BudgetHold, reason):
            self.quote(**kwargs)

    def test_stage_one_is_preflight_only(self):
        with mock.patch.object(c,"estimate_cost",return_value=4.8):
            x=self.quote()
        self.assertFalse(x["paid_post_permitted"])
        self.assertFalse(x["retry_authorized"])
        self.assertTrue(x["independent_global_guard_required"])
        self.assertEqual(x["hard_request_cap_usd"], 5)
        self.assertEqual(x["program_max_usd"], 30)
        self.assertEqual(x["protected_build_reserve_usd"], 10)

    def test_stage_two_only_verified_native_sandbox_failure(self):
        with mock.patch.object(c,"estimate_cost",return_value=4.2):
            a=self.quote(stage=2)
        self.assertTrue(a["stage_two_requires_native_failed_sandbox"])
        other=dict(work_id="ASTRA-BUILD-M1-20261121-S1",stage=1,status="COMPLETED",
                   sandbox_receipt_sha256="a"*64,native_run_id=123,attempt_terminal=True)
        self.assert_hold("PRIOR_FAILED_NATIVE_SANDBOX_REQUIRED",stage=2,prior=other)

    def test_stage_two_no_ambiguous_paid_retry(self):
        x=dict(work_id="ASTRA-BUILD-M1-20261121-S1",stage=1,
               status="VERIFIED_SANDBOX_TEST_FAILURE",
               sandbox_receipt_sha256="b"*64,
               native_run_id=123,attempt_terminal=False)
        self.assert_hold("PRIOR_FAILED_NATIVE_SANDBOX_REQUIRED",stage=2,prior=x)

    def test_quote_cannot_overrun_request_cap(self):
        with mock.patch.object(c,"estimate_cost",return_value=5.000001):
            self.assert_hold("STAGE_OVER_USD5")
        with mock.patch.object(c,"estimate_cost",return_value=5.0):
            self.assertEqual(self.quote()["worst_case_usd"],5.0)

    def test_600kb_is_size_ceiling_not_spend_permission(self):
        with mock.patch.object(c,"estimate_cost",return_value=20.0):
            self.assert_hold("STAGE_OVER_USD5",request_bytes=600_000)
        with mock.patch.object(c,"estimate_cost",return_value=1.0) as cost:
            self.quote(request_bytes=600_000)
            self.assertEqual(cost.call_args.args[1],620_000)
        self.assert_hold("INPUT_600KB",request_bytes=600_001)

    def test_bad_model_effort_and_stage(self):
        self.assert_hold("MODEL_OR_EFFORT",model="gpt-6.1-sol")
        self.assert_hold("MODEL_OR_EFFORT",reasoning_effort="high")
        self.assert_hold("BUILD_STAGE",stage=3)
        self.assert_hold("BUILD_STAGE",stage=True)
        self.assert_hold("STAGE_WORK_ID",work_id="ASTRA-BUILD-M3-20261121-S1")

    def test_bad_prior_shape(self):
        self.assert_hold("REPAIR_EVIDENCE_MISSING|PRIOR_SCHEMA",stage=2,prior={"status":"UNKNOWN"})

    def test_build_reservation_at_max_30(self):
        rows=[]
        for m in ("M1","M2","M3"):
            for stage in (1,2):
                rows.append({"work_id":f"ASTRA-BUILD-{m}-20261121-S{stage}",
                             "upper_usd":5.0,"status":"OWNER_RESERVED_PREHTTP"})
        x=c.validate_program_reservations(rows)
        self.assertEqual(x["current_reserved_upper_usd"],30)
        self.assertFalse(x["paid_authority"])
        rows[0]["upper_usd"]=5.01
        with self.assertRaises(c.BudgetHold):
            c.validate_program_reservations(rows)

    def test_duplicate_reservation_rejected(self):
        x={"work_id":"ASTRA-BUILD-M1-20261121-S1","upper_usd":5,"status":"OWNER_RESERVED_PREHTTP"}
        with self.assertRaisesRegex(c.BudgetHold,"BUILD_WORK_ID"):
            c.validate_program_reservations([x,x])

    def test_not_a_paid_trigger(self):
        self.assertFalse(c.validate_program_reservations([])["paid_authority"])
        with self.assertRaises(c.BudgetHold):
            c.validate_program_reservations([{
                "work_id":"ASTRA-BUILD-M1-20261121-S1",
                "upper_usd":5,"status":"SETTLED_AND_RETRYABLE"}])


if __name__ == "__main__":
    unittest.main()
