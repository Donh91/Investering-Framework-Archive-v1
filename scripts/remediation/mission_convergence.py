#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc
CONTRACT = "MISSION_CONVERGENCE_RECEIPT_v1"
ASSESSMENT_CONTRACT = "MISSION_CONVERGENCE_ASSESSMENT_v1"
STATUS_CONVERGED = "CONVERGED"
STATUS_NOT_CONVERGED = "NOT_CONVERGED"
LEGACY_COMPLETION_CONTRACT = "CODEX_RESEARCH_COMPLETION_RECEIPT_v1"
ACTIVATION_UTC = "2026-09-13T15:30:00Z"
GAP_TYPES = {"missing", "partial", "contradicts", "unrequested"}
REQUIREMENT_STATUS = {"SATISFIED", "BLOCKED"}


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _nonempty_strings(values: Any, error: str) -> list[str]:
    if not isinstance(values, list) or any(not isinstance(x, str) or not x.strip() for x in values):
        raise ValueError(error)
    return [x.strip() for x in values]


def task_for_candidate(repo_root: Path, candidate_id: str) -> dict[str, Any]:
    state = read_json(repo_root / "LATEST_CODEX_EXECUTION_STATE.json")
    matches = [
        row for row in state.get("tasks", [])
        if isinstance(row, dict)
        and row.get("source_type") == "RESEARCH_INTAKE"
        and row.get("candidate_id") == candidate_id
    ]
    if len(matches) != 1:
        raise ValueError("RESEARCH_TASK_NOT_UNIQUE_OR_MISSING")
    return matches[0]


def candidate_for_task(repo_root: Path, task: dict[str, Any]) -> dict[str, Any]:
    path = repo_root / str(task.get("candidate_path") or "")
    if not path.is_file():
        raise ValueError("CANDIDATE_PATH_MISSING")
    data = read_json(path)
    if not isinstance(data, dict) or data.get("candidate_id") != task.get("candidate_id"):
        raise ValueError("CANDIDATE_DOCUMENT_INVALID")
    return data


def requirement_inventory(task: dict[str, Any], candidate: dict[str, Any]) -> list[dict[str, str]]:
    inventory: list[dict[str, str]] = []

    objective = str(candidate.get("objective") or task.get("objective") or "").strip()
    if not objective:
        raise ValueError("CONVERGENCE_OBJECTIVE_MISSING")
    inventory.append({"source_ref": "objective", "text": objective, "kind": "OBJECTIVE"})

    tests = candidate.get("acceptance_tests")
    if not isinstance(tests, dict):
        raise ValueError("CONVERGENCE_ACCEPTANCE_TESTS_MISSING")
    for polarity in ("positive", "negative"):
        values = _nonempty_strings(tests.get(polarity), f"CONVERGENCE_{polarity.upper()}_TESTS_INVALID")
        if not values:
            raise ValueError(f"CONVERGENCE_{polarity.upper()}_TESTS_EMPTY")
        for idx, text in enumerate(values, 1):
            inventory.append({
                "source_ref": f"acceptance:{polarity}:{idx}",
                "text": text,
                "kind": f"ACCEPTANCE_{polarity.upper()}",
            })

    allowed = _nonempty_strings(candidate.get("allowed_change_scope"), "CONVERGENCE_ALLOWED_SCOPE_INVALID")
    if not allowed:
        raise ValueError("CONVERGENCE_ALLOWED_SCOPE_EMPTY")
    inventory.append({
        "source_ref": "authority:allowed_change_scope",
        "text": " | ".join(allowed),
        "kind": "AUTHORITY_BOUNDARY",
    })

    forbidden = _nonempty_strings(candidate.get("forbidden_changes"), "CONVERGENCE_FORBIDDEN_CHANGES_INVALID")
    if not forbidden:
        raise ValueError("CONVERGENCE_FORBIDDEN_CHANGES_EMPTY")
    inventory.append({
        "source_ref": "authority:forbidden_changes",
        "text": " | ".join(forbidden),
        "kind": "AUTHORITY_BOUNDARY",
    })

    gate = str(candidate.get("post_fix_gate") or task.get("post_fix_gate") or "").strip()
    if gate:
        inventory.append({"source_ref": "post_fix_gate", "text": gate, "kind": "POST_FIX_GATE"})

    return inventory


