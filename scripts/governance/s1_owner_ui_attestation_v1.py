"""Strict S1 owner-native UI comment validator, read-only advisory.

The supplied record is UNTRUSTED. Existing S1 must independently retrieve the
original native GitHub comment REST resource and verify provenance, head,
policy blob, comment ID and body at action time. This helper cannot authorize a
merge, enable unattended S1 or authenticate itself.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import re
from typing import Any
from urllib.parse import urlparse

CONTRACT = "S1_OWNER_UI_RELEASE_ATTESTATION_V1"
REPO = "Donh91/Investering-Framework-Archive-v1"
SHA = re.compile(r"^[0-9a-f]{40}$")
ALLOWED_DECISIONS = frozenset((
    "APPROVE_HIGH_IMPACT",
    "APPROVE_STAGED_S",
    "APPROVE_D2_WAIVER_DOCS_ONLY",
    "APPROVE_D2_WAIVER_LOW_CODE",
))

def _timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00").astimezone(timezone.utc)
    except ValueError:
        return None

def _deny(reason: str) -> dict[str, Any]:
    return {
        "contract": CONTRACT,
        "status": "REJECTED_OR_UNVERIFIED",
        "reason": reason,
        "authorized": False,
        "externally_authenticated": False,
    }

def classify_native_ui_comment(
    record: Any,
    *,
    pr_number: int,
    head_sha: str,
    policy_blob_sha: str,
    decision: str,
) -> dict[str, Any]:
    """Check GitHub REST *shape* only. Never trust this as proof of native fetch."""
    if (type(pr_number) is not int or pr_number < 1 or
            type(head_sha) is not str or not SHA.fullmatch(head_sha) or
            type(policy_blob_sha) is not str or not SHA.fullmatch(policy_blob_sha) or
            decision not in ALLOWED_DECISIONS):
        return _deny("EXPECTED_SCOPE_INVALID")
    if not isinstance(record, dict):
        return _deny("NATIVE_RECORD_MISSING")
    user = record.get("user")
    if (not isinstance(user, dict) or user.get("login") != "Donh91"
            or user.get("type") != "User"
            or record.get("author_association") != "OWNER"):
        return _deny("OWNER_IDENTITY_NOT_PROVEN")
    if ("performed_via_github_app" not in record or
            record["performed_via_github_app"] is not None):
        return _deny("APP_AUTHORED_OR_UNVERIFIED")
    comment_id = record.get("id")
    if type(comment_id) is not int or comment_id < 1:
        return _deny("COMMENT_ID_MISSING")
    url = record.get("html_url")
    if not isinstance(url, str):
        return _deny("COMMENT_LINK_MISSING")
    parsed = urlparse(url)
    if (parsed.scheme != "https" or parsed.netloc != "github.com"
            or parsed.username is not None or parsed.password is not None
            or parsed.query or parsed.fragment != f"issuecomment-{comment_id}"
            or parsed.path not in (
                f"/{REPO}/issues/1156",
                f"/{REPO}/pull/{pr_number}",
            )):
        return _deny("COMMENT_LOCATION_UNVERIFIED")
    created = _timestamp(record.get("created_at"))
    updated = _timestamp(record.get("updated_at"))
    if created is None or updated is None or updated < created:
        return _deny("COMMENT_CLOCK_UNVERIFIED")
    expected_body = (
        f"S1_OWNER_UI_RELEASE_ATTESTATION_v1\n"
        f"repo={REPO}\n"
        f"pr={pr_number}\n"
        f"head={head_sha}\n"
        f"policy_blob={policy_blob_sha}\n"
        f"decision={decision}"
    )
    body = record.get("body")
    if type(body) is not str or body != expected_body:
        return _deny("OWNER_DECISION_SCOPE_OR_EXACT_HEAD_MISMATCH")
    # Even a well-formed record could be forged before this helper is called.
    # All positive results remain *candidates*, with no release authorization.
    body_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
    return {
        "contract": CONTRACT,
        "status": "UI_COMMENT_CANDIDATE_REQUIRES_INDEPENDENT_NATIVE_READBACK",
        "reason": "SYNTAX_AND_DECLARED_UI_PROVENANCE_MATCH",
        "comment_id": comment_id,
        "head_sha": head_sha,
        "policy_blob_sha": policy_blob_sha,
        "decision": decision,
        "created_at": record["created_at"],
        "updated_at": record["updated_at"],
        "body_sha256": body_hash,
        "authorized": False,
        "externally_authenticated": False,
    }
