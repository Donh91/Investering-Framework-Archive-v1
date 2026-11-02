#!/usr/bin/env python3
"""One-time public-source packet for owner-authorized Terra Max endgame review.

Never reads the private data plane, credentials, wallets, portfolio or external Vault.
The resulting packet is an advisory input, NOT a verified fix or trading instruction.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

PUBLIC_FILES = (
    "AGENTS.md",
    "LATEST_HANDOFF.json",
    "03_DAILY_CAPTURE_LOGS/hourly/LATEST.json",
    "05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json",
    "scripts/data_ping/compass_event_refresh.py",
    ".github/workflows/hourly-sequence-capture.yml",
    ".github/workflows/native-market-recovery.yml",
    "scripts/cycle_navigator/check_publication_lineage.py",
    "scripts/cycle_navigator/verify_hourly_pages_handoff.py",
    "scripts/cycle_navigator/build_weekly_cycle_navigator.py",
    "scripts/cycle_navigator/daily_price_journey.py",
    "scripts/research/shared_row_tournament_monitor.py",
    ".github/workflows/shared-row-tournament-research-gate.yml",
    "tests/research/test_shared_row_consumer_integrity.py",
    "01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md",
)
PUBLIC_URLS = (
    "https://donh91.github.io/Investering-Framework-Archive-v1/data/latest.json",
    "https://donh91.github.io/Investering-Framework-Archive-v1/data/publication-lineage.json",
)
PUBLIC_PR_NUMBERS = (1814, 1815, 1823)
MAX_FILE_PREVIEW = 6200
MAX_PACKET_BYTES = 145000
MODEL = "gpt-6.1-terra"
REASONING = "max"
MISSION_CONTRACT = "TERRA_MAX_ENDGAME_GITHUB_ONCE_v1"


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def clipped(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    leading = max(1, limit - 950)
    return text[:leading] + "\n[OMITTED_MIDDLE]\n" + text[-800:]


def approved_public_path(path: str) -> bool:
    if path not in PUBLIC_FILES or path.startswith("/") or ".." in path.split("/"):
        return False
    forbidden = {"secrets", "private", ".env", "wallet", "vault", "credentials"}
    return not any(part.lower() in forbidden for part in path.split("/"))


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], stderr=subprocess.STDOUT, text=True).strip()


def source_at_sha(sha: str, path: str) -> dict[str, Any]:
    if not approved_public_path(path):
        raise ValueError("NON_PUBLIC_SOURCE_DENIED:" + path)
    proc = subprocess.run(["git", "show", sha + ":" + path], capture_output=True)
    if proc.returncode != 0:
        return {"path": path, "status": "SOURCE_MISSING", "evidence": "NOT_VERIFIED"}
    raw = proc.stdout
    return {
        "path": path,
        "status": "SOURCE_READ",
        "bytes": len(raw),
        "sha256": sha256(raw),
        "excerpt_only": len(raw) > MAX_FILE_PREVIEW,
        "excerpt": clipped(raw.decode("utf-8", "replace"), MAX_FILE_PREVIEW),
    }


def fetch_public_json(url: str, limit: int = 6000) -> dict[str, Any]:
    if url not in PUBLIC_URLS:
        raise ValueError("EXTERNAL_URL_NOT_ALLOWLISTED")
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "framework-terra-endgame-once/1"})
        with urllib.request.urlopen(request, timeout=12) as response:
            raw = response.read(1_000_001)
        if len(raw) > 1_000_000:
            raise ValueError("PUBLIC_RESPONSE_SIZE_LIMIT")
        value = json.loads(raw)
        return {
            "url": url,
            "status": "RETRIEVED",
            "sha256": sha256(raw),
            "excerpt_only": len(raw) > limit,
            "excerpt": clipped(json.dumps(value, ensure_ascii=False, sort_keys=True), limit),
        }
    except (ValueError, OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        return {"url": url, "status": "UNAVAILABLE", "error_class": type(exc).__name__}


def fetch_public_pr(number: int) -> dict[str, Any]:
    if number not in PUBLIC_PR_NUMBERS:
        raise ValueError("UNAPPROVED_PR_NUMBER")
    url = (
        "https://api.github.com/repos/Donh91/"
        "Investering-Framework-Archive-v1/pulls/" + str(number)
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "framework-terra-endgame-once/1",
    }
    token = os.getenv("GH_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=12) as response:
            raw = response.read(250001)
        if len(raw) > 250000:
            raise ValueError("PR_SIZE_LIMIT")
        data = json.loads(raw)
        return {
            "number": number,
            "url": data.get("html_url"),
            "state": data.get("state"),
            "draft": data.get("draft"),
            "updated_at": data.get("updated_at"),
            "head_sha": (data.get("head") or {}).get("sha"),
            "base_sha": (data.get("base") or {}).get("sha"),
            "mergeable": data.get("mergeable"),
            "body_excerpt": clipped(str(data.get("body") or ""), 1800),
        }
    except (ValueError, OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        return {"number": number, "status": "UNAVAILABLE", "error_class": type(exc).__name__}


def prompt_text() -> str:
    return """ONE-TIME TERRA MAX ENGINEERING ENDGAME — public-source advisory only.