def normalize_assessment(
    assessment: dict[str, Any],
    inventory: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    if assessment.get("contract") != ASSESSMENT_CONTRACT:
        raise ValueError("CONVERGENCE_ASSESSMENT_CONTRACT_INVALID")

    expected = {item["source_ref"] for item in inventory}
    coverage = assessment.get("coverage")
    if not isinstance(coverage, list):
        raise ValueError("CONVERGENCE_COVERAGE_INVALID")

    normalized_coverage: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in coverage:
        if not isinstance(item, dict):
            raise ValueError("CONVERGENCE_COVERAGE_ITEM_INVALID")
        ref = str(item.get("source_ref") or "").strip()
        status = str(item.get("status") or "").strip()
        evidence = _nonempty_strings(item.get("evidence"), "CONVERGENCE_EVIDENCE_INVALID")
        if ref not in expected:
            raise ValueError(f"CONVERGENCE_UNKNOWN_SOURCE_REF:{ref}")
        if ref in seen:
            raise ValueError(f"CONVERGENCE_DUPLICATE_SOURCE_REF:{ref}")
        if status not in REQUIREMENT_STATUS:
            raise ValueError(f"CONVERGENCE_STATUS_INVALID:{ref}")
        if not evidence:
            raise ValueError(f"CONVERGENCE_EVIDENCE_REQUIRED:{ref}")
        seen.add(ref)
        normalized_coverage.append({"source_ref": ref, "status": status, "evidence": evidence})

    missing_refs = sorted(expected - seen)
    if missing_refs:
        raise ValueError("CONVERGENCE_REQUIREMENT_COVERAGE_INCOMPLETE:" + ",".join(missing_refs))

    gaps = assessment.get("gaps", [])
    if not isinstance(gaps, list):
        raise ValueError("CONVERGENCE_GAPS_INVALID")
    normalized_gaps: list[dict[str, Any]] = []
    for gap in gaps:
        if not isinstance(gap, dict):
            raise ValueError("CONVERGENCE_GAP_ITEM_INVALID")
        gap_type = str(gap.get("gap_type") or "").strip()
        source_ref = str(gap.get("source_ref") or "").strip()
        evidence = _nonempty_strings(gap.get("evidence"), "CONVERGENCE_GAP_EVIDENCE_INVALID")
        if gap_type not in GAP_TYPES:
            raise ValueError("CONVERGENCE_GAP_TYPE_INVALID")
        if source_ref and source_ref not in expected:
            raise ValueError("CONVERGENCE_GAP_SOURCE_REF_INVALID")
        if not evidence:
            raise ValueError("CONVERGENCE_GAP_EVIDENCE_REQUIRED")
        normalized_gaps.append({"gap_type": gap_type, "source_ref": source_ref or None, "evidence": evidence})

    blocked = any(item["status"] != "SATISFIED" for item in normalized_coverage)
    status = STATUS_NOT_CONVERGED if blocked or normalized_gaps else STATUS_CONVERGED
    return normalized_coverage, normalized_gaps, status


def build_receipt(
    repo_root: Path,
    candidate_id: str,
    merge_commit_sha: str,
    pr_number: int,
    assessment_path: Path,
    *,
    assessed_at_utc: str | None = None,
) -> dict[str, Any]:
    task = task_for_candidate(repo_root, candidate_id)
    if task.get("state") not in {"POST_FIX_OBSERVATION", "IN_REMEDIATION"}:
        raise ValueError("TASK_NOT_IN_CONVERGENCE_ELIGIBLE_STATE")
    candidate = candidate_for_task(repo_root, task)
    inventory = requirement_inventory(task, candidate)
    assessment = read_json(assessment_path)
    if not isinstance(assessment, dict):
        raise ValueError("CONVERGENCE_ASSESSMENT_DOCUMENT_INVALID")
    if assessment.get("candidate_id") != candidate_id:
        raise ValueError("CONVERGENCE_ASSESSMENT_CANDIDATE_MISMATCH")
    coverage, gaps, status = normalize_assessment(assessment, inventory)

    receipt = {
        "contract": CONTRACT,
        "status": status,
        "candidate_id": candidate_id,
        "signature": task.get("signature"),
        "candidate_sha256": task.get("candidate_sha256"),
        "task_contract_sha256": task.get("task_contract_sha256"),
        "pr_number": pr_number,
        "merge_commit_sha": merge_commit_sha,
        "assessed_at_utc": assessed_at_utc or now_iso(),
        "requirements": inventory,
        "coverage": coverage,
        "gaps": gaps,
        "authority": "CLOSURE_GATE_ONLY_NO_MARKET_OR_PORTFOLIO_AUTHORITY",
    }
    receipt["receipt_sha256"] = canonical_hash({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    return receipt


def validate_receipt(repo_root: Path, task: dict[str, Any], completion: dict[str, Any]) -> dict[str, Any] | None:
    path = repo_root / "research/codex/convergence" / f"{task['candidate_id']}.json"
    if not path.is_file():
        return None
    try:
        receipt = read_json(path)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(receipt, dict):
        return None
    if receipt.get("contract") != CONTRACT or receipt.get("status") != STATUS_CONVERGED:
        return None
    if receipt.get("candidate_id") != task.get("candidate_id") or receipt.get("signature") != task.get("signature"):
        return None
    if receipt.get("candidate_sha256") != task.get("candidate_sha256"):
        return None
    if receipt.get("task_contract_sha256") != task.get("task_contract_sha256"):
        return None
    if receipt.get("merge_commit_sha") != completion.get("merge_commit_sha"):
        return None
    if receipt.get("pr_number") != completion.get("pr_number"):
        return None
    if receipt.get("authority") != "CLOSURE_GATE_ONLY_NO_MARKET_OR_PORTFOLIO_AUTHORITY":
        return None
    if receipt.get("gaps") != []:
        return None
    coverage = receipt.get("coverage")
    requirements = receipt.get("requirements")
    if not isinstance(coverage, list) or not isinstance(requirements, list):
        return None
    expected = {str(x.get("source_ref")) for x in requirements if isinstance(x, dict)}
    actual = {str(x.get("source_ref")) for x in coverage if isinstance(x, dict) and x.get("status") == "SATISFIED"}
    if not expected or expected != actual:
        return None
    if any(not isinstance(x.get("evidence"), list) or not x.get("evidence") for x in coverage if isinstance(x, dict)):
        return None
    declared = str(receipt.get("receipt_sha256") or "")
    actual_hash = canonical_hash({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    return receipt if declared and declared == actual_hash else None


def completion_requires_convergence(completion: dict[str, Any]) -> bool:
    if completion.get("contract") != LEGACY_COMPLETION_CONTRACT:
        return True
    verified = str(completion.get("verified_at_utc") or "")
    return bool(verified and verified >= ACTIVATION_UTC)


def validate_active_completions(repo_root: Path) -> dict[str, Any]:
    state_path = repo_root / "LATEST_CODEX_EXECUTION_STATE.json"
    if not state_path.is_file():
        raise ValueError("CODEX_EXECUTION_STATE_MISSING")
    state = read_json(state_path)
    failures: list[str] = []
    checked = 0
    for task in state.get("tasks", []):
        if not isinstance(task, dict) or task.get("source_type") != "RESEARCH_INTAKE":
            continue
        path = repo_root / "research/codex/completions" / f"{task.get('candidate_id')}.json"
        if not path.is_file():
            continue
        completion = read_json(path)
        if not isinstance(completion, dict) or not completion_requires_convergence(completion):
            continue
        checked += 1
        if validate_receipt(repo_root, task, completion) is None:
            failures.append(str(task.get("candidate_id")))
    if failures:
        raise ValueError("MISSION_CONVERGENCE_REQUIRED:" + ",".join(sorted(failures)))
    return {"status": "PASS", "checked": checked}


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("--repo-root", type=Path, default=Path("."))
    build.add_argument("--candidate-id", required=True)
    build.add_argument("--merge-commit-sha", required=True)
    build.add_argument("--pr-number", type=int, required=True)
    build.add_argument("--assessment-json", type=Path, required=True)

    validate = sub.add_parser("validate-active-completions")
    validate.add_argument("--repo-root", type=Path, default=Path("."))

    args = parser.parse_args()
    if args.command == "build":
        assessment_path = args.assessment_json
        if not assessment_path.is_absolute():
            assessment_path = args.repo_root / assessment_path
        receipt = build_receipt(
            args.repo_root,
            args.candidate_id,
            args.merge_commit_sha,
            args.pr_number,
            assessment_path,
        )
        out = args.repo_root / "research/codex/convergence" / f"{args.candidate_id}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"status": receipt["status"], "path": str(out), "receipt_sha256": receipt["receipt_sha256"]}, sort_keys=True))
        if receipt["status"] != STATUS_CONVERGED:
            raise SystemExit(2)
    else:
        print(json.dumps(validate_active_completions(args.repo_root), sort_keys=True))


if __name__ == "__main__":
    main()
