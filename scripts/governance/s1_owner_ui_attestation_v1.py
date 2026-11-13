"""S1 native NON-APP comment shape validator, read-only advisory.

Critical limitation: performed_via_github_app == null does NOT prove a human
used the GitHub website: a direct PAT REST call can also produce null. This
module can never authorize release, attest human presence, or bootstrap an
unattended policy. Human owner authorization must instead be direct and
contemporaneous in a human-interactive owner session (not scheduled S1), or
independently verified offline owner-signed approval from a protected key.
Caller-supplied GitHub JSON must be re-read natively by a trusted operator.
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
    auditor_evidence_url: str | None = None,
) -> dict[str, Any]:
    """Check GitHub REST *shape* only. Never trust this as proof of native fetch."""
    if (type(pr_number) is not int or pr_number < 1 or
            type(head_sha) is not str or not SHA.fullmatch(head_sha) or
            type(policy_blob_sha) is not str or not SHA.fullmatch(policy_blob_sha) or
            decision not in ALLOWED_DECISIONS):
        return _deny("EXPECTED_SCOPE_INVALID")
    waiver = decision.startswith("APPROVE_D2_WAIVER_")
    if waiver:
        if not isinstance(auditor_evidence_url, str):
            return _deny("INDEPENDENT_AUDITOR_EVIDENCE_REQUIRED")
        audit_url = urlparse(auditor_evidence_url)
        if (audit_url.scheme != "https" or audit_url.netloc != "github.com"
                or audit_url.path != f"/{REPO}/issues/1156"
                or audit_url.query
                or re.fullmatch(r"issuecomment-[1-9][0-9]*", audit_url.fragment or "") is None):
            return _deny("INDEPENDENT_AUDITOR_EVIDENCE_INVALID")
    elif auditor_evidence_url is not None:
        return _deny("UNEXPECTED_AUDITOR_EVIDENCE")
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
        + (f"\nauditor_evidence_url={auditor_evidence_url}" if waiver else "")
    )
    body = record.get("body")
    if type(body) is not str or body != expected_body:
        return _deny("OWNER_DECISION_SCOPE_OR_EXACT_HEAD_MISMATCH")
    # A null App field is NOT an independently verified human-only factor.
    # An owner PAT can create exactly the same native comment. Never treat
    # a positive candidate as interactive user approval or a release grant.
    body_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
    return {
        "contract": CONTRACT,
        "status": "NON_APP_COMMENT_CANDIDATE_NOT_OWNER_AUTHORIZATION",
        "reason": "NATIVE_SHAPE_MATCHES_BUT_PAT_OR_UI_INDISCERNIBLE",
        "comment_id": comment_id,
        "head_sha": head_sha,
        "policy_blob_sha": policy_blob_sha,
        "decision": decision,
        "auditor_evidence_url": auditor_evidence_url if waiver else None,
        "human_only_factor_verified": False,
        "created_at": record["created_at"],
        "updated_at": record["updated_at"],
        "body_sha256": body_hash,
        "authorized": False,
        "externally_authenticated": False,
    }
