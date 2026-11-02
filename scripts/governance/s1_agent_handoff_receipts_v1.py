"""S1 v4.3 read-only cross-agent receipt verifier.

Validates the SHAPE of a request/ACK/result chain. It does not authenticate
GitHub actors, prove agent execution, grant merge authority or call providers.
"""
from datetime import datetime
from urllib.parse import urlparse
import re

SHA = re.compile(r"^[a-f0-9]{40}$")
STEPS = ["REQUESTED", "ACKNOWLEDGED", "ACCEPTED", "RESULT_DELIVERED", "S1_VERIFIED"]


class ReceiptError(ValueError):
    pass


def _time(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ReceiptError("UTC Z timestamp required")
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ReceiptError("invalid timestamp") from exc


def _url(value):
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and parsed.netloc == "github.com" and (
        parsed.path.startswith("/Donh91/") and not parsed.fragment
    )


def validate_chain(events):
    """Reject missing ACK, forged sender, head drift and replay.

    Caller must additionally cross-check native GitHub actor and job/event IDs
    in authenticated repos before marking delivery or execution as proven.
    """
    if not isinstance(events, list) or not events:
        raise ReceiptError("missing request")
    start = events[0]
    keys = ("request_id", "source_head", "source_fingerprint",
            "sender", "recipient", "original_url")
    if any(not start.get(k) for k in keys):
        raise ReceiptError("missing request binding")
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
        "source_head": start["source_head"],
        "structural_state": status,
        "events_checked": len(events),
        "authenticated_delivery": False,
        "actual_job_execution_proven": False,
        "release_authorized": False,
        "reason": "AUTHENTICATED_NATIVE_READBACK_STILL_REQUIRED",
    }
