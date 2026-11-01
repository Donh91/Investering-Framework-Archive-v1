#!/usr/bin/env python3
"""One explicitly owner-authorized Terra High P0 repair analysis, no app or scheduler.

Only emits source-bound advisory evidence. Its PR CI dispatch is restricted to an
exact owner/branch and a durable issue-comment single-use claim before any API call.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import urllib.request
from pathlib import Path
from typing import Any

REPO = "Donh91/Investering-Framework-Archive-v1"
ISSUE = 1156
MARKER = "[TERRA_HIGH_P0_OWNER_ONCE_CLAIM_v1]"
BOT = "github-actions[bot]"
MODEL = "gpt-6.1-terra"
MODEL_EFFORT = "high"
MAX_CONTEXT_BYTES = 32000
PAGE_SIZE = 25
MAX_PAGES = 100
SOURCE_FILES = (
    "03_DAILY_CAPTURE_LOGS/hourly/LATEST.json",
    ".github/workflows/hourly-sequence-capture.yml",
    ".github/workflows/native-market-recovery.yml",
    "scripts/cycle_navigator/verify_hourly_pages_handoff.py",
    "scripts/data_ping/compass_event_refresh.py",
    "05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json",
)
CDN_URLS = (
    "https://donh91.github.io/Investering-Framework-Archive-v1/data/latest.json",
    "https://donh91.github.io/Investering-Framework-Archive-v1/data/publication-lineage.json",
)


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True, stderr=subprocess.STDOUT, timeout=20).strip()


def source_file(main_sha: str, path: str) -> dict:
    if path not in SOURCE_FILES:
        raise ValueError("PUBLIC_SOURCE_ALLOWLIST_REQUIRED")
    raw = subprocess.check_output(["git", "show", main_sha + ":" + path], timeout=25)
    # Always bind previews to exact file SHA. Unseen bytes are not evidence.
    text = raw.decode("utf-8", errors="replace")
    preview = text[:2800]
    return {
        "path": path, "bytes": len(raw), "sha256": sha(raw),
        "preview": preview, "clipped": len(text) > len(preview),
    }


def cdn_readback(url: str) -> dict:
    if url not in CDN_URLS:
        raise ValueError("CDN_URL_NOT_APPROVED")
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "terra-high-p0-once/1"}), timeout=18) as res:
            raw = res.read(200001)
        if len(raw) > 200000:
            raise ValueError("CDN_DATA_TOO_LARGE")
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise ValueError("CDN_DATA_NOT_OBJECT")
        # Public data summary only; do not repackage large market snapshots.
        return {
            "url": url, "status": "FETCHED_JSON",
            "raw_sha256": sha(raw), "keys": sorted(parsed.keys())[:38],
            "preview": json.dumps(parsed, sort_keys=True)[:2100],
        }
    except Exception as exc:
        return {"url": url, "status": "UNAVAILABLE", "error_class": type(exc).__name__}


def build(output: Path) -> dict:
    main_sha = git("rev-parse", "refs/remotes/origin/main")
    if len(main_sha) != 40:
        raise ValueError("MAIN_SHA_NOT_FROZEN")
    source = [source_file(main_sha, path) for path in SOURCE_FILES]
    cdn = [cdn_readback(url) for url in CDN_URLS]
    if any(d.get("status") != "FETCHED_JSON" for d in cdn):
        raise ValueError("P0_PUBLIC_CDN_READBACK_UNAVAILABLE")
    hourly = next(r for r in source if r["path"].endswith("/LATEST.json") and "/hourly/" in r["path"])
    context = {
        "contract": "TERRA_HIGH_P0_ONCE_GITHUB_v1",
        "source_commit_sha": main_sha,
        "scope": "P0_HOURLY_COMPASS_CN_PAGES_ONLY",
        "source_files": source,
        "cdn_readbacks": cdn,
        "source_truth": "IMMUTABLE_PUBLIC_MAIN_AND_CDN_READBACK",
        "prohibited": ["private_data", "API_KEY", "trading", "forecast_reconstruction", "source_write", "self_merge"],
        "requirements": {
            "natural_source_windows": 6,
            "max_lag_minutes": 90,
            "fail_closed_stale": True,
            "exact_source_public_equality": True,
        },
        "hourly_source_sha256": hourly["sha256"],
    }
    data = canonical(context)
    if len(data) > MAX_CONTEXT_BYTES:
        raise ValueError("P0_CONTEXT_UNBOUNDED")
    prompt = (
        "ONE FINITE TECHNICAL REPAIR REQUEST, NOT A GENERAL FRAMEWORK AUDIT. "
        "Inspect ONLY the P0 Hourly→Official Kompas PRO→Cycle Navigator→GitHub Pages chain. "
        "Output exactly ONE highest-leverage evidence-backed root-cause candidate; "
        "if the snapshot cannot prove the root cause, say BLOCKED and identify the one missing observation. "
        "Use <= 2 evidence_for, <= 2 evidence_against, <= 2 uncertainties, <= 2 hypotheses, each under 350 characters. "
        "Put actionable defect as P0|FILE|REPRO|MINIMAL_CODE_CHANGE|NEGATIVE_TEST|PRODUCTION_ACCEPTANCE "
        "in evidence_against. Cite exact supplied paths and frozen source SHA only. "
        "Acceptance must require SIX consecutive natural <=90-minute source→public equal windows. "
        "Do not infer a failure from a clipped code preview. Avoid generic advice, architecture essays, "
        "new bots, new PRs, AppDeploy, fabricated data, trading, automatic code writes or merges. "
        "Return compact strict JSON using existing gateway schema; forecast_candidates MUST equal []."
    )
    output.mkdir(parents=True, exist_ok=True)
    (output / "context.json").write_bytes(data)
    (output / "prompt.txt").write_text(prompt + "\n")
    result = {
        "contract": context["contract"],
        "main_sha": main_sha,
        "context_sha256": sha(data),
        "context_bytes": len(data),
        "prompt_sha256": sha(prompt.encode()),
        "model": MODEL,
        "reasoning_effort": MODEL_EFFORT,
        "public_cdn_reads": len(cdn),
    }
    (output / "manifest.json").write_bytes(canonical(result))
    return result


def gh(method: str, route: str, payload: dict | None = None) -> dict | list:
    token = os.environ.get("GH_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_ISSUE_TOKEN_UNAVAILABLE")
    data = None if payload is None else canonical(payload)
    req = urllib.request.Request("https://api.github.com" + route, data=data, method=method,
        headers={"Accept": "application/vnd.github+json", "Authorization": "Bearer " + token,
                 "X-GitHub-Api-Version": "2022-11-28", "Content-Type": "application/json",
                 "User-Agent": "terra-high-p0-once/1"})
    with urllib.request.urlopen(req, timeout=30) as response:
        raw = response.read(400001)
    if len(raw) > 400000:
        raise RuntimeError("GITHUB_COMMENT_RESPONSE_TOO_LARGE")
    return json.loads(raw)


def existing_claim() -> dict | None:
    base = "/repos/" + REPO + "/issues/" + str(ISSUE) + "/comments"
    for page in range(1, MAX_PAGES + 1):
        rows = gh("GET", base + f"?per_page={PAGE_SIZE}&page={page}")
        if not isinstance(rows, list) or len(rows) > PAGE_SIZE:
            raise RuntimeError("INVALID_COMMENT_PAGE")
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("user"), dict):
                raise RuntimeError("INVALID_COMMENT_ROW")
            if row["user"].get("login") == BOT and str(row.get("body") or "").startswith(MARKER):
                return {"id": row.get("id"), "url": row.get("html_url")}
        if len(rows) < PAGE_SIZE:
            return None
    raise RuntimeError("INCOMPLETE_COMMENT_CENSUS")


def claim(run_id: str, main_sha: str) -> dict:
    if os.environ.get("GITHUB_RUN_ATTEMPT") != "1" or os.environ.get("GITHUB_ACTOR") != "Donh91":
        raise RuntimeError("OWNER_FIRST_ATTEMPT_ONLY")
    if not run_id.isdecimal() or len(main_sha) != 40:
        raise ValueError("INVALID_RUN_SOURCE_BINDING")
    if existing_claim():
        raise RuntimeError("P0_HIGH_PAID_LIABILITY_ALREADY_CLAIMED")
    body = "\n".join([
        MARKER, "",
        "One owner-approved Terra 6.1 HIGH P0 engineering analysis, not a Max rerun.",
        "Run: https://github.com/" + REPO + "/actions/runs/" + run_id,
        "Frozen main SHA: " + main_sha,
        "One paid attempt, no auto retry or code/merge authority.",
        "Existing USD 40/month and USD 3/call guards. Separate from consumed Terra Max claim.",
    ])
    result = gh("POST", "/repos/" + REPO + "/issues/" + str(ISSUE) + "/comments", {"body": body})
    if not isinstance(result, dict) or not isinstance(result.get("id"), int):
        raise RuntimeError("CLAIM_ACK_UNVERIFIED_NO_PAID_CALL")
    return {"claim_id": result["id"], "run_id": run_id}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["build", "claim"])
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--run-id")
    parser.add_argument("--main-sha")
    args = parser.parse_args()
    if args.action == "build":
        if args.output_dir is None:
            raise SystemExit("OUTPUT_DIR_REQUIRED")
        print(json.dumps(build(args.output_dir), sort_keys=True))
    else:
        if not args.run_id or not args.main_sha:
            raise SystemExit("CLAIM_BINDING_REQUIRED")
        print(json.dumps(claim(args.run_id, args.main_sha), sort_keys=True))


if __name__ == "__main__":
    main()
