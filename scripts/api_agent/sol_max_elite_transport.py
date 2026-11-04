#!/usr/bin/env python3
"""Source-bound, no-surprise transport for existing owner-approved Sol MAX tasks.

The model never receives git credentials or acquires repository write authority.
Production remains gated until both original billing and public storage consent
are independently recorded. A timed-out POST is an UNKNOWN paid attempt, never
permission to repeat the same request.
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
from datetime import date
from pathlib import Path
from typing import Any

REPO = "Donh91/Investering-Framework-Archive-v1"
BATCH = "research/api_agent/coordination/S1_SOL_MAX_ELITE_BOUNDED_BATCH_20261104.json"
MODEL, EFFORT = "gpt-6.1-sol", "max"
ISSUE = 1156
CLAIM_PREFIX = "S1_SOL_ELITE_NATIVE_PAID_CLAIM_V1"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
RESPONSE_ID = re.compile(r"^resp_[A-Za-z0-9_-]{4,180}$")
MISSION_ID = re.compile(r"^S1-[A-Z]+(?:-[A-Z]+)*-20261104$")
SOURCE_MAX = 120000
FILE_MAX = 35000
OUTPUT_TOKENS = 45000
INPUT_BOUND = 145000
INPUT_PRICE, OUTPUT_PRICE = 2.0, 10.0
PRICING_RECHECK_AFTER = date(2026, 12, 4)
CREDENTIALS = (
    rb"sk-proj-[A-Za-z0-9_-]{16,}",
    rb"ghp_[A-Za-z0-9]{20,}",
    rb"github_pat_[A-Za-z0-9_-]{16,}",
    rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
)


def canonical(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_safe_relative(path: str) -> None:
    if not isinstance(path, str) or not path:
        raise ValueError("SOURCE_PATH_NOT_PUBLIC_ALLOWLISTED")
    p = Path(path)
    if (p.is_absolute()
            or any(part in (".", "..", "") for part in p.parts)
            or str(p) != path or path.startswith(("Donh91/", ".git/"))
            or any(part.casefold() in ("secrets", "vault", ".env", "private")
                   for part in p.parts)):
        raise ValueError("SOURCE_PATH_NOT_PUBLIC_ALLOWLISTED")


def read_registration(root: Path) -> dict:
    try:
        obj = json.loads((root / BATCH).read_text())
    except (OSError, UnicodeError, ValueError) as exc:
        raise ValueError("ELITE_REGISTRATION_MISSING_OR_INVALID") from exc
    if not isinstance(obj, dict):
        raise ValueError("ELITE_REGISTRATION_NOT_OBJECT")
    pay = obj.get("payment_policy")
    status = obj.get("state")
    active = status == "OWNER_APPROVED_DISPATCH"
    if (status not in ("REGISTERED_NOT_EXECUTING", "OWNER_APPROVED_DISPATCH")
            or obj.get("dispatch_enabled") is not active
            or obj.get("contract") != "S1_SOL_MAX_ELITE_BOUNDED_BATCH_v1"
            or obj.get("repo") != REPO
            or (obj.get("model"), obj.get("reasoning_effort")) != (MODEL, EFFORT)
            or not isinstance(pay, dict)
            or (pay.get("owner_monthly_hard_stop_usd"),
                pay.get("owner_global_reserve_usd"), pay.get("per_call_max_usd")) != (30, 12, 3)
            or pay.get("do_not_retry_unresolved_paid_post") is not True
            or pay.get("no_auto_paid_trigger_until_reconciled") is not (not active)
            or obj.get("max_concurrent_paid_missions") != 1
            or obj.get("forbid_new_scheduler_agent_or_writer") is not True):
        raise ValueError("ELITE_REGISTRATION_CONTRACT_INVALID")
    missions = obj.get("definitions")
    if not isinstance(missions, list) or len(missions) != 5:
        raise ValueError("ELITE_MISSION_CENSUS_INVALID")
    ids = [item.get("id") for item in missions if isinstance(item, dict)]
    if (len(ids) != 5 or any(not isinstance(k, str) for k in ids)
            or len(set(ids)) != 5):
        raise ValueError("ELITE_MISSION_CENSUS_INVALID")
    return obj


def choose(root: Path, mission: str) -> tuple[dict, dict]:
    if not isinstance(mission, str) or MISSION_ID.fullmatch(mission) is None:
        raise ValueError("INVALID_ELITE_MISSION_ID")
    batch = read_registration(root)
    matching = [item for item in batch["definitions"]
                if isinstance(item, dict) and item.get("id") == mission]
    if len(matching) != 1:
        raise ValueError("ELITE_MISSION_NOT_REGISTERED")
    item = matching[0]
    if (item.get("owner_issue") not in (1156, 1157, 1516)
            or item.get("priority") not in ("P0", "P1")
            or not isinstance(item.get("scope"), list)
            or len(item["scope"]) not in range(1, 10)
            or len(set(item["scope"])) != len(item["scope"])):
        raise ValueError("ELITE_MISSION_SCOPE_INVALID")
    return batch, item


def render_source(root: Path, mission: str, head: str) -> dict:
    """Bind exact public source bytes and all requested test targets."""
    if HEX40.fullmatch(head) is None:
        raise ValueError("SOURCE_HEAD_INVALID")
    batch, item = choose(root, mission)
    sources, total = {}, 0
    for path in sorted(item["scope"]):
        check_safe_relative(path)
        try:
            real = (root / path).resolve(strict=True)
            if not real.is_relative_to(root.resolve(strict=True)) or not real.is_file():
                raise ValueError("NON_FILE_OR_PATH_ESCAPE")
            body = real.read_bytes()
        except (OSError, RuntimeError, ValueError) as exc:
            raise ValueError("ELITE_PUBLIC_SOURCE_UNAVAILABLE:" + path) from exc
        total += len(body)
        if len(body) > FILE_MAX or total > SOURCE_MAX or any(
                re.search(pattern, body) for pattern in CREDENTIALS):
            raise ValueError("ELITE_PUBLIC_SOURCE_OVERSIZED_OR_SECRET:" + path)
        try:
            content = body.decode("utf-8")
        except UnicodeError as exc:
            raise ValueError("ELITE_SOURCE_NOT_TEXT") from exc
        sources[path] = {"sha256": digest(body), "bytes": len(body), "content": content}
    if not sources:
        raise ValueError("ELITE_SOURCE_EMPTY")
    packet = {
        "contract": "S1_SOL_ELITE_SOURCE_PACKET_v1",
        "repo": REPO, "source_head": head,
        "mission_id": mission, "original_owner_issue": item["owner_issue"],
        "original_pr": item.get("original_pr"), "source_files": sources,
        "instructions": item["deliverable"],
        "tests_required": item["tests"], "kill_condition": item["kill"],
        "authority": "PATCH_CANDIDATE_ONLY_NO_SOURCE_WRITE_NO_MERGE",
    }
    raw = canonical(packet)
    if len(raw) > SOURCE_MAX + 20000:
        raise ValueError("ELITE_PACKET_OVERSIZED")
    return {"packet": packet, "context_sha256": digest(raw),
            "source_head": head, "file_count": len(sources),
            "dispatch_enabled": batch.get("dispatch_enabled") is True,
            "state": batch.get("state"),
            "cost_ceiling_usd": expected_max_cost()}


def expected_max_cost() -> float:
    if date.today() > PRICING_RECHECK_AFTER:
        raise ValueError("ELITE_PRICING_STALE")
    # One-token-per-byte conservatively bounds the <=140 kB public packet.
    upper = (INPUT_BOUND * INPUT_PRICE + OUTPUT_TOKENS * OUTPUT_PRICE) / 1_000_000
    if upper > 3:
        raise ValueError("ELITE_COST_CAP_EXCEEDED")
    return round(upper, 6)


def require_paid_authority(batch: dict) -> None:
    # New owner qualification has to be recorded in a reviewable main commit.
    # We refuse to infer consent from the old PR1877-specific approval.
    if (batch.get("dispatch_enabled") is not True
            or batch.get("state") != "OWNER_APPROVED_DISPATCH"
            or batch.get("public_storage_consent_30_days") is not True
            or batch.get("billing_liability_for_run_41870364609") != "RECONCILED"
            or batch.get("payment_policy", {}).get("no_auto_paid_trigger_until_reconciled") is not False):
        raise ValueError("ELITE_PAID_DISPATCH_STILL_GATED")


def checked_request(packet: dict) -> dict:
    instructions = (
        "You are an advisory public-source code-patch author, never a GitHub writer. "
        "Return a minimal code diff limited to the source_files keys, or ABSTAIN. "
        "No credentials, new workflows, bypasses, invented source attestation, "
        "fictional tests, market/trade authority, or historical forecast rewrites. "
        "Tests and edge cases must be explicit; always preserve fail-closed behavior."
    )
    return {
        "model": MODEL, "reasoning": {"effort": EFFORT},
        "max_output_tokens": OUTPUT_TOKENS, "background": True, "store": True,
        "instructions": instructions,
        "input": [{"role": "user", "content": [
            {"type": "input_text", "text": canonical(packet).decode()}]}],
        "text": {"format": {"type": "json_schema", "name": "s1_sol_elite_patch_v1",
            "strict": True, "schema": {"type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["PATCH", "ABSTAIN"]},
                    "unified_diff": {"type": "string"},
                    "rationale": {"type": "string"},
                    "tests": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["status", "unified_diff", "rationale", "tests"],
                "additionalProperties": False}}},
    }


def claim_body(mission: str, head: str, claim_key: str) -> str:
    if (MISSION_ID.fullmatch(mission) is None or HEX40.fullmatch(head) is None
            or re.fullmatch(r"[0-9a-f]{64}", claim_key) is None):
        raise ValueError("ELITE_CLAIM_INVALID")
    return f"{CLAIM_PREFIX} MISSION={mission} HEAD={head} CLAIM={claim_key} MAX_USD=3.00"


def check_unspent_claim(comments: list[dict], mission: str) -> None:
    """A claim locks a mission forever until separately reconciled by owner."""
    for item in comments:
        body = str(item.get("body") or "")
        if (body.startswith(CLAIM_PREFIX)
                and f" MISSION={mission} " in body
                and (item.get("user") or {}).get("login") == "github-actions[bot]"):
            raise ValueError("ELITE_MISSION_ALREADY_CLAIMED_NO_REPOST")


def verify_native_claim(claim: dict, request_payload: dict, *,
                        native_reader, environment: dict) -> None:
    """Check real actor/run and unique hash-bound bot claim before paid POST.

    GitHub's workflow concurrency must serialize claims across all eligible
    paid lanes. A rerun of the original workflow attempt is never billable.
    """
    if (claim.get("status") != "NATIVE_VERIFIED_PRE_HTTP"
            or type(claim.get("id")) is not int or claim["id"] < 1
            or not isinstance(claim.get("body"), str)
            or not isinstance(claim.get("mission"), str)
            or not isinstance(claim.get("source_head"), str)
            or not isinstance(claim.get("origin_run_id"), str)
            or environment.get("GITHUB_RUN_ATTEMPT") != "1"
            or environment.get("GITHUB_RUN_ID") != claim["origin_run_id"]
            or environment.get("GITHUB_ACTOR") != "Donh91"
            or environment.get("GITHUB_REPOSITORY") != REPO):
        raise ValueError("ELITE_NATIVE_CLAIM_OR_RUN_MISSING")
    expected = claim_body(claim["mission"], claim["source_head"],
                          digest(canonical(request_payload)))
    if claim["body"] != expected:
        raise ValueError("ELITE_NATIVE_CLAIM_HASH_MISMATCH")
    comment = native_reader("issues/comments/" + str(claim["id"]))
    run = native_reader("actions/runs/" + claim["origin_run_id"])
    if (str(comment.get("id")) != str(claim["id"])
            or str(comment.get("body") or "").strip() != expected
            or (comment.get("user") or {}).get("login") != "github-actions[bot]"
            or str(run.get("id")) != claim["origin_run_id"]
            or run.get("name") != "Framework Learning Supervisor"
            or run.get("event") != "issue_comment"
            or run.get("actor", {}).get("login") != "Donh91"
            or run.get("head_sha") != claim["source_head"]):
        raise ValueError("ELITE_NATIVE_CLAIM_NOT_AUTHENTICATED")



def attest_paid_source(root: Path, registration: dict, claim: dict,
                       request_payload: dict) -> None:
    """Prevent a model prompt from silently becoming a new source authority."""
    current = read_registration(root)
    if canonical(current) != canonical(registration):
        raise ValueError("ELITE_MAIN_REGISTRATION_CHANGED")
    mission, head = claim.get("mission"), claim.get("source_head")
    try:
        checkout = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL, timeout=15).decode().strip()
        dirty = subprocess.run(["git", "-C", str(root), "diff", "--quiet"],
                               timeout=15, check=False).returncode
        staged_dirty = subprocess.run(["git", "-C", str(root), "diff", "--cached", "--quiet"],
                                      timeout=15, check=False).returncode
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError("ELITE_SOURCE_GIT_ATTESTATION_UNAVAILABLE") from exc
    if checkout != head or dirty != 0 or staged_dirty != 0:
        raise ValueError("ELITE_CHECKOUT_HEAD_OR_DIRTY_SOURCE")
    expected = render_source(root, mission, head)["packet"]
    if canonical(request_payload) != canonical(checked_request(expected)):
        raise ValueError("ELITE_API_PAYLOAD_NOT_BOUND_TO_PUBLIC_CHECKOUT")

def submit_one(root: Path, registration: dict, request_payload: dict, claim: dict,
               output: Path, api_key: str, *, native_reader,
               environment: dict, post=urllib.request.urlopen) -> dict:
    """One externally claimed POST, UNKNOWN on any interruption; no retry."""
    require_paid_authority(registration)
    if (not api_key or request_payload.get("model") != MODEL
            or request_payload.get("background") is not True
            or request_payload.get("store") is not True
            or request_payload.get("reasoning", {}).get("effort") != EFFORT
            or request_payload.get("max_output_tokens") != OUTPUT_TOKENS
            or request_payload.get("input") is None):
        raise ValueError("ELITE_PROVIDER_REQUEST_UNAUTHORIZED")
    attest_paid_source(root, registration, claim, request_payload)
    verify_native_claim(claim, request_payload, native_reader=native_reader,
                        environment=environment)
    if output.exists():
        raise ValueError("ELITE_OUTPUT_ALREADY_EXISTS_NO_SECOND_POST")
    state = {"contract": "S1_SOL_ELITE_ATTEMPT_v1", "claim_id": claim["id"],
             "claim_body": claim["body"], "state": "POST_OUTCOME_UNKNOWN",
             "billable_attempts_allowed": 0}
    # A single immutable local attempt key prevents a different output path
    # from buying the SAME mission twice within one GitHub run attempt.
    marker = root / "runtime/s1-sol-elite-payment-lock" / (claim["mission"] + ".json")
    marker.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(marker, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise ValueError("ELITE_MISSION_ALREADY_SUBMITTED_IN_THIS_RUN") from exc
    with os.fdopen(fd, "wb") as lock:
        lock.write(canonical(state))
        lock.flush()
        os.fsync(lock.fileno())
    output.mkdir(parents=True, exist_ok=False)
    (output / "attempt.json").write_bytes(canonical(state))
    req = urllib.request.Request("https://api.openai.com/v1/responses",
          data=canonical(request_payload),
          headers={"Authorization": "Bearer " + api_key,
                   "Content-Type": "application/json"}, method="POST")
    try:
        with post(req, timeout=75) as res:
            response = json.loads(res.read(100000))
        rid = response.get("id")
        if not isinstance(rid, str) or RESPONSE_ID.fullmatch(rid) is None:
            raise ValueError("ELITE_RESPONSE_ID_MISSING")
        handle = {**state, "state": "SUBMITTED_GET_ONLY", "response_id": rid,
                  "provider_state": response.get("status")}
        (output / "response_handle.json").write_bytes(canonical(handle))
        (output / "attempt.json").write_bytes(canonical(handle))
        return handle
    except Exception:
        # No HTTP status, timeout, JSON parse or ID mismatch authorizes retry.
        (output / "attempt.json").write_bytes(canonical(state))
        raise


def collect_one(response_id: str, api_key: str,
                *, get=urllib.request.urlopen) -> tuple[int, dict]:
    if not isinstance(response_id, str) or RESPONSE_ID.fullmatch(response_id) is None or not api_key:
        raise ValueError("ELITE_GET_REQUIRES_VERIFIED_RESPONSE_ID_AND_KEY")
    req = urllib.request.Request("https://api.openai.com/v1/responses/" + response_id,
                                 headers={"Authorization": "Bearer " + api_key}, method="GET")
    try:
        with get(req, timeout=45) as res:
            raw = res.read(1_000_001)
            if len(raw) > 1_000_000:
                raise ValueError("ELITE_RESPONSE_OVERSIZED")
            body = json.loads(raw)
            if body.get("id") != response_id:
                raise ValueError("ELITE_RESPONSE_ID_MISMATCH")
            return res.status, body
    except urllib.error.HTTPError as exc:
        return exc.code, {}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["preflight", "collect"])
    p.add_argument("--repo-root", type=Path, default=Path("."))
    p.add_argument("--mission", default="")
    p.add_argument("--source-head", default="")
    p.add_argument("--output-dir", type=Path)
    p.add_argument("--response-id", default="")
    args = p.parse_args()
    if args.mode == "preflight":
        result = render_source(args.repo_root, args.mission, args.source_head)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "source.json").write_bytes(canonical(result["packet"]))
        result.pop("packet")
        print(json.dumps(result, sort_keys=True))
    elif args.mode == "collect":
        # This low-level command needs a separately native-verified handle.
        # A plain user-supplied response ID is not an execution credential.
        raise SystemExit("NATIVE_ARTIFACT_AND_CLAIM_VERIFICATION_REQUIRED")


if __name__ == "__main__":
    main()
