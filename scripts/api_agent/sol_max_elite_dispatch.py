#!/usr/bin/env python3
"""Existing-S1 owner-comment Sol MAX submit/GET-only Actions adapter.

No private source, autonomous source write, new schedule, retry POST or merge.
Only a native, one-use GitHub issue-comment claim can admit a paid POST.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

from scripts.api_agent import sol_max_elite_transport as t

SUBMIT = re.compile(r"^\[S1_SOL_MAX_ELITE\] mission=(S1-[A-Z-]+-20261104)$")
COLLECT = re.compile(r"^\[S1_SOL_MAX_ELITE_COLLECT\] run=([1-9][0-9]{0,17})$")
MAX_ELITE_CLAIMS = 5
MINIMUM_FREE_AFTER_CLAIM_USD = 12.0
MAX_NEW_CLAIM_USD = 3.0


def gh(*args: str) -> str:
    if not os.environ.get("GH_TOKEN"):
        raise ValueError("GH_TOKEN_REQUIRED")
    return subprocess.check_output(["gh", *args], text=True, timeout=90)


def api(path: str) -> dict:
    return json.loads(gh("api", "repos/" + t.REPO + "/" + path))


def owner_event(event_file: Path, *, mode: str) -> tuple[str, dict]:
    try:
        event = json.loads(event_file.read_text())
    except (OSError, ValueError) as exc:
        raise ValueError("ELITE_NATIVE_OWNER_EVENT_UNAVAILABLE") from exc
    comment = event.get("comment") or {}
    issue = event.get("issue") or {}
    body = comment.get("body")
    if (issue.get("number") != t.ISSUE
            or comment.get("author_association") != "OWNER"
            or (comment.get("user") or {}).get("login") != "Donh91"
            or os.environ.get("GITHUB_EVENT_NAME") != "issue_comment"
            or os.environ.get("GITHUB_ACTOR") != "Donh91"
            or os.environ.get("GITHUB_REPOSITORY") != t.REPO):
        raise ValueError("ELITE_NOT_OWNER_ISSUE_COMMENT")
    pattern = SUBMIT if mode == "submit" else COLLECT
    m = pattern.fullmatch(body.strip()) if isinstance(body, str) else None
    if m is None:
        raise ValueError("ELITE_COMMENT_MARKER_INVALID")
    return m.group(1), event


def current_checkout(root: Path) -> str:
    head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"],
                                   text=True, timeout=20).strip()
    if t.HEX40.fullmatch(head) is None:
        raise ValueError("ELITE_CHECKOUT_NOT_SHA")
    native_head = api("git/ref/heads/main").get("object", {}).get("sha")
    if native_head != head or os.environ.get("GITHUB_SHA") != head:
        raise ValueError("ELITE_STALE_MAIN_NO_PAYMENT")
    return head


def preflight(root: Path, out: Path, event_file: Path) -> dict:
    mission, event = owner_event(event_file, mode="submit")
    head = current_checkout(root)
    result = t.render_source(root, mission, head)
    request = t.checked_request(result["packet"])
    out.mkdir(parents=True, exist_ok=True)
    (out / "source.json").write_bytes(t.canonical(result["packet"]))
    (out / "request.json").write_bytes(t.canonical(request))
    batch = t.read_registration(root)
    state, gate = "GATED", "OWNER_DISPATCH_NOT_RELEASED"
    try:
        t.require_paid_authority(batch)
        state, gate = "READY", "NATIVE_COST_AND_CLAIM_CHECK_NEXT"
    except ValueError as exc:
        gate = str(exc)
    admission = {
        "contract": "S1_SOL_ELITE_ADMISSION_v1",
        "mission": mission, "head": head, "state": state,
        "paid_allowed": state == "READY",
        "gate": gate, "source_sha256": result["context_sha256"],
        "request_sha256": t.digest(t.canonical(request)),
        "trigger_comment_id": (event["comment"] or {}).get("id"),
        "estimated_max_usd": result["cost_ceiling_usd"],
        "no_new_paid_post_when_gated": True,
    }
    (out / "admission.json").write_bytes(t.canonical(admission))
    return admission


def all_native_claims() -> list[dict]:
    try:
        pages = json.loads(gh("api", "--paginate", "--slurp",
                             f"repos/{t.REPO}/issues/{t.ISSUE}/comments?per_page=100"))
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        raise ValueError("ELITE_NATIVE_CLAIM_CENSUS_UNAVAILABLE") from exc
    if not isinstance(pages, list) or not pages or any(not isinstance(p, list) for p in pages):
        raise ValueError("ELITE_NATIVE_CLAIM_CENSUS_UNTRUSTED")
    claims = []
    pattern = re.compile(
        r"^S1_SOL_ELITE_NATIVE_PAID_CLAIM_V1 MISSION=S1-[A-Z-]+-20261104 "
        r"HEAD=[0-9a-f]{40} CLAIM=[0-9a-f]{64} MAX_USD=3[.]00$")
    for page in pages:
        for row in page:
            if not isinstance(row, dict):
                raise ValueError("ELITE_NATIVE_CLAIM_ROW_INVALID")
            body = str(row.get("body") or "").strip()
            if body.startswith(t.CLAIM_PREFIX):
                if (row.get("user") or {}).get("login") != "github-actions[bot]" or not pattern.fullmatch(body):
                    raise ValueError("ELITE_NATIVE_CLAIM_SCHEMA_OR_ACTOR_INVALID")
                claims.append(row)
    return claims


def check_budget(root: Path, claims: list[dict]) -> dict:
    process = subprocess.run([
        "python", "scripts/api_agent/check_monthly_cost_guard.py",
        "--receipt-root", "research/api_agent/outputs",
        "--hard-stop-usd", "30", "--reserve-usd", "12"],
        cwd=root, capture_output=True, text=True, check=False, timeout=90)
    if process.returncode != 0:
        raise ValueError("ELITE_MONTHLY_BUDGET_GUARD_FAILED")
    try:
        result = json.loads(process.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError) as exc:
        raise ValueError("ELITE_COST_RECEIPT_UNVERIFIABLE") from exc
    remaining = result.get("remaining_usd")
    if (result.get("status") != "PASS"
            or not isinstance(remaining, (float, int))
            or isinstance(remaining, bool)
            or len(claims) >= MAX_ELITE_CLAIMS
            # A claim is never released automatically, even after a known ID.
            or remaining <= MINIMUM_FREE_AFTER_CLAIM_USD +
                 (len(claims) + 1) * MAX_NEW_CLAIM_USD):
        raise ValueError("ELITE_NATIVE_BUDGET_OR_CLAIM_LIMIT")
    return {"remaining": remaining, "already_claimed": len(claims)}


def require_original_owner_run(head: str) -> dict:
    if (os.environ.get("GITHUB_RUN_ATTEMPT") != "1"
            or os.environ.get("GITHUB_EVENT_NAME") != "issue_comment"):
        raise ValueError("ELITE_RERUN_OR_DIFFERENT_EVENT_NO_POST")
    rid = os.environ.get("GITHUB_RUN_ID")
    if not rid or not re.fullmatch(r"[1-9][0-9]{0,17}", rid):
        raise ValueError("ELITE_RUN_ID_MISSING")
    run = api("actions/runs/" + rid)
    if (str(run.get("id")) != rid
            or run.get("head_sha") != head
            or run.get("event") != "issue_comment"
            or run.get("name") != "Framework Learning Supervisor"
            or (run.get("actor") or {}).get("login") != "Donh91"):
        raise ValueError("ELITE_NATIVE_OWNER_RUN_INVALID")
    return run


def reserve(root: Path, out: Path, event_file: Path) -> dict:
    mission, _ = owner_event(event_file, mode="submit")
    admission = json.loads((out / "admission.json").read_text())
    source = json.loads((out / "source.json").read_text())
    request = json.loads((out / "request.json").read_text())
    batch = t.read_registration(root)
    t.require_paid_authority(batch)
    head = current_checkout(root)
    if (admission.get("mission") != mission or admission.get("head") != head
            or admission.get("state") != "READY"
            or admission.get("paid_allowed") is not True
            or admission.get("source_sha256") != t.digest(t.canonical(source))
            or admission.get("request_sha256") != t.digest(t.canonical(request))
            or request != t.checked_request(source)
            or source.get("mission_id") != mission):
        raise ValueError("ELITE_PREFLIGHT_OR_SOURCE_DRIFT")
    run = require_original_owner_run(head)
    claims = all_native_claims()
    t.check_unspent_claim(claims, mission)
    cost = check_budget(root, claims)
    body = t.claim_body(mission, head, admission["request_sha256"])
    # This is the ONE durable pre-HTTP claim. Losing the response ID can NEVER
    # authorize a second POST or replacement claim for this mission.
    gh("issue", "comment", str(t.ISSUE), "--repo", t.REPO, "--body", body)
    evidence = [row for row in all_native_claims() if str(row.get("body") or "").strip() == body]
    if len(evidence) != 1 or type(evidence[0].get("id")) is not int:
        raise ValueError("ELITE_PAID_CLAIM_NATIVE_READBACK_FAILED")
    claim = {
        "status": "NATIVE_VERIFIED_PRE_HTTP",
        "id": evidence[0]["id"], "body": body,
        "mission": mission, "source_head": head,
        "origin_run_id": str(run["id"]),
        "estimated_cost_ceiling_usd": admission["estimated_max_usd"],
        "remaining_before_claim_usd": cost["remaining"],
    }
    (out / "reservation.json").write_bytes(t.canonical(claim))
    return claim


def submit(root: Path, out: Path, event_file: Path) -> dict:
    mission, _ = owner_event(event_file, mode="submit")
    batch = t.read_registration(root)
    request = json.loads((out / "request.json").read_text())
    claim = json.loads((out / "reservation.json").read_text())
    if claim["mission"] != mission or current_checkout(root) != claim["source_head"]:
        raise ValueError("ELITE_CLAIM_MAIN_DRIFT")
    key = os.environ.get("OPENAI_API_KEY", "")
    return t.submit_one(root, batch, request, claim, out / "post", key,
                        native_reader=api, environment=os.environ)


def collect(out: Path, artifact: Path, event_file: Path) -> dict:
    origin, _ = owner_event(event_file, mode="collect")
    if os.environ.get("GITHUB_RUN_ATTEMPT") != "1":
        raise ValueError("ELITE_COLLECT_RERUN_DISALLOWED")
    source = json.loads((artifact / "source.json").read_text())
    request = json.loads((artifact / "request.json").read_text())
    claim = json.loads((artifact / "reservation.json").read_text())
    handle = json.loads((artifact / "post/response_handle.json").read_text())
    if (claim.get("origin_run_id") != origin
            or claim.get("source_head") != source.get("source_head")
            or handle.get("claim_id") != claim.get("id")
            or handle.get("claim_body") != claim.get("body")
            or request != t.checked_request(source)
            or t.digest(t.canonical(request)) not in claim.get("body", "")):
        raise ValueError("ELITE_ORIGIN_ARTIFACT_DRIFT")
    native = api("actions/runs/" + origin)
    comment = api("issues/comments/" + str(claim["id"]))
    if (native.get("name") != "Framework Learning Supervisor"
            or native.get("event") != "issue_comment"
            or native.get("head_sha") != claim["source_head"]
            or (native.get("actor") or {}).get("login") != "Donh91"
            or (comment.get("user") or {}).get("login") != "github-actions[bot]"
            or str(comment.get("body") or "").strip() != claim["body"]):
        raise ValueError("ELITE_ORIGIN_NATIVE_PROOF_FAILED")
    status, response = t.collect_one(handle["response_id"],
                                      os.environ.get("OPENAI_API_KEY", ""))
    state = "GET_RETRY_ALLOWED_NO_POST"
    if status == 200 and response.get("status") in ("completed", "incomplete", "failed", "cancelled"):
        state = response["status"].upper()
    elif status == 404:
        state = "EXPIRED_NO_REPOST"
    elif status == 200:
        state = "PENDING_GET_ONLY"
    result = {
        "contract": "S1_SOL_ELITE_GET_RECEIPT_v1",
        "origin_run": origin, "response_id": handle["response_id"],
        "mission": claim["mission"], "source_head": claim["source_head"],
        "context_sha256": t.digest(t.canonical(source)),
        "status": state, "http_status": status,
        "provider_usage": response.get("usage") if status == 200 else None,
        "billing_status": "UNRECONCILED_ESTIMATE_ONLY",
        "new_paid_post": False, "source_applied": False,
        "merge_authorized": False,
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "receipt.json").write_bytes(t.canonical(result))
    if state == "COMPLETED":
        # Store the untrusted public-source response for actual independent
        # patch parsing and original-branch review; NEVER execute it here.
        (out / "provider_response.json").write_bytes(t.canonical(response))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=("preflight", "reserve", "submit", "collect"))
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path)
    parser.add_argument("--event-file", type=Path, required=True)
    args = parser.parse_args()
    if args.operation == "preflight":
        result = preflight(args.repo_root, args.output_dir, args.event_file)
    elif args.operation == "reserve":
        result = reserve(args.repo_root, args.output_dir, args.event_file)
    elif args.operation == "submit":
        result = submit(args.repo_root, args.output_dir, args.event_file)
    else:
        if args.artifact_dir is None:
            raise ValueError("ELITE_COLLECT_ARTIFACT_REQUIRED")
        result = collect(args.output_dir, args.artifact_dir, args.event_file)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
