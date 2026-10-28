"""Produce a bounded, original-source evidence packet for an owner-approved Terra API work unit."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUEUE = Path("research/api_agent/ENDGAME_PROGRESS_QUEUE_v1.json")
WORK_ID_RE = re.compile(r"[A-Z][A-Z0-9_]{7,74}")


def manifest(data: object) -> dict:
    if not isinstance(data, dict) or data.get("contract") != "TERRA_ENDGAME_PROGRESS_QUEUE_v1":
        raise ValueError("INVALID_ENDGAME_QUEUE_CONTRACT")
    work = data.get("active")
    if not isinstance(work, dict) or not WORK_ID_RE.fullmatch(str(work.get("work_id", ""))):
        raise ValueError("INVALID_WORK_ID")
    if int(work.get("owner_pr", 0)) not in (1825, 1814, 1823):
        raise ValueError("UNAPPROVED_EXISTING_PR_SCOPE")
    if not re.fullmatch(r"[0-9a-f]{40}", str(work.get("expected_pr_head", ""))):
        raise ValueError("EXPECTED_PR_HEAD_MISSING_OR_INVALID")
    paths = work.get("paths", [])
    if not isinstance(paths, list) or not (1 <= len(paths) <= 9):
        raise ValueError("SOURCE_LIST_MISSING_OR_UNBOUNDED")
    for p in paths:
        if not isinstance(p, str) or not p or p.startswith("/") or "\\" in p or ".." in Path(p).parts:
            raise ValueError("INVALID_SOURCE_PATH")
        if not p.startswith(("scripts/", "tests/", ".github/workflows/", "05_CYCLE_NAVIGATOR/", "04_MARKET_LEARNING/", "06_RESEARCH_LAB/", "03_DAILY_CAPTURE_LOGS/")):
            raise ValueError("UNAUTHORIZED_SOURCE_PREFIX")
    if len(str(work.get("objective", ""))) > 2500:
        raise ValueError("OBJECTIVE_UNBOUNDED")
    return work


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT, stderr=subprocess.DEVNULL)


def build(output: Path, queue: Path = QUEUE) -> dict:
    work = manifest(json.loads((ROOT / queue).read_text()))
    main = git("rev-parse", "refs/remotes/origin/main").decode().strip()
    evidence = []
    for path in work["paths"]:
        try:
            raw = git("show", f"{main}:{path}")
            evidence.append({"path": path, "sha256": hashlib.sha256(raw).hexdigest(),
                             "bytes": len(raw), "excerpt": (lambda t: t if len(t) <= 21000 else t[:5500] + "\\n...[SOURCE_EXCERPT_TRUNCATED]...\\n" + t[-14500:])(raw.decode("utf-8", "replace"))})
        except subprocess.CalledProcessError:
            evidence.append({"path": path, "status": "SOURCE_UNAVAILABLE"})

    repo = os.environ.get("GITHUB_REPOSITORY")
    if repo != "Donh91/Investering-Framework-Archive-v1":
        raise ValueError("ORIGINAL_REPOSITORY_AUTHORITY_UNVERIFIED")
    pr = json.loads(subprocess.check_output(
        ["gh", "api", f"repos/{repo}/pulls/{work['owner_pr']}"], timeout=20))
    original_head = str(pr["head"]["sha"])
    if original_head != work["expected_pr_head"] or pr["state"] != "open":
        raise ValueError("PR_HEAD_CHANGED_OR_NOT_OPEN_FAIL_CLOSED")
    changed = json.loads(subprocess.check_output(
        ["gh", "api", f"repos/{repo}/pulls/{work['owner_pr']}/files?per_page=100"], timeout=20))
    pr_evidence = {"number": work["owner_pr"],"head_sha":original_head,
                   "head_branch":pr["head"]["ref"],"base_sha":pr["base"]["sha"],
                   "draft":pr["draft"],"files":[{"path":f["filename"],
                   "status":f["status"],"patch":str(f.get("patch") or "")[:4200]}
                   for f in changed[:9]]}
    packet = {"contract":"TERRA_ENDGAME_PROGRESS_PACKET_v1","work_id":work["work_id"],
              "owner_pr":work["owner_pr"],"owner_issue":work.get("owner_issue"),
              "exact_original_main_sha":main,"original_pr":pr_evidence,"evidence":evidence,"public_only":True,
              "backup_and_separation_are_not_verified":True,"production_authority":False}
    output.mkdir(parents=True, exist_ok=True)
    (output / "context.json").write_text(json.dumps(packet,ensure_ascii=False,sort_keys=True))
    (output / "prompt.txt").write_text(
        "Owner ENDGAME actual code closure. Work ID: " + work["work_id"] + ". Target existing PR #"
        + str(work["owner_pr"]) + ". Objective: " + str(work["objective"])
        + ". You MUST propose minimal directly testable modifications for this ORIGINAL PR, "
        "or a precise SOURCE_BLOCKED status when source is unavailable. DO NOT output a new planning PR, "
        "third reviewer PR, theoretical forecast, performance edge or stale W39 bridge as W45. "
        "Distinguish source-time from event-time, benchmark from real issuer. "
        "Provide exact tests, proof or falsifier in a concise STRICT JSON response with forecast_candidates=[].")
    (output / "manifest.json").write_text(json.dumps({"work_id":work["work_id"],"main_sha":main,
                                  "source_count":len(evidence),"source_hashes":
                                  {x["path"]:x.get("sha256") for x in evidence}},sort_keys=True))
    return packet


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != "build":
        raise SystemExit("Usage: endgame_progress_packet.py build OUTPUT_DIR")
    p=build(Path(sys.argv[2]))
    print("ENDGAME_PACKET_FROZEN", p["work_id"], p["exact_original_main_sha"], len(p["evidence"]))
