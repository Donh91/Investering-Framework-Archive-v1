"""Read-only source-bound native GitHub attestation for existing S1 G1 handoff.

Consumes injected authenticated GitHub REST and artifact readers. No provider
calls, GitHub writes, retries, model invocation, release or market authority.
A CODEX_READY packet and a synthetic/shape-only receipt are never native ACKs.
"""
from __future__ import annotations

import hashlib
import json
import re
from urllib.parse import urlparse

from scripts.governance.s1_agent_handoff_receipts_v1 import ReceiptError, validate_chain

SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
REPO = re.compile(r"Donh91/[A-Za-z0-9_.-]+\Z")
COMMENT_PATH = re.compile(r"/Donh91/([A-Za-z0-9_.-]+)/issues/([0-9]+)\Z")
COMMENT_FRAGMENT = re.compile(r"issuecomment-([0-9]+)\Z")
NON_EXECUTION_PREFIXES = (
    "set up job", "complete job", "checkout", "post checkout",
    "run actions/checkout@", "post run actions/checkout@",
    "run actions/setup-", "post run actions/setup-",
    "run actions/cache@", "post run actions/cache@",
)


def _trusted_steps(required_steps):
    # Pinned by an authenticated original owner, never by an issue body/model.
    if (not isinstance(required_steps, (tuple, list))
            or not 2 <= len(required_steps) <= 8
            or any(not isinstance(x, str) or not 3 <= len(x.strip()) <= 90
                   for x in required_steps)):
        raise ReceiptError("TRUSTED_EXECUTION_AND_TEST_STEPS_REQUIRED")
    names = [x.strip().casefold() for x in required_steps]
    if len(set(names)) != len(names) or any(
        x.startswith(NON_EXECUTION_PREFIXES) for x in names
    ):
        raise ReceiptError("SETUP_STEP_CANNOT_PROVE_RECIPIENT_EXECUTION")
    return names


def _blocked(reason, structure=None):
    return {
        "contract": "S1_NATIVE_HANDOFF_AUTH_v1",
        "structural_state": (structure or {}).get("structural_state", "UNKNOWN"),
        "request_binding_sha256": (structure or {}).get("request_binding_sha256"),
        "status": "UNKNOWN_OR_BLOCKED",
        "reason": reason,
        "authenticated_delivery": False,
        "actual_job_execution_proven": False,
        "result_artifact_verified": False,
        "release_authorized": False,
    }


def _native_comment(event, *, repo, login, binding, native_get):
    url = event.get("native_event_url")
    p = urlparse(url or "")
    m, f = COMMENT_PATH.fullmatch(p.path), COMMENT_FRAGMENT.fullmatch(p.fragment)
    if (p.scheme != "https" or p.netloc != "github.com" or p.query
            or m is None or f is None or f"Donh91/{m.group(1)}" != repo):
        raise ReceiptError("UNBOUND_NATIVE_COMMENT_URL")
    comment_id = int(f.group(1))
    native = native_get(f"/repos/{repo}/issues/comments/{comment_id}")
    if (not isinstance(native, dict) or native.get("id") != comment_id
            or native.get("html_url") != url
            or (native.get("user") or {}).get("login") != login
            or native.get("created_at") != event.get("at_utc")):
        raise ReceiptError("NATIVE_COMMENT_ID_ACTOR_OR_TIME_MISMATCH")
    try:
        body = json.loads(native.get("body") or "")
    except (ValueError, TypeError) as exc:
        raise ReceiptError("NATIVE_COMMENT_NOT_TYPED") from exc
    if not isinstance(body, dict) or body.get("contract") != "S1_HANDOFF_NATIVE_V1":
        raise ReceiptError("NATIVE_COMMENT_CONTRACT_MISMATCH")
    for key in ("request_id", "source_head", "source_fingerprint", "state"):
        if body.get(key) != event.get(key):
            raise ReceiptError("NATIVE_COMMENT_REQUEST_REPLAY")
    if body.get("request_binding_sha256") != binding:
        raise ReceiptError("NATIVE_COMMENT_BINDING_MISMATCH")
    return body


