#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import urllib.parse
import urllib.request
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.remediation.write_codex_research_completion_receipt import build_completion_receipt
from scripts.remediation.mission_convergence import completion_requires_convergence, validate_receipt as validate_convergence_receipt

SPEC_CONTRACT = "CODEX_POST_FIX_VERIFICATION_SPECS_v1"


def read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def is_ancestor(repo_root: Path, ancestor: str, descendant: str) -> bool:
    if not ancestor or not descendant:
        return False
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "merge-base", "--is-ancestor", ancestor, descendant],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return proc.returncode == 0


def github_run_provider(repository: str, token: str) -> Callable[[str], list[dict[str, Any]]]:
    def load(workflow: str) -> list[dict[str, Any]]:
        encoded = urllib.parse.quote(workflow, safe="")
        url = f"https://api.github.com/repos/{repository}/actions/workflows/{encoded}/runs?branch=main&status=completed&per_page=100"
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "framework-post-fix-verifier",
            },
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            value = json.loads(response.read().decode("utf-8"))
        runs = value.get("workflow_runs", []) if isinstance(value, dict) else []
        return runs if isinstance(runs, list) else []
    return load


def json_path(value: Any, dotted: str) -> Any:
    current = value
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(dotted)
        current = current[part]
    return current


def evaluate_predicate(
    repo_root: Path,
    task: dict[str, Any],
    predicate: dict[str, Any],
    run_provider: Callable[[str], list[dict[str, Any]]],
) -> tuple[bool, str]:
    kind = str(predicate.get("kind") or "")
    if kind == "N_CONSECUTIVE_SUCCESSFUL_RUNS":
        workflow = str(predicate.get("workflow") or "")
        count = int(predicate.get("count") or 0)
        runs = sorted(run_provider(workflow), key=lambda x: str(x.get("created_at") or ""), reverse=True)
        eligible = [
            row for row in runs
            if row.get("status") == "completed"
            and is_ancestor(repo_root, str(task.get("merge_commit_sha") or ""), str(row.get("head_sha") or ""))
        ]
        sample = eligible[:count]
        successes = sum(row.get("conclusion") == "success" for row in sample)
        ok = count > 0 and len(sample) == count and successes == count
        run_states = [f"{row.get('id')}:{row.get('conclusion')}" for row in sample]
        return ok, f"{workflow}: successful_runs={successes}/{count} sampled_runs={','.join(run_states)}"
    if kind == "NO_MERGED_RESEARCH_ZOMBIES":
        state = read_json(repo_root / "LATEST_CODEX_EXECUTION_STATE.json", {}) or {}
        zombies: list[str] = []
        for row in state.get("tasks", []):
            if not isinstance(row, dict) or row.get("source_type") != "RESEARCH_INTAKE":
                continue
            candidate_id = str(row.get("candidate_id") or "")
            merge_path = repo_root / "research/codex/merges" / f"{candidate_id}.json"
            if merge_path.exists() and row.get("state") in {"CODEX_READY", "IN_REMEDIATION"}:
                zombies.append(candidate_id)
        return not zombies, "merged_research_zombies=" + (",".join(zombies) if zombies else "0")
    if kind == "JSON_PATH_EQUALS":
        path = repo_root / str(predicate.get("path") or "")
        value = read_json(path, {})
        try:
            actual = json_path(value, str(predicate.get("field") or ""))
        except KeyError:
            return False, f"{path}:missing:{predicate.get('field')}"
        expected = predicate.get("value")
        return actual == expected, f"{path.relative_to(repo_root)}:{predicate.get('field')}={actual!r}"
    return False, f"UNSUPPORTED_PREDICATE:{kind}"


