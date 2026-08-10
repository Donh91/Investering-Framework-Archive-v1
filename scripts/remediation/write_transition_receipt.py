#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def build_receipt(repo: Path, signature: str, branch: str, pr_number: int | None = None) -> dict[str, Any]:
    tasks_doc = read_json(repo / "LATEST_CODEX_READY_TASKS.json")
    health = read_json(repo / "research/architecture_health/LATEST_AUTOMATION_HEALTH.json")
    tasks = [t for t in tasks_doc.get("tasks", []) if isinstance(t, dict) and t.get("signature") == signature]
    if len(tasks) != 1:
        raise ValueError("CODEX_READY_TASK_NOT_UNIQUE_OR_MISSING")
    task = tasks[0]
    if task.get("source_health_generated_at_utc") and task.get("source_health_generated_at_utc") != health.get("generated_at_utc"):
        raise ValueError("STALE_TASK_HEALTH_GENERATION_MISMATCH")

    contract_fields = {k: task.get(k) for k in (
        "signature", "workflow", "finding", "objective", "precondition", "success_evidence",
        "clean_noop_condition", "stop_condition", "escalation_condition", "allowed_change_scope",
        "forbidden_changes", "required_evidence", "post_fix_gate"
    )}
    if task.get("task_contract_sha256") != canonical_hash(contract_fields):
        raise ValueError("TASK_CONTRACT_HASH_MISMATCH")

    fresh_findings = set()
    for workflow in health.get("workflows", []):
        if not isinstance(workflow, dict):
            continue
        name = str(workflow.get("workflow") or "UNKNOWN")
        for finding in workflow.get("findings", []):
            raw = f"{name}|{finding}".encode()
            fresh_findings.add(hashlib.sha256(raw).hexdigest()[:20])
    if signature not in fresh_findings:
        raise ValueError("STALE_TASK_NO_CHANGE")
    if not branch or branch in {"main", "master"} or branch.startswith("backup/"):
        raise ValueError("UNSAFE_REMEDIATION_BRANCH")

    receipt = {
        "contract": "REMEDIATION_TRANSITION_RECEIPT_v1",
        "signature": signature,
        "state": "IN_REMEDIATION",
        "workflow": task.get("workflow"),
        "finding": task.get("finding"),
        "branch": branch,
        "pr_number": pr_number,
        "recorded_at_utc": now_iso(),
        "source_health_generated_at_utc": health.get("generated_at_utc"),
        "latest_run_id": task.get("latest_run_id"),
        "objective": task.get("objective"),
        "precondition": task.get("precondition"),
        "success_evidence": task.get("success_evidence"),
        "clean_noop_condition": task.get("clean_noop_condition"),
        "stop_condition": task.get("stop_condition"),
        "escalation_condition": task.get("escalation_condition"),
        "allowed_change_scope": task.get("allowed_change_scope"),
        "forbidden_changes": task.get("forbidden_changes"),
        "post_fix_gate": task.get("post_fix_gate"),
        "task_contract_sha256": task.get("task_contract_sha256"),
    }
    receipt["receipt_sha256"] = canonical_hash({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    return receipt


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, default=Path("."))
    p.add_argument("--signature", required=True)
    p.add_argument("--branch", required=True)
    p.add_argument("--pr-number", type=int)
    args = p.parse_args()
    receipt = build_receipt(args.repo_root, args.signature, args.branch, args.pr_number)
    out = args.repo_root / "research/remediation/transitions" / f"{args.signature}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "IN_REMEDIATION", "path": str(out), "receipt_sha256": receipt["receipt_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
