#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc
REQUIRED_FORBIDDEN = {
    "market gates",
    "model weights",
    "canonical authority",
    "portfolio logic",
    "API budget",
    "new policy semantics",
}
ACTIVE_REMEDIATION_STATES = {"IN_REMEDIATION", "POST_FIX_OBSERVATION", "REOPENED"}
CONTRACT_FIELDS = (
    "signature", "workflow", "finding", "objective", "precondition", "success_evidence",
    "clean_noop_condition", "stop_condition", "escalation_condition", "allowed_change_scope",
    "forbidden_changes", "required_evidence", "post_fix_gate",
)


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def research_signature(candidate_id: str) -> str:
    return hashlib.sha256(f"RESEARCH_CODEX|{candidate_id}".encode()).hexdigest()[:20]


def task_contract_hash(task: dict[str, Any]) -> str:
    return canonical_hash({k: task.get(k) for k in CONTRACT_FIELDS})


def candidate_files(repo: Path) -> list[Path]:
    root = repo / "research/codex/intake"
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*.json") if p.is_file())


def validate_candidate(path: Path, data: dict[str, Any]) -> tuple[str, list[str]]:
    hard: list[str] = []
    missing: list[str] = []
    if data.get("contract") != "CODEX_RESEARCH_CANDIDATE_v1":
        hard.append("CONTRACT")
    candidate_id = str(data.get("candidate_id") or "")
    if not candidate_id or path.stem != candidate_id:
        hard.append("CANDIDATE_ID_PATH")
    if data.get("status") != "SUBMITTED":
        hard.append("STATUS")
    if data.get("authority_boundary") != "CODE_REMEDIATION_ONLY":
        hard.append("AUTHORITY_BOUNDARY")
    if bool(data.get("requires_framework_owner_authority")):
        hard.append("FRAMEWORK_OWNER_AUTHORITY_REQUIRED")
    forbidden = {str(x) for x in data.get("forbidden_changes", [])}
    if not REQUIRED_FORBIDDEN.issubset(forbidden):
        hard.append("FORBIDDEN_BOUNDARY_INCOMPLETE")
    scopes = data.get("allowed_change_scope")
    if not isinstance(scopes, list) or not scopes or any(not isinstance(x, str) or not x.strip() for x in scopes):
        missing.append("ALLOWED_CHANGE_SCOPE")
    if not str(data.get("objective") or "").strip():
        missing.append("OBJECTIVE")
    evidence = data.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        missing.append("EVIDENCE")
    if not str(data.get("reproduction") or "").strip():
        missing.append("REPRODUCTION")
    tests = data.get("acceptance_tests")
    if not isinstance(tests, dict) or not tests.get("positive") or not tests.get("negative"):
        missing.append("POSITIVE_AND_NEGATIVE_ACCEPTANCE_TESTS")
    if hard:
        return "REJECTED", hard + missing
    if missing:
        return "NEEDS_MORE_EVIDENCE", missing
    return "VALID", []


