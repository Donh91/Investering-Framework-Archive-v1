"""Bounded owner-receipt intake for the existing WIRE-0 pilot.

An owner attestation is evidence input, not independent scientific adjudication,
a merge authorization, or proof that calibration was applied. No workflow actor
is admitted until its run provenance has an independently configured verifier.
"""
import json
import hashlib
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

class ReceiptConflict(ValueError):
    pass


def receipt_from_comments(comments, action_id):
    """Accept exactly one distinct, unchanged owner receipt; conflicting claims fail closed."""
    if not isinstance(comments, list):
        raise ValueError("invalid comments census")
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
            raise ReceiptConflict("malformed claim for action")
        candidates.append((comment["id"], data))
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0])
    if any(data != candidates[0][1] for _, data in candidates):
        raise ReceiptConflict("conflicting claims for action")
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

def _get_native(path):
    request = Request(f"https://api.github.com/repos/{REPO}/{path}",
                      headers={"Accept": "application/vnd.github+json", "User-Agent": "research-receipt-reader-v1"})
    with urlopen(request, timeout=8) as response:
        raw = response.read(MAX_RESPONSE + 1)
    if len(raw) > MAX_RESPONSE:
        raise ValueError("oversize native metadata")
    obj = json.loads(raw, object_pairs_hook=_unique)
    if not isinstance(obj, dict):
        raise ValueError("invalid native metadata")
    return obj


def verify_native_metadata(data, get=_get_native):
    """Bounded WIRE-0 native metadata check, NOT readback or independent science."""
    # The only original-owner implementation for this pilot is #2357.
    if data.get("pr") != 2357:
        return "NATIVE_METADATA_MISMATCH"
    pr = get("pulls/2357")
    run = get(f"actions/runs/{data['native_run_id']}")
    base = pr.get("base") or {}
    if (pr.get("number") != 2357 or pr.get("merged") is not True
            or pr.get("merge_commit_sha") != data["merge_sha"]
            or base.get("ref") != "main" or (base.get("repo") or {}).get("full_name") != REPO
            or run.get("id") != data["native_run_id"] or run.get("head_sha") != data["merge_sha"]
            or run.get("head_branch") != "main" or (run.get("repository") or {}).get("full_name") != REPO
            or run.get("path") != ".github/workflows/shadow-registry-weekly.yml"
            or run.get("status") != "completed" or run.get("conclusion") != "success"):
        return "NATIVE_METADATA_MISMATCH"
    return "NATIVE_METADATA_MATCH_INDEPENDENCE_UNVERIFIED"


def _attestation(comment_id, data):
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return {"contract": "WIRE0_HISTORICAL_ATTESTATION_v1", "action_id": ACTION_ID,
            "source_fingerprint": SOURCE_FP, "comment_id": comment_id,
            "claim_sha256": hashlib.sha256(encoded).hexdigest(),
            "claimed_pr": data["pr"], "claimed_merge_sha": data["merge_sha"],
            "claimed_native_run_id": data["native_run_id"],
            "claimed_review_receipt_id": data["review_receipt_id"],
            "claimed_outcome_status": data["outcome"]["status"],
            "scientific_authority": False}


def _prior_attestation(previous):
    old = (previous or {}).get("wire0_historical_attestation")
    if (not isinstance(old, dict) or old.get("contract") != "WIRE0_HISTORICAL_ATTESTATION_v1"
            or old.get("action_id") != ACTION_ID or old.get("source_fingerprint") != SOURCE_FP
            or old.get("scientific_authority") is not False
            or not _id(old.get("comment_id")) or not isinstance(old.get("claim_sha256"), str)
            or not re.fullmatch(r"[0-9a-f]{64}", old["claim_sha256"])):
        return None
    # Only known, value-free fields survive a mutable prior snapshot.
    allowed = {"contract", "action_id", "source_fingerprint", "comment_id", "claim_sha256",
               "claimed_pr", "claimed_merge_sha", "claimed_native_run_id",
               "claimed_review_receipt_id", "claimed_outcome_status", "scientific_authority"}
    if (set(old) != allowed or not _id(old.get("claimed_pr"))
            or not _id(old.get("claimed_native_run_id")) or not _id(old.get("claimed_review_receipt_id"))
            or not _sha(old.get("claimed_merge_sha"))
            or old.get("claimed_outcome_status") not in ("VERIFIED", "FALSIFIED", "BLOCKED")):
        return None
    return dict(old)


def attach_owner_receipt(state, fetch=fetch_owner_comments, *, previous=None, verify=None):
    """Separate persistent historical claims from current evidence and science.

    Shared owner identity is not independent review. R1 and an authenticated
    scientific verifier are required before any scientific outcome is populated.
    """
    prior = _prior_attestation(previous)
    result_state = dict(state)
    if prior:
        result_state["wire0_historical_attestation"] = prior
    active = state.get("active_heavy_workstreams", [])
    if (state.get("sentinel_verdict") != "PASS" or state.get("binding_integrity") != "PRIMARY_COMPLETE"
            or state.get("primary_source") != "SHADOW_REGISTRY"
            or state.get("primary_target") != "CYCLE_NAVIGATOR_RESEARCH_FAMILY"
            or len(active) != 1 or active[0].get("specialist_action") != "RECOVER_EVALUATOR"
            or active[0].get("evidence_fingerprint") != SOURCE_FP):
        return result_state
    proof = dict(state["execution_proof"])
    proof.update({"action_id": ACTION_ID, "receipt_status": "ABSENT",
                  "receipt_verification": "NOT_VERIFIED", "native_run_id": None,
                  "original_owner_pr": None, "independent_review": None,
                  "main_readback": None, "scientific_outcome": None,
                  "learning_calibration_applied": False})
    result_state["execution_proof"] = proof
    if fetch is None:
        proof["receipt_status"] = "NOT_CHECKED"
        return result_state
    try:
        result = receipt_from_comments(fetch(), ACTION_ID)
        claim = _attestation(*result) if result else None
    except ReceiptConflict:
        proof["receipt_status"] = "CONFLICT"
        return result_state
    except (OSError, ValueError, TypeError):
        proof["receipt_status"] = "SOURCE_UNAVAILABLE"
        return result_state
    if claim is None:
        if prior:
            proof["receipt_status"] = "HISTORICAL_CLAIM_NOT_CURRENTLY_PRESENT"
        return result_state
    if prior and prior["claim_sha256"] != claim["claim_sha256"]:
        proof["receipt_status"] = "CONFLICT"
        return result_state
    result_state["wire0_historical_attestation"] = prior or claim
    proof.update({"receipt_status": "OWNER_ATTESTATION_RECEIVED",
                  "receipt_comment_id": claim["comment_id"],
                  "status": "OWNER_RECEIPT_PENDING_INDEPENDENT_VERIFICATION",
                  "required_next_proof": "INDEPENDENT_NATIVE_AND_SCIENTIFIC_VERIFIER"})
    if verify is not None:
        try:
            native = verify(result[1])
            proof["receipt_verification"] = native if native in (
                "NATIVE_METADATA_MATCH_INDEPENDENCE_UNVERIFIED", "NATIVE_METADATA_MISMATCH") else "NOT_VERIFIED"
        except (OSError, ValueError, TypeError):
            proof["receipt_verification"] = "NATIVE_SOURCE_UNAVAILABLE"
    # Even a native metadata match does not prove readback, review independence,
    # or a scientific disposition. No claimed fields enter execution authority.
    return result_state
