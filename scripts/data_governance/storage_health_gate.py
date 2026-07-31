#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os
from pathlib import Path

DEFAULT_POLICY = Path("research/data_governance/STORAGE_HEALTH_POLICY_FREE_v1.json")
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__"}
BULK_SUFFIXES = {".zip", ".gz", ".7z", ".parquet", ".feather", ".db", ".sqlite", ".png", ".jpg", ".jpeg", ".pdf"}

def scan(root: Path, policy: dict) -> dict:
    total = 0
    files = 0
    warnings = []
    violations = []
    soft = policy["git_file_limits_mib"]["soft_warn"] * 1024 * 1024
    hard = policy["git_file_limits_mib"]["hard_block"] * 1024 * 1024
    for path in root.rglob("*"):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        size = path.stat().st_size
        total += size
        files += 1
        rel = path.relative_to(root).as_posix()
        if size > hard:
            violations.append({"path": rel, "bytes": size, "reason": "FILE_OVER_HARD_LIMIT"})
        elif size > soft:
            warnings.append({"path": rel, "bytes": size, "reason": "FILE_OVER_SOFT_LIMIT"})
        if path.suffix.lower() in BULK_SUFFIXES and size > soft:
            violations.append({"path": rel, "bytes": size, "reason": "BULK_BINARY_IN_GIT"})
    mib = total / 1024 / 1024
    t = policy["repo_size_thresholds_mib"]
    if mib <= t["green_max"]: level = "GREEN"
    elif mib <= t["yellow_max"]: level = "YELLOW"
    elif mib <= t["orange_max"]: level = "ORANGE"
    else: level = "RED"
    if level == "RED": violations.append({"reason": "REPO_SIZE_RED", "mib": round(mib, 3)})
    return {"contract":"STORAGE_HEALTH_REPORT_v1","repo_bytes":total,"repo_mib":round(mib,3),"file_count":files,"level":level,"warnings":warnings,"violations":violations,"status":"PASS" if not violations else "FAIL"}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    policy = json.loads(args.policy.read_text(encoding="utf-8"))
    report = scan(args.root.resolve(), policy)
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["status"] == "PASS" else 2

if __name__ == "__main__":
    raise SystemExit(main())
