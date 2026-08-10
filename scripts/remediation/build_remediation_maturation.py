#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc
STATES = {
    "OBSERVED", "SUSPECTED_TRANSIENT", "PERSISTING", "CONFIRMED",
    "NEEDS_MORE_EVIDENCE", "CODEX_READY", "IN_REMEDIATION",
    "POST_FIX_OBSERVATION", "RESOLVED", "REOPENED", "CLEARED_NO_CHANGE",
}
IMMEDIATE = {"HASH_MISMATCH", "FALSE_PASS", "SECURITY", "DATA_LOSS", "CANONICAL_CORRUPTION"}
TRANSIENT = {"RATE_LIMIT", "TIMEOUT", "SCHEDULE_DELAY", "SOURCE_UNAVAILABLE", "PUSH_CONFLICT"}
CLASS_C_MARKERS = {"MODEL_WEIGHT", "CANONICAL_PREDECESSOR", "PORTFOLIO", "AUTHORITY_BOUNDARY", "API_BUDGET"}
NON_ACTIONABLE_FINDINGS = {"EXPECTED_BLOCK", "PENDING_FIRST_EXPECTED_RUN", "RETIRED_WORKFLOW_LOCAL_FILE_PRESENT"}


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def signature(workflow: str, finding: str) -> str:
    raw = f"{workflow}|{finding}".encode()
    return hashlib.sha256(raw).hexdigest()[:20]


def risk_class(finding: str) -> str:
    upper = finding.upper()
    if any(marker in upper for marker in CLASS_C_MARKERS):
        return "C_FRAMEWORK_OWNER"
    if any(marker in upper for marker in IMMEDIATE):
        return "B_CODEX_PR_IMMEDIATE"
    if upper in {"LATEST_RUN_FAILED", "REPEATED_CONSECUTIVE_FAILURES", "SCHEDULE_STALE", "NO_RUN_HISTORY"}:
        return "B_CODEX_PR"
    return "A_SELF_HEAL_OR_OBSERVE"


def evidence_threshold(workflow: dict[str, Any], finding: str) -> int:
    if any(marker in finding.upper() for marker in IMMEDIATE):
        return 1
    if finding == "REPEATED_CONSECUTIVE_FAILURES":
        return 2
    if workflow.get("scheduled") and int(workflow.get("cron_count") or 0) >= 4:
        return 3
    if workflow.get("scheduled"):
        return 2
    return 2


def post_fix_gate(workflow: dict[str, Any]) -> str:
    return "3_SUCCESSFUL_EXPECTED_RUNS" if workflow.get("scheduled") else "CI_PLUS_ONE_PRODUCTION_SHAPE_RUN"


def task_contract(name: str, finding: str, sig: str, workflow: dict[str, Any]) -> dict[str, Any]:
    allowed = [f".github/workflows/{name}", "directly related scripts and tests"]
    forbidden = ["market gates", "model weights", "canonical authority", "portfolio logic"]
    gate = post_fix_gate(workflow)
    required = ["workflow job logs", "reproduction or repeated identical signature", "positive and negative acceptance tests"]
    return {
        "objective": f"Resolve {finding} for {name} with the smallest bounded code change that satisfies the existing acceptance gates.",
        "precondition": f"Fresh Automation Production Health still contains signature {sig} for {name}/{finding}, and verified lifecycle state does not make the finding non-actionable.",
        "success_evidence": required + [gate],
        "clean_noop_condition": "The finding is absent from fresh health, is non-actionable under verified lifecycle semantics, or the target workflow has been superseded or retired.",
        "stop_condition": "Stop without code changes if the precondition fails, the finding cannot be reproduced from scoped evidence, or the required fix exceeds allowed change scope.",
        "escalation_condition": "Escalate to the framework owner if resolution requires market gates, model weights, canonical authority, portfolio logic, API budget, or new policy semantics.",
        "allowed_change_scope": allowed,
        "forbidden_changes": forbidden,
        "required_evidence": required,
        "post_fix_gate": gate,
        "transition_receipt_required": True,
        "transition_receipt_path": f"research/remediation/transitions/{sig}.json",
        "fresh_state_preflight_command": f"python scripts/remediation/write_transition_receipt.py --signature {sig} --branch <TASK_BRANCH>",
    }


