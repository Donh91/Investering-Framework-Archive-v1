"""BUILD_v1 native original receipt / sandbox binding tests, no model API."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.api_agent import astra_build_admit_v1 as a
from scripts.api_agent import astra_build_receipt_v1 as r
from scripts.api_agent import astra_build_sandbox_v1 as sb
from scripts.research import owner_astra_mission_v1 as owner


class BuildReceiptTest(unittest.TestCase):
    def setUp(self):
        self.mid = "ASTRA-BUILD-M1-20261121-S1"
        self.scope = {
            "contract": a.SCOPE_CONTRACT, "mission_id": self.mid,
            "main_sha": "f"*40, "test_command_id":"M1",
            "allowlist":["tests/learning/**"],
            "source_files":{"tests/learning/new_test.py":None},
            "stage":1, "previous_repair":None}
        self.proposal = {
            "status":"BUILD","test_command_id":"M1","rationale":"source-based",
            "risks":[],"files":[{"path":"tests/learning/new_test.py",
                                   "action":"create","content":"def test_one():\n    assert True\n"}]}
        self.raw = a.canonical(self.proposal)
        self.original_admission = a.admit(self.raw,self.scope)
        self.manifest = {
            "contract":"ASTRA_MISSION_REQUEST_V1",
            "mission_id":self.mid,
            "release_main_sha":self.scope["main_sha"],
            "request_sha256":"a"*64,"bundle_sha256":"b"*64,
            "model":"gpt-6.2-astra","reasoning_effort":"max",
            "request_bytes":45000,"max_output_tokens":8192,
            "input_token_upper":65000,"worst_case_usd":4.5}
        self.paid = {
            "contract":"ASTRA_MISSION_RECEIPT_V1",
            "mission_id":self.mid,"work_id":self.mid,
            "release_main_sha":self.scope["main_sha"],
            "run_id":"123","request_sha256":"a"*64,"bundle_sha256":"b"*64,
            "status":"completed","incomplete_details":None,
            "no_retry":True,"research_only":True,"usage_valid":True,
            "model":"gpt-6.2-astra","reasoning_effort":"max",
            "provider_reasoning_effort":"max","provider_model":"gpt-6.2-astra","response_id":"resp_test1234",
            "output_sha256":a.digest(self.raw),"bytes":len(self.raw),
            "usage":{"input_tokens":40_000,"output_tokens":2_000},
            "estimated_upper_usd":2.5}
        tests=[{"returncode":0,"status":"PASS","completed_tests_observed":1},
               {"returncode":0,"status":"PASS","completed_tests_observed":1}]
        baseline=[dict(x) for x in tests]
        self.sandbox = {
            "contract":"ASTRA_BUILD_SANDBOX_RECEIPT_v1",
            "mission_id":self.mid,"main_sha":self.scope["main_sha"],
            "proposal_sha256":a.digest(self.raw),
            "admission_sha256":a.digest(a.canonical(self.original_admission)),
            "test_command_id":"M1", "network":"none","image":sb.IMAGE,
            "secrets":False,"paid_authority":False,"merge_authority":False,
            "status":"TEST_COMPLETION_UNATTESTED","tests":tests,
            "native_suite_baseline":baseline,"independent_completion_attested":False}

    def bind(self):
        return r.bind(raw_report=self.raw,source_manifest=self.manifest,
                      paid_receipt=self.paid,admitted=self.original_admission,
                      tested=self.sandbox,approved_scope=self.scope,
                      verified_current_run_id="123")

    def test_exact_binding_no_release_authority(self):
        result=self.bind()
        self.assertEqual(result["status"],"TEST_COMPLETION_HOLD")
        self.assertEqual(result["test_count"],2)
        self.assertFalse(result["all_fixed_tests_passed"])
        self.assertFalse(result["merge_authority"])
        self.assertFalse(result["paid_authority"])
        self.assertEqual(result["raw_model_response_sha256"],a.digest(self.raw))

    def test_actual_collector_to_build_receipt_binding(self):
        # A synthetic GET-only provider completion is passed through the real
        # owner collector, then the real BUILD binder, with NO paid POST.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            mission_dir = "06_RESEARCH_LAB/astra_missions/" + self.mid
            manifest = dict(self.manifest, mission_dir=mission_dir)
            claim = {
                "mission_id": self.mid, "response_id": "resp_test1234",
                "run_id": "123", "release_main_sha": self.scope["main_sha"],
                "request_sha256": manifest["request_sha256"],
                "bundle_sha256": manifest["bundle_sha256"],
                "owner_reserved_usd": 5.0,
                "claim_comment_id": 11, "trigger_comment_id": 12,
            }
            owner.core.write_once(out / "handle.json", claim)
            owner.core.write_once(out / "source_manifest.json", manifest)
            provider = {
                "id": "resp_test1234", "model": owner.MODEL,
                "reasoning": {"effort": "max"},
                "status": "completed", "incomplete_details": None,
                "max_output_tokens": manifest["max_output_tokens"],
                "output_text": self.raw.decode("utf-8"),
                "usage": {"input_tokens": 1200, "output_tokens": 800},
            }
            with mock.patch.object(owner.core, "required_env", return_value="fake_no_network"), \
                 mock.patch.object(owner.core, "http_json", return_value=provider) as api:
                self.assertEqual(owner.collect(out, sleep=lambda _: None), 0)
                api.assert_called_once()
                self.assertEqual(api.call_args.args[0], "GET")
            actual = json.loads((out / "receipt.json").read_text())
            self.assertEqual(actual["provider_reasoning_effort"], "max")
            self.assertEqual(actual["output_sha256"], a.digest(self.raw))
            self.manifest = manifest
            self.paid = actual
            self.assertEqual(self.bind()["status"], "TEST_COMPLETION_HOLD")

    def test_collector_absent_provider_effort_is_not_qualified(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            manifest = dict(self.manifest, mission_dir="06_RESEARCH_LAB/astra_missions/" + self.mid)
            owner.core.write_once(out / "source_manifest.json", manifest)
            owner.core.write_once(out / "handle.json", {
                "mission_id": self.mid, "response_id": "resp_test1234",
                "run_id": "123", "release_main_sha": self.scope["main_sha"],
                "request_sha256": manifest["request_sha256"], "bundle_sha256": manifest["bundle_sha256"],
                "owner_reserved_usd": 5.0, "claim_comment_id": 11, "trigger_comment_id": 12,
            })
            provider = {
                "id": "resp_test1234", "model": owner.MODEL,
                "status": "completed", "output_text": self.raw.decode("utf-8"),
                "usage": {"input_tokens": 1200, "output_tokens": 800},
            }
            with mock.patch.object(owner.core, "required_env", return_value="fake_no_network"), \
                 mock.patch.object(owner.core, "http_json", return_value=provider):
                self.assertEqual(owner.collect(out, sleep=lambda _: None), 3)
            actual = json.loads((out / "receipt.json").read_text())
            self.assertIsNone(actual["provider_reasoning_effort"])
            self.manifest = manifest
            self.paid = actual
            with self.assertRaisesRegex(r.ReceiptBlocked, "MODEL_EFFORT_BOND"):
                self.bind()

    def test_modified_source_manifest_rejected(self):
        self.manifest["bundle_sha256"]="c"*64
        with self.assertRaisesRegex(r.ReceiptBlocked,"REQUEST_BOND"):
            self.bind()

    def test_wrong_native_run_rejected(self):
        self.paid["run_id"]="124"
        with self.assertRaisesRegex(r.ReceiptBlocked,"NATIVE_RUN_BOND"):
            self.bind()

    def test_wrong_main_sha_rejected(self):
        self.paid["release_main_sha"]="0"*40
        with self.assertRaisesRegex(r.ReceiptBlocked,"MAIN_SHA"):
            self.bind()

    def test_partial_paid_response_rejected(self):
        self.paid["status"]="incomplete"
        with self.assertRaisesRegex(r.ReceiptBlocked,"PAID_RECEIPT_NOT_FINAL"):
            self.bind()

    def test_paid_cap_violation_rejected(self):
        self.paid["estimated_upper_usd"]=5.01
        with self.assertRaisesRegex(r.ReceiptBlocked,"PAID_CAP_USD5"):
            self.bind()

    def test_provider_model_or_reasoning_mismatch(self):
        self.paid["provider_reasoning_effort"]="high"
        with self.assertRaisesRegex(r.ReceiptBlocked,"MODEL_EFFORT_BOND"):
            self.bind()

    def test_provider_model_is_independently_checked(self):
        self.paid["provider_model"] = "gpt-6.2-sol"
        with self.assertRaisesRegex(r.ReceiptBlocked, "MODEL_EFFORT_BOND"):
            self.bind()
        self.paid["provider_model"] = "gpt-6.2-astra-2026-11-21"
        self.assertEqual(self.bind()["status"], "TEST_COMPLETION_HOLD")

    def test_raw_report_tampering_detected(self):
        self.raw+=b"x"
        with self.assertRaisesRegex(r.ReceiptBlocked,"RAW_REPORT_BOND"):
            self.bind()

    def test_sandbox_different_admission_hash(self):
        self.sandbox["admission_sha256"]="0"*64
        with self.assertRaisesRegex(r.ReceiptBlocked,"SANDBOX_BOND"):
            self.bind()

    def test_sandbox_network_changed_denied(self):
        self.sandbox["network"]="bridge"
        with self.assertRaisesRegex(r.ReceiptBlocked,"SANDBOX_BOND"):
            self.bind()

    def test_sandbox_test_fail_is_not_release(self):
        self.sandbox["status"]="TEST_FAILURE"
        self.sandbox["tests"][1]={"returncode":1,"status":"TEST_FAILURE","completed_tests_observed":0}
        self.assertEqual(self.bind()["status"],"TEST_FAILURE_OR_INCOMPLETE")

    def test_false_pass_claim_rejected(self):
        self.sandbox["status"]="PASS"
        self.sandbox["tests"][1]={"returncode":1,"status":"TEST_FAILURE","completed_tests_observed":0}
        with self.assertRaisesRegex(r.ReceiptBlocked,"FALSE_SANDBOX_SUCCESS"):
            self.bind()

    def test_false_green_without_independent_completion_denied(self):
        self.sandbox["status"]="PASS"
        with self.assertRaisesRegex(r.ReceiptBlocked,"FALSE_SANDBOX_SUCCESS"):
            self.bind()

    def test_forged_native_attestor_claim_denied(self):
        self.sandbox["independent_completion_attested"]=True
        with self.assertRaisesRegex(r.ReceiptBlocked,"UNREVIEWED_TEST_ATTESTOR"):
            self.bind()

    def test_suite_count_cannot_decrease_or_promote(self):
        self.sandbox["tests"][0]["completed_tests_observed"]=0
        self.sandbox["status"]="TEST_FAILURE"
        self.assertEqual(self.bind()["status"],"TEST_FAILURE_OR_INCOMPLETE")

    def test_incomplete_test_census_denied(self):
        self.sandbox["tests"].pop()
        with self.assertRaisesRegex(r.ReceiptBlocked,"TEST_CENSUS"):
            self.bind()

    def test_600kb_specific_scope(self):
        self.manifest["request_bytes"]=600001
        with self.assertRaisesRegex(r.ReceiptBlocked,"REQUEST_600KB"):
            self.bind()

    def test_unverified_input_upper(self):
        self.paid["usage"]["input_tokens"]=65001
        with self.assertRaisesRegex(r.ReceiptBlocked,"USAGE_BOUND"):
            self.bind()


if __name__ == "__main__":
    unittest.main()
