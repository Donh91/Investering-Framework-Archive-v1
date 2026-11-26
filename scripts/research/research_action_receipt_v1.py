"""Bounded owner-receipt intake for the existing WIRE-0 pilot.

An owner attestation is evidence input, not independent scientific adjudication,
a merge authorization, or proof that calibration was applied. No workflow actor
is admitted until its run provenance has an independently configured verifier.
"""
import json
import re
from datetime import datetime
from urllib.request import Request, urlopen

REPO = "Donh91/Investering-Framework-Archive-v1"
OWNER_ID = 160772984
OWNER_LOGIN = "Donh91"
ISSUE = 1516
ACTION_ID = "13d1b85e8767f77d95a3"
SOURCE_FP = "4c1b652a80e791aa2a4efc83aff2bdb347889a8d5359685af78117ae2c0dd36c"
CONTRACT = "RESEARCH_ACTION_RECEIPT_v1"
SHA = re.compile(r"[0-9a-f]{40}")
MAX_PAGES = 20
MAX_RESPONSE = 8 * 1024 * 1024

def _id(value):
    return type(value) is int and value > 0

def _sha(value):
    return isinstance(value, str) and SHA.fullmatch(value) is not None

def _timestamp(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return None

def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result

def receipt_from_comments(comments, action_id):
    """Accept exactly one distinct, unchanged owner receipt; conflicting claims fail closed."""
    if not isinstance(comments, list):
        return None
    candidates = []
    for comment in comments:
        if not isinstance(comment, dict):
            continue
        user = comment.get("user")
        created = _timestamp(comment.get("created_at"))
        updated = _timestamp(comment.get("updated_at"))
        if (not isinstance(user, dict) or user.get("id") != OWNER_ID
                or user.get("login") != OWNER_LOGIN
                or comment.get("author_association") != "OWNER"
                or comment.get("performed_via_github_app") is not None
                or created is None or updated != created
                or not _id(comment.get("id"))):
            continue
        body = comment.get("body")
        if not isinstance(body, str) or len(body) > 16000:
            continue
        match = re.fullmatch(r"\s*RESEARCH_ACTION_RECEIPT_v1\s*\n```json\s*\n(.*?)\n```\s*", body, re.S)
        if not match:
            continue
        try:
            data = json.loads(match.group(1), object_pairs_hook=_unique)
        except (ValueError, TypeError):
            continue
        if not isinstance(data, dict) or data.get("contract") != CONTRACT or data.get("action_id") != action_id:
            continue
        # A malformed claim for this action is ambiguity, not permission to accept a different claim.
        readback = data.get("readback")
        outcome = data.get("outcome")
        if (not _id(data.get("pr")) or not _sha(data.get("merge_sha"))
                or not _id(data.get("native_run_id")) or not _id(data.get("review_receipt_id"))
                or not isinstance(readback, dict) or readback.get("merge_sha") != data["merge_sha"]
                or readback.get("changed_blobs_match") is not True
                or not isinstance(outcome, dict) or outcome.get("status") not in ("VERIFIED", "FALSIFIED", "BLOCKED")
                or not isinstance(outcome.get("reason"), str) or not outcome["reason"].strip()):
            return None
        candidates.append((comment["id"], data))
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0])
    if any(data != candidates[0][1] for _, data in candidates):
        return None
    return candidates[0]

def fetch_owner_comments():
    """Public GitHub REST metadata, no token, no paid API. Incomplete pages are not evidence."""
    comments = []
    for page in range(1, MAX_PAGES + 1):
        url = f"https://api.github.com/repos/{REPO}/issues/{ISSUE}/comments?per_page=100&page={page}"
        request = Request(url, headers={"Accept": "application/vnd.github+json",
                                       "User-Agent": "research-receipt-reader-v1"})
        with urlopen(request, timeout=8) as response:
            raw = response.read(MAX_RESPONSE + 1)
            if len(raw) > MAX_RESPONSE:
                raise ValueError("oversize comments page")
            rows = json.loads(raw)
            more = 'rel="next"' in response.headers.get("Link", "")
        if not isinstance(rows, list) or len(rows) > 100:
            raise ValueError("invalid comments page")
        comments.extend(rows)
        if not more:
            return comments
    raise ValueError("incomplete comments census")

def attach_owner_receipt(state, fetch=fetch_owner_comments):
    """Wire only the exact ACK-bound registry action, not unrelated meta ledger keys."""
    active = state.get("active_heavy_workstreams", [])
    if (state.get("sentinel_verdict") != "PASS" or state.get("binding_integrity") != "PRIMARY_COMPLETE"
            or state.get("primary_source") != "SHADOW_REGISTRY"
            or state.get("primary_target") != "CYCLE_NAVIGATOR_RESEARCH_FAMILY"
            or len(active) != 1 or active[0].get("specialist_action") != "RECOVER_EVALUATOR"
            or active[0].get("evidence_fingerprint") != SOURCE_FP):
        return state
    proof = dict(state["execution_proof"])
    proof.update({"action_id": ACTION_ID, "receipt_status": "MISSING_OR_UNVERIFIED"})
    try:
        result = receipt_from_comments(fetch(), ACTION_ID)
    except (OSError, ValueError, TypeError):
        result = None
    if result:
        comment_id, data = result
        proof.update({"receipt_status": "OWNER_ATTESTATION_RECEIVED",
                      "receipt_comment_id": comment_id,
                      "status": "OWNER_RECEIPT_PENDING_INDEPENDENT_VERIFICATION",
                      "native_run_id": data["native_run_id"],
                      "original_owner_pr": data["pr"],
                      "independent_review": data["review_receipt_id"],
                      "main_readback": data["readback"],
                      "scientific_outcome": data["outcome"],
                      "required_next_proof": "INDEPENDENT_NATIVE_AND_SCIENTIFIC_VERIFIER",
                      "learning_calibration_applied": False})
    return {**state, "execution_proof": proof}