def _valid_transition_receipt(data: dict[str, Any], path: Path) -> tuple[bool, str | None]:
    sig = str(data.get("signature") or "")
    if data.get("contract") != "REMEDIATION_TRANSITION_RECEIPT_v1":
        return False, "CONTRACT"
    if data.get("state") != "IN_REMEDIATION":
        return False, "STATE"
    if not sig or path.stem != sig:
        return False, "SIGNATURE_PATH"
    branch = str(data.get("branch") or "")
    if not branch or branch in {"main", "master"} or branch.startswith("backup/"):
        return False, "BRANCH"
    workflow = str(data.get("workflow") or "")
    finding = str(data.get("finding") or "")
    if not workflow or not finding or signature(workflow, finding) != sig:
        return False, "SIGNATURE_CONTENT"
    declared_hash = str(data.get("receipt_sha256") or "")
    actual_hash = canonical_hash({k: v for k, v in data.items() if k != "receipt_sha256"})
    if not declared_hash or declared_hash != actual_hash:
        return False, "HASH"
    if not data.get("task_contract_sha256"):
        return False, "TASK_CONTRACT_HASH"
    return True, None


def load_transition_receipts(repo: Path) -> tuple[dict[str, dict[str, Any]], list[dict[str, str]]]:
    root = repo / "research/remediation/transitions"
    receipts: dict[str, dict[str, Any]] = {}
    errors: list[dict[str, str]] = []
    if not root.exists():
        return receipts, errors
    for path in sorted(root.glob("*.json")):
        data = read_json(path, {})
        if not isinstance(data, dict):
            errors.append({"path": str(path.relative_to(repo)), "reason": "NOT_OBJECT"})
            continue
        valid, reason = _valid_transition_receipt(data, path)
        if valid:
            receipts[str(data["signature"])] = data
        else:
            errors.append({"path": str(path.relative_to(repo)), "reason": str(reason)})
    return receipts, errors


