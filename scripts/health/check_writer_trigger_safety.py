from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def has_job_main_guard(text: str) -> bool:
    return re.search(r"(?m)^\s{4}if:\s*.*github\.ref\s*==\s*['\"]refs/heads/main['\"]", text) is not None


def checkout_has_main_pin(text: str) -> bool:
    blocks = re.split(r"(?m)^\s*- uses:\s*actions/checkout@", text)[1:]
    return any(re.search(r"(?m)^\s+ref:\s*main\s*$", block.split("\n      - ", 1)[0]) is not None for block in blocks)


def inspect(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    writes_main = "contents: write" in text and "git push" in text and "HEAD:main" in text
    if not writes_main:
        return []

    findings: list[str] = []
    push_trigger = re.search(r"(?m)^  push:\s*$", text) is not None
    manual_trigger = re.search(r"(?m)^  workflow_dispatch:\s*$", text) is not None
    main_guard = has_job_main_guard(text)
    pinned = checkout_has_main_pin(text)
    writer_group = re.search(r"(?m)^\s+group:\s*framework-main-writer\s*$", text) is not None

    if push_trigger:
        findings.append("PUSH_TRIGGERED_MAIN_WRITER")
    if manual_trigger and not (main_guard or pinned):
        findings.append("UNPINNED_MANUAL_MAIN_WRITER")
    if not pinned:
        findings.append("MAIN_WRITER_CHECKOUT_NOT_PINNED")
    if not writer_group:
        findings.append("MAIN_WRITER_WITHOUT_SHARED_CONCURRENCY")
    return findings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workflow-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = []
    for path in sorted(list(args.workflow_root.glob("*.yml")) + list(args.workflow_root.glob("*.yaml"))):
        findings = inspect(path)
        if findings:
            rows.append({"path": str(path), "findings": findings})
    result = {
        "contract": "WRITER_TRIGGER_SAFETY_v2",
        "status": "PASS" if not rows else "FAIL",
        "violations": rows,
        "rules": [
            "A main writer must never run from a generic push event.",
            "A manually dispatchable main writer must be pinned to main by job guard or checkout ref.",
            "Every main-writing workflow must include an explicit main checkout; immutable downstream checkouts may use a frozen commit.",
            "Every main writer must serialize through framework-main-writer concurrency.",
        ],
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps(result, sort_keys=True))
    if rows:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
