"""Owner-gated GET-only recovery probe for existing Sol MAX response.

It makes no POST, claims no budget, writes no source, and never treats a
response for an older PR source HEAD as current patch authority.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

REPO = "Donh91/Investering-Framework-Archive-v1"
PR = 1877
SOURCE_HEAD = "c41c82751d191dbfe9309ff7fa5bf15acb2fd817"
RESPONSE_ID = "resp_03e71ec085f63bf5006aeb2721ec5487d19d2d452c126d1336"
LAUNCH_MESSAGE = "chore(s1): GET-only recover Sol MAX response 41830814618 [S1_SOL_GET_RESCUE_20261104]"

def authorized(head, repo, *, git_run=subprocess.check_output):
    if repo != REPO or not re.fullmatch(r"[0-9a-f]{40}", head):
        raise ValueError("BAD_REPO_OR_HEAD")
    live = git_run(["git", "rev-parse", "HEAD"], text=True, timeout=30).strip()
    subject = git_run(["git", "log", "-1", "--format=%s"], text=True, timeout=30).strip()
    if live != head:
        raise ValueError("CHECKOUT_HEAD_DRIFT")
    if subject != LAUNCH_MESSAGE:
        return False
    if not os.environ.get("GH_TOKEN"):
        raise ValueError("NATIVE_HEAD_READBACK_REQUIRED")
    native = json.loads(git_run(
        ["gh", "api", f"repos/{repo}/pulls/{PR}"], text=True, timeout=45))
    return (native.get("state") == "open"
            and native.get("draft") is False
            and native.get("head", {}).get("sha") == head
            and native.get("head", {}).get("repo", {}).get("full_name") == repo)

def fetch_once(key, *, urlopen=urllib.request.urlopen):
    if not key:
        raise ValueError("OPENAI_KEY_MISSING")
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses/" + RESPONSE_ID,
        headers={"Authorization": "Bearer " + key}, method="GET")
    try:
        with urlopen(request, timeout=35) as response:
            if response.status != 200:
                return response.status, {}
            raw = response.read(1_000_001)
            if len(raw) > 1_000_000:
                raise ValueError("PROVIDER_RESPONSE_TOO_LARGE")
            return 200, json.loads(raw)
    except urllib.error.HTTPError as exc:
        return exc.code, {}

def interpret(http, response):
    receipt = {
        "contract": "S1_SOL_MAX_GET_ONLY_PROBE_v1",
        "response_id": RESPONSE_ID,
        "original_source_head": SOURCE_HEAD,
        "http_status": http,
        "paid_post_performed": False,
        "automatic_patch_application": False,
        "provider_billing": "NOT_RECONCILED",
    }
    if http == 404:
        receipt["state"] = "EXPIRED_OR_NOT_STORED"
        return receipt, None
    if http in (429, 500, 502, 503, 504):
        receipt["state"] = "TRANSIENT_GET_ERROR"
        return receipt, None
    if http != 200:
        receipt["state"] = "RETRIEVAL_DENIED_OR_UNKNOWN"
        return receipt, None
    if response.get("id") != RESPONSE_ID:
        receipt["state"] = "MISMATCHED_RESPONSE_ID"
        return receipt, None
    status = response.get("status")
    if status not in ("queued", "in_progress", "completed", "incomplete", "failed", "cancelled"):
        receipt["state"] = "UNKNOWN_PROVIDER_STATUS"
        return receipt, None
    receipt["state"] = "PENDING_COLLECT" if status in ("queued", "in_progress") else status.upper()
    usage = response.get("usage") or {}
    receipt["usage"] = {
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "reasoning_tokens": (usage.get("output_tokens_details") or {}).get("reasoning_tokens"),
    }
    receipt["incomplete_details"] = response.get("incomplete_details")
    # Never print raw model output to public logs or autoapply it to a newer HEAD.
    return receipt, response if status == "completed" else None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--head", required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("runtime/sol-get-only"))
    args = parser.parse_args()
    if not authorized(args.head, os.environ.get("GITHUB_REPOSITORY", "")):
        print('{"status":"NOT_AUTHORIZED_GET_ONLY_LAUNCH"}')
        return
    receipt, completed = interpret(*fetch_once(os.environ.get("OPENAI_API_KEY", "")))
    receipt["launch_head"] = args.head
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "receipt.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    if completed is not None:
        (args.output_dir / "untrusted_response.json").write_text(
            json.dumps(completed, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in receipt.items()
                      if k not in ("usage", "incomplete_details")}, sort_keys=True))

if __name__ == "__main__":
    main()
