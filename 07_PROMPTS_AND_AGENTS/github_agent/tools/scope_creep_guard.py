#!/usr/bin/env python3
"""Dependency-free, read-only scope-creep guard for Codex diffs."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Sequence

DEPS = {
    "requirements.txt", "pyproject.toml", "poetry.lock", "package.json",
    "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "Pipfile", "Pipfile.lock",
}
CONTRACT_RE = re.compile(r"(schema|contract|api|protocol|canonical|DATA_PING|portfolio|market)", re.I)
WORKFLOW_RE = re.compile(r"(^|/)\.github/workflows/", re.I)
DIFF_PATH_RE = re.compile(r"^diff --git a/(.*?) b/(.*)$")


class DiffSourceError(RuntimeError):
    """Raised when the requested diff source cannot be read deterministically."""


def run_git(args: Sequence[str]) -> tuple[int, str, str]:
    result = subprocess.run(
        ["git", *args],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode, result.stdout, result.stderr.strip()


def read_diff(ns: argparse.Namespace) -> str:
    if ns.staged:
        code, stdout, stderr = run_git(["diff", "--cached", "--find-renames"])
        if code:
            raise DiffSourceError(f"git diff --cached failed: {stderr or 'unknown git error'}")
        return stdout
    if ns.base:
        code, stdout, stderr = run_git(["diff", "--find-renames", ns.base, "--"])
        if code:
            raise DiffSourceError(f"git diff base {ns.base!r} failed: {stderr or 'unknown git error'}")
        return stdout
    if ns.diff == "-":
        return sys.stdin.read()
    try:
        return Path(ns.diff).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise DiffSourceError(f"unable to read diff file {ns.diff!r}: {exc}") from exc


def parse(diff: str) -> tuple[list[str], list[dict[str, str | None]], int]:
    paths: list[str] = []
    statuses: list[dict[str, str | None]] = []
    current: str | None = None
    plus = minus = max_hunk = 0
    for line in diff.splitlines():
        match = DIFF_PATH_RE.match(line)
        if match:
            if current:
                max_hunk = max(max_hunk, plus + minus)
            current = match.group(2)
            paths.append(current)
            plus = minus = 0
        elif line.startswith("deleted file mode"):
            statuses.append({"path": current, "status": "deleted"})
        elif line.startswith("rename from") or line.startswith("rename to"):
            statuses.append({"path": current, "status": "renamed"})
        elif line.startswith("@@"):
            max_hunk = max(max_hunk, plus + minus)
            plus = minus = 0
        elif line.startswith("+") and not line.startswith("+++"):
            plus += 1
        elif line.startswith("-") and not line.startswith("---"):
            minus += 1
    if current:
        max_hunk = max(max_hunk, plus + minus)
    return sorted(set(paths)), statuses, max_hunk


def subsystem(path: str) -> str:
    parts = Path(path).parts
    return parts[0] if parts else path


def finding(code: str, classification: str, evidence: object) -> dict[str, object]:
    return {"code": code, "classification": classification, "evidence": evidence}


def analyze(intent: str, diff: str) -> dict[str, object]:
    paths, statuses, max_hunk = parse(diff)
    subsystems = sorted({subsystem(path) for path in paths})
    findings: list[dict[str, object]] = []
    allowed = [
        word.lower().strip("`.,:;()[]")
        for word in intent.split()
        if "/" in word or "github" in word.lower() or "agent" in word.lower()
    ]
    unrelated = [
        path for path in paths
        if allowed and not any(token in path.lower() for token in allowed)
    ]
    if unrelated and len(subsystems) > 1:
        findings.append(finding("UNRELATED_PATH_FAMILY", "JUSTIFY", unrelated))
    dependencies = [path for path in paths if Path(path).name in DEPS]
    if dependencies:
        findings.append(finding("DEPENDENCY_MANIFEST_CHANGE", "BLOCK_REVIEW", dependencies))
    workflows = [path for path in paths if WORKFLOW_RE.search(path)]
    if workflows:
        findings.append(finding("WORKFLOW_OR_SCHEDULE_CHANGE", "BLOCK_REVIEW", workflows))
    contracts = [
        path for path in paths
        if CONTRACT_RE.search(path) and "github_agent/tools" not in path
    ]
    if contracts:
        findings.append(finding("PUBLIC_CONTRACT_OR_AUTHORITY_SIGNAL", "SPLIT", contracts))
    if statuses:
        findings.append(finding("DESTRUCTIVE_OR_MOVE_SIGNAL", "BLOCK_REVIEW", statuses))
    if max_hunk > 250:
        findings.append(finding("OVERSIZED_HUNK", "JUSTIFY", max_hunk))
    if not findings:
        findings.append(finding("NO_SCOPE_CREEP_SIGNALS", "KEEP", []))
    overall = (
        "KEEP"
        if all(item["classification"] == "KEEP" for item in findings)
        else "BLOCK_REVIEW"
        if any(item["classification"] == "BLOCK_REVIEW" for item in findings)
        else "JUSTIFY"
    )
    return {
        "tool": "scope_creep_guard",
        "status": overall,
        "intent": intent,
        "changed_paths": paths,
        "subsystems": subsystems,
        "findings": findings,
        "limitations": [
            "Deterministic path/text checks only; no semantic LLM review.",
            "Formatting-only spill is only detectable when represented by diff/path signals.",
            "Market impact is not inferred.",
        ],
    }


def source_error_result(intent: str, error: str) -> dict[str, object]:
    return {
        "tool": "scope_creep_guard",
        "status": "BLOCK_REVIEW",
        "intent": intent,
        "changed_paths": [],
        "subsystems": [],
        "findings": [finding("DIFF_SOURCE_UNAVAILABLE", "BLOCK_REVIEW", error)],
        "limitations": ["No scope decision is valid when the requested diff source cannot be read."],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    intent_group = parser.add_mutually_exclusive_group(required=True)
    intent_group.add_argument("--intent")
    intent_group.add_argument("--intent-file")
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--staged", action="store_true")
    source_group.add_argument("--base")
    source_group.add_argument("--diff")
    ns = parser.parse_args()
    intent = ns.intent or Path(ns.intent_file).read_text(encoding="utf-8").strip()
    try:
        result = analyze(intent, read_diff(ns))
        exit_code = 0
    except DiffSourceError as exc:
        result = source_error_result(intent, str(exc))
        exit_code = 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
