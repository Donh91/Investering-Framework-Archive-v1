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


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, default=Path("."))
    p.add_argument("--candidate-id", required=True)
    p.add_argument("--merge-commit-sha", required=True)
    p.add_argument("--pr-number", type=int, required=True)
    p.add_argument("--evidence", action="append", required=True)
    args = p.parse_args()

    state = read_json(args.repo_root / "LATEST_CODEX_EXECUTION_STATE.json")
    matches = [
        t for t in state.get("tasks", [])
        if isinstance(t, dict) and t.get("candidate_id") == args.candidate_id and t.get("source_type") == "RESEARCH_INTAKE"
    ]
    if len(matches) != 1:
        raise ValueError("RESEARCH_TASK_NOT_UNIQUE_OR_MISSING")
    task = matches[0]
    if task.get("state") not in {"IN_REMEDIATION", "POST_FIX_OBSERVATION"}:
        raise ValueError("TASK_NOT_IN_VERIFIABLE_REMEDIATION_STATE")
    receipt = {
        "contract": "CODEX_RESEARCH_COMPLETION_RECEIPT_v1",
        "status": "VERIFIED",
        "candidate_id": args.candidate_id,
        "signature": task.get("signature"),
        "candidate_sha256": task.get("candidate_sha256"),
        "task_contract_sha256": task.get("task_contract_sha256"),
        "pr_number": args.pr_number,
        "merge_commit_sha": args.merge_commit_sha,
        "verified_at_utc": now_iso(),
        "verification_evidence": args.evidence,
        "post_fix_gate": task.get("post_fix_gate"),
    }
    receipt["receipt_sha256"] = canonical_hash({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    out = args.repo_root / "research/codex/completions" / f"{args.candidate_id}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "VERIFIED", "path": str(out), "receipt_sha256": receipt["receipt_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
