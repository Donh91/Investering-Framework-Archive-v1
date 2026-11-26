"""Pure binding between one native Astra response and a no-secret BUILD sandbox.

Does not download artifacts, call APIs, write Git, approve builds or create PRs.
Caller must authenticate same-run GitHub artifact provenance and first verify
the unique owner claim and receipt in an unprivileged separate job.
"""
from __future__ import annotations

from scripts.api_agent import astra_build_admit_v1 as admission
from scripts.api_agent import astra_build_cost_v1 as cost
from scripts.api_agent import astra_build_sandbox_v1 as sandbox

MODEL = "gpt-6.2-astra"
MAX_REPORT_BYTES = admission.MAX_RAW_JSON_BYTES
CONTRACT = "ASTRA_BUILD_EVIDENCE_BINDING_v1"

class ReceiptBlocked(admission.AdmissionBlocked):
    pass

def require(cond, reason):
    if not cond:
        raise ReceiptBlocked(reason)

def bind(*, raw_report: bytes, source_manifest: dict, paid_receipt: dict,
         admitted: dict, tested: dict, approved_scope: dict,
         verified_current_run_id: str):
    """Bind full-source report, original owner receipt, admission and tests.

    All caller-supplied objects must originate from separately authenticated
    native artifacts; no JSON text from the model is treated as an instruction.
    """
    require(type(raw_report) is bytes and 0 < len(raw_report) <= MAX_REPORT_BYTES,
            "RAW_REPORT_BYTES")
    admission.verify_scope(approved_scope)
    mission=approved_scope["mission_id"]
    require(type(verified_current_run_id) is str
            and verified_current_run_id.isdigit()
            and int(verified_current_run_id) > 0, "NATIVE_RUN_ID")
    require(type(source_manifest) is dict
            and type(paid_receipt) is dict
            and type(admitted) is dict
            and type(tested) is dict, "RECEIPT_SHAPE")
    require(source_manifest.get("mission_id") == mission
            and paid_receipt.get("mission_id") == mission
            and paid_receipt.get("work_id") == mission,
            "RECEIPT_MISSION")
    require(source_manifest.get("contract") == "ASTRA_MISSION_REQUEST_V1"
            and paid_receipt.get("contract") == "ASTRA_MISSION_RECEIPT_V1",
            "NATIVE_CONTRACT")
    require(source_manifest.get("release_main_sha") == approved_scope["main_sha"]
            and paid_receipt.get("release_main_sha") == approved_scope["main_sha"],
            "MAIN_SHA")
    require(str(paid_receipt.get("run_id")) == verified_current_run_id,
            "NATIVE_RUN_BOND")
    for field in ("request_sha256", "bundle_sha256"):
        require(isinstance(source_manifest.get(field), str)
                and admission.HEX64.fullmatch(source_manifest[field])
                and paid_receipt.get(field) == source_manifest[field],
                "REQUEST_BOND_"+field)
    require(paid_receipt.get("status") == "completed"
            and paid_receipt.get("incomplete_details") is None
            and paid_receipt.get("no_retry") is True
            and paid_receipt.get("research_only") is True
            and paid_receipt.get("usage_valid") is True,
            "PAID_RECEIPT_NOT_FINAL")
    require(source_manifest.get("model") == MODEL
            and source_manifest.get("reasoning_effort") == "max"
            and paid_receipt.get("model") == MODEL
            and paid_receipt.get("reasoning_effort") == "max"
            and paid_receipt.get("provider_reasoning_effort") == "max",
            "MODEL_EFFORT_BOND")
    require(type(source_manifest.get("request_bytes")) is int
            and 0 < source_manifest["request_bytes"] <= cost.MAX_REQUEST_BYTES,
            "REQUEST_600KB")
    require(type(source_manifest.get("max_output_tokens")) is int,
            "OUTPUT_TOKEN_LIMIT")
    require(paid_receipt.get("output_sha256") == admission.digest(raw_report)
            and paid_receipt.get("bytes") == len(raw_report),
            "RAW_REPORT_BOND")
    usage=paid_receipt.get("usage")
    require(type(usage) is dict
            and type(usage.get("input_tokens")) is int
            and type(usage.get("output_tokens")) is int
            and 0 <= usage["input_tokens"] <= source_manifest.get("input_token_upper", -1)
            and 0 <= usage["output_tokens"] <= source_manifest["max_output_tokens"],
            "USAGE_BOUND")
    quoted=source_manifest.get("worst_case_usd")
    charge=paid_receipt.get("estimated_upper_usd")
    require(type(quoted) in (int,float) and type(charge) in (int,float)
            and 0 <= charge <= quoted <= cost.MAX_STAGE_USD,
            "PAID_CAP_USD5")
    original = admission.admit(raw_report, approved_scope)
    require(admitted == original, "ADMISSION_RESULT_MISMATCH")
    require(tested.get("contract") == "ASTRA_BUILD_SANDBOX_RECEIPT_v1"
            and tested.get("mission_id") == mission
            and tested.get("main_sha") == approved_scope["main_sha"]
            and tested.get("proposal_sha256") == admission.digest(raw_report)
            and tested.get("admission_sha256") == admission.digest(admission.canonical(original))
            and tested.get("test_command_id") == approved_scope["test_command_id"]
            and tested.get("network") == "none"
            and tested.get("image") == sandbox.IMAGE
            and tested.get("secrets") is False
            and tested.get("paid_authority") is False
            and tested.get("merge_authority") is False,
            "SANDBOX_BOND")
    tests=tested.get("tests")
    baseline=tested.get("native_suite_baseline")
    expected_count=len(admission.TEST_COMMANDS[approved_scope["test_command_id"]])
    require(type(tests) is list and type(baseline) is list
            and len(tests) == len(baseline) == expected_count and expected_count > 0,
            "TEST_CENSUS")
    require(all(type(x) is dict and x.get("status") in ("PASS", "TEST_FAILURE")
                and type(x.get("returncode")) is int
                and type(x.get("completed_tests_observed")) is int
                and x["completed_tests_observed"] >= 0 for x in tests),
            "TEST_STATUSES")
    require(all(type(x) is dict and x.get("status") == "PASS"
                and x.get("returncode") == 0
                and type(x.get("completed_tests_observed")) is int
                and x["completed_tests_observed"] > 0 for x in baseline),
            "UNVERIFIED_BASELINE")
    # No trusted test-completion attestor exists in the pinned Python-only
    # image. Return an explicit HOLD even when the candidate shows normal CLI
    # output. This prevents exit(0) and forged stdout from becoming a PASS.
    require(tested.get("independent_completion_attested") is False,
            "UNREVIEWED_TEST_ATTESTOR")
    observed = all(x["status"] == "PASS" and x["returncode"] == 0
                   and x["completed_tests_observed"] >= baseline[i]["completed_tests_observed"]
                   for i, x in enumerate(tests))
    require(tested.get("status") == ("TEST_COMPLETION_UNATTESTED" if observed else "TEST_FAILURE"),
            "FALSE_SANDBOX_SUCCESS")
    status = "TEST_COMPLETION_HOLD" if observed else "TEST_FAILURE_OR_INCOMPLETE"
    return {"contract": CONTRACT, "status": status,
            "mission_id": mission, "stage": approved_scope["stage"],
            "release_main_sha": approved_scope["main_sha"],
            "native_paid_run_id": verified_current_run_id,
            "native_request_sha256": source_manifest["request_sha256"],
            "source_manifest_sha256": admission.digest(admission.canonical(source_manifest)),
            "raw_model_response_sha256": admission.digest(raw_report),
            "response_id": paid_receipt.get("response_id"),
            "model": MODEL, "effort": "max",
            "input_tokens": usage["input_tokens"],
            "output_tokens": usage["output_tokens"],
            "estimated_paid_usd": charge,
            "admission_sha256": admission.digest(admission.canonical(original)),
            "sandbox_receipt_sha256": admission.digest(admission.canonical(tested)),
            "fixed_test_id": approved_scope["test_command_id"],
            "test_count": len(tests), "all_fixed_tests_passed":
            status == "TESTED_PASS_REVIEW_REQUIRED",
            "body_and_coverage_attested_by_native_writer": False,
            "paid_authority": False, "merge_authority": False,
            "review_required": True}
