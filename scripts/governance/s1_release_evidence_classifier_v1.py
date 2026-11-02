"""Read-only evidence stage classifier for S1 post-merge observations."""

import re

_SHA40 = re.compile(r"^[0-9a-f]{40}$")


def _sha(value):
    return isinstance(value, str) and _SHA40.fullmatch(value) is not None


def classify_release_evidence(record):
    """Return an evidence level, never release or trading authorization.

    GitHub identities, URLs and source material must be verified by the caller.
    This code classifies supplied records, not their external authenticity.
    """
    if not isinstance(record, dict) or not _sha(record.get("original_head")):
        return {"stage": "INVALID_INPUT", "authorized": False}
    head = record["original_head"]
    jobs = record.get("required_pr_jobs")
    if not isinstance(jobs, list) or not jobs:
        return {"stage": "CI_NOT_PROVEN", "authorized": False}
    for job in jobs:
        if (not isinstance(job, dict)
                or job.get("head") != head
                or job.get("event") != "pull_request"
                or job.get("status") != "completed"
                or job.get("conclusion") != "success"
                or type(job.get("executed_test_steps")) is not int
                or job["executed_test_steps"] < 1):
            return {"stage": "CI_NOT_PROVEN", "authorized": False}
    if not _sha(record.get("merge_sha")) or not _sha(record.get("main_sha")):
        return {"stage": "CI_ONLY", "authorized": False}
    blobs = record.get("changed_main_blobs")
    if not isinstance(blobs, list) or not blobs:
        return {"stage": "MAIN_NOT_PROVEN", "authorized": False}
    for blob in blobs:
        if (not isinstance(blob, dict) or not blob.get("path")
                or not _sha(blob.get("expected_sha"))
                or blob.get("actual_sha") != blob["expected_sha"]):
            return {"stage": "MAIN_NOT_PROVEN", "authorized": False}
    natural = record.get("natural_consumer")
    if not isinstance(natural, dict):
        return {"stage": "MAIN_READBACK_SUPPLIED", "authorized": False}
    if (natural.get("event") != "natural"
            or not natural.get("run_url")
            or not natural.get("consumer_url")
            or not natural.get("source_id")
            or natural.get("source_id") != natural.get("delivered_source_id")
            or natural.get("clock_eligible") is not True):
        return {"stage": "PRODUCTION_NOT_PROVEN", "authorized": False}
    return {"stage": "PROD_EVIDENCE_SUPPLIED_NEEDS_AUTHENTICATION",
            "authorized": False, "externally_authenticated": False}
