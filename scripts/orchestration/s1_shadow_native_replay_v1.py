"""Read-only S1 historical-evidence replay. Never authenticates its own inputs.

Accepts snapshots fetched by an authenticated external reader. Every result is
non-authoritative, even if its input claims to be native. No network, disk
writes, leases, releases, payments, scheduling, or production decisions.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from typing import Any

_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def _sha(value: Any) -> bool:
    return isinstance(value, str) and _SHA40.fullmatch(value) is not None


def _stable_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def _result(identity: str, stage: str, trigger: str, fingerprint: str | None) -> dict[str, Any]:
    return {"identity": identity, "stage": stage, "next_trigger": trigger,
            "fingerprint": fingerprint, "source_authenticated": False,
            "release_authorized": False, "s1_merge_credit": False,
            "production_verified": False, "side_effects": False}


def classify_snapshot(row: Any) -> dict[str, Any]:
    """Evaluate supplied data, not underlying GitHub authenticity.

    `native_main_contains_merge` and `consumer_verified` booleans are purposely
    ignored: no actor may authorize closure by passing self-reported flags.
    A merged original requires authenticated independent main/tree readback;
    natural production requires a separately authenticated consumer event.
    """
    if not isinstance(row, dict):
        return _result("UNKNOWN", "INVALID_INPUT", "VALID_OBJECT_REQUIRED", None)
    repo, number = row.get("repo"), row.get("original_pr")
    if not (isinstance(repo, str) and _REPO.fullmatch(repo)
            and type(number) is int and number > 0):
        return _result("UNKNOWN", "INVALID_INPUT", "VALID_ORIGINAL_ID_REQUIRED", None)
    identity = f"{repo}#{number}"
    # Fingerprint all material native gate deltas, never only the code HEAD.
    # A mergeability/review/rules/lease/source change must reactivate a case.
    fields = ("repo", "original_pr", "head_sha", "base_sha", "main_sha",
              "state", "draft", "merged", "mergeable", "merge_sha",
              "required_pr_jobs", "changed_main_blobs", "natural_consumer",
              "review_state", "rule_census", "source_binding", "active_editor_lease")
    try:
        fingerprint = _stable_hash({k: row.get(k) for k in fields})
    except (TypeError, ValueError):
        return _result(identity, "INVALID_INPUT", "JSON_FINITE_INPUT_REQUIRED", None)
    if not _sha(row.get("head_sha")):
        return _result(identity, "MISSING_HEAD", "EXACT_NATIVE_HEAD", fingerprint)
    if row.get("state") not in {"open", "closed"} or type(row.get("merged")) is not bool:
        return _result(identity, "INVALID_INPUT", "CURRENT_NATIVE_PR_STATE", fingerprint)
    if row["state"] == "open":
        if row["merged"]:
            return _result(identity, "INCONSISTENT", "RECHECK_NATIVE_PR_STATE", fingerprint)
        if row.get("draft") is True:
            return _result(identity, "BLOCKED_DRAFT", "AUTHORITATIVE_NON_DRAFT_RELEASE_GATE", fingerprint)
        if row.get("mergeable") is False:
            return _result(identity, "BLOCKED_MERGEABILITY", "NEW_HEAD_OR_CONFLICT_FIX", fingerprint)
        return _result(identity, "OPEN_NEEDS_NATIVE_GATES", "FRESH_RULES_REVIEWS_CI_LEASE", fingerprint)
    if not row["merged"]:
        return _result(identity, "CLOSED_NOT_MERGED", "PROVE_SUPERSESSION_OR_TERMINAL_BLOCK", fingerprint)
    if not _sha(row.get("merge_sha")):
        return _result(identity, "MERGED_MISSING_SHA", "NATIVE_MERGE_SHA", fingerprint)
    jobs = row.get("required_pr_jobs")
    if not isinstance(jobs, list) or not jobs:
        return _result(identity, "MERGED_CI_NOT_PROVEN", "EXACT_HEAD_PR_EVENT_JOB_STEPS", fingerprint)
    for job in jobs:
        if (not isinstance(job, dict)
                or job.get("head") != row["head_sha"]
                or job.get("event") != "pull_request"
                or job.get("status") != "completed"
                or job.get("conclusion") != "success"
                or type(job.get("executed_test_steps")) is not int
                or job["executed_test_steps"] < 1):
            return _result(identity, "MERGED_CI_NOT_PROVEN", "EXACT_HEAD_PR_EVENT_JOB_STEPS", fingerprint)
    blobs = row.get("changed_main_blobs")
    if (not isinstance(blobs, list) or not blobs
            or any(not isinstance(b, dict) or not isinstance(b.get("path"), str)
                   or not b["path"] or not _sha(b.get("expected_sha"))
                   or b.get("actual_sha") != b["expected_sha"] for b in blobs)):
        return _result(identity, "MERGED_MAIN_NOT_PROVEN", "READ_BACK_CURRENT_MAIN_BLOBS", fingerprint)
    consumer = row.get("natural_consumer")
    if not isinstance(consumer, dict):
        return _result(identity, "POST_FIX_OBSERVATION_CANDIDATE", "NATURAL_PRODUCER_CONSUMER_EVENT", fingerprint)
    if (consumer.get("event") != "natural"
            or consumer.get("clock_eligible") is not True
            or not consumer.get("source_id")
            or consumer.get("source_id") != consumer.get("delivered_source_id")
            or not consumer.get("run_url") or not consumer.get("consumer_url")):
        return _result(identity, "PRODUCTION_EVIDENCE_MISMATCH", "RECHECK_NATURAL_SOURCE_CONSUMER", fingerprint)
    return _result(identity, "NATIVE_AUTHENTICATION_REQUIRED", "INDEPENDENT_AUTHENTICATED_CLOSURE_CHECK", fingerprint)


def replay(snapshots: Any) -> dict[str, Any]:
    if not isinstance(snapshots, list):
        raise ValueError("EXPECTED_SNAPSHOT_LIST")
    if len(snapshots) > 200:
        raise ValueError("BOUNDED_REPLAY_MAX_200")
    results = [classify_snapshot(row) for row in snapshots]
    keys = [r["identity"] for r in results if r["identity"] != "UNKNOWN"]
    counts = Counter(keys)
    return {"contract": "S1_NATIVE_SHADOW_REPLAY_v1", "authority": "NONE_SHADOW_ONLY",
            "input_count": len(snapshots), "distinct_originals": len(counts),
            "duplicate_originals": sorted(k for k, count in counts.items() if count > 1),
            "stage_counts": dict(sorted(Counter(r["stage"] for r in results).items())),
            "s1_verified_closures": 0, "s1_automatic_merge_credit": 0,
            "results": results}


def main() -> int:
    import sys
    raw = json.load(sys.stdin, parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))
    print(json.dumps(replay(raw), sort_keys=True, separators=(",", ":"), allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
