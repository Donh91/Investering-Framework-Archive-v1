"""P0 discovery coverage reconciliation, owned by existing #1512/#1157/#1156.

Pure, bounded, read-only **supplied-snapshot** evaluator. The authenticated
caller, not this code, must prove source scope, native issue/PR state, issuer
identity, policy and follow-through. No GitHub access, new queue, scheduler,
private payload, dispatch, market or release authority.

CLI: python scripts/orchestration/cross_repo_owner_coverage_v1.py < public-snapshot.json
Public snapshots ONLY. Private repo names/issue text/source rows are rejected;
the separate restricted owners remain responsible for private reconciliation.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from typing import Any

PUBLIC = (
    "Donh91/Investering-Framework-Archive-v1",
    "Donh91/Eksperimenter-framework-",
    "Donh91/CycleNavigator-scores",
)
_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_KINDS = {"ISSUE", "PR", "RESEARCH", "SHADOW"}
_STATES = {"OPEN", "CLOSED", "MERGED", "PROPOSED", "INCUBATING",
           "WAITING_FOR_DATA", "WAITING_FOR_MAPPING", "MATURED_INCONCLUSIVE",
           "QUARANTINED", "BLOCKED", "REJECTED", "SUPERSEDED"}
_WAIT = {"INCUBATING", "WAITING_FOR_DATA", "WAITING_FOR_MAPPING",
         "MATURED_INCONCLUSIVE", "QUARANTINED", "BLOCKED"}
_DONE = {"CLOSED", "MERGED", "REJECTED", "SUPERSEDED"}
_OWNER = re.compile(r"^Donh91/[A-Za-z0-9_.-]+#([1-9][0-9]*)$")


def _fingerprint(row: dict[str, Any]) -> str:
    # No passive wall-clock field; an unchanged case stays quiet.
    columns = ("repo", "number", "kind", "state", "priority_hint",
               "owner_ref", "owner_decision", "owner_receipt_ref",
               "next_trigger", "admission_state", "original_pr",
               "source_clock_verified", "source_head_sha")
    data = {k: row.get(k) for k in columns}
    return hashlib.sha256(json.dumps(data, sort_keys=True, allow_nan=False,
                                     separators=(",", ":")).encode()).hexdigest()


def _safe_ref(row: dict[str, Any]) -> str | None:
    repo, number = row.get("repo"), row.get("number")
    if repo not in PUBLIC or type(number) is not int or number <= 0:
        return None
    return f"{repo}#{number}"


def _row_status(row: dict[str, Any]) -> tuple[str, str, str]:
    state, kind = row.get("state"), row.get("kind")
    if kind not in _KINDS or state not in _STATES:
        return "INVALID_SOURCE_STATE", "NONE", "VALID_ORIGINAL_STATE"
    owner = row.get("owner_ref")
    has_owner = isinstance(owner, str) and bool(_OWNER.fullmatch(owner))
    trigger = row.get("next_trigger")
    has_trigger = isinstance(trigger, str) and bool(trigger.strip())
    decision = row.get("owner_decision")
    receipt = row.get("owner_receipt_ref")
    if decision not in (None, "NOT_ASSESSED", "REJECTED", "DEDUPED",
                        "WAIT", "ADMITTED", "PROSPECTIVE"):
        return "INVALID_OWNER_DECISION", "NONE", "REVALIDATE_EXISTING_OWNER"
    if state in _DONE:
        return "TERMINAL_READBACK_REQUIRED", "OWNER_ONLY", "NATIVE_SOURCE_AND_OUTCOME_PROOF"
    if state in _WAIT or decision == "WAIT":
        if not has_trigger:
            return "WAIT_TRIGGER_UNSPECIFIED", "EXISTING_OWNER", "BOUNDED_TRIGGER_REQUIRED"
        return "WAIT_WITH_TRIGGER", "EXISTING_OWNER", trigger.strip()
    if decision in ("REJECTED", "DEDUPED"):
        return "OWNER_DISPOSITION_RECHECK", "EXISTING_OWNER", "AUTHENTICATE_OWNER_RECEIPT"
    if not has_owner:
        return "OWNER_UNRESOLVED", "STRATEGIST_ADVISORY", "EXISTING_OWNER_ASSIGNMENT"
    if decision in ("ADMITTED", "PROSPECTIVE"):
        # An untrusted receipt link never authenticates the owner or starts a job.
        if not isinstance(receipt, str) or not receipt.strip():
            return "ADMISSION_RECEIPT_MISSING", "EXISTING_OWNER", "NATIVE_OWNER_RECEIPT"
        if kind == "SHADOW":
            return "FORWARD_TEST_REVIEW_ONLY", "RESEARCH_SHADOW", "GOVERNED_SOURCE_AND_OUTCOME"
        if kind == "RESEARCH":
            return "RESEARCH_HANDOFF_REVIEW_ONLY", "STRATEGIST_ADVISORY", "NATIVE_OWNER_DISPOSITION"
        return "OWNER_EXECUTION_REVIEW_ONLY", "S1_ADVISORY", "NATIVE_CURRENT_RELEASE_GATES"
    if kind in ("SHADOW", "RESEARCH"):
        return "RESEARCH_REVIEW_NOT_DISPATCHED", "RESEARCH_SHADOW", "NOVEL_MATERIAL_EVIDENCE"
    return "TRACKED_NO_AUTO_DISPATCH", "EXISTING_OWNER", "MATERIAL_DELTA_OR_ELIGIBLE_ACTION"


def reconcile(packet: Any) -> dict[str, Any]:
    """Never issue a verified closure, task, priority, action or private claim."""
    if not isinstance(packet, dict) or packet.get("contract") != "CROSS_REPO_PUBLIC_SNAPSHOT_v1":
        raise ValueError("WRONG_PUBLIC_INPUT_CONTRACT")
    coverage, rows = packet.get("coverage"), packet.get("rows")
    if not isinstance(coverage, dict) or not isinstance(rows, list) or len(rows) > 500:
        raise ValueError("INVALID_OR_UNBOUNDED_INPUT")
    if set(coverage) != set(PUBLIC):
        raise ValueError("PUBLIC_SCOPE_EXACTLY_THREE_REPOS_REQUIRED")
    view = {}
    for repo in PUBLIC:
        entry = coverage[repo]
        if not isinstance(entry, dict) or entry.get("status") not in (
                "COMPLETE", "PARTIAL", "UNAVAILABLE", "NOT_CHECKED"):
            raise ValueError("INVALID_REPO_COVERAGE")
        sha = entry.get("main_sha")
        if entry["status"] in ("COMPLETE", "PARTIAL") and not (
                isinstance(sha, str) and _SHA40.fullmatch(sha)):
            raise ValueError("MISSING_SOURCE_MAIN_SHA")
        view[repo] = {"status": entry["status"],
                      "scope_claim_only_not_authenticated": True,
                      "source_main_sha": sha if entry["status"] in ("COMPLETE", "PARTIAL") else None}
    seen = set()
    out = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("INVALID_PUBLIC_SOURCE_ROW")
        # Reject restricted repo content BEFORE copying any fields into output.
        ref = _safe_ref(row)
        if ref is None:
            raise ValueError("RESTRICTED_OR_INVALID_REPOSITORY_ROW")
        if row.get("kind") not in _KINDS or row.get("state") not in _STATES:
            raise ValueError("INVALID_KIND_OR_STATE")
        if row.get("priority_hint") not in ("P0", "P1", "P2", "NONE"):
            raise ValueError("INVALID_PRIORITY_HINT")
        if view[row["repo"]]["status"] not in ("COMPLETE", "PARTIAL"):
            raise ValueError("ROW_FROM_UNCHECKED_REPOSITORY")
        if "body" in row or "private" in row or "payload" in row or "title" in row:
            raise ValueError("SOURCE_PAYLOAD_NOT_ALLOWED")
        if ref in seen:
            # A single original may appear as title P0 and label P0.
            # Dedupe rather than inflating the active denominator.
            out.append({"original": ref, "disposition": "DUPLICATE_SOURCE_REF",
                        "lane": "NONE", "next_trigger": "ORIGINAL_SOURCE_CHANGED",
                        "fingerprint": None, "authenticated": False,
                        "automatic_dispatch": False, "verified_closure": False})
            continue
        seen.add(ref)
        state, lane, trigger = _row_status(row)
        # Source head is optional for GitHub issues, mandatory if provided.
        sha = row.get("source_head_sha")
        if sha is not None and not (isinstance(sha, str) and _SHA40.fullmatch(sha)):
            state, lane, trigger = "INVALID_SOURCE_SHA", "NONE", "FRESH_NATIVE_SHA"
        try:
            fingerprint = _fingerprint(row)
        except (TypeError, ValueError):
            raise ValueError("NON_JSON_OR_NONFINITE_SOURCE_ROW") from None
        out.append({"original": ref, "disposition": state, "lane": lane,
                    "next_trigger": trigger, "priority_hint": row["priority_hint"],
                    "fingerprint": fingerprint, "authenticated": False,
                    "automatic_dispatch": False, "verified_closure": False})
    counts = Counter(r["disposition"] for r in out)
    return {"contract": "CROSS_REPO_OWNER_COVERAGE_SHADOW_v1",
            "authority": "READ_ONLY_ADVISORY_NO_SOURCE_AUTHENTICATION",
            "public_repos": view,
            "private_domain_coverage": "NOT_ASSESSED_PUBLIC_BOUNDARY",
            "vault_coverage": "INTENTIONALLY_OUT_OF_SCOPE",
            "public_scope_complete_claim_only": all(v["status"] == "COMPLETE" for v in view.values()),
            "fully_authenticated": False, "all_framework_P0_covered": False,
            "total_supplied_rows": len(rows), "distinct_originals": len(seen),
            "duplicate_input_count": counts["DUPLICATE_SOURCE_REF"],
            "p0_title_or_label_candidates": sum(
                r.get("priority_hint") == "P0" for r in out),
            "unresolved_owner_candidates": counts["OWNER_UNRESOLVED"],
            "accepted_handoff_verified": 0, "automatic_dispatch_count": 0,
            "s1_own_closure_count": 0,
            "disposition_counts": dict(sorted(counts.items())),
            "observations": out}


def main() -> int:
    import sys
    packet = json.load(sys.stdin, parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))
    print(json.dumps(reconcile(packet), sort_keys=True, separators=(",", ":"),
                     allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
