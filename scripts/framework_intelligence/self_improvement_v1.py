#!/usr/bin/env python3
"""Derived, non-authoritative self-improvement readout for existing Supervisor.

Owners: GitHub issues #1156 (operational repair) and #1157 (scientific evolution).
This module NEVER invokes agents, pays for APIs, retries workflows, changes rules,
edits source inputs, approves PRs, or promotes a market/skill experiment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HEALTH_CONTRACT = "AUTOMATION_PRODUCTION_HEALTH_v2_1"
EXPERIMENT_CONTRACT = "EXPERIMENT_LIFECYCLE_REGISTRY_v1"
OUTPUT_CONTRACT = "SELF_IMPROVEMENT_ADVISORY_v1"
VERDICTS = (
    "DOCUMENTED_IMPROVEMENT", "UNPROVEN", "FALSIFIED", "KILLED",
    "REGRESSED", "INSUFFICIENT_EVIDENCE",
)
RESEARCH_STATES = {
    "MATURED_SUPPORTED", "MATURED_NOT_SUPPORTED", "MATURED_INCONCLUSIVE",
    "TARGET_UNIT_QUARANTINED", "WAITING_FOR_DATA", "WAITING_FOR_MAPPING",
    "INCUBATING", "PROPOSED",
}


def _read(path: Path, expected_contract: str) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    doc = json.loads(raw)
    if not isinstance(doc, dict) or doc.get("contract") != expected_contract:
        raise ValueError(f"wrong_contract:{path.name}")
    return doc, hashlib.sha256(raw).hexdigest()


def _timestamp(value: Any) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("missing_or_non_utc_timestamp")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("naive_timestamp")
    return result


def _fingerprint(workflow: str, findings: list[str]) -> str:
    basis = json.dumps(
        {"workflow": workflow, "findings": sorted(set(findings))},
        sort_keys=True, separators=(",", ":"),
    )
    return hashlib.sha256(basis.encode()).hexdigest()


def _source_age_status(generated: Any, now: datetime, max_age_hours: float = 36) -> str:
    age = (now - _timestamp(generated)).total_seconds() / 3600
    return "CURRENT" if -0.25 <= age <= max_age_hours else "STALE"


def build_snapshot(root: Path, output: Path, *, now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("now_must_be_timezone_aware")
    health, health_sha = _read(
        root / "research/architecture_health/LATEST_AUTOMATION_HEALTH.json",
        HEALTH_CONTRACT,
    )
    registry, registry_sha = _read(
        root / "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json",
        EXPERIMENT_CONTRACT,
    )
    if not isinstance(health.get("workflows"), list):
        raise ValueError("missing_health_workflow_census")
    candidates = registry.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("missing_experiment_candidate_census")
    if registry.get("candidate_count") != len(candidates):
        raise ValueError("candidate_count_mismatch")

    identifiers: set[str] = set()
    state_counts: Counter[str] = Counter()
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ValueError("malformed_experiment_candidate")
        identifier = candidate.get("candidate_id")
        state = candidate.get("state")
        if not isinstance(identifier, str) or not identifier or identifier in identifiers:
            raise ValueError("missing_or_duplicate_candidate_identity")
        if state not in RESEARCH_STATES:
            raise ValueError("unknown_experiment_state")
        identifiers.add(identifier)
        state_counts[state] += 1
    if dict(state_counts) != {
        key: value for key, value in (registry.get("state_counts") or {}).items() if value
    }:
        raise ValueError("experiment_state_counts_mismatch")

    # Proven scientific improvement requires frozen endpoint/baseline, independent
    # prospective or held-out evidence and safety verification. The experiment
    # registry alone contains no such admission. In particular SUPPORTED != PROVEN.
    scoreboard: Counter[str] = Counter({k: 0 for k in VERDICTS})
    challengers = []
    for candidate in sorted(candidates, key=lambda x: x["candidate_id"]):
        state = candidate["state"]
        if state in {"INCUBATING", "WAITING_FOR_DATA", "WAITING_FOR_MAPPING", "PROPOSED"}:
            verdict = "INSUFFICIENT_EVIDENCE"
        else:
            verdict = "UNPROVEN"
        scoreboard[verdict] += 1
        if state in {"MATURED_SUPPORTED", "MATURED_NOT_SUPPORTED", "MATURED_INCONCLUSIVE", "TARGET_UNIT_QUARANTINED"}:
            challengers.append({
                "candidate_id": candidate["candidate_id"],
                "source_state": state,
                "verdict": verdict,
                "matured_outcome_count": candidate.get("matured_outcome_count", 0),
                "reason": "No independently verified, preregistered baseline and held-out improvement gate in this input",
                "automatic_promotion": False,
            })

    # Read previous derived snapshot for recurrence only, never scientific authority.
    prior = {}
    if output.exists():
        prior, _ = _read(output, OUTPUT_CONTRACT)
    prior_incidents = {
        x.get("fingerprint"): x for x in prior.get("incidents", [])
        if isinstance(x, dict) and x.get("fingerprint")
    }
    incidents = []
    workflows_seen: set[str] = set()
    for item in health["workflows"]:
        if not isinstance(item, dict):
            raise ValueError("malformed_health_workflow")
        workflow = item.get("workflow")
        if not isinstance(workflow, str) or not workflow or workflow in workflows_seen:
            raise ValueError("missing_or_duplicate_workflow")
        workflows_seen.add(workflow)
        if item.get("status") != "RED":
            continue
        findings = item.get("findings") or []
        if not isinstance(findings, list) or not all(isinstance(x, str) for x in findings):
            raise ValueError("malformed_health_findings")
        fingerprint = _fingerprint(workflow, findings)
        old = prior_incidents.get(fingerprint, {})
        live = item.get("live") if isinstance(item.get("live"), dict) else {}
        latest = live.get("latest_run") if isinstance(live.get("latest_run"), dict) else {}
        run_id = latest.get("id")
        # Re-processing an identical health receipt is NOT another observation.
        increment = 1 if not old or (run_id is not None and run_id != old.get("observed_run_id")) else 0
        count = int(old.get("observation_count", 0)) + increment
        incidents.append({
            "fingerprint": fingerprint,
            "workflow": workflow,
            "findings": sorted(set(findings)),
            "classification": "UNKNOWN",
            "observed_run_id": run_id,
            "first_seen_at_utc": old.get("first_seen_at_utc") or now.isoformat().replace("+00:00", "Z"),
            "last_seen_at_utc": now.isoformat().replace("+00:00", "Z"),
            "observation_count": count,
            "automatic_retry_allowed": False,
            "automatic_code_write_allowed": False,
            "route": "EXISTING_REMEDIATION_OWNER",
            "owner_issue": 1156,
            "reason": "Health status alone cannot establish transient cause, reproduce a deterministic defect or authorize a repair",
        })

    health_status = _source_age_status(health.get("generated_at_utc"), now)
    registry_status = _source_age_status(registry.get("generated_at_utc"), now)
    current = health_status == "CURRENT" and registry_status == "CURRENT"
    result = {
        "contract": OUTPUT_CONTRACT,
        "authority": {
            "type": "ADVISORY_DERIVED_READ_ONLY",
            "canonical_effect": False, "portfolio_action": False,
            "automatic_promotion": False, "automatic_merge": False,
            "automatic_code_write": False, "automatic_api_payment": False,
        },
        "generated_at_utc": now.isoformat().replace("+00:00", "Z"),
        "source_paths": {
            "automation_health": "research/architecture_health/LATEST_AUTOMATION_HEALTH.json",
            "experiment_registry": "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json",
        },
        "source_sha256": {"automation_health": health_sha, "experiment_registry": registry_sha},
        "input_health": "CURRENT" if current else "STALE",
        "input_freshness": {"automation_health": health_status, "experiment_registry": registry_status},
        "operational_verdict": "INSUFFICIENT_EVIDENCE" if not current else ("NEEDS_DIAGNOSIS" if incidents else "NO_RED_HEALTH_INCIDENTS"),
        "incident_count": len(incidents),
        "incidents": sorted(incidents, key=lambda x: x["workflow"]),
        "scoreboard": {key: scoreboard[key] for key in VERDICTS},
        "candidate_count": len(candidates),
        "challengers": challengers,
        "existing_owners": {"self_healing": 1156, "adaptive_evolution": 1157},
        "promotion_policy": "NONE_BY_THIS_REPORT; prospective held-out evidence and independent governance required",
        "repair_policy": "NO_RETRIES_OR_AUTOMATIC_MERGE_BY_THIS_REPORT; existing remediation remains executor",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    temporary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    temporary.replace(output)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output", default="research/framework_learning/LATEST_SELF_IMPROVEMENT_V1.json")
    args = parser.parse_args()
    result = build_snapshot(Path(args.repo_root), Path(args.repo_root) / args.output)
    print(json.dumps({
        "contract": result["contract"], "operational_verdict": result["operational_verdict"],
        "incident_count": result["incident_count"],
        "documented_improvements": result["scoreboard"]["DOCUMENTED_IMPROVEMENT"],
        "unproven": result["scoreboard"]["UNPROVEN"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
