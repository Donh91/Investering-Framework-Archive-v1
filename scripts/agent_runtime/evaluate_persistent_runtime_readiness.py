#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def count_event_markers(root: Path) -> dict[str, int]:
    markers = {
        "cross_run_context_loss_or_manual_handover_events": (
            "CONTEXT_LOSS", "HANDOVER_RECONSTRUCTION", "MISSING_HANDOFF", "SESSION_STATE_LOSS"
        ),
        "interrupted_long_task_events": (
            "INTERRUPTED_LONG_TASK", "PREMATURE_EXIT", "COMPACTION_EXIT", "TASK_INTERRUPTED"
        ),
        "message_delivery_or_continuation_failures": (
            "MESSAGE_DELIVERY_FAILED", "CONTINUATION_FAILED", "DELIVERY_RECEIPT_MISSING"
        ),
        "scheduled_state_loss_events": (
            "SCHEDULED_STATE_LOSS", "STATE_NOT_RESUMED", "SCHEDULE_CLAIM_LOST"
        ),
    }
    counts = {key: 0 for key in markers}
    roots = [root / "09_SOURCE_QA/incidents", root / "research/remediation"]
    for base in roots:
        for path in base.rglob("*") if base.exists() else []:
            if not path.is_file() or path.suffix.lower() not in {".json", ".jsonl", ".md", ".txt"}:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore").upper()
            except OSError:
                continue
            for key, terms in markers.items():
                if any(term in text for term in terms):
                    counts[key] += 1
    return counts


def contract_presence(root: Path, contracts: list[str]) -> dict[str, bool]:
    result: dict[str, bool] = {}
    searchable = [root / "00_FMOS", root / "01_CORE_FRAMEWORK", root / "07_PROMPTS_AND_AGENTS", root / "research"]
    for contract in contracts:
        found = False
        for base in searchable:
            if found or not base.exists():
                continue
            for path in base.rglob("*"):
                if not path.is_file() or path.suffix.lower() not in {".json", ".jsonl", ".md", ".txt", ".yaml", ".yml"}:
                    continue
                try:
                    if contract in path.read_text(encoding="utf-8", errors="ignore"):
                        found = True
                        break
                except OSError:
                    continue
        result[contract] = found
    return result


def evaluate(root: Path, candidate_path: Path, upstream_path: Path | None = None) -> dict[str, Any]:
    candidate = read_json(candidate_path, {})
    if candidate.get("contract") != "PERSISTENT_AGENT_RUNTIME_CANDIDATE_v1":
        raise ValueError("invalid_candidate_contract")

    health = read_json(root / "research/architecture_health/LATEST_AUTOMATION_HEALTH.json", {})
    remediation = read_json(root / "research/remediation/LATEST_REMEDIATION_QUEUE.json", {})
    handoff = read_json(root / "LATEST_HANDOFF.json", {})
    upstream = read_json(upstream_path, {}) if upstream_path else {}

    need_counts = count_event_markers(root)
    need_thresholds = candidate["internal_need_thresholds"]
    need_checks = {key: need_counts.get(key, 0) >= int(value) for key, value in need_thresholds.items()}

    contracts = contract_presence(root, candidate["required_internal_contracts"])
    contract_ready = all(contracts.values())

    automation_red_count = int(health.get("red_count") or (1 if str(health.get("status")).upper() == "RED" else 0))
    remediation_items = remediation.get("items", []) if isinstance(remediation.get("items"), list) else []
    unresolved_p0 = sum(
        1 for item in remediation_items
        if isinstance(item, dict)
        and str(item.get("priority") or item.get("risk_class") or "").upper().startswith("P0")
        and item.get("state") not in {"RESOLVED", "CLOSED"}
    )
    handoff_text = json.dumps(handoff, sort_keys=True).upper()
    hash_mismatches = handoff_text.count("HASH_MISMATCH")
    pointers = handoff.get("pointers", {}) if isinstance(handoff.get("pointers"), dict) else {}
    missing_pointers = sum(1 for value in pointers.values() if not isinstance(value, dict) or not value.get("path"))

    stability = {
        "automation_red_count": automation_red_count,
        "unresolved_p0_remediation_count": unresolved_p0,
        "hash_mismatch_count": hash_mismatches,
        "missing_required_handoff_pointer_count": missing_pointers,
        "successful_observation_runs": int(upstream.get("successful_observation_runs") or 0),
    }
    req = candidate["stability_requirements"]
    stability_checks = {
        "automation_red_count": stability["automation_red_count"] <= int(req["automation_red_count"]),
        "unresolved_p0_remediation_count": stability["unresolved_p0_remediation_count"] <= int(req["unresolved_p0_remediation_count"]),
        "hash_mismatch_count": stability["hash_mismatch_count"] <= int(req["hash_mismatch_count"]),
        "missing_required_handoff_pointer_count": stability["missing_required_handoff_pointer_count"] <= int(req["missing_required_handoff_pointer_count"]),
        "minimum_successful_observation_runs": stability["successful_observation_runs"] >= int(req["minimum_successful_observation_runs"]),
    }

    upstream_requirements = candidate["upstream_requirements"]
    upstream_checks = {key: bool(upstream.get(key, False)) for key in upstream_requirements if key != "minimum_observation_days"}
    upstream_checks["minimum_observation_days"] = int(upstream.get("observation_days") or 0) >= int(upstream_requirements["minimum_observation_days"])

    need_ready = all(need_checks.values())
    stability_ready = all(stability_checks.values())
    upstream_ready = all(upstream_checks.values())

    if not need_ready or not stability_ready:
        stage = "INCUBATING"
    elif not contract_ready:
        stage = "READY_FOR_CONTRACT_BUILD"
    elif not upstream_ready:
        stage = "READY_FOR_SIMULATION"
    else:
        stage = "READY_FOR_ISOLATED_CANARY"

    blockers = []
    for group, checks in (("internal_need", need_checks), ("contracts", contracts), ("stability", stability_checks), ("upstream", upstream_checks)):
        blockers.extend(f"{group}:{key}" for key, passed in checks.items() if not passed)

    result = {
        "contract": "PERSISTENT_AGENT_RUNTIME_READINESS_v1",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "candidate_id": candidate["candidate_id"],
        "status": "READY" if stage == "READY_FOR_ISOLATED_CANARY" else "NOT_READY",
        "recommended_stage": stage,
        "maximum_automatic_stage": candidate["maximum_automatic_stage"],
        "internal_need": {"counts": need_counts, "thresholds": need_thresholds, "checks": need_checks},
        "internal_contracts": {"presence": contracts, "ready": contract_ready},
        "operational_stability": {"observed": stability, "checks": stability_checks},
        "upstream_maturity": {"observed": upstream, "checks": upstream_checks},
        "blockers": blockers,
        "authority": "ARCHITECTURE_READINESS_ONLY",
        "automatic_installation": False,
        "automatic_secret_access": False,
        "automatic_merge": False,
        "runtime_authority": False,
    }
    result["readiness_sha256"] = hashlib.sha256(canonical(result)).hexdigest()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--upstream-evidence", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = evaluate(args.repo_root, args.candidate, args.upstream_evidence)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical(result))
    print(json.dumps({"status": result["status"], "recommended_stage": result["recommended_stage"], "blockers": len(result["blockers"])}, sort_keys=True))


if __name__ == "__main__":
    main()