Objective: solve the known problems and terminate the existing remediation queue;
do not propose recurring analysis, new supervisors, new Apps/AppDeploy,
unnecessary PRs, new source writers, invented market data, or speculative tuning.

P0 Hourly → Official Kompas PRO → Cycle Navigator → actual GitHub Pages:
Identify root causes and the smallest code-level repair plus deterministic positive
and adversarial negative tests. Acceptance: SIX consecutive naturally eligible
<=90-minute source-to-public windows, exact source/public equality, fail-closed
stale/expiry/mismatch/double-dispatch checks. External AppDeploy clock is NOT
required, is NOT an authorized production writer, and must not be proposed as
a dependency. Current source and CDN evidence must be read literally.

P1 Original prospective BTC/ETH seven-day source → immutable freeze → Graph B:
Use EXISTING #1820 producer and existing Graph B adapter, do not synthesize
or backfill missing 7 points, do not confuse observations with forecasts.
State the smallest code-level repair, exact tests, natural W45 issuance and
GitHub Pages readback acceptance, or explicit honest abstention.

P2 Task 2 Shared Row scientific admissibility and closure of #1814:
Respect PIT admission, hashes, source ancestry, deduplication, maturity vs
pairwise divergence, and zero historical edge proof. Provide minimal CI/source
clock repair and fixture tests. High-impact workflow edits require independent
safepoint and recovery-credential separation; do not propose bypasses.
#1815 SITE design is NOT a data-chain blocker. #1823 model routing is
not a reason to expand API spend or create another supervisor.

For EACH track, output a prioritized reproducible P0/P1 defect in
evidence_against formatted TRACK|SEVERITY|FILE|REPRO|SMALLEST_SAFE_FIX,
and specific deterministic CODE_CHANGE, TEST, ACCEPTANCE proposals in hypotheses
with exact existing owner/PR routing. State unverified natural evidence in
uncertainties. Prefer fewer high-confidence fixes over large wishlists.

CRITICAL: This is one API source-bound engineering packet, NOT a repository
edit or production verification. If source proof is absent, explicitly mark
BLOCKED/UNVERIFIED. forecast_candidates MUST be []. No portfolio advice,
no market/score rewriting, no automatic code, merge or trading authority.
Return only the existing strict gateway JSON schema.
"""


def build(root: Path, output_dir: Path) -> dict[str, Any]:
    if not (root / ".git").exists():
        raise ValueError("EXACT_GIT_WORKTREE_REQUIRED")
    # origin/main is fetched and frozen at job start, never a moving link mid-run.
    base_sha = git("rev-parse", "refs/remotes/origin/main")
    if len(base_sha) != 40:
        raise ValueError("FULL_SOURCE_SHA_REQUIRED")
    source_files = [source_at_sha(base_sha, path) for path in PUBLIC_FILES]
    public_cdns = [fetch_public_json(url) for url in PUBLIC_URLS]
    prs = [fetch_public_pr(number) for number in PUBLIC_PR_NUMBERS]
    context = {
        "contract": MISSION_CONTRACT,
        "source_control_plane": "Donh91/Investering-Framework-Archive-v1",
        "source_commit_sha": base_sha,
        "model_expected": MODEL,
        "reasoning_expected": REASONING,
        "authority": "ADVISORY_ONLY_NO_WRITES",
        "restricted_provider_data": "NOT_INCLUDED",
        "public_source_files": source_files,
        "public_pages_readbacks": public_cdns,
        "existing_prs": prs,
        "completion_target": (
            "P0 six natural eligible windows; P1 original freeze/7d Graph B or honest "
            "abstention; P2 valid PIT/source-clock/CI and scientifically sound rows"
        ),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(context, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if len(raw) > MAX_PACKET_BYTES:
        raise ValueError("BOUNDED_PUBLIC_CONTEXT_EXCEEDED")
    (output_dir / "context.json").write_bytes(raw)
    prompt = prompt_text()
    (output_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    manifest = {
        "contract": MISSION_CONTRACT,
        "source_commit_sha": base_sha,
        "context_sha256": sha256(raw),
        "prompt_sha256": sha256(prompt.encode()),
        "context_bytes": len(raw),
        "source_file_count": len(source_files),
        "source_missing_count": sum(x["status"] != "SOURCE_READ" for x in source_files),
        "public_readback_success_count": sum(x["status"] == "RETRIEVED" for x in public_cdns),
        "api_calls_from_packet_builder": 0,
        "source_authority": "PUBLIC_CONTROL_PLANE_ONLY",
        "automatic_code_write": False,
        "automatic_merge": False,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.repo_root, args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
