#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.remediation.merge_codex_research_intake import (  # noqa: E402
    canonical_hash,
    now_iso,
    read_json,
    valid_transition,
)

MERGE_CONTRACT = "CODEX_RESEARCH_MERGE_RECEIPT_v1"
MERGE_STATUS = "MERGED_VERIFIED"
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def _gh_json(args: list[str]) -> Any:
    proc = subprocess.run(
        ["gh", "api", *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or f"exit={proc.returncode}"
        raise RuntimeError(f"GITHUB_API_UNAVAILABLE:{detail}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("GITHUB_API_NON_JSON_RESPONSE") from exc


def fetch_pr(repo_name: str, pr_number: int) -> dict[str, Any]:
    value = _gh_json([f"repos/{repo_name}/pulls/{pr_number}"])
    if not isinstance(value, dict):
        raise RuntimeError("GITHUB_PR_RESPONSE_INVALID")
    return value


def fetch_branch_prs(repo_name: str, branch: str) -> list[dict[str, Any]]:
    owner = repo_name.split("/", 1)[0]
    value = _gh_json([
        "--method", "GET",
        f"repos/{repo_name}/pulls",
        "-f", "state=closed",
        "-f", f"head={owner}:{branch}",
        "-f", "per_page=100",
    ])
    if not isinstance(value, list):
        raise RuntimeError("GITHUB_PR_LIST_RESPONSE_INVALID")
    return [row for row in value if isinstance(row, dict)]


def verify_merged_pr(
    repo_name: str,
    transition: dict[str, Any],
    *,
    fetch_one: Callable[[str, int], dict[str, Any]] = fetch_pr,
    fetch_many: Callable[[str, str], list[dict[str, Any]]] = fetch_branch_prs,
) -> dict[str, Any] | None:
    branch = str(transition.get("branch") or "")
    declared_pr = transition.get("pr_number")
    if declared_pr is not None:
        if isinstance(declared_pr, bool) or not isinstance(declared_pr, int) or declared_pr <= 0:
            raise ValueError("TRANSITION_PR_NUMBER_INVALID")
        candidates = [fetch_one(repo_name, declared_pr)]
    else:
        candidates = fetch_many(repo_name, branch)

    merged: list[dict[str, Any]] = []
    for pr in candidates:
        if not pr.get("merged_at"):
            continue
        head = pr.get("head") or {}
        if str(head.get("ref") or "") != branch:
            continue
        head_repo = str(((head.get("repo") or {}).get("full_name")) or "")
        if head_repo != repo_name:
            continue
        merge_sha = str(pr.get("merge_commit_sha") or "")
        if not SHA40.fullmatch(merge_sha):
            continue
        if declared_pr is not None and pr.get("number") != declared_pr:
            continue
        merged.append(pr)

    if not merged:
        return None
    if len(merged) != 1:
        raise RuntimeError("AMBIGUOUS_MERGED_PR_FOR_TRANSITION_BRANCH")
    return merged[0]


def build_merge_receipt(task: dict[str, Any], transition: dict[str, Any], pr: dict[str, Any], verified_at: str | None = None) -> dict[str, Any]:
    merge_sha = str(pr.get("merge_commit_sha") or "")
    pr_number = pr.get("number")
    merged_at = str(pr.get("merged_at") or "")
    if not SHA40.fullmatch(merge_sha) or isinstance(pr_number, bool) or not isinstance(pr_number, int) or pr_number <= 0 or not merged_at:
        raise ValueError("MERGED_PR_METADATA_INVALID")
    receipt = {
        "contract": MERGE_CONTRACT,
        "status": MERGE_STATUS,
        "signature": task.get("signature"),
        "candidate_id": task.get("candidate_id"),
        "candidate_sha256": task.get("candidate_sha256"),
        "task_contract_sha256": task.get("task_contract_sha256"),
        "transition_receipt_sha256": transition.get("receipt_sha256"),
        "branch": transition.get("branch"),
        "pr_number": pr_number,
        "merge_commit_sha": merge_sha,
        "merged_at_utc": merged_at,
        "verified_at_utc": verified_at or now_iso(),
        "post_fix_gate": task.get("post_fix_gate"),
        "authority": "OBSERVABILITY_ONLY_NO_COMPLETION_AUTHORITY",
    }
    receipt["receipt_sha256"] = canonical_hash({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    return receipt


def validate_existing_merge_receipt(path: Path, expected: dict[str, Any]) -> bool:
    current = read_json(path, {})
    if not isinstance(current, dict):
        raise RuntimeError("EXISTING_MERGE_RECEIPT_INVALID")
    declared = str(current.get("receipt_sha256") or "")
    actual = canonical_hash({k: v for k, v in current.items() if k != "receipt_sha256"})
    if not declared or declared != actual:
        raise RuntimeError("EXISTING_MERGE_RECEIPT_HASH_INVALID")
    for key in (
        "contract", "status", "signature", "candidate_id", "candidate_sha256",
        "task_contract_sha256", "transition_receipt_sha256", "branch", "pr_number",
        "merge_commit_sha", "merged_at_utc", "post_fix_gate", "authority",
    ):
        if current.get(key) != expected.get(key):
            raise RuntimeError(f"EXISTING_MERGE_RECEIPT_CONTRADICTION:{key}")
    return True


def reconcile(
    repo_root: Path,
    repo_name: str,
    *,
    fetch_one: Callable[[str, int], dict[str, Any]] = fetch_pr,
    fetch_many: Callable[[str, str], list[dict[str, Any]]] = fetch_branch_prs,
    verified_at: str | None = None,
) -> dict[str, Any]:
    state = read_json(repo_root / "LATEST_CODEX_EXECUTION_STATE.json", {})
    tasks = [row for row in state.get("tasks", []) if isinstance(row, dict)]
    reconciled: list[dict[str, Any]] = []
    pending: list[dict[str, Any]] = []
    skipped = 0

    for task in tasks:
        if task.get("source_type") != "RESEARCH_INTAKE" or task.get("state") not in {"IN_REMEDIATION", "POST_FIX_OBSERVATION"}:
            skipped += 1
            continue
        transition = valid_transition(repo_root, task)
        if transition is None:
            pending.append({"candidate_id": task.get("candidate_id"), "reason": "VALID_TRANSITION_REQUIRED"})
            continue
        try:
            pr = verify_merged_pr(repo_name, transition, fetch_one=fetch_one, fetch_many=fetch_many)
        except RuntimeError as exc:
            pending.append({"candidate_id": task.get("candidate_id"), "reason": str(exc)})
            continue
        if pr is None:
            pending.append({"candidate_id": task.get("candidate_id"), "reason": "BOUND_PR_NOT_VERIFIED_MERGED"})
            continue

        receipt = build_merge_receipt(task, transition, pr, verified_at=verified_at)
        out = repo_root / "research/codex/merges" / f"{task['candidate_id']}.json"
        if out.exists():
            validate_existing_merge_receipt(out, receipt)
            status = "ALREADY_PRESENT"
            current = read_json(out, {})
            receipt_sha = current.get("receipt_sha256")
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            status = "CREATED"
            receipt_sha = receipt["receipt_sha256"]
        reconciled.append({
            "candidate_id": task.get("candidate_id"),
            "pr_number": pr.get("number"),
            "merge_commit_sha": pr.get("merge_commit_sha"),
            "merge_receipt_path": out.relative_to(repo_root).as_posix(),
            "merge_receipt_sha256": receipt_sha,
            "status": status,
            "next_state": "POST_FIX_OBSERVATION",
        })

    return {
        "contract": "CODEX_RESEARCH_MERGE_RECONCILIATION_v2",
        "repository": repo_name,
        "reconciled": reconciled,
        "pending": pending,
        "skipped_non_active": skipped,
        "completion_receipts_created": 0,
        "resolution_authorized": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", ""))
    args = parser.parse_args()
    if not args.repository or "/" not in args.repository:
        raise SystemExit("GITHUB_REPOSITORY_REQUIRED")
    result = reconcile(args.repo_root, args.repository)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