def verify(
    repo_root: Path,
    specs_path: Path,
    run_provider: Callable[[str], list[dict[str, Any]]],
    *,
    write: bool = True,
) -> dict[str, Any]:
    state = read_json(repo_root / "LATEST_CODEX_EXECUTION_STATE.json", {}) or {}
    specs = read_json(specs_path, {}) or {}
    if specs.get("contract") != SPEC_CONTRACT:
        raise ValueError("POST_FIX_SPEC_CONTRACT_INVALID")
    tasks = {str(row.get("candidate_id")): row for row in state.get("tasks", []) if isinstance(row, dict) and row.get("candidate_id")}
    report: dict[str, Any] = {"contract": "CODEX_POST_FIX_VERIFICATION_REPORT_v1", "verified": [], "blocked": [], "skipped": []}
    for spec in specs.get("candidates", []):
        candidate_id = str(spec.get("candidate_id") or "")
        task = tasks.get(candidate_id)
        if not task or task.get("state") != "POST_FIX_OBSERVATION":
            report["skipped"].append({"candidate_id": candidate_id, "reason": "NOT_POST_FIX_OBSERVATION"})
            continue
        completion_path = repo_root / "research/codex/completions" / f"{candidate_id}.json"
        if completion_path.exists():
            report["skipped"].append({"candidate_id": candidate_id, "reason": "COMPLETION_ALREADY_EXISTS"})
            continue
        checks: list[dict[str, Any]] = []
        passed = True
        for predicate in spec.get("predicates", []):
            ok, evidence = evaluate_predicate(repo_root, task, predicate, run_provider)
            checks.append({"kind": predicate.get("kind"), "pass": ok, "evidence": evidence})
            passed = passed and ok
        if not checks or not passed:
            report["blocked"].append({"candidate_id": candidate_id, "checks": checks})
            continue
        evidence = [f"AUTO_VERIFIER:{row['kind']}:{row['evidence']}" for row in checks]
        receipt = build_completion_receipt(
            repo_root,
            candidate_id,
            str(task.get("merge_commit_sha") or ""),
            int(task.get("pr_number") or 0),
            evidence,
        )
        if completion_requires_convergence(receipt):
            convergence = validate_convergence_receipt(repo_root, task, receipt)
            if convergence is None:
                checks.append({
                    "kind": "MISSION_CONVERGENCE",
                    "pass": False,
                    "evidence": "MISSION_CONVERGENCE_REQUIRED",
                })
                report["blocked"].append({"candidate_id": candidate_id, "checks": checks})
                continue
            checks.append({
                "kind": "MISSION_CONVERGENCE",
                "pass": True,
                "evidence": f"receipt_sha256={convergence.get('receipt_sha256')}",
            })
        if write:
            completion_path.parent.mkdir(parents=True, exist_ok=True)
            completion_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        report["verified"].append({"candidate_id": candidate_id, "receipt_sha256": receipt["receipt_sha256"], "checks": checks})
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--specs", type=Path, default=Path("research/codex/post_fix_verification_specs_v1.json"))
    parser.add_argument("--repository")
    parser.add_argument("--token")
    parser.add_argument("--workflow-runs-fixture", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    specs_path = args.specs if args.specs.is_absolute() else args.repo_root / args.specs
    if args.workflow_runs_fixture:
        fixture_path = args.workflow_runs_fixture if args.workflow_runs_fixture.is_absolute() else args.repo_root / args.workflow_runs_fixture
        fixture = read_json(fixture_path, {}) or {}
        provider = lambda workflow: list(fixture.get(workflow, []))
    else:
        if not args.repository or not args.token:
            raise ValueError("GITHUB_REPOSITORY_AND_TOKEN_REQUIRED")
        provider = github_run_provider(args.repository, args.token)
    report = verify(args.repo_root, specs_path, provider, write=not args.dry_run)
    out = args.repo_root / "research/codex/post_fix_verification/LATEST.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"verified": len(report["verified"]), "blocked": len(report["blocked"]), "skipped": len(report["skipped"])}, sort_keys=True))


if __name__ == "__main__":
    main()
