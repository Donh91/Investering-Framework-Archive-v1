#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc
CONTRACT_FIELDS = (
    "signature", "workflow", "finding", "objective", "precondition", "success_evidence",
    "clean_noop_condition", "stop_condition", "escalation_condition", "allowed_change_scope",
    "forbidden_changes", "required_evidence", "post_fix_gate",
)


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def research_signature(candidate_id: str) -> str:
    return hashlib.sha256(f"RESEARCH_CODEX|{candidate_id}".encode()).hexdigest()[:20]


def build_receipt(repo: Path, signature: str, branch: str, pr_number: int | None = None) -> dict[str, Any]:
    tasks_doc = read_json(repo / "LATEST_CODEX_READY_TASKS.json")
    matches = [t for t in tasks_doc.get("tasks", []) if isinstance(t, dict) and t.get("signature") == signature]
    if len(matches) != 1:
        raise ValueError("CODEX_READY_RESEARCH_TASK_NOT_UNIQUE_OR_MISSING")
    task = matches[0]
    if task.get("source_type") != "RESEARCH_INTAKE":
        raise ValueError("NOT_RESEARCH_INTAKE_TASK")
    candidate_id = str(task.get("candidate_id") or "")
    candidate_path = str(task.get("candidate_path") or "")
    if not candidate_id or not candidate_path:
        raise ValueError("CANDIDATE_ID_OR_PATH_MISSING")
    candidate = read_json(repo / candidate_path)
    if candidate.get("contract") != "CODEX_RESEARCH_CANDIDATE_v1" or candidate.get("status") != "SUBMITTED":
        raise ValueError("CANDIDATE_NOT_FRESH_SUBMITTED")
    if candidate.get("authority_boundary") != "CODE_REMEDIATION_ONLY" or candidate.get("requires_framework_owner_authority"):
        raise ValueError("CANDIDATE_AUTHORITY_CHANGED")
    if research_signature(candidate_id) != signature:
        raise ValueError("RESEARCH_SIGNATURE_MISMATCH")
    candidate_sha = canonical_hash(candidate)
    if candidate_sha != task.get("candidate_sha256"):
        raise ValueError("STALE_CANDIDATE_HASH_MISMATCH")
    contract = {k: task.get(k) for k in CONTRACT_FIELDS}
    if canonical_hash(contract) != task.get("task_contract_sha256"):
        raise ValueError("TASK_CONTRACT_HASH_MISMATCH")
    if not branch or branch in {"main", "master"} or branch.startswith("backup-") or branch.startswith("backup/"):
        raise ValueError("UNSAFE_REMEDIATION_BRANCH")

    receipt = {
        "contract": "CODEX_RESEARCH_TRANSITION_RECEIPT_v1",
        "state": "IN_REMEDIATION",
        "signature": signature,
        "candidate_id": candidate_id,
        "candidate_path": candidate_path,
        "candidate_sha256": candidate_sha,
        "branch": branch,
        "pr_number": pr_number,
        "recorded_at_utc": now_iso(),
        "objective": task.get("objective"),
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
    out = args.repo_root / "research/codex/transitions" / f"{args.signature}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "IN_REMEDIATION", "path": str(out), "receipt_sha256": receipt["receipt_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
