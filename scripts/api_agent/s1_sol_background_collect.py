"""Retrieve one already paid Sol background response, never submit inference.

Reuses native previous-run GitHub artifacts and a bot-issued payment claim.
Artifact source HEAD is immutable; a current branch change never authorizes
applying old generated source. This module has NO POST or repository writer.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

REPO = "Donh91/Investering-Framework-Archive-v1"
PR = 1877
HEAD = re.compile(r"^[a-f0-9]{40}$")
RID = re.compile(r"^resp_[A-Za-z0-9_-]{4,180}$")
HEX = re.compile(r"^[a-f0-9]{64}$")
RUN_ID = re.compile(r"^[1-9][0-9]{0,17}$")
MODEL = "gpt-6.1-sol"
EFFORT = "max"
CLAIM_PREFIX = "S1_SOL_MAX_PATCH_RESERVATION_V1"
CLAIM_TAIL = "PR=1877 MODEL=gpt-6.1-sol EFFORT=max MAX_USD=0.75"


def api(path: str) -> dict:
    if not os.environ.get("GH_TOKEN"):
        raise ValueError("NATIVE_GITHUB_AUTH_REQUIRED")
    return json.loads(subprocess.check_output(
        ["gh", "api", "repos/" + REPO + "/" + path],
        text=True, timeout=45))


def verify_native_artifact(artifact_dir: Path, origin_run: str, *, read_native=api) -> dict:
    """Fail closed on a forged response ID, blob or non-owner origin."""
    if not RUN_ID.fullmatch(origin_run):
        raise ValueError("INVALID_ORIGIN_RUN")
    try:
        handle = json.loads((artifact_dir / "response_handle.json").read_text())
        reserve = json.loads((artifact_dir / "reservation.json").read_text())
        context = (artifact_dir / "context.json").read_bytes()
    except (OSError, ValueError) as exc:
        raise ValueError("ORIGIN_ARTIFACT_INCOMPLETE") from exc
    rid, source_head, fingerprint = (
        handle.get("response_id"), handle.get("source_head"),
        handle.get("context_sha256"))
    if (not isinstance(rid, str) or RID.fullmatch(rid) is None
            or not isinstance(source_head, str) or HEAD.fullmatch(source_head) is None
            or not isinstance(fingerprint, str) or HEX.fullmatch(fingerprint) is None
            or hashlib.sha256(context).hexdigest() != fingerprint):
        raise ValueError("ORIGIN_HANDLE_INVALID_OR_CONTEXT_DRIFT")
    try:
        context_data = json.loads(context)
    except ValueError as exc:
        raise ValueError("ORIGIN_CONTEXT_INVALID") from exc
    if (context_data.get("source_head") != source_head
            or context_data.get("repo") != REPO
            or context_data.get("original_pr") != PR
            or context_data.get("contract") != "S1_SOL_MAX_PATCH_CONTEXT_v1"):
        raise ValueError("ORIGIN_CONTEXT_FOREIGN")
    claim_id = reserve.get("claim_id")
    if (type(claim_id) is not int or claim_id < 1
            or handle.get("reservation_claim_id") != claim_id
            or handle.get("model") != MODEL
            or handle.get("reasoning_effort") != EFFORT
            or reserve.get("model") != MODEL or reserve.get("effort") != EFFORT
            or reserve.get("source_head") != source_head
            or reserve.get("status") != "RESERVED"):
        raise ValueError("ORIGIN_CLAIM_BINDING_INVALID")
    run = read_native("actions/runs/" + origin_run)
    if (str(run.get("id")) != origin_run
            or run.get("name") != "Framework Learning Supervisor"
            or run.get("event") != "pull_request"
            or run.get("head_sha") != source_head):
        raise ValueError("ORIGIN_GITHUB_RUN_INVALID")
    native = read_native("issues/comments/" + str(claim_id))
    expected = f"{CLAIM_PREFIX} HEAD={source_head} {CLAIM_TAIL}"
    if (native.get("body", "").strip() != expected
            or (native.get("user") or {}).get("login") != "github-actions[bot]"):
        raise ValueError("ORIGIN_NATIVE_PAYMENT_CLAIM_INVALID")
    return {"response_id": rid, "source_head": source_head,
            "context_sha256": fingerprint, "claim_id": claim_id,
            "origin_run_id": origin_run,
            "storage_consent": handle.get("storage_consent")}


def retrieve_once(handle: dict, key: str, *, request=urllib.request.urlopen):
    """One GET, no POST, retries or model invocation."""
    if not key:
        raise ValueError("OPENAI_API_KEY_MISSING")
    rid = handle["response_id"]
    req = urllib.request.Request(
        "https://api.openai.com/v1/responses/" + rid,
        headers={"Authorization": "Bearer " + key}, method="GET")
    try:
        with request(req, timeout=45) as response:
            if response.status != 200:
                return response.status, {}
            content = response.read(1_000_001)
            if len(content) > 1_000_000:
                raise ValueError("UNTRUSTED_PROVIDER_RESULT_OVERSIZED")
            return 200, json.loads(content)
    except urllib.error.HTTPError as error:
        return error.code, {}


def interpret(handle: dict, status: int, obj: dict) -> dict:
    result = {"contract": "S1_SOL_BACKGROUND_COLLECT_V1",
              **handle, "http_status": status, "paid_post_performed": False,
              "automatic_source_application": False,
              "provider_billing": "NOT_RECONCILED"}
    if status == 404:
        result["state"] = "EXPIRED_OR_NOT_STORED"
    elif status in (429, 500, 502, 503, 504):
        result["state"] = "RETRYABLE_GET_ONLY"
    elif status != 200 or obj.get("id") != handle["response_id"]:
        result["state"] = "PROVIDER_OR_ID_MISMATCH"
    elif obj.get("status") in ("queued", "in_progress"):
        result["state"] = "PENDING_COLLECT"
    elif obj.get("status") in ("completed", "incomplete", "failed", "cancelled"):
        result["state"] = obj["status"].upper()
        usage = obj.get("usage") or {}
        result["usage"] = {
            "input_tokens": usage.get("input_tokens"),
            "output_tokens": usage.get("output_tokens"),
            "reasoning_tokens": (usage.get("output_tokens_details") or {}).get("reasoning_tokens"),
        }
        result["incomplete_details"] = obj.get("incomplete_details")
    else:
        result["state"] = "UNKNOWN_PROVIDER_STATUS"
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--origin-run", required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    # This lane is a manual read-only collector; production writer never runs.
    if os.environ.get("GITHUB_ACTOR") != "Donh91":
        raise ValueError("NON_OWNER_COLLECT_DISALLOWED")
    handle = verify_native_artifact(args.artifact_dir, args.origin_run)
    status, obj = retrieve_once(handle, os.environ.get("OPENAI_API_KEY", ""))
    receipt = interpret(handle, status, obj)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "receipt.json").write_text(
        json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    if receipt["state"] == "COMPLETED":
        # Untrusted model output, retained for exact original-head review ONLY.
        (args.out / "untrusted_response.json").write_text(
            json.dumps(obj, sort_keys=True) + "\n")
    print(json.dumps({"state": receipt["state"], "http_status": status,
                      "origin_run_id": args.origin_run, "paid_post_performed": False,
                      "automatic_source_application": False}, sort_keys=True))


if __name__ == "__main__":
    main()
