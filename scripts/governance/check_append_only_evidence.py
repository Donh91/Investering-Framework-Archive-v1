#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

PROTECTED_PREFIXES = (
    "research/codex/transitions/",
    "research/codex/merges/",
    "research/codex/direct_merges/",
    "research/codex/completions/",
    "research/codex/convergence/",
    "research/architecture_health/history/",
    "09_SOURCE_QA/incidents/",
)


def protected(path: str) -> bool:
    path = path.replace("\\", "/").lstrip("./")
    return any(path.startswith(prefix) for prefix in PROTECTED_PREFIXES)


def diff_entries(repo_root: Path, base_ref: str, head_ref: str) -> list[tuple[str, list[str]]]:
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "diff", "--name-status", "-M", f"{base_ref}...{head_ref}"],
        text=True,
        capture_output=True,
        check=True,
    )
    rows: list[tuple[str, list[str]]] = []
    for raw in proc.stdout.splitlines():
        if not raw.strip():
            continue
        parts = raw.split("\t")
        rows.append((parts[0], parts[1:]))
    return rows


def violations(entries: list[tuple[str, list[str]]]) -> list[str]:
    bad: list[str] = []
    for status, paths in entries:
        touched = [path for path in paths if protected(path)]
        if not touched:
            continue
        if status == "A" and len(paths) == 1:
            continue
        bad.append(f"{status}:{' -> '.join(paths)}")
    return bad


def check(repo_root: Path, base_ref: str, head_ref: str) -> list[str]:
    return violations(diff_entries(repo_root, base_ref, head_ref))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--base-ref", required=True)
    parser.add_argument("--head-ref", default="HEAD")
    args = parser.parse_args()
    bad = check(args.repo_root, args.base_ref, args.head_ref)
    if bad:
        print("APPEND_ONLY_EVIDENCE_VIOLATION")
        for row in bad:
            print(row)
        raise SystemExit(1)
    print("APPEND_ONLY_EVIDENCE_PASS")


if __name__ == "__main__":
    main()
