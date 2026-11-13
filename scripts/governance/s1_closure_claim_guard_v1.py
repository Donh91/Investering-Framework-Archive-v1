"""Read-only, untrusted-input S1 closure CLAIM guard (Task 3 research).

This is NOT a native GitHub authenticator, permission check, release gate,
scheduler, metrics producer or source of verified S1 success.
A structurally complete payload is ALWAYS still pending native verification.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

S1_TASK_ID = "6ae5fd466b48819187abc224ec0f1c5f"
_SHA = re.compile(r"^[a-f0-9]{40}$")


def _sha(value: object) -> bool:
    return isinstance(value, str) and bool(_SHA.fullmatch(value))


def _utc(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.astimezone(timezone.utc) if parsed.tzinfo else None
    except (ValueError, OverflowError):
        return None


_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_MERGE_STATE_SOURCES = {"GITHUB_REST", "GITHUB_GRAPHQL", "LOCAL_GIT_MERGE_TREE"}
# A scheduled run may start late, but not hours after its slot; S1 runs hourly.
_MAX_SCHEDULE_LAG_SECONDS = 3600


def _ic3_receipt_reasons(record: Mapping[str, Any], pr: Mapping[str, Any], ci: Mapping[str, Any]) -> list[str]:
    """IC-3 (Grok S1 pilot 2026-11-11; ChatGPT #1156 6816178550): receipt fields that make a
    scheduled S1 decision joinable and replayable. Strictly additive reasons: can only demote a
    candidate, never authenticate it. Supplied values stay untrusted until native readback."""
    out: list[str] = []
    sched = _utc(record.get("scheduled_for_utc"))
    start = _utc(record.get("task_started_at"))
    if sched is None:
        out.append("MISSING_SCHEDULED_FOR_UTC")
    elif start is not None and start < sched:
        out.append("TASK_STARTED_BEFORE_SCHEDULE")
    elif start is not None and (start - sched).total_seconds() > _MAX_SCHEDULE_LAG_SECONDS:
        out.append("TASK_START_NOT_BOUND_TO_SCHEDULE")
    provenance_source = record.get("task_provenance_source")
    if type(provenance_source) is not str or provenance_source not in {"AUTOMATIONS_RUN_DETAILS", "SELF_ATTESTED"}:
        out.append("TASK_PROVENANCE_SOURCE_NOT_DECLARED")
    lease = record.get("writer_lease")
    lease = lease if isinstance(lease, Mapping) else {}
    if lease.get("active") is not False or not isinstance(lease.get("ref"), str) or not lease["ref"].strip():
        out.append("WRITER_LEASE_STATE_NOT_SUPPLIED")
    msc = record.get("merge_state_check")
    msc = msc if isinstance(msc, Mapping) else {}
    merge_source = msc.get("source")
    checked = _utc(msc.get("checked_at_utc"))
    if (type(merge_source) is not str or merge_source not in _MERGE_STATE_SOURCES
            or checked is None
            or msc.get("head_sha") != pr.get("head_sha")):
        out.append("MERGE_STATE_SOURCE_NOT_BOUND")
    else:
        # The merge-state check must be fresh evidence from THIS run, taken before the merge.
        merged = _utc(pr.get("merged_at"))
        if start is None or merged is None or not (start <= checked <= merged):
            out.append("MERGE_STATE_CHECK_STALE_OR_AFTER_MERGE")
    cls = record.get("classifier")
    cls = cls if isinstance(cls, Mapping) else {}
    if not (_sha(cls.get("blob_sha")) and isinstance(cls.get("disposition"), str)
            and isinstance(cls.get("output_sha256"), str) and _SHA256.fullmatch(cls["output_sha256"])):
        out.append("CLASSIFIER_IO_NOT_BOUND")
    ids = ci.get("executed_test_ids")
    if (not isinstance(ids, list) or not ids or any(type(t) is not str or not t.strip() for t in ids)
            or len(set(ids)) != len(ids)):
        out.append("EXECUTED_TEST_IDS_NOT_SUPPLIED")
    elif type(ci.get("executed_test_count")) is not int or len(ids) != ci["executed_test_count"]:
        # A partial or inflated test-ID list cannot stand in for the claimed count.
        # This is structural only; native CI provenance still needs independent readback.
        out.append("EXECUTED_TEST_IDS_COUNT_MISMATCH")
    if not isinstance(pr.get("merged_by"), str) or not pr["merged_by"].strip():
        out.append("MERGE_ACTOR_NOT_SUPPLIED")
    return out


def inspect_claim(record: Mapping[str, Any]) -> dict[str, Any]:
    """Check untrusted reported evidence for obvious false-positive claims.

    The result can NEVER upgrade supplied JSON to authenticated S1 execution.
    Exact GitHub/task native readback by the existing owner is still required.
    """
    if not isinstance(record, Mapping):
        raise ValueError("Expected a JSON object")

    case_type = record.get("case_type")
    if isinstance(case_type, str) and case_type in {"research_only", "partial_publication", "no_eligible_case"}:
        return {
            "classification": {
                "research_only": "ADVISORY_RESEARCH_ONLY",
                "partial_publication": "PARTIAL_PUBLICATION_NOT_COMPLETION",
                "no_eligible_case": "NO_ELIGIBLE_CASE_OBSERVED",
            }[case_type],
            "candidate_for_native_check": False,
            "s1_own_merged_verified": False,
            "full_autonomy_verified": False,
            "prod_verified": False,
            "eligible_denominator": "UNKNOWN",
            "reasons": ["Non-closure inputs are not autonomous outcomes"],
            "native_verification_required": True,
        }

    reasons: list[str] = []
    if case_type != "original_merge":
        reasons.append("CASE_TYPE_NOT_ORIGINAL_MERGE")
    if record.get("origin") != "natural_scheduled_s1":
        reasons.append("NOT_NATURALLY_SCHEDULED_S1_ORIGIN")
    if record.get("task_id") != S1_TASK_ID:
        reasons.append("WRONG_OR_MISSING_EXISTING_TASK_ID")
    if not isinstance(record.get("task_run_id"), str) or not record["task_run_id"].strip():
        reasons.append("MISSING_SAVED_TASK_RUN_ID")

    pr = record.get("pr")
    pr = pr if isinstance(pr, Mapping) else {}
    if not isinstance(pr.get("number"), int) or isinstance(pr.get("number"), bool) or pr["number"] < 1:
        reasons.append("INVALID_ORIGINAL_PR_NUMBER")
    if pr.get("original") is not True or pr.get("merged") is not True:
        reasons.append("ORIGINAL_MERGED_STATE_NOT_SUPPLIED")
    if not _sha(pr.get("head_sha")) or not _sha(pr.get("merge_sha")):
        reasons.append("MISSING_EXACT_NATIVE_SHA")
    if pr.get("merge_expected_head_sha") != pr.get("head_sha"):
        reasons.append("EXPECTED_HEAD_NOT_BOUND")
    if pr.get("main_blob_readback") is not True:
        reasons.append("MAIN_BLOB_READBACK_NOT_SUPPLIED")
    if pr.get("review_rules_checked") is not True:
        reasons.append("REVIEW_RULES_CHECK_NOT_SUPPLIED")

    ci = record.get("ci")
    ci = ci if isinstance(ci, Mapping) else {}
    if (ci.get("event") != "pull_request"
            or ci.get("head_sha") != pr.get("head_sha")
            or ci.get("conclusion") != "success"
            or not isinstance(ci.get("executed_test_count"), int)
            or isinstance(ci.get("executed_test_count"), bool)
            or ci.get("executed_test_count", 0) < 1):
        reasons.append("EXACT_HEAD_SUBSTANTIVE_PR_CI_NOT_SUPPLIED")

    task_start = _utc(record.get("task_started_at"))
    task_end = _utc(record.get("task_completed_at"))
    merge_time = _utc(pr.get("merged_at"))
    if not (task_start and merge_time and task_end and task_start <= merge_time <= task_end):
        reasons.append("NATIVE_MERGE_TIME_NOT_WITHIN_SCHEDULED_RUN")
    reasons.extend(_ic3_receipt_reasons(record, pr, ci))

    # A complete shape is a candidate ONLY, never native authority.
    candidate = not reasons
    return {
        "classification": (
            "NATIVE_PROVENANCE_READBACK_REQUIRED" if candidate
            else "UNSUPPORTED_S1_OWN_CLOSURE_CLAIM"
        ),
        "candidate_for_native_check": candidate,
        "s1_own_merged_verified": False,
        "full_autonomy_verified": False,
        "prod_verified": False,
        "eligible_denominator": "UNKNOWN",
        "reasons": reasons,
        "native_verification_required": True,
        "required_external_checks": [
            "authentic scheduled task run and invocation provenance",
            "native original PR identity/HEAD, real review policy and CI job steps",
            "native merge expected-head invocation, actor, main and blob readback",
            "for delegated execution: independently authenticated request/ACK/job/result/S1-consumption; for direct: actual natural scheduled tool provenance",
            "separate natural producer/consumer evidence for PROD_VERIFIED",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="S1 untrusted claim guard, read only")
    parser.add_argument("input", type=Path, help="Untrusted JSON object, no private data")
    args = parser.parse_args()
    result = inspect_claim(json.loads(args.input.read_text(encoding="utf-8")))
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
