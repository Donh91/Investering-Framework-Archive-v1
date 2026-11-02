"""S1 v4.3 read-only cross-agent receipt verifier.

Validates the SHAPE of a request/ACK/result chain. It does not authenticate
GitHub actors, prove agent execution, grant merge authority or call providers.
"""
from datetime import datetime
from urllib.parse import urlparse, unquote
import re
import hashlib
import json

SHA = re.compile(r"^[a-f0-9]{40}$")
REQUEST_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{11,127}$")
UTC_STAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
STEPS = ["REQUESTED", "ACKNOWLEDGED", "ACCEPTED", "RESULT_DELIVERED", "S1_VERIFIED"]


class ReceiptError(ValueError):
    pass


def _time(value):
    if not isinstance(value, str) or UTC_STAMP.fullmatch(value) is None:
        raise ReceiptError("UTC Z timestamp required")
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ReceiptError("invalid timestamp") from exc


def _url(value):
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    # Shape-only validation must not accept path traversal under the trusted owner.
    segments = unquote(parsed.path).replace(chr(92), "/").split("/")
    if any(segment in (".", "..") for segment in segments):
        return False
    return parsed.scheme == "https" and parsed.netloc == "github.com" and (
        parsed.path.startswith("/Donh91/") and (not parsed.fragment or re.fullmatch(r"(?:issuecomment-\d+|discussion_r\d+|pullrequestreview-\d+)", parsed.fragment) is not None)
    )


def validate_chain(events):
    """Reject missing ACK, forged sender, head drift and replay.

    Caller must additionally cross-check native GitHub actor and job/event IDs
    in authenticated repos before marking delivery or execution as proven.
    """
    if not isinstance(events, list) or not events:
        raise ReceiptError("missing request")
    start = events[0]
    if not isinstance(start, dict):
        raise ReceiptError("request object required")
    keys = ("request_id", "source_head", "source_fingerprint",
            "sender", "recipient", "original_url")
    if any(not start.get(k) for k in keys):
        raise ReceiptError("missing request binding")
    if not isinstance(start["request_id"], str) or REQUEST_ID.fullmatch(start["request_id"]) is None:
        raise ReceiptError("unique typed request id required")
    if not isinstance(start["source_fingerprint"], str) or len(start["source_fingerprint"]) < 8:
        raise ReceiptError("source fingerprint too weak")
    if any(not isinstance(start[k], str) for k in keys):
        raise ReceiptError("request keys must be strings")
    if not SHA.fullmatch(start["source_head"]):
        raise ReceiptError("exact 40-character source SHA required")
    if start["sender"] == start["recipient"]:
        raise ReceiptError("independent recipient required")
    if not _url(start["original_url"]):
        raise ReceiptError("original GitHub owner URL required")
    binding = tuple(start[k] for k in keys)
    previous_time = None
    status = None
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise ReceiptError("invalid event")
        if tuple(event.get(k) for k in keys) != binding:
            raise ReceiptError("cross-head/request replay")
        now = _time(event.get("at_utc"))
        if previous_time is not None and now <= previous_time:
            raise ReceiptError("time not increasing")
        previous_time = now
        proposed = event.get("state")
        actor = event.get("actor")
        if index == 0:
            if proposed != "REQUESTED" or actor != start["sender"]:
                raise ReceiptError("initial request invalid")
        elif status in ("REJECTED", "TIMED_OUT", "S1_VERIFIED"):
            raise ReceiptError("already terminal")
        elif proposed == "TIMED_OUT":
            if status == "RESULT_DELIVERED":
                raise ReceiptError("a delivered result must be verified, not dropped")
            if actor != start["sender"]:
                raise ReceiptError("only sender may expire")
        elif proposed == "REJECTED":
            if status not in ("REQUESTED", "ACKNOWLEDGED") or actor != start["recipient"]:
                raise ReceiptError("invalid rejection")
        elif (status, proposed) not in set(zip(STEPS, STEPS[1:])):
            raise ReceiptError("missing or reordered handshake state")
        elif actor != (start["sender"] if proposed == "S1_VERIFIED" else start["recipient"]):
            raise ReceiptError("wrong receiving actor")
        if not _url(event.get("native_event_url")):
            raise ReceiptError("missing native event reference")
        if proposed == "RESULT_DELIVERED" and not _url(event.get("result_url")):
            raise ReceiptError("result proof required")
        if proposed == "S1_VERIFIED":
            if event.get("verification") not in ("PASS", "BLOCKED"):
                raise ReceiptError("S1 verification result required")
            if not _url(event.get("verification_url")):
                raise ReceiptError("verification evidence required")
        status = proposed
    return {
        "request_id": start["request_id"],
        "request_binding_sha256": hashlib.sha256(json.dumps(dict(zip(keys, binding)), sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest(),
        "source_head": start["source_head"],
        "structural_state": status,
        "reported_verification_outcome": events[-1].get("verification") if status == "S1_VERIFIED" else None,
        "events_checked": len(events),
        "authenticated_delivery": False,
        "actual_job_execution_proven": False,
        "release_authorized": False,
        "reason": "AUTHENTICATED_NATIVE_READBACK_STILL_REQUIRED",
    }


def handoff_followup(events, observed_at_utc, timeout_minutes, attempts, max_attempts=2):
    """Bounded non-dispatch guidance. Time passage is NOT an ACK or PR trigger."""
    result = validate_chain(events)
    if (type(timeout_minutes) is not int or not 1 <= timeout_minutes <= 10080
            or type(attempts) is not int or not 1 <= attempts
            or type(max_attempts) is not int or not 1 <= max_attempts <= 3):
        raise ReceiptError("invalid bounded retry policy")
    if attempts > max_attempts:
        raise ReceiptError("retry ledger inconsistent")
    now = _time(observed_at_utc)
    recent = _time(events[-1]["at_utc"])
    if now < recent:
        raise ReceiptError("observation predates last receipt")
    state = result["structural_state"]
    if state in ("REJECTED", "TIMED_OUT", "S1_VERIFIED"):
        action = "TERMINAL_NO_DISPATCH"
    elif state == "RESULT_DELIVERED":
        action = "VERIFY_NATIVE_RESULT_NOW"
    elif (now - recent).total_seconds() < timeout_minutes * 60:
        action = "AWAIT_EXISTING_RECEIVER"
    elif state in ("ACKNOWLEDGED", "ACCEPTED"):
        # A real recipient already owns the request. Never retry it.
        # Finite escalation after three inactivity windows, no ghost dispatch.
        action = ("RECEIVER_STALLED_ESCALATE_ORIGINAL_OWNER"
                  if (now - recent).total_seconds() >= timeout_minutes * 180
                  else "RECEIVER_RESULT_OVERDUE_NO_DUPLICATE_REQUEST")
    elif attempts < max_attempts:
        action = "RETRY_ONLY_IF_NATIVE_INTAKE_AUTHORIZED"
    else:
        action = "DEAD_LETTER_ESCALATE_WITH_ORIGINAL_OWNER"
    return {
        "request_binding_sha256": result["request_binding_sha256"],
        "structural_state": state,
        "next_action": action,
        "automatically_dispatched": False,
        "delivery_authenticated": False,
        "retries_remaining": max_attempts - attempts,
    }
