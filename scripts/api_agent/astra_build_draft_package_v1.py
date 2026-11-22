"""No-secret, no-write materialization of ONE review-only BUILD output draft.

The caller authenticates the original paid same-run receipt, source SHA,
owner event, trusted scope, and sandbox evidence first. This file only builds
a portable, bounded JSON artifact for a separate owner-authenticated GitHub
connector to create a DRAFT PR. It never creates/merges PRs or calls provider.
"""
from __future__ import annotations

import hashlib
from scripts.api_agent import astra_build_admit_v1 as admission

CONTRACT = "ASTRA_BUILD_DRAFT_PR_PACKAGE_v1"
ELIGIBLE = "PREFILTER_ELIGIBLE_DRAFT_PR_ONLY"
MAX_PACKAGE_BYTES = 800_000


class DraftPackageBlocked(admission.AdmissionBlocked):
    pass


def _require(condition, reason):
    if not condition:
        raise DraftPackageBlocked(reason)


def build(*, raw: bytes, scope: dict, verdict: dict) -> bytes:
    admission.verify_scope(scope)
    _require(type(verdict) is dict and verdict.get("contract") ==
             "ASTRA_BUILD_EVIDENCE_BINDING_v1" and verdict.get("status") == ELIGIBLE,
             "DRAFT_NOT_PREFILTER_ELIGIBLE")
    _require(verdict.get("mission_id") == scope["mission_id"]
             and verdict.get("release_main_sha") == scope["main_sha"]
             and verdict.get("fixed_test_id") == scope["test_command_id"],
             "DRAFT_MISSION_OR_MAIN_DRIFT")
    _require(verdict.get("raw_model_response_sha256") == admission.digest(raw),
             "DRAFT_REPORT_SHA_DRIFT")
    _require(verdict.get("paid_authority") is False
             and verdict.get("merge_authority") is False
             and verdict.get("review_required") is True
             and verdict.get("independent_native_pr_ci_pending") is True
             and verdict.get("output_eligibility") == "ONE_DRAFT_PR_NO_AUTOMERGE",
             "DRAFT_IMPROPER_AUTHORITY")
    receipt = admission.admit(raw, scope)
    _require(receipt["status"] == "ADMITTED_UNTRUSTED_CODE_TEST_REQUIRED"
             and verdict.get("admission_sha256") == admission.digest(admission.canonical(receipt)),
             "DRAFT_ADMISSION_DRIFT")
    source = admission.parse_untrusted(raw)
    rows = []
    hashes = {item["path"]: item for item in receipt["files"]}
    for item in source["files"]:
        expected = hashes[item["path"]]
        encoded = item["content"].encode("utf-8")
        _require(admission.digest(encoded) == expected["sha256"]
                 and expected["action"] == item["action"], "DRAFT_FILE_SHA_DRIFT")
        rows.append({
            "path": item["path"], "action": item["action"],
            "utf8_full_file": item["content"], "sha256": expected["sha256"],
            "bytes": expected["bytes"], "preimage_sha256": expected["preimage_sha256"]
        })
    _require(len(rows) and len(rows) == len(hashes), "DRAFT_FILES_MISSING")
    package = {
        "contract": CONTRACT, "status": "STAGED_FOR_ONE_DRAFT_PR",
        "mission_id": scope["mission_id"], "main_sha": scope["main_sha"],
        "model_report_sha256": admission.digest(raw),
        "binding_receipt_sha256": admission.digest(admission.canonical(verdict)),
        "admission_sha256": verdict["admission_sha256"],
        "test_command_id": scope["test_command_id"],
        "prefilter_status": verdict["status"],
        "source_files": scope["source_files"],
        "files": sorted(rows, key=lambda r: r["path"]),
        "total_source_bytes": receipt["total_content_bytes"],
        "review": {
            "pr_mode": "DRAFT_ONLY",
            "native_ci": "MUST_RUN_ON_EXACT_OUTPUT_PR_HEAD",
            "codex": "EXACT_HEAD_REVIEW_REQUIRED",
            "claude": "INDEPENDENT_HIGH_IMPACT_REVIEW_REQUIRED",
            "merge": "OWNER_PRESENT_ONLY",
        },
        "permissions": {
            "git_write_performed": False,
            "merge_performed": False,
            "live_trading": False,
            "paid_provider_action_performed": False
        }
    }
    data = admission.canonical(package) + b"\n"
    _require(len(data) <= MAX_PACKAGE_BYTES, "DRAFT_PACKAGE_TOO_LARGE")
    return data