def build(repo: Path) -> dict[str, Any]:
    health = read_json(repo / "research/architecture_health/LATEST_AUTOMATION_HEALTH.json", {})
    prior = read_json(repo / "research/remediation/LATEST_REMEDIATION_QUEUE.json", {})
    prior_by_sig = {x.get("signature"): x for x in prior.get("items", []) if isinstance(x, dict)}
    transition_by_sig, transition_errors = load_transition_receipts(repo)
    current_signatures: set[str] = set()
    items: list[dict[str, Any]] = []

    for workflow in health.get("workflows", []):
        if not isinstance(workflow, dict):
            continue
        name = str(workflow.get("workflow") or "UNKNOWN")
        live = workflow.get("live") if isinstance(workflow.get("live"), dict) else {}
        failure_streak = int(live.get("failure_streak") or 0)
        success_streak = int(live.get("success_streak") or 0)
        latest = live.get("latest_run") if isinstance(live.get("latest_run"), dict) else {}
        for finding in workflow.get("findings", []):
            finding = str(finding)
            if finding in NON_ACTIONABLE_FINDINGS:
                continue
            sig = signature(name, finding)
            current_signatures.add(sig)
            old = prior_by_sig.get(sig, {})
            transition = transition_by_sig.get(sig)
            old_transition = old.get("transition_receipt") if isinstance(old.get("transition_receipt"), dict) else {}
            transition_is_new = bool(transition) and transition.get("receipt_sha256") != old_transition.get("receipt_sha256")
            observations = int(old.get("observations") or 0) + 1
            threshold = evidence_threshold(workflow, finding)
            rclass = risk_class(finding)
            upper = finding.upper()
            contract = task_contract(name, finding, sig, workflow)

            if old.get("state") in {"POST_FIX_OBSERVATION", "RESOLVED"}:
                state = "REOPENED"
                route = "CODEX_PR" if rclass.startswith("B_") else "OBSERVE"
            elif old.get("state") == "REOPENED" and not transition_is_new:
                state = "REOPENED"
                route = "CODEX_PR" if rclass.startswith("B_") else "OBSERVE"
            elif transition is not None and (transition_is_new or old.get("state") == "IN_REMEDIATION"):
                state = "IN_REMEDIATION"
                route = "CODEX_PR_IN_PROGRESS"
            elif any(marker in upper for marker in CLASS_C_MARKERS):
                state = "NEEDS_MORE_EVIDENCE"
                route = "FRAMEWORK_OWNER_PROPOSAL_ONLY"
            elif any(marker in upper for marker in IMMEDIATE):
                state = "CODEX_READY"
                route = "CODEX_PR"
            elif upper in TRANSIENT and observations < threshold:
                state = "SUSPECTED_TRANSIENT"
                route = "OBSERVE"
            elif finding == "LATEST_RUN_FAILED" and failure_streak < threshold:
                state = "OBSERVED"
                route = "OBSERVE"
            elif observations >= threshold or failure_streak >= threshold:
                state = "CODEX_READY" if rclass.startswith("B_") else "PERSISTING"
                route = "CODEX_PR" if rclass.startswith("B_") else "SELF_HEAL_ALLOWLIST_OR_OBSERVE"
            else:
                state = "PERSISTING" if observations > 1 else "OBSERVED"
                route = "OBSERVE"

            row = {
                "signature": sig,
                "workflow": name,
                "finding": finding,
                "state": state,
                "risk_class": rclass,
                "route": route,
                "observations": observations,
                "required_observations": threshold,
                "first_observed_at_utc": old.get("first_observed_at_utc") or now_iso(),
                "last_observed_at_utc": now_iso(),
                "failure_streak": failure_streak,
                "success_streak": success_streak,
                "latest_run_id": latest.get("id"),
                "latest_run_url": latest.get("html_url"),
                "lifecycle_state": workflow.get("lifecycle_state", "ACTIVE"),
                "source_health_generated_at_utc": health.get("generated_at_utc"),
                **contract,
            }
            if transition is not None:
                row["transition_receipt"] = transition
            row["task_contract_sha256"] = canonical_hash({k: row[k] for k in (
                "signature", "workflow", "finding", "objective", "precondition", "success_evidence",
                "clean_noop_condition", "stop_condition", "escalation_condition", "allowed_change_scope",
                "forbidden_changes", "required_evidence", "post_fix_gate"
            )})
            items.append(row)

    for sig, old in prior_by_sig.items():
        if sig in current_signatures:
            continue
        state = old.get("state")
        transition = transition_by_sig.get(sig)
        old_transition = old.get("transition_receipt") if isinstance(old.get("transition_receipt"), dict) else {}
        transition_is_new = bool(transition) and transition.get("receipt_sha256") != old_transition.get("receipt_sha256")
        if state in {"IN_REMEDIATION", "POST_FIX_OBSERVATION"} or transition_is_new:
            successes = int(old.get("post_fix_successes") or 0) + 1
            resolved = successes >= 3
            row = dict(old)
            row.update({
                "state": "RESOLVED" if resolved else "POST_FIX_OBSERVATION",
                "route": "OBSERVE_POST_FIX" if not resolved else "NONE",
                "post_fix_successes": successes,
                "last_evaluated_at_utc": now_iso(),
                "terminal_reason": "POST_FIX_GATE_SATISFIED" if resolved else None,
            })
            if transition is not None:
                row["transition_receipt"] = transition
            items.append(row)
        elif state in {"CODEX_READY", "REOPENED"}:
            row = dict(old)
            row.update({
                "state": "CLEARED_NO_CHANGE",
                "route": "NONE",
                "last_evaluated_at_utc": now_iso(),
                "terminal_reason": "FINDING_ABSENT_BEFORE_REMEDIATION_BINDING",
            })
            items.append(row)

    codex = [x for x in items if x.get("state") == "CODEX_READY"]
    needs = [x for x in items if x.get("state") in {"OBSERVED", "SUSPECTED_TRANSIENT", "PERSISTING", "NEEDS_MORE_EVIDENCE"}]
    active_remediation = [x for x in items if x.get("state") in {"IN_REMEDIATION", "POST_FIX_OBSERVATION", "REOPENED"}]
    return {
        "contract": "REMEDIATION_MATURATION_ENGINE_v1",
        "contract_revision": "1.1",
        "authority": "OPERATIONAL_REMEDIATION_ROUTING_ONLY",
        "generated_at_utc": now_iso(),
        "source_health_generated_at_utc": health.get("generated_at_utc"),
        "items": sorted(items, key=lambda x: (x.get("state", ""), x.get("workflow", ""), x.get("finding", ""))),
        "summary": {
            "total": len(items),
            "codex_ready": len(codex),
            "needs_more_evidence": len(needs),
            "active_remediation": len(active_remediation),
        },
        "codex_ready_tasks": codex,
        "needs_more_evidence": needs,
        "active_remediation": active_remediation,
        "transition_receipt_errors": transition_errors,
        "self_heal_allowlist": ["rerun_failed_job", "regenerate_dashboard", "rebuild_pointer_from_hash_verified_output", "publish_failure_receipt"],
        "automatic_code_write": False,
        "automatic_merge": False,
        "framework_state_change": False,
        "portfolio_action": False,
    }


def write_outputs(data: dict[str, Any], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "LATEST_REMEDIATION_QUEUE.json").write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "LATEST_CODEX_READY_TASKS.json").write_text(json.dumps({"contract":"CODEX_READY_TASKS_v1","contract_revision":"1.1","generated_at_utc":data["generated_at_utc"],"tasks":data["codex_ready_tasks"]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "LATEST_NEEDS_MORE_EVIDENCE.json").write_text(json.dumps({"contract":"NEEDS_MORE_EVIDENCE_v1","generated_at_utc":data["generated_at_utc"],"items":data["needs_more_evidence"]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (out / "REMEDIATION_HISTORY.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"generated_at_utc":data["generated_at_utc"],"summary":data["summary"]}, sort_keys=True) + "\n")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()
    write_outputs(build(args.repo_root), args.output_dir)


if __name__ == "__main__":
    main()