def build_research_task(repo: Path, path: Path, data: dict[str, Any], candidate_sha: str) -> dict[str, Any]:
    cid = str(data["candidate_id"])
    sig = research_signature(cid)
    rel = path.relative_to(repo).as_posix()
    priority = str(data.get("requested_priority") or "NORMAL").upper()
    if priority not in {"NORMAL", "EXPEDITED"}:
        priority = "NORMAL"
    gate = str(data.get("post_fix_gate") or "CI_PLUS_ONE_PRODUCTION_SHAPE_RUN")
    allowed = list(data["allowed_change_scope"])
    forbidden = sorted(REQUIRED_FORBIDDEN | {str(x) for x in data.get("forbidden_changes", [])})
    evidence = [str(e.get("ref") or e.get("summary") or "") if isinstance(e, dict) else str(e) for e in data.get("evidence", [])]
    evidence = [x for x in evidence if x]
    workflow = f"research-intake/{cid}"
    finding = str(data.get("finding_key") or "RESEARCH_CODE_REMEDIATION_CANDIDATE")
    task: dict[str, Any] = {
        "signature": sig,
        "workflow": workflow,
        "finding": finding,
        "source_type": "RESEARCH_INTAKE",
        "candidate_id": cid,
        "candidate_path": rel,
        "candidate_sha256": candidate_sha,
        "requested_priority": priority,
        "submitted_at_utc": data.get("submitted_at_utc"),
        "objective": data["objective"],
        "precondition": (
            f"Candidate {cid} still exists on main at {rel} with SHA-256 {candidate_sha}, "
            "status SUBMITTED and authority_boundary CODE_REMEDIATION_ONLY; no superseding fix or duplicate task has made it stale."
        ),
        "success_evidence": ["candidate-linked reproduction", "positive and negative acceptance tests", gate],
        "clean_noop_condition": (
            "The candidate is superseded, already fixed, duplicates a current health task, "
            "or fresh evidence no longer reproduces the bounded code defect."
        ),
        "stop_condition": (
            "Stop without code changes if candidate hash/status/authority changed, reproduction fails, "
            "or the required fix exceeds allowed_change_scope."
        ),
        "escalation_condition": (
            "Escalate to FRAMEWORK_OWNER if resolution requires market gates, model weights, canonical authority, "
            "portfolio logic, API budget or new policy semantics."
        ),
        "allowed_change_scope": allowed,
        "forbidden_changes": forbidden,
        "required_evidence": evidence + ["reproduction", "positive and negative acceptance tests"],
        "post_fix_gate": gate,
        "transition_receipt_required": True,
        "transition_receipt_path": f"research/codex/transitions/{sig}.json",
        "fresh_state_preflight_command": (
            f"python scripts/remediation/write_codex_research_transition_receipt.py --signature {sig} --branch <TASK_BRANCH>"
        ),
        "risk_class": "B_CODEX_PR_RESEARCH",
        "route": "CODEX_PR",
        "state": "CODEX_READY",
        "lifecycle_state": "ACTIVE",
        "latest_run_id": None,
        "latest_run_url": None,
        "observations": 1,
        "failure_streak": 0,
        "success_streak": 0,
        "first_observed_at_utc": data.get("submitted_at_utc"),
        "last_observed_at_utc": now_iso(),
    }
    task["task_contract_sha256"] = task_contract_hash(task)
    return task


def valid_transition(repo: Path, task: dict[str, Any]) -> dict[str, Any] | None:
    path = repo / str(task["transition_receipt_path"])
    d = read_json(path, {})
    if not d or d.get("contract") != "CODEX_RESEARCH_TRANSITION_RECEIPT_v1":
        return None
    if d.get("signature") != task["signature"] or d.get("candidate_id") != task["candidate_id"]:
        return None
    if d.get("candidate_sha256") != task["candidate_sha256"]:
        return None
    if d.get("task_contract_sha256") != task["task_contract_sha256"]:
        return None
    declared = str(d.get("receipt_sha256") or "")
    actual = canonical_hash({k: v for k, v in d.items() if k != "receipt_sha256"})
    if not declared or declared != actual:
        return None
    branch = str(d.get("branch") or "")
    if not branch or branch in {"main", "master"} or branch.startswith("backup-") or branch.startswith("backup/"):
        return None
    return d


def valid_completion(repo: Path, task: dict[str, Any]) -> dict[str, Any] | None:
    path = repo / "research/codex/completions" / f"{task['candidate_id']}.json"
    d = read_json(path, {})
    if not d or d.get("contract") != "CODEX_RESEARCH_COMPLETION_RECEIPT_v1" or d.get("status") != "VERIFIED":
        return None
    if d.get("signature") != task["signature"] or d.get("candidate_id") != task["candidate_id"]:
        return None
    if d.get("candidate_sha256") != task["candidate_sha256"] or d.get("task_contract_sha256") != task["task_contract_sha256"]:
        return None
    if not d.get("merge_commit_sha") or not d.get("verification_evidence"):
        return None
    declared = str(d.get("receipt_sha256") or "")
    actual = canonical_hash({k: v for k, v in d.items() if k != "receipt_sha256"})
    return d if declared and declared == actual else None


