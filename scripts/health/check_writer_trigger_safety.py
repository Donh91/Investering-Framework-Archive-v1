from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PR_ISOLATED_WRITER_GROUP = "${{ github.event_name == 'pull_request' && format('{0}-pr-{1}', github.workflow, github.event.pull_request.number) || 'framework-main-writer' }}"
MARKET_WRITER_GROUP = "framework-market-owner-writer"
PR_ISOLATED_MARKET_WRITER_GROUP = "${{ github.event_name == 'pull_request' && format('{0}-pr-{1}', github.workflow, github.event.pull_request.number) || 'framework-market-owner-writer' }}"
MARKET_WRITER_ALLOWLIST = {
    "hourly-sequence-capture.yml",
    "entry-signal-ledger.yml",
    "native-handlekompas.yml",
    "native-market-recovery.yml",
    "intraday-execution-research.yml",
    "compass-event-refresh.yml",
    "daily-compass.yml",
}


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
    pr_trigger = re.search(r"(?m)^  pull_request:\s*$", text) is not None
    manual_trigger = re.search(r"(?m)^  workflow_dispatch:\s*$", text) is not None
    main_guard = has_job_main_guard(text)
    pinned = checkout_has_main_pin(text)
    group_match = re.search(r"(?m)^\s+group:\s*([^\n#]+)", text)
    group_value = group_match.group(1).strip().strip("'\"") if group_match else None
    queue_match = re.search(r"(?m)^\s+queue:\s*([^\n#]+)", text)
    queue_value = queue_match.group(1).strip().strip("'\"") if queue_match else None
    cancel_match = re.search(r"(?m)^\s+cancel-in-progress:\s*([^\n#]+)", text)
    cancel_value = cancel_match.group(1).strip().strip("'\"") if cancel_match else None
    global_writer_group = group_value in {"framework-main-writer", PR_ISOLATED_WRITER_GROUP}
    market_writer_group = path.name in MARKET_WRITER_ALLOWLIST and group_value in {
        MARKET_WRITER_GROUP,
        PR_ISOLATED_MARKET_WRITER_GROUP,
    }
    writer_group = global_writer_group or market_writer_group

    if push_trigger:
        findings.append("PUSH_TRIGGERED_MAIN_WRITER")
    if manual_trigger and not (main_guard or pinned):
        findings.append("UNPINNED_MANUAL_MAIN_WRITER")
    if not pinned:
        findings.append("MAIN_WRITER_CHECKOUT_NOT_PINNED")
    if not writer_group:
        findings.append("MAIN_WRITER_WITHOUT_SHARED_CONCURRENCY")
    elif queue_value != "max":
        findings.append("MAIN_WRITER_WITHOUT_MAX_QUEUE")
    elif cancel_value not in {None, "false"}:
        findings.append("MAIN_WRITER_QUEUE_CANCEL_CONFLICT")
    if pr_trigger and group_value in {"framework-main-writer", MARKET_WRITER_GROUP}:
        findings.append("PR_VALIDATION_COMPETES_WITH_MAIN_WRITER")
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
            "Every production main writer must serialize through framework-main-writer, except the explicit latency-critical market-owner allowlist which serializes through framework-market-owner-writer.",
            "Every approved writer group member must use queue: max so later group members cannot replace a pending production writer.",
            "A workflow with pull_request validation and production main writes must isolate PR runs from framework-main-writer.",
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
