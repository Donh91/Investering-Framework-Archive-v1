"""Review-only fail-closed S1 release snapshot classifier. Never authorizes release."""
from __future__ import annotations
import re

SHA40 = re.compile(r"[0-9a-f]{40}\Z")

def classify(snapshot: dict) -> dict:
    """Classify evidence without claiming identity, GitHub rights or merge consent."""
    def block(reason):
        return {"status": "BLOCKED", "reason": reason, "release_authorized": False}
    if not isinstance(snapshot, dict):
        return block("INVALID_SNAPSHOT")
    for key in ("head", "main", "review_head", "owner_head", "ci_head"):
        if not isinstance(snapshot.get(key), str) or not SHA40.fullmatch(snapshot[key]):
            return block("INVALID_OR_MISSING_SHA_" + key.upper())
    if len({snapshot[k] for k in ("head", "review_head", "owner_head", "ci_head")}) != 1:
        return block("STALE_HEAD_BINDING")
    if snapshot.get("owner_authenticated") is not True:
        return block("OWNER_MANDATE_UNVERIFIED")
    if snapshot.get("effective_write") is not True:
        return block("EFFECTIVE_WRITE_UNVERIFIED")
    if snapshot.get("one_editor_lease") is not True:
        return block("EDITOR_LEASE_UNVERIFIED")
    if snapshot.get("rules_verified") is not True:
        return block("ENFORCED_RULES_UNKNOWN")
    if snapshot.get("native_reviews_satisfied") is not True:
        return block("NATIVE_REVIEW_GATE_UNSATISFIED")
    if snapshot.get("source_and_science_satisfied") is not True:
        return block("SOURCE_SCIENCE_UNVERIFIED")
    if snapshot.get("high_impact") is True and snapshot.get("independent_custody") is not True:
        return block("HIGH_IMPACT_CUSTODY_UNATTESTED")
    if snapshot.get("remote_write_state") != "CONFIRMED":
        return block("PARTIAL_OR_UNKNOWN_REMOTE_WRITE")
    if snapshot.get("main_unchanged") is not True:
        return block("MAIN_MOVED_REVALIDATE")
    required = snapshot.get("required_tests")
    executed = snapshot.get("executed_tests")
    if not isinstance(required, list) or not required or len(set(required)) != len(required):
        return block("REQUIRED_TEST_MANIFEST_UNVERIFIED")
    if not isinstance(executed, list) or not set(required).issubset(set(executed)):
        return block("RELEASE_CI_NOT_EXECUTED")
    if snapshot.get("ci_pr_event") is not True or snapshot.get("ci_success") is not True:
        return block("EXACT_HEAD_PR_CI_UNVERIFIED")
    return {"status": "EVIDENCE_COMPLETE_RECHECK_NATIVE", "reason": "ADVISORY_ONLY_NOT_MERGE_CONSENT", "release_authorized": False}
