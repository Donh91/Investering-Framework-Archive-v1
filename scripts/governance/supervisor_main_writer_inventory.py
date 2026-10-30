"""Read-only inventory of obvious direct-main writes in GitHub Actions YAML.

This is a migration aid, NOT a cross-actor lock, ruleset, or merge approval.
Unrecognized/API/dynamic writers and runtime principal permissions remain unknown.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

CRITICAL = frozenset({
    "hourly-sequence-capture.yml",
    "native-handlekompas.yml",
    "daily-compass.yml",
    "compass-event-refresh.yml",
    "native-market-recovery.yml",
    "cycle-navigator-weekly-publication.yml",
    "framework-learning-supervisor.yml",
})

# Deliberately bounded: evidence of a syntactically identifiable main write,
# never evidence that other workflows are safe or that this writer ran.
PUSH_MAIN = re.compile(
    r"\bgit\s+push\b[^\n]*(?:\bHEAD:(?:refs/heads/)?main\b|\brefs/heads/main\b|\borigin\s+main\b)",
    re.IGNORECASE,
)
API_MAIN = re.compile(
    r"\b(?:gh\s+api|curl)\b[^\n]*(?:git/refs/heads/main|/git/refs/heads/main)",
    re.IGNORECASE,
)
def concurrency_groups(source: str) -> list[str]:
    """Bounded YAML evidence: only workflow and jobs.<name> concurrency.group.

    This intentionally does not claim to parse all YAML or enforce a lock.
    Nested env.group and shell here-documents must not masquerade as locks.
    """
    groups: set[str] = set()
    parents: list[tuple[int, str]] = []
    block_indent: int | None = None
    for raw in source.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if block_indent is not None:
            if indent > block_indent:
                continue
            block_indent = None
        match = re.match(r"^ *-? ?([A-Za-z0-9_-]+):(?:[ \t]*(.*))?$", raw)
        if not match:
            continue
        key = match.group(1)
        value = (match.group(2) or "").strip()
        while parents and indent <= parents[-1][0]:
            parents.pop()
        path = [name for _, name in parents]
        if key == "group" and value and (
            path == ["concurrency"]
            or (len(path) == 3 and path[0] == "jobs" and path[-1] == "concurrency")
        ):
            groups.add(value)
        if value.startswith(("|", ">")):
            block_indent = indent
        if not value or value.startswith("#"):
            parents.append((indent, key))
    return sorted(groups)

CONTENT_WRITE = re.compile(r"^\s*contents:\s*write\s*(?:#.*)?$", re.MULTILINE)


def analyze_workflow(path: Path, workflow_dir: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    evidence = []
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if PUSH_MAIN.search(line) or API_MAIN.search(line):
            evidence.append({"line": number, "expression": line[:240]})
    if not evidence:
        return None
    return {
        "workflow": path.relative_to(workflow_dir).as_posix(),
        "critical_publication_or_supervision": path.name in CRITICAL,
        "concurrency_groups_seen": concurrency_groups(text),
        "contents_write_declared": bool(CONTENT_WRITE.search(text)),
        "direct_main_write_evidence": evidence,
        "principal": "UNVERIFIED_RUNTIME",
        "trigger": "UNVERIFIED_RUNTIME",
        "target_output_paths": "UNVERIFIED_RUNTIME",
    }


def census(root: Path) -> dict:
    workflow_dir = root / ".github" / "workflows"
    if not workflow_dir.is_dir():
        raise FileNotFoundError(f"Not a checked-out workflow directory: {workflow_dir}")
    files = sorted(set(workflow_dir.rglob("*.yml")) | set(workflow_dir.rglob("*.yaml")))
    writers = [entry for path in files
               if (entry := analyze_workflow(path, workflow_dir)) is not None]
    captured_critical = {w["workflow"].split("/")[-1] for w in writers}
    return {
        "contract": "SUPERVISOR_MAIN_WRITER_INVENTORY_v1_READ_ONLY",
        "workflow_files_scanned": len(files),
        "obvious_direct_main_writer_workflows": len(writers),
        "critical_writers_not_detected": sorted(CRITICAL - captured_critical),
        "writers": writers,
        "coverage": "BOUNDED_REGEX_EVIDENCE_NOT_EXHAUSTIVE",
        "platform_enforced_serialization": "NOT_ASSESSED",
        "kill_switch_enforced": "NOT_ASSESSED",
        "merge_release_authority": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."))
    args = parser.parse_args()
    print(json.dumps(census(args.repo), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
