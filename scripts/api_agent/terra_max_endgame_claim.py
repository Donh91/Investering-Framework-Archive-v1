#!/usr/bin/env python3
"""Atomic-enough one-time API liability claim under GitHub Actions serial concurrency.

This helper never calls OpenAI. A published GitHub issue comment is the durable
no-retry latch. If creation is uncertain, execution stops before any paid call.
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request

REPOSITORY = "Donh91/Investering-Framework-Archive-v1"
ISSUE = 1156
MARKER = "[TERRA_MAX_ENDGAME_ONCE_CLAIM_v1]"
BOT = "github-actions[bot]"


def api(method: str, route: str, payload: dict | None = None) -> dict | list:
    token = os.environ.get("GH_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_ISSUE_TOKEN_UNAVAILABLE")
    data = None if payload is None else json.dumps(payload, separators=(",", ":")).encode()
    req = urllib.request.Request(
        "https://api.github.com" + route,
        data=data,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + token,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "terra-max-owner-once/1",
            "Content-Type": "application/json",
        },
        method=method,
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        raw = response.read(400_001)
    if len(raw) > 400_000:
        raise RuntimeError("GITHUB_RECEIPT_RESPONSE_TOO_LARGE")
    return json.loads(raw)


def existing_claim() -> dict | None:
    route = "/repos/" + REPOSITORY + "/issues/" + str(ISSUE) + "/comments"
    for page in range(1, 15):
        comments = api("GET", route + "?per_page=100&page=" + str(page))
        if not isinstance(comments, list):
            raise RuntimeError("INVALID_GITHUB_ISSUE_COMMENT_COLLECTION")
        for comment in comments:
            if (
                (comment.get("user") or {}).get("login") == BOT
                and str(comment.get("body") or "").startswith(MARKER)
            ):
                return {"id": comment.get("id"), "url": comment.get("html_url")}
        if len(comments) < 100:
            return None
    raise RuntimeError("GITHUB_COMMENT_CENSUS_NOT_EXHAUSTIVE")


def claim(run_id: str, source_sha: str) -> dict:
    if os.environ.get("GITHUB_ACTOR") != "Donh91":
        raise RuntimeError("GITHUB_OWNER_ACTOR_REQUIRED")
    if os.environ.get("GITHUB_RUN_ATTEMPT") != "1":
        raise RuntimeError("NO_PAID_RERUN")
    if not run_id.isdecimal() or len(source_sha) != 40:
        raise RuntimeError("INVALID_SOURCE_RUN_BINDING")
    if existing_claim():
        raise RuntimeError("ONE_TIME_PAID_LIABILITY_ALREADY_CLAIMED")
    body = "\n".join(
        [
            MARKER,
            "",
            "Owner-authorized one-time public-source Terra Max endgame API liability.",
            "Action run: https://github.com/" + REPOSITORY + "/actions/runs/" + run_id,
            "Frozen source main SHA: " + source_sha,
            "Model: gpt-6.1-terra / reasoning max; exactly one API attempt.",
            "Budget: existing USD 40 monthly hard stop and USD 3 single-call ceiling.",
            "No automatic paid retries. Any missing API receipt is UNKNOWN liability.",
            "No AppDeploy, code writes, merge, market authority or trades.",
        ]
    )
    route = "/repos/" + REPOSITORY + "/issues/" + str(ISSUE) + "/comments"
    result = api("POST", route, {"body": body})
    if not isinstance(result, dict) or not isinstance(result.get("id"), int):
        raise RuntimeError("GITHUB_CLAIM_ACK_UNVERIFIED_NO_PAID_CALL")
    return {"claim_id": result["id"], "claim_url": result.get("html_url"), "run_id": run_id}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--run-id", required=True)
    p.add_argument("--source-sha", required=True)
    args = p.parse_args()
    print(json.dumps(claim(args.run_id, args.source_sha), sort_keys=True))


if __name__ == "__main__":
    main()
