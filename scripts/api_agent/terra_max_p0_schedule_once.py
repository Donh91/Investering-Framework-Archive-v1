#!/usr/bin/env python3
"""Second owner-authorized Terra MAX P0 schedule-liveness closure, no app or scheduler.

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
MARKER = "[TERRA_MAX_P0_SCHEDULE_CLOSURE_ONCE_CLAIM_v1]"
BOT = "github-actions[bot]"
MODEL = "gpt-6.1-terra"
MODEL_EFFORT = "max"
MAX_CONTEXT_BYTES = 48000
PAGE_SIZE = 25
MAX_PAGES = 100
SOURCE_FILES = (
    "03_DAILY_CAPTURE_LOGS/hourly/LATEST.json",
    ".github/workflows/hourly-sequence-capture.yml",
    ".github/workflows/native-market-recovery.yml",
    ".github/workflows/compass-event-refresh.yml",
    ".github/workflows/daily-raw-owner-capture.yml",
    "scripts/health/native_market_recovery.py",
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
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "terra-max-p0-schedule-once/1"}), timeout=18) as res:
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
        "contract": "TERRA_MAX_P0_SCHEDULE_CLOSURE_GITHUB_v1",
        "source_commit_sha": main_sha,
        "scope": "P0_HOURLY_SCHEDULER_LIVENESS_AND_INDEPENDENT_RECOVERY_ONLY",
        "historical_verified_github_evidence": {
            "label": "OWNER_VERIFIED_2026_10_27_RECEIPTS_NOT_CURRENT_SLA_CLAIM",
            "primary_schedule_events_utc": ["00", "06", "13"],
            "native_recovery_schedule_events_utc": ["00", "06", "13"],
            "missing_closed_hours_before_17_utc": ["02","03","04","07","08","09","14"],
            "independent_recovery_run": "40531700614",
            "independent_recovery_attempt": 2,
            "recovered_hourly_run": "40553440169",
            "recovered_hour_closed_utc": "2026-10-27T17:00:00Z",
            "public_pages_run": "40553564176",
            "pages_lineage_equality": "PASS",
            "pages_parity": "PASS",
            "pages_release_age_minutes": 46.03,
            "natural_six_window_proof": "ABSENT",
            "authority": "READ_ONLY_HISTORICAL_INCIDENT_FACTS_NO_PROSPECTIVE_BACKFILL"
        },
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
        "SECOND EXPLICITLY OWNER-AUTHORIZED FINITE TERRA MAX MISSION. NOT A RERUN OF "
        "THE CONSUMED THREE-TRACK MAX CALL. Solve ONLY P0 scheduling liveness "
        "and Hourly→Official Kompas PRO→Cycle Navigator→GitHub Pages. "
        "Observed issue: both Hourly :12 and Native Recovery :24 depend on the same "
        "GitHub schedule mechanism; on Oct27 naturally started at only 00/06/13 UTC "
        "with missing hourly source periods. Independent Chat-initiated rerun of "
        "EXISTING Compass Event Refresh detect job successfully dispatched the "
        "existing Hourly owner and published 17:00Z to actual Pages CDN with "
        "exact source/public equality PASS. That is NOT six NATURAL hour proofs. "
        "Adversarially compare native cron vs this independent conditional Chat "
        "auditor hourly wake, owner idempotency, 65-minute stale gate, cooldown, "
        "double-dispatch, GitHub active-job checks, real future UTC windows. "
        "Choose ONE smallest SAFE already-owned action; recommend specific "
        "existing FILE, REPRO, minimal patch or instruction, positive/negative "
        "tests, stale/expiry/rollback, six-window natural acceptance. "
        "No new jobs, AppDeploy, paid retries, new writers, private-data transfer, "
        "portfolio or trade actions, fabricated data, self-merge, or backfill. "
        "Root cause of GitHub schedule service is UNKNOWN absent provider proof. "
        "Output strict JSON COMPACT: summary <=450 chars; each evidence_for, "
        "evidence_against, uncertainties and hypotheses <=2 strings <=350 chars. "
        "Include actual known source sha and evidence limitations. forecast_candidates MUST equal []."
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
                 "User-Agent": "terra-max-p0-schedule-once/1"})
    with urllib.request.urlopen(req, timeout=30) as response:
        raw = response.read(400001)
    if len(raw) > 400000:
        raise RuntimeError("GITHUB_COMMENT_RESPONSE_TOO_LARGE")
    return json.loads(raw)


def scan_existing_marker(marker: str) -> dict | None:
    base = "/repos/" + REPO + "/issues/" + str(ISSUE) + "/comments"
    for page in range(1, MAX_PAGES + 1):
        rows = gh("GET", base + f"?per_page={PAGE_SIZE}&page={page}")
        if not isinstance(rows, list) or len(rows) > PAGE_SIZE:
            raise RuntimeError("INVALID_COMMENT_PAGE")
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("user"), dict):
                raise RuntimeError("INVALID_COMMENT_ROW")
            if row["user"].get("login") == BOT and str(row.get("body") or "").startswith(marker):
                return {"id": row.get("id"), "url": row.get("html_url")}
        if len(rows) < PAGE_SIZE:
            return None
    raise RuntimeError("INCOMPLETE_COMMENT_CENSUS")


def existing_claim() -> dict | None:
    return scan_existing_marker(MARKER)


def claim(run_id: str, main_sha: str) -> dict:
    if os.environ.get("GITHUB_RUN_ATTEMPT") != "1" or os.environ.get("GITHUB_ACTOR") != "Donh91":
        raise RuntimeError("OWNER_FIRST_ATTEMPT_ONLY")
    if not run_id.isdecimal() or len(main_sha) != 40:
        raise ValueError("INVALID_RUN_SOURCE_BINDING")
    if existing_claim():
        raise RuntimeError("P0_MAX_SCHEDULE_PAID_LIABILITY_ALREADY_CLAIMED")
    # The second owner authorization is valid only AFTER original MAX single-use
    # liability was claimed. Never allow this to replace or revive first mission.
    previous = scan_existing_marker("[TERRA_MAX_ENDGAME_ONCE_CLAIM_v1]")
    if not previous:
        raise RuntimeError("ORIGINAL_MAX_CLAIM_MISSING_NO_SECOND_MISSION")
    body = "\n".join([
        MARKER, "",
        "Distinct second owner-approved Terra 6.1 MAX schedule-liveness P0 engineering claim; old Max and High are already consumed.",
        "Run: https://github.com/" + REPO + "/actions/runs/" + run_id,
        "Frozen main SHA: " + main_sha,
        "One paid attempt, no auto retry or code/merge authority.",
        "Existing USD 40/month and USD 3/call guards; a new unique paid marker independent of consumed Max/High claims.",
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
