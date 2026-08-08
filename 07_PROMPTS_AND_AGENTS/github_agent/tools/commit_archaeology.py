#!/usr/bin/env python3
"""Dependency-free, read-only commit archaeology for a tracked file."""
from __future__ import annotations

import argparse
import collections
import json
import re
import subprocess
from typing import Sequence

REF_RE = re.compile(r"(?:#\d+|PR\s*#?\d+|pull request\s*#?\d+)", re.I)
SIG_RE = re.compile(r"\b(revert|workaround|todo|fixme|hack|temporary)\b", re.I)


def git(args: Sequence[str]) -> tuple[int, str, str]:
    result = subprocess.run(["git", *args], text=True, capture_output=True, check=False)
    return result.returncode, result.stdout, result.stderr.strip()


def validate_line_range(start: int | None, end: int | None) -> str | None:
    if (start is None) != (end is None):
        return "Both --start and --end are required for a line range."
    if start is not None and (start < 1 or end < start):
        return "Line range must satisfy 1 <= start <= end."
    return None


def changed_paths_for_commit(sha: str) -> list[str]:
    code, stdout, _ = git(["show", "--format=", "--name-only", sha])
    if code:
        return []
    return sorted({line.strip() for line in stdout.splitlines() if line.strip()})


def commits(path: str, start: int | None = None, end: int | None = None) -> tuple[list[dict[str, object]], str | None]:
    if start is not None and end is not None:
        args = ["log", "--format=%H%x1f%aI%x1f%an%x1f%s", f"-L{start},{end}:{path}"]
    else:
        args = ["log", "--follow", "--format=%H%x1f%aI%x1f%an%x1f%s", "--", path]
    code, stdout, stderr = git(args)
    if code:
        return [], stderr or "unknown git history error"
    items: list[dict[str, object]] = []
    for line in stdout.splitlines():
        if line.count("\x1f") != 3:
            continue
        sha, date, author, subject = line.split("\x1f", 3)
        items.append({
            "sha": sha,
            "date": date,
            "author": author,
            "subject": subject,
            "paths": changed_paths_for_commit(sha),
        })
    return list(reversed(items)), None


def path_aliases(path: str) -> tuple[list[str], str | None]:
    code, stdout, stderr = git(["log", "--follow", "--name-status", "--format=", "--", path])
    if code:
        return [], stderr or "unknown alias history error"
    aliases = {path}
    for line in stdout.splitlines():
        parts = line.split("\t")
        if len(parts) >= 3 and parts[0].startswith("R"):
            aliases.update(parts[1:3])
        elif len(parts) >= 2 and parts[0] and parts[0][0] in "ACDMRTUXB":
            aliases.add(parts[-1])
    aliases.discard(path)
    return sorted(aliases), None


def blame(path: str, start: int | None = None, end: int | None = None) -> dict[str, object]:
    args = ["blame", "--line-porcelain"]
    if start is not None and end is not None:
        args.extend(["-L", f"{start},{end}"])
    args.extend(["--", path])
    code, stdout, _ = git(args)
    if code:
        return {"evidence_class": "NOT_DETERMINABLE", "counts": {}}
    counts = collections.Counter(
        line[7:] for line in stdout.splitlines() if line.startswith("author ")
    )
    return {"evidence_class": "FACT_FROM_GIT", "counts": dict(sorted(counts.items()))}


def analyze(path: str, start: int | None = None, end: int | None = None, text: bool = False) -> dict[str, object]:
    range_error = validate_line_range(start, end)
    if range_error:
        return {
            "tool": "commit_archaeology",
            "path": path,
            "status": "INVALID_LINE_RANGE",
            "evidence_class": "NOT_DETERMINABLE",
            "error": range_error,
        }

    code, _, _ = git(["ls-files", "--error-unmatch", path])
    if code:
        return {
            "tool": "commit_archaeology",
            "path": path,
            "status": "NOT_TRACKED",
            "evidence_class": "NOT_DETERMINABLE",
            "note": "Path is not tracked by local Git history.",
        }

    timeline, history_error = commits(path, start, end)
    if history_error:
        return {
            "tool": "commit_archaeology",
            "path": path,
            "line_range": [start, end] if start is not None else None,
            "status": "GIT_HISTORY_ERROR",
            "evidence_class": "NOT_DETERMINABLE",
            "error": history_error,
        }
    if not timeline:
        return {
            "tool": "commit_archaeology",
            "path": path,
            "line_range": [start, end] if start is not None else None,
            "status": "NO_HISTORY",
            "evidence_class": "NOT_DETERMINABLE",
            "note": "Git returned no relevant commits.",
        }

    if start is None:
        aliases, alias_error = path_aliases(path)
        alias_evidence = "FACT_FROM_GIT" if aliases else "NOT_DETERMINABLE"
    else:
        aliases, alias_error = [], "Alias discovery is not supported for line-range history."
        alias_evidence = "NOT_DETERMINABLE"

    alias_set = set(aliases)
    co_changes = collections.Counter(
        changed_path
        for commit in timeline
        for changed_path in commit["paths"]
        if changed_path != path and changed_path not in alias_set
    )
    metadata_signals = []
    for commit in timeline:
        references = REF_RE.findall(str(commit["subject"]))
        signals = SIG_RE.findall(str(commit["subject"]))
        if references or signals:
            metadata_signals.append({
                "sha": commit["sha"],
                "evidence_class": "HEURISTIC_FROM_COMMIT_TEXT",
                "references": references,
                "signals": signals,
                "subject": commit["subject"],
            })

    return {
        "tool": "commit_archaeology",
        "path": path,
        "line_range": [start, end] if start is not None else None,
        "status": "OK",
        "introducing_commit": {
            "evidence_class": "FACT_FROM_GIT",
            "sha": timeline[0]["sha"],
        },
        "timeline": [
            {key: commit[key] for key in ("sha", "date", "author", "subject")}
            for commit in timeline
        ],
        "aliases_or_renames": {
            "evidence_class": alias_evidence,
            "paths": aliases,
            "limitation": alias_error,
        },
        "co_changed_files": {
            "evidence_class": "FACT_FROM_GIT",
            "counts": dict(sorted(co_changes.items())),
        },
        "metadata_signals": metadata_signals,
        "blame_author_counts": blame(path, start, end),
        "change_risk_note": {
            "evidence_class": "HEURISTIC_FROM_COMMIT_TEXT",
            "text": "Higher caution if history shows many authors, renames, co-changes, or revert/workaround/TODO signals.",
        },
        "limitations": [
            "Uses only local Git history; remote PR discussions are not inspected.",
            "Commit text signals are heuristic, not authority.",
            "Blame counts are evidence, not ownership authority.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--start", type=int)
    parser.add_argument("--end", type=int)
    parser.add_argument("--text", action="store_true")
    ns = parser.parse_args()
    data = analyze(ns.path, ns.start, ns.end, ns.text)
    if ns.text:
        print(f"{data['status']}: {data['path']}")
        print(json.dumps(data.get("introducing_commit", {}), sort_keys=True))
    else:
        print(json.dumps(data, indent=2, sort_keys=True))
    return 0 if data["status"] == "OK" else 2


if __name__ == "__main__":
    raise SystemExit(main())
