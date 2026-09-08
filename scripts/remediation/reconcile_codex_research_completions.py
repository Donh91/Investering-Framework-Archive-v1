#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Callable

from scripts.remediation.write_codex_research_completion_receipt import (
    build_completion_receipt,
    canonical_hash,
)

SHA40 = re.compile(r"^[0-9a-f]{40}$")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(value, indent=2, sort_keys=True) + "\n"
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, path)
    finally:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass


def valid_transition(task: dict[str, Any], transition: dict[str, Any]) -> bool:
    if transition.get("contract") != "CODEX_RESEARCH_TRANSITION_RECEIPT_v1":
        return False
    if transition.get("state") != "IN_REMEDIATION":
        return False
    if transition.get("signature") != task.get("signature"):
        return False
    if transition.get("candidate_id") != task.get("candidate_id"):
        return False
    if transition.get("candidate_sha256") != task.get("candidate_sha256"):
        return False
    if transition.get("task_contract_sha256") != task.get("task_contract_sha256"):
        return False
    branch = str(transition.get("branch") or "")
    if not branch or branch in {"main", "master"} or branch.startswith(("backup-", "backup/")):
        return False
    declared = str(transition.get("receipt_sha256") or "")
    actual = canonical_hash({k: v for k, v in transition.items() if k != "receipt_sha256"})
    return bool(declared) and declared == actual


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
    return [x for x in value if isinstance(x, dict)]


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
        if str(((pr.get("head") or {}).get("ref")) or "") != branch:
            continue
        head_repo = str((((pr.get("head") or {}).get("repo") or {}).get("full_name")) or "")
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


def _existing_completion_valid(path: Path, expected: dict[str, Any]) -> bool:
    if not path.exists():
        return False
    current = read_json(path)
    if not isinstance(current, dict):
        raise RuntimeError("EXISTING_COMPLETION_INVALID")
    declared = str(current.get("receipt_sha256") or "")
    actual = canonical_hash({k: v for k, v in current.items() if k != "receipt_sha256"})
    if not declared or declared != actual:
        raise RuntimeError("EXISTING_COMPLETION_HASH_INVALID")
    immutable_fields = (
        "contract", "status", "candidate_id", "signature", "candidate_sha256",
        "task_contract_sha256", "pr_number", "merge_commit_sha", "post_fix_gate",
    )
    if any(current.get(k) != expected.get(k) for k in immutable_fields):
        raise RuntimeError("EXISTING_COMPLETION_CONTRADICTS_VERIFIED_MERGE")
    return True


def reconcile(
    repo_root: Path,
    repo_name: str,
    *,
    fetch_one: Callable[[str, int], dict[str, Any]] = fetch_pr,
    fetch_many: Callable[[str, str], list[dict[str, Any]]] = fetch_branch_prs,
) -> dict[str, Any]:
    state_path = repo_root / "LATEST_CODEX_EXECUTION_STATE.json"
    state = read_json(state_path)
    tasks = [x for x in state.get("tasks", []) if isinstance(x, dict)]

    reconciled: list[dict[str, Any]] = []
    pending: list[dict[str, Any]] = []
    skipped = 0

    for task in tasks:
        if task.get("source_type") != "RESEARCH_INTAKE" or task.get("state") != "IN_REMEDIATION":
            skipped += 1
            continue
        transition_rel = str(task.get("transition_receipt_path") or "")
        if not transition_rel:
            pending.append({"candidate_id": task.get("candidate_id"), "reason": "TRANSITION_PATH_MISSING"})
            continue
        transition_path = repo_root / transition_rel
        if not transition_path.exists():
            pending.append({"candidate_id": task.get("candidate_id"), "reason": "TRANSITION_MISSING"})
            continue
        transition = read_json(transition_path)
        if not isinstance(transition, dict) or not valid_transition(task, transition):
            raise RuntimeError(f"INVALID_TRANSITION:{task.get('candidate_id')}")

        try:
            pr = verify_merged_pr(
                repo_name,
                transition,
                fetch_one=fetch_one,
                fetch_many=fetch_many,
            )
        except RuntimeError as exc:
            pending.append({"candidate_id": task.get("candidate_id"), "reason": str(exc)})
            continue

        if pr is None:
            pending.append({"candidate_id": task.get("candidate_id"), "reason": "BOUND_PR_NOT_VERIFIED_MERGED"})
            continue

        pr_number = int(pr["number"])
        merge_sha = str(pr["merge_commit_sha"])
        evidence = [
            f"github_pr:{repo_name}#{pr_number}",
            f"merge_commit:{merge_sha}",
            f"transition_receipt:{transition_rel}",
        ]
        receipt = build_completion_receipt(
            repo_root,
            str(task["candidate_id"]),
            merge_sha,
            pr_number,
            evidence,
        )
        out = repo_root / "research/codex/completions" / f"{task['candidate_id']}.json"
        if _existing_completion_valid(out, receipt):
            reconciled.append({
                "candidate_id": task.get("candidate_id"),
                "pr_number": pr_number,
                "merge_commit_sha": merge_sha,
                "status": "ALREADY_PRESENT",
            })
            continue
        write_json_atomic(out, receipt)
        reconciled.append({
            "candidate_id": task.get("candidate_id"),
            "pr_number": pr_number,
            "merge_commit_sha": merge_sha,
            "status": "MATERIALIZED",
        })

    return {
        "contract": "CODEX_RESEARCH_COMPLETION_RECONCILIATION_v1",
        "repository": repo_name,
        "reconciled": reconciled,
        "pending": pending,
        "skipped_non_active": skipped,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, default=Path("."))
    p.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", ""))
    args = p.parse_args()
    if not args.repository or "/" not in args.repository:
        raise SystemExit("GITHUB_REPOSITORY_REQUIRED")
    result = reconcile(args.repo_root, args.repository)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
