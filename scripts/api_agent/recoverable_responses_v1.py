"""One-paid-POST, durable-handle, GET-only Responses background transport.

The existing owner must provide a separately admitted, public-only paid claim.
This module never issues a second POST for an existing attempt, even on error.
A successful transport is not a qualified research result or release approval.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.request
from pathlib import Path
from typing import Any, Callable

RESPONSE_ID = re.compile(r"resp_[A-Za-z0-9_-]{4,180}\Z")
TERMINAL = {"completed", "failed", "cancelled", "incomplete"}


class PendingResponse(RuntimeError):
    """The response is still running; retain the exact handle for GET-only rescue."""


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _write_once(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(canonical(value))
        stream.flush()
        os.fsync(stream.fileno())


def _read(path: Path) -> dict:
    result = json.loads(path.read_text())
    if not isinstance(result, dict):
        raise ValueError("BACKGROUND_INVALID_DURABLE_RECORD")
    return result


def _validate_payload(payload: dict) -> None:
    if (payload.get("model") != "gpt-6.1-sol"
            or (payload.get("reasoning") or {}).get("effort") != "max"
            or payload.get("background") is not True
            or payload.get("store") is not True):
        raise ValueError("BACKGROUND_PAYLOAD_NOT_ADMITTED")


def start(payload: dict, api_key: str, output_dir: Path, *,
          post: Callable = urllib.request.urlopen) -> dict:
    """Persist a one-use claim BEFORE network I/O, and the ID before any GET.

    A disconnected POST is ambiguous. No retry is permitted by this function.
    """
    _validate_payload(payload)
    if not api_key:
        raise ValueError("BACKGROUND_API_KEY_MISSING")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("BACKGROUND_ATTEMPT_EXISTS_NO_REPOST")
    output_dir.mkdir(parents=True, exist_ok=True)
    request_sha = digest(payload)
    _write_once(output_dir / "attempt.json", {
        "contract": "RECOVERABLE_SOL_ATTEMPT_V1",
        "request_sha256": request_sha,
        "state": "POST_OUTCOME_UNKNOWN",
        "max_paid_posts": 1,
        "additional_posts_authorized": 0,
    })
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=canonical(payload),
        headers={"Authorization": "Bearer " + api_key,
                 "Content-Type": "application/json"},
        method="POST",
    )
    # No general retry handler. Network failure leaves POST_OUTCOME_UNKNOWN.
    with post(request, timeout=75) as response:
        raw = response.read(200_001)
    if len(raw) > 200_000:
        raise ValueError("BACKGROUND_SUBMISSION_RESPONSE_OVERSIZED")
    body = json.loads(raw)
    response_id = body.get("id")
    if not isinstance(response_id, str) or RESPONSE_ID.fullmatch(response_id) is None:
        raise ValueError("BACKGROUND_RESPONSE_ID_UNAVAILABLE_NO_REPOST")
    handle = {
        "contract": "RECOVERABLE_SOL_HANDLE_V1",
        "request_sha256": request_sha,
        "response_id": response_id,
        "state": "GET_ONLY",
        "max_paid_posts": 1,
        "additional_posts_authorized": 0,
    }
    _write_once(output_dir / "response_handle.json", handle)
    return handle


def collect(payload: dict, api_key: str, output_dir: Path, *,
            get: Callable = urllib.request.urlopen) -> dict:
    """Read an exact durable ID by GET. This method contains no POST path."""
    _validate_payload(payload)
    attempt = _read(output_dir / "attempt.json")
    handle = _read(output_dir / "response_handle.json")
    source_sha = digest(payload)
    if (attempt.get("contract") != "RECOVERABLE_SOL_ATTEMPT_V1"
            or handle.get("contract") != "RECOVERABLE_SOL_HANDLE_V1"
            or attempt.get("request_sha256") != source_sha
            or handle.get("request_sha256") != source_sha
            or handle.get("state") != "GET_ONLY"
            or attempt.get("max_paid_posts") != 1
            or handle.get("additional_posts_authorized") != 0):
        raise ValueError("BACKGROUND_HANDLE_SOURCE_OR_CLAIM_MISMATCH")
    response_id = handle.get("response_id")
    if not isinstance(response_id, str) or RESPONSE_ID.fullmatch(response_id) is None or not api_key:
        raise ValueError("BACKGROUND_RESPONSE_ID_OR_KEY_INVALID")
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses/" + response_id,
        headers={"Authorization": "Bearer " + api_key}, method="GET",
    )
    with get(request, timeout=45) as response:
        raw = response.read(2_000_001)
    if len(raw) > 2_000_000:
        raise ValueError("BACKGROUND_POLL_RESPONSE_OVERSIZED")
    body = json.loads(raw)
    if body.get("id") != response_id:
        raise ValueError("BACKGROUND_PROVIDER_RESPONSE_ID_MISMATCH")
    status = body.get("status")
    if status in ("queued", "in_progress"):
        raise PendingResponse("BACKGROUND_RESPONSE_STILL_PENDING_GET_ONLY")
    if status not in TERMINAL:
        raise ValueError("BACKGROUND_UNRECOGNIZED_PROVIDER_STATUS")
    if status != "completed":
        # Only provider status/reason and integer token counters are
        # exported. Never publish response content, request data or secrets.
        details = body.get("incomplete_details") or {}
        if not isinstance(details, dict):
            details = {}
        raw_reason = details.get("reason")
        reason = (raw_reason if raw_reason in
                  ("max_output_tokens", "content_filter") else "unknown")
        usage = body.get("usage")
        if not isinstance(usage, dict):
            usage = {}
        output_details = usage.get("output_tokens_details")
        if not isinstance(output_details, dict):
            output_details = {}
        def bounded_token(value):
            return value if type(value) is int and 0 <= value <= 10_000_000 else None
        evidence = {
            "contract": "SOL_BACKGROUND_TERMINAL_DIAGNOSTIC_V1",
            "response_id_sha256": hashlib.sha256(response_id.encode()).hexdigest(),
            "provider_status": status,
            "incomplete_reason": reason if status == "incomplete" else "not_applicable",
            "input_tokens": bounded_token(usage.get("input_tokens")),
            "output_tokens": bounded_token(usage.get("output_tokens")),
            "reasoning_tokens": bounded_token(output_details.get("reasoning_tokens")),
            "additional_paid_posts": 0,
            "request_sha256": source_sha,
        }
        _write_once(output_dir / "terminal_evidence.json", evidence)
        raise ValueError("BACKGROUND_TERMINAL_" + str(status).upper()
                         + "_REASON_" + evidence["incomplete_reason"].upper())
    return body


def submit_or_resume(payload: dict, api_key: str, output_dir: Path, *,
                     resume: bool = False, max_polls: int = 35,
                     poll_interval: float = 12,
                     post: Callable = urllib.request.urlopen,
                     get: Callable = urllib.request.urlopen,
                     sleep: Callable = time.sleep) -> dict:
    """Poll one saved response; otherwise make ONE paid request and save handle."""
    if resume:
        if not (output_dir / "response_handle.json").is_file():
            raise ValueError("BACKGROUND_NO_HANDLE_NO_REPOST")
    else:
        start(payload, api_key, output_dir, post=post)
    for index in range(max_polls):
        try:
            return collect(payload, api_key, output_dir, get=get)
        except PendingResponse:
            if index + 1 == max_polls:
                raise
            sleep(poll_interval)
    raise AssertionError("unreachable")