def authenticate_native_chain(
    events, *, expected_source_head, expected_binding_sha256,
    origin_repo, recipient_repo, sender_login, recipient_login,
    native_get, artifact_bytes_get, required_execution_steps,
):
    """Native-reader injection must come from a trusted authenticated caller."""
    try:
        structural = validate_chain(events)
        if (not isinstance(expected_source_head, str)
                or not SHA40.fullmatch(expected_source_head)
                or not isinstance(expected_binding_sha256, str)
                or not SHA256.fullmatch(expected_binding_sha256)
                or not all(isinstance(r, str) and REPO.fullmatch(r)
                           for r in (origin_repo, recipient_repo))
                or not sender_login or not recipient_login
                or sender_login == recipient_login):
            raise ReceiptError("INVALID_TRUSTED_SOURCE_OR_PRINCIPALS")
        if (structural["source_head"] != expected_source_head
                or structural["request_binding_sha256"] != expected_binding_sha256):
            raise ReceiptError("STALE_HEAD_OR_REQUEST_BINDING")
        state = structural["structural_state"]
        if state == "REQUESTED":
            return _blocked("NO_NATIVE_RECIPIENT_ACK", structural)
        if state not in ("ACKNOWLEDGED", "ACCEPTED", "RESULT_DELIVERED", "S1_VERIFIED"):
            return _blocked("NO_ADMISSIBLE_RECEIVER_STATE", structural)
        for row in events:
            login = (sender_login if row["state"] in ("REQUESTED", "S1_VERIFIED")
                     else recipient_login)
            _native_comment(row, repo=origin_repo, login=login,
                            binding=expected_binding_sha256, native_get=native_get)
        if state in ("ACKNOWLEDGED", "ACCEPTED"):
            return {
                "contract": "S1_NATIVE_HANDOFF_AUTH_v1",
                "structural_state": state,
                "request_binding_sha256": expected_binding_sha256,
                "status": "NATIVE_RECIPIENT_ACK_ONLY",
                "reason": "AUTHENTICATED_ACK_WITHOUT_EXECUTION_PROOF",
                "authenticated_delivery": True,
                "actual_job_execution_proven": False,
                "result_artifact_verified": False,
                "release_authorized": False,
            }
        result_event = next(e for e in events if e["state"] == "RESULT_DELIVERED")
        body = _native_comment(
            result_event, repo=origin_repo, login=recipient_login,
            binding=expected_binding_sha256, native_get=native_get)
        run_id, job_id, artifact_id = (
            body.get("workflow_run_id"), body.get("workflow_job_id"),
            body.get("artifact_id"))
        if any(type(n) is not int or n < 1 for n in (run_id, job_id, artifact_id)):
            raise ReceiptError("MISSING_NATIVE_RUN_JOB_OR_ARTIFACT")
        receiver_head = body.get("receiver_head_sha")
        artifact_digest = body.get("artifact_sha256")
        if (not isinstance(receiver_head, str)
                or not SHA40.fullmatch(receiver_head)
                or not isinstance(artifact_digest, str)
                or not SHA256.fullmatch(artifact_digest)):
            raise ReceiptError("MISSING_NATIVE_SOURCE_OR_ARTIFACT_BINDING")
        run = native_get(f"/repos/{recipient_repo}/actions/runs/{run_id}")
        job = native_get(f"/repos/{recipient_repo}/actions/jobs/{job_id}")
        if (not isinstance(run, dict) or not isinstance(job, dict)
                or run.get("id") != run_id
                or run.get("repository", {}).get("full_name") != recipient_repo
                or run.get("head_sha") != receiver_head
                or (run.get("actor") or {}).get("login") != recipient_login
                or run.get("event") not in ("workflow_dispatch", "repository_dispatch", "pull_request")
                or run.get("status") != "completed" or run.get("conclusion") != "success"
                or job.get("id") != job_id or job.get("run_id") != run_id
                or job.get("status") != "completed" or job.get("conclusion") != "success"):
            raise ReceiptError("NATIVE_RUN_JOB_ACTOR_OR_SOURCE_MISMATCH")
        required = _trusted_steps(required_execution_steps)
        steps = job.get("steps")
        if not isinstance(steps, list) or not all(
            any(isinstance(step, dict)
                and step.get("status") == "completed"
                and step.get("conclusion") == "success"
                and str(step.get("name", "")).strip().casefold() == name
                for step in steps)
            for name in required
        ):
            raise ReceiptError("REQUIRED_NATIVE_EXECUTION_OR_TEST_STEP_NOT_EXECUTED")
        listings = native_get(f"/repos/{recipient_repo}/actions/runs/{run_id}/artifacts")
        listed = listings.get("artifacts") if isinstance(listings, dict) else None
        artifact = next((a for a in (listed or []) if isinstance(a, dict)
                         and a.get("id") == artifact_id), None)
        if (artifact is None or artifact.get("workflow_run", {}).get("id") != run_id
                or artifact.get("expired") is not False):
            raise ReceiptError("RESULT_ARTIFACT_NOT_NATIVE_OR_EXPIRED")
        data = artifact_bytes_get(recipient_repo, artifact_id)
        if not isinstance(data, bytes) or hashlib.sha256(data).hexdigest() != artifact_digest:
            raise ReceiptError("RESULT_ARTIFACT_BYTES_MISMATCH")
        try:
            receipt = json.loads(data)
        except (ValueError, TypeError) as exc:
            raise ReceiptError("RESULT_ARTIFACT_NOT_JSON") from exc
        if (not isinstance(receipt, dict)
                or receipt.get("contract") != "S1_RECIPIENT_RESULT_v1"
                or receipt.get("request_id") != events[0]["request_id"]
                or receipt.get("source_head") != expected_source_head
                or receipt.get("source_fingerprint") != events[0]["source_fingerprint"]
                or receipt.get("request_binding_sha256") != expected_binding_sha256
                or receipt.get("workflow_run_id") != run_id
                or receipt.get("workflow_job_id") != job_id):
            raise ReceiptError("ARTIFACT_WORK_ID_OR_SOURCE_REPLAY")
        return {
            "contract": "S1_NATIVE_HANDOFF_AUTH_v1",
            "structural_state": state,
            "request_binding_sha256": expected_binding_sha256,
            "status": "OBSERVED_EXECUTION_NOT_RELEASE",
            "reason": "NATIVE_ACTOR_JOB_AND_RESULT_ARTIFACT_VERIFIED",
            "recipient_login": recipient_login,
            "workflow_run_id": run_id,
            "workflow_job_id": job_id,
            "artifact_id": artifact_id,
            "authenticated_delivery": True,
            "actual_job_execution_proven": True,
            "result_artifact_verified": True,
            "release_authorized": False,
        }
    except (ReceiptError, KeyError, TypeError, AttributeError, ValueError) as exc:
        return _blocked(str(exc), structural if "structural" in locals() else None)