def append_ledger(repo: Path, current: list[dict[str, Any]]) -> None:
    state_path = repo / "research/codex/LATEST_CODEX_EXECUTION_STATE.json"
    ledger_path = repo / "research/codex/CODEX_EXECUTION_LEDGER.jsonl"
    prior = read_json(state_path, {})
    prior_by_sig = {str(x.get("signature")): x for x in prior.get("tasks", []) if isinstance(x, dict)}
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    at = now_iso()
    for task in current:
        sig = str(task.get("signature") or "")
        if not sig:
            continue
        previous = prior_by_sig.get(sig, {})
        state = str(task.get("state") or "")
        if previous.get("state") == state and previous.get("task_contract_sha256") == task.get("task_contract_sha256"):
            continue
        event = {
            "contract": "CODEX_EXECUTION_EVENT_v1",
            "recorded_at_utc": at,
            "signature": sig,
            "state": state,
            "source_type": task.get("source_type", "AUTOMATION_HEALTH"),
            "workflow": task.get("workflow"),
            "finding": task.get("finding"),
            "candidate_id": task.get("candidate_id"),
            "objective": task.get("objective"),
            "task_contract_sha256": task.get("task_contract_sha256"),
            "previous_state": previous.get("state"),
            "transition_receipt_path": task.get("transition_receipt_path"),
            "post_fix_gate": task.get("post_fix_gate"),
        }
        lines.append(json.dumps(event, sort_keys=True))
    if lines:
        with ledger_path.open("a", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
    state = {
        "contract": "CODEX_EXECUTION_STATE_v1",
        "generated_at_utc": at,
        "authority": "OBSERVABILITY_ONLY_LATEST_CODEX_READY_TASKS_REMAINS_QUEUE_AUTHORITY",
        "queue_authority": "LATEST_CODEX_READY_TASKS.json",
        "ledger_path": "research/codex/CODEX_EXECUTION_LEDGER.jsonl",
        "history_scope": "FORWARD_FROM_CODEX_INTAKE_V1_ACTIVATION_PLUS_CURRENT_STATE_BASELINE",
        "tasks": current,
        "summary": {
            "total": len(current),
            "codex_ready": sum(1 for x in current if x.get("state") == "CODEX_READY"),
            "in_remediation": sum(1 for x in current if x.get("state") == "IN_REMEDIATION"),
            "post_fix_observation": sum(1 for x in current if x.get("state") == "POST_FIX_OBSERVATION"),
            "resolved": sum(1 for x in current if x.get("state") == "RESOLVED"),
            "needs_more_evidence": sum(1 for x in current if x.get("state") in {"OBSERVED", "SUSPECTED_TRANSIENT", "PERSISTING", "NEEDS_MORE_EVIDENCE"}),
        },
    }
    write_json(state_path, state)
    write_json(repo / "LATEST_CODEX_EXECUTION_STATE.json", state)


def merge(repo: Path, output_dir: Path) -> dict[str, Any]:
    queue_path = output_dir / "LATEST_REMEDIATION_QUEUE.json"
    ready_path = output_dir / "LATEST_CODEX_READY_TASKS.json"
    needs_path = output_dir / "LATEST_NEEDS_MORE_EVIDENCE.json"
    queue = read_json(queue_path, {})
    ready_doc = read_json(ready_path, {"tasks": []})
    needs_doc = read_json(needs_path, {"items": []})

    base_items = [x for x in queue.get("items", []) if isinstance(x, dict)]
    base_ready = [x for x in ready_doc.get("tasks", []) if isinstance(x, dict)]
    base_needs = [x for x in needs_doc.get("items", []) if isinstance(x, dict)]
    by_sig = {str(x.get("signature")): x for x in base_items if x.get("signature")}
    ready_by_sig = {str(x.get("signature")): x for x in base_ready if x.get("signature")}
    needs_by_sig = {str(x.get("signature")): x for x in base_needs if x.get("signature")}
    intake_errors: list[dict[str, Any]] = []
    intake_states: list[dict[str, Any]] = []

    for path in candidate_files(repo):
        data = read_json(path, {})
        rel = path.relative_to(repo).as_posix()
        status, reasons = validate_candidate(path, data if isinstance(data, dict) else {})
        if status == "REJECTED":
            intake_errors.append({"candidate_path": rel, "status": status, "reasons": reasons})
            continue
        if not isinstance(data, dict):
            continue
        cid = str(data.get("candidate_id") or path.stem)
        linked = str(data.get("linked_health_signature") or "")
        candidate_sha = canonical_hash(data)

        if linked and linked in by_sig:
            item = {"candidate_id": cid, "candidate_path": rel, "candidate_sha256": candidate_sha}
            for target in (by_sig.get(linked), ready_by_sig.get(linked), needs_by_sig.get(linked)):
                if not isinstance(target, dict):
                    continue
                sources = list(target.get("research_intake_sources") or [])
                if item not in sources:
                    sources.append(item)
                target["research_intake_sources"] = sources
            intake_states.append({
                "candidate_id": cid,
                "candidate_path": rel,
                "state": "DEDUPED_TO_HEALTH_TASK",
                "linked_health_signature": linked,
                "candidate_sha256": candidate_sha,
            })
            continue

        task = build_research_task(repo, path, data, candidate_sha)
        sig = task["signature"]
        ready_by_sig.pop(sig, None)
        needs_by_sig.pop(sig, None)

        if status == "NEEDS_MORE_EVIDENCE":
            task["state"] = "NEEDS_MORE_EVIDENCE"
            task["route"] = "EVIDENCE"
            task["missing_evidence"] = reasons
            needs_by_sig[sig] = task
        else:
            completion = valid_completion(repo, task)
            transition = valid_transition(repo, task)
            if completion:
                task["state"] = "RESOLVED"
                task["route"] = "NONE"
                task["completion_receipt_path"] = f"research/codex/completions/{cid}.json"
                task["completion_receipt_sha256"] = completion.get("receipt_sha256")
                task["merge_commit_sha"] = completion.get("merge_commit_sha")
                task["pr_number"] = completion.get("pr_number")
                task["verified_at_utc"] = completion.get("verified_at_utc")
            elif transition:
                task["state"] = "IN_REMEDIATION"
                task["route"] = "CODEX_PR"
                task["transition_receipt_sha256"] = transition.get("receipt_sha256")
                task["remediation_branch"] = transition.get("branch")
                task["pr_number"] = transition.get("pr_number")
                task["remediation_started_at_utc"] = transition.get("recorded_at_utc")
            else:
                ready_by_sig[sig] = task

        by_sig[sig] = task
        intake_states.append({
            "candidate_id": cid,
            "candidate_path": rel,
            "candidate_sha256": candidate_sha,
            "signature": sig,
            "state": task["state"],
            "linked_health_signature": linked or None,
        })

    all_items = list(by_sig.values())
    all_ready = [x for x in ready_by_sig.values() if x.get("state") == "CODEX_READY"]
    all_needs = [x for x in needs_by_sig.values() if x.get("state") in {"OBSERVED", "SUSPECTED_TRANSIENT", "PERSISTING", "NEEDS_MORE_EVIDENCE"}]
    all_active = [x for x in all_items if x.get("state") in ACTIVE_REMEDIATION_STATES]

    sort_key = lambda x: (0 if x.get("requested_priority") == "EXPEDITED" else 1, str(x.get("signature")))
    all_items.sort(key=lambda x: (str(x.get("state", "")), str(x.get("workflow", "")), str(x.get("finding", ""))))
    all_ready.sort(key=sort_key)
    all_needs.sort(key=lambda x: str(x.get("signature")))
    all_active.sort(key=lambda x: str(x.get("signature")))

    queue["items"] = all_items
    queue["codex_ready_tasks"] = all_ready
    queue["needs_more_evidence"] = all_needs
    queue["active_remediation"] = all_active
    queue["research_intake"] = intake_states
    queue["research_intake_errors"] = intake_errors
    queue["research_intake_count"] = len(intake_states)
    queue["research_intake_error_count"] = len(intake_errors)
    summary = dict(queue.get("summary") or {})
    summary.update({
        "total": len(all_items),
        "codex_ready": len(all_ready),
        "needs_more_evidence": len(all_needs),
        "active_remediation": len(all_active),
        "research_intake": len(intake_states),
        "research_intake_errors": len(intake_errors),
    })
    queue["summary"] = summary

    generated_at = now_iso()
    ready_doc["contract_revision"] = "1.2"
    ready_doc["generated_at_utc"] = generated_at
    ready_doc["tasks"] = all_ready
    ready_doc["research_intake_enabled"] = True
    ready_doc["queue_sources"] = ["AUTOMATION_HEALTH", "RESEARCH_INTAKE"]
    needs_doc["generated_at_utc"] = generated_at
    needs_doc["items"] = all_needs

    write_json(queue_path, queue)
    write_json(ready_path, ready_doc)
    write_json(needs_path, needs_doc)
    write_json(repo / "research/codex/LATEST_CODEX_INTAKE_STATUS.json", {
        "contract": "CODEX_INTAKE_STATUS_v1",
        "generated_at_utc": generated_at,
        "candidate_count": len(intake_states),
        "error_count": len(intake_errors),
        "candidates": intake_states,
        "errors": intake_errors,
    })
    append_ledger(repo, all_items)
    return {
        "codex_ready": len(all_ready),
        "research_intake": len(intake_states),
        "errors": len(intake_errors),
        "preserved_health_items": len(base_items),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, default=Path("."))
    p.add_argument("--output-dir", type=Path, default=Path("research/remediation"))
    args = p.parse_args()
    result = merge(args.repo_root, args.output_dir)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
