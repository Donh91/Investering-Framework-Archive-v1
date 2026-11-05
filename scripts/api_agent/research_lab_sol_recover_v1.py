"""GET-only continuation for a native owner-paid Research Lab Sol background run.

This uses the existing Research Lab owner/workflow/issue. It does not create a
new paid claim, POST, supervisor, scheduler or independent source authority.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

from scripts.api_agent import api_gateway as gateway
from scripts.api_agent import recoverable_responses_v1 as transport

REPO = "Donh91/Investering-Framework-Archive-v1"
CLAIM_PREFIX = "RL_SOL_MAX_PRE_HTTP_CLAIM_V1"
ID = re.compile(r"[1-9][0-9]{0,17}\Z")
SHA40 = re.compile(r"[a-f0-9]{40}\Z")


def gh_api(path: str):
    result = subprocess.check_output(
        ["gh", "api", "repos/" + REPO + "/" + path],
        text=True, timeout=90,
    )
    return json.loads(result)


def _read(path: Path):
    return json.loads(path.read_text())


def parse_owner_collect(event_path: Path) -> str:
    event = _read(event_path)
    body = (event.get("comment") or {}).get("body")
    match = re.fullmatch(r"\[RESEARCH_LAB_SOL_COLLECT\] origin=([1-9][0-9]{0,17})",
                         body.strip() if isinstance(body, str) else "")
    if (not match or os.environ.get("GITHUB_EVENT_NAME") != "issue_comment"
            or os.environ.get("GITHUB_ACTOR") != "Donh91"
            or os.environ.get("GITHUB_REPOSITORY") != REPO
            or os.environ.get("GITHUB_RUN_ATTEMPT") != "1"
            or (event.get("issue") or {}).get("number") != 1476
            or (event.get("comment") or {}).get("author_association") != "OWNER"
            or ((event.get("comment") or {}).get("user") or {}).get("login") != "Donh91"):
        raise ValueError("RECOVERY_NOT_AUTHENTICATED_OWNER_COMMENT")
    return match.group(1)


def verify_original(origin: str, artifact: Path, *, fetch=gh_api) -> dict:
    """Verify origin's genuine billing claim before trusting any artifact."""
    if not ID.fullmatch(origin):
        raise ValueError("RECOVERY_RUN_ID_INVALID")
    manifest = _read(artifact / "context_manifest.json")
    context = _read(artifact / "context.json")
    registry = _read(artifact / "effective_registry.json")
    attempt = _read(artifact / "output" / "transport" / "attempt.json")
    handle = _read(artifact / "output" / "transport" / "response_handle.json")
    source_sha = manifest.get("current_main_sha")
    mission = manifest.get("mission_id")
    trigger = manifest.get("comment_id")
    cfg = (registry.get("tasks") or {}).get("RESEARCH_LAB_SOL_ANALYSIS") or {}
    if (not isinstance(source_sha, str) or SHA40.fullmatch(source_sha) is None
            or not isinstance(mission, str)
            or not isinstance(trigger, str) or not ID.fullmatch(trigger)
            or manifest.get("context_sha256") != gateway.sha256_bytes(
                (artifact / "context.json").read_bytes())
            or context.get("mission_id") != mission
            or context.get("private_data_included") is not False
            or context.get("public_source_only") is not True
            or context.get("authority") != "ADVISORY_READ_ONLY"
            or (cfg.get("model"), cfg.get("reasoning_effort")) != ("gpt-6.1-sol", "max")
            or cfg.get("recoverable_background") is not True
            or cfg.get("public_background_storage_authorized") is not True
            or cfg.get("max_attempts") != 1
            or attempt.get("state") != "POST_OUTCOME_UNKNOWN"
            or attempt.get("max_paid_posts") != 1
            or handle.get("state") != "GET_ONLY"):
        raise ValueError("RECOVERY_PUBLIC_SOURCE_OR_HANDLE_INVALID")
    run = fetch("actions/runs/" + origin)
    comment = fetch("issues/comments/" + trigger)
    if (str(run.get("id")) != origin
            or run.get("event") != "issue_comment"
            or run.get("name") != "Research Lab Sol Mission Dispatcher"
            # The event SHA may predate the checkout of main. The checkout's
            # exact source SHA is independently frozen by the bot's native
            # pre-HTTP claim, the source manifest and the request hash.
            or not isinstance(run.get("head_sha"), str)
            or SHA40.fullmatch(run["head_sha"]) is None
            or (run.get("actor") or {}).get("login") != "Donh91"
            or (comment.get("user") or {}).get("login") != "Donh91"
            or (comment.get("issue_url") or "").rstrip("/") !=
                "https://api.github.com/repos/" + REPO + "/issues/1476"
            or "[RESEARCH_LAB_SOL] mission=" + mission not in
                (comment.get("body") or "")):
        raise ValueError("RECOVERY_ORIGIN_RUN_OR_OWNER_NOT_AUTHENTICATED")
    # The unique pre-HTTP claim is owned by github-actions[bot], never
    # reconstructed from the user's own comment or an uploaded artifact.
    found = []
    page = 1
    while True:
        rows = fetch("issues/1476/comments?per_page=100&page=" + str(page))
        if not isinstance(rows, list):
            raise ValueError("RECOVERY_CLAIM_CENSUS_INVALID")
        found += [r for r in rows if str(r.get("body") or "").strip() ==
                  (CLAIM_PREFIX + " mission=" + mission + " head=" + source_sha +
                   " trigger=" + trigger + " max_usd=3.00")
                  and (r.get("user") or {}).get("login") == "github-actions[bot]"]
        if len(rows) < 100:
            break
        page += 1
        if page > 100:
            raise ValueError("RECOVERY_CLAIM_CENSUS_TOO_LARGE")
    if len(found) != 1:
        raise ValueError("RECOVERY_NATIVE_PRE_HTTP_CLAIM_NOT_UNIQUE")
    # Recompute request bytes and compare to both immutable transport
    # records. The subsequent api_gateway --resume-background repeats this.
    payload = gateway.build_request("RESEARCH_LAB_SOL_ANALYSIS", cfg,
                                    (artifact / "prompt.txt").read_text(), context)
    payload.update({"background": True, "store": True})
    expected = transport.digest(payload)
    if attempt.get("request_sha256") != expected or handle.get("request_sha256") != expected:
        raise ValueError("RECOVERY_API_REQUEST_HASH_MISMATCH")
    return {"status": "AUTHENTICATED_ORIGIN_GET_ONLY", "mission": mission,
            "trigger_comment": trigger, "origin_run": origin,
            "source_main_sha": source_sha,
            "claim_comment_id": found[0].get("id"),
            "response_id": handle.get("response_id"),
            "additional_paid_posts": 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-file", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-origin", required=True)
    args = parser.parse_args()
    actual = parse_owner_collect(args.event_file)
    if actual != args.expected_origin:
        raise SystemExit("RECOVERY_COMMENT_ORIGIN_MISMATCH")
    verified = verify_original(actual, args.artifact_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(verified, sort_keys=True, indent=2) + "\n")
    print(json.dumps(verified, sort_keys=True))


if __name__ == "__main__":
    main()
