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
import os
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


def _health_input_issues(health: dict[str, Any], workflows: list[dict[str, Any]],
                         previous: dict[str, Any]) -> tuple[list[str], float]:
    """Fail closed on self-contradictory or blind health receipts.

    Status normalization is retained for backward compatibility; unrecognized
    values never count as healthy. No finding here authorizes an automatic fix.
    """
    issues: list[str] = []
    counts: Counter[str] = Counter()
    with_live = 0
    for item in workflows:
        if not isinstance(item, dict):
            raise ValueError("malformed_health_workflow")
        raw = item.get("status")
        status = raw.strip().upper() if isinstance(raw, str) else ""
        status = "AMBER" if status == "YELLOW" else status
        if status not in {"GREEN", "AMBER", "RED"}:
            issues.append("UNRECOGNIZED_WORKFLOW_STATUS")
        else:
            counts[status] += 1
        if isinstance(item.get("live"), dict) and isinstance(item["live"].get("latest_run"), dict):
            with_live += 1
    top_raw = health.get("status")
    top = top_raw.strip().upper() if isinstance(top_raw, str) else ""
    top = "AMBER" if top == "YELLOW" else top
    if top not in {"GREEN", "AMBER", "RED"}:
        issues.append("TOP_LEVEL_STATUS_UNRECOGNIZED")
    elif top == "RED" and not counts["RED"]:
        issues.append("TOP_LEVEL_RED_WITHOUT_RED_ROWS")
    elif top == "GREEN" and counts["RED"]:
        issues.append("TOP_LEVEL_GREEN_WITH_RED_ROWS")
    if health.get("api_error"):
        issues.append("HEALTH_API_ERROR_REPORTED")
    for field, expected in (("red_count", counts["RED"]), ("amber_count", counts["AMBER"]),
                            ("green_count", counts["GREEN"]), ("workflow_count", len(workflows))):
        reported = health.get(field)
        if reported is not None and (type(reported) is not int or reported != expected):
            issues.append("HEALTH_CENSUS_COUNT_MISMATCH")
            break
    coverage = with_live / len(workflows) if workflows else 0.0
    previous_coverage = previous.get("health_live_coverage")
    if (type(previous_coverage) in (int, float) and
            previous_coverage - coverage >= 0.5):
        issues.append("SUSPECTED_LIVE_COVERAGE_COLLAPSE")
    try:
        previous_source_time = _timestamp(previous["source_generated_at_utc"]["automation_health"])
        current_source_time = _timestamp(health.get("generated_at_utc"))
        if current_source_time < previous_source_time:
            issues.append("SOURCE_TIME_REGRESSION")
    except (KeyError, TypeError, ValueError, AttributeError):
        # Malformed previous metadata cannot lock the live advisory writer.
        # It must never be accepted as proof of recovery or freshness.
        issues.append("PRIOR_SOURCE_BINDING_UNREADABLE")
    return list(dict.fromkeys(issues)), coverage


def _safe_write(root: Path, output: Path, value: dict[str, Any]) -> None:
    root_real, target_real = root.resolve(), output.resolve()
    if root_real not in target_real.parents:
        raise ValueError("output_outside_repo_root")
    source_paths = (
        root / "research/architecture_health/LATEST_AUTOMATION_HEALTH.json",
        root / "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json",
    )
    if target_real in {p.resolve() for p in source_paths}:
        raise ValueError("output_collides_with_source")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)


def build_snapshot(root: Path, output: Path, *, now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("now_must_be_timezone_aware")
    now = now.astimezone(timezone.utc)
    # Never overwrite a source receipt, including when caller supplies --output.
    if root.resolve() not in output.resolve().parents or output.resolve() in {
        (root / "research/architecture_health/LATEST_AUTOMATION_HEALTH.json").resolve(),
        (root / "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json").resolve(),
    }:
        raise ValueError("output_path_not_safe")
    health, health_sha = _read(
        root / "research/architecture_health/LATEST_AUTOMATION_HEALTH.json",
        HEALTH_CONTRACT,
    )
    registry, registry_sha = _read(
        root / "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json",
        EXPERIMENT_CONTRACT,
    )
    workflows = health.get("workflows")
    if not isinstance(workflows, list):
        raise ValueError("missing_health_workflow_census")
    census_empty = len(workflows) == 0
    candidates = registry.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("missing_experiment_candidate_census")
    if type(registry.get("candidate_count")) is not int or registry["candidate_count"] != len(candidates):
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
    declared_counts = registry.get("state_counts")
    if (not isinstance(declared_counts, dict) or
            any(type(value) is not int or value < 0 for value in declared_counts.values())):
        raise ValueError("malformed_experiment_state_counts")
    if dict(state_counts) != {key: value for key, value in declared_counts.items() if value}:
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
                "matured_outcome_count": (candidate.get("matured_outcome_count", 0)
                    if type(candidate.get("matured_outcome_count", 0)) is int and candidate.get("matured_outcome_count", 0) >= 0
                    else None),
                "evidence_direction": ("NEGATIVE" if state == "MATURED_NOT_SUPPORTED" else
                    "POSITIVE_UNVERIFIED" if state == "MATURED_SUPPORTED" else
                    "INCONCLUSIVE" if state == "MATURED_INCONCLUSIVE" else "QUARANTINED"),
                "reason": "No independently verified, preregistered baseline and held-out improvement gate in this input",
                "automatic_promotion": False,
            })

    # Read previous derived snapshot for recurrence only, never scientific authority.
    prior: dict[str, Any] = {}
    prior_status = "ABSENT"
    if output.exists():
        try:
            prior, _ = _read(output, OUTPUT_CONTRACT)
            historical = prior.get("incident_history", prior.get("incidents", []))
            if (not isinstance(historical, list)
                    or any(not isinstance(x, dict)
                           or not isinstance(x.get("fingerprint"), str)
                           or not x.get("fingerprint") for x in historical)
                    or len({x["fingerprint"] for x in historical}) != len(historical)):
                raise ValueError("malformed_previous_incident_history")
            prior_status = "VALID"
        except (ValueError, TypeError, UnicodeDecodeError):
            prior, prior_status = {}, "INVALID_IGNORED"
    historical = prior.get("incident_history", prior.get("incidents", []))
    prior_incidents = {
        x["fingerprint"]: x for x in historical
        if isinstance(x, dict) and isinstance(x.get("fingerprint"), str)
    }
    history_by_key = dict(prior_incidents)
    health_status = _source_age_status(health.get("generated_at_utc"), now)
    registry_status = _source_age_status(registry.get("generated_at_utc"), now)
    current = health_status == "CURRENT" and registry_status == "CURRENT"
    health_issues, live_coverage = _health_input_issues(health, workflows, prior)
    prior_source_sha = prior.get("source_sha256")
    if not isinstance(prior_source_sha, dict):
        prior_source_sha = {}
    source_changed = health_sha != prior_source_sha.get("automation_health")
    trustworthy_new_receipt = current and not health_issues and source_changed
    source_timestamp = _timestamp(health.get("generated_at_utc")).isoformat().replace("+00:00", "Z")
    incidents = []
    status_issues: list[str] = health_issues.copy()
    workflows_seen: set[str] = set()
    for item in workflows:
        if not isinstance(item, dict):
            raise ValueError("malformed_health_workflow")
        workflow = item.get("workflow")
        if not isinstance(workflow, str) or not workflow or workflow in workflows_seen:
            raise ValueError("missing_or_duplicate_workflow")
        workflows_seen.add(workflow)
        raw_status = item.get("status")
        if not isinstance(raw_status, str):
            status_issues.append(f"{workflow}:MISSING_OR_INVALID_STATUS")
            continue
        status = raw_status.strip().upper()
        if status == "YELLOW":
            status = "AMBER"
        if status not in {"GREEN", "AMBER", "RED"}:
            status_issues.append(f"{workflow}:UNKNOWN_STATUS:{status[:48]}")
            continue
        if status == "GREEN":
            continue
        findings = item.get("findings") or []
        if not isinstance(findings, list) or not all(isinstance(x, str) for x in findings):
            raise ValueError("malformed_health_findings")
        fingerprint = _fingerprint(workflow, findings)
        old = prior_incidents.get(fingerprint, {})
        live = item.get("live") if isinstance(item.get("live"), dict) else {}
        latest = live.get("latest_run") if isinstance(live.get("latest_run"), dict) else {}
        run_id = latest.get("id")
        # Count a unique, fresh and consistent SOURCE observation only once.
        # A/B/A run ID flapping must never inflate recurrence, and no-run-id
        # receipts can be distinguished by their immutable source checksum.
        keys = old.get("observed_keys")
        if not isinstance(keys, list):
            legacy_run = old.get("observed_run_id")
            keys = [f"run:{legacy_run}"] if legacy_run is not None else []
        keys = [key for key in keys if isinstance(key, str)][-50:]
        key = f"run:{run_id}" if run_id is not None else f"receipt:{health_sha}"
        seen = key in keys
        increment = int(trustworthy_new_receipt and not seen)
        prior_count = old.get("observation_count", 0)
        if type(prior_count) is not int or prior_count < 0:
            prior_count = 0
        count = prior_count + increment
        if increment:
            keys = (keys + [key])[-50:]
        record = {
            "fingerprint": fingerprint,
            "workflow": workflow,
            "findings": sorted(set(findings)),
            "severity": status,
            "classification": "UNKNOWN",
            "observed_run_id": run_id,
            "first_seen_at_utc": old.get("first_seen_at_utc") or
                (source_timestamp if increment else None),
            "last_seen_at_utc": source_timestamp if increment else old.get("last_seen_at_utc"),
            "observation_count": count,
            "observed_keys": keys,
            "counted_in_this_snapshot": bool(increment),
            "automatic_retry_allowed": False,
            "automatic_code_write_allowed": False,
            "route": "EXISTING_REMEDIATION_OWNER",
            "owner_issue": 1156,
            "reason": "Health status alone cannot establish transient cause, reproduce a deterministic defect or authorize a repair",
        }
        incidents.append(record)
        if trustworthy_new_receipt:
            history_by_key[fingerprint] = record

    # Never silently erase corrupted recurrence evidence and then claim no
    # problems on the next green health run. This is a DERIVED advisory only:
    # persistent RED integrity-loss evidence, no repaired history invented.
    integrity_fp = _fingerprint("__SELF_IMPROVEMENT_HISTORY__", ["PRIOR_INCIDENT_HISTORY_INVALID"])
    old_integrity = prior_incidents.get(integrity_fp)
    history_integrity_lost = prior_status == "INVALID_IGNORED" or old_integrity is not None
    if history_integrity_lost:
        old_integrity = old_integrity if isinstance(old_integrity, dict) else {}
        count = old_integrity.get("observation_count", 1)
        if type(count) is not int or count < 1:
            count = 1
        stamp = now.isoformat().replace("+00:00", "Z")
        integrity_incident = {
            "fingerprint": integrity_fp,
            "workflow": "__SELF_IMPROVEMENT_HISTORY__",
            "findings": ["PRIOR_INCIDENT_HISTORY_INVALID"],
            "severity": "RED",
            "classification": "HISTORY_INTEGRITY_LOSS",
            "observed_run_id": None,
            "first_seen_at_utc": old_integrity.get("first_seen_at_utc") or stamp,
            "last_seen_at_utc": stamp,
            "observation_count": count,
            "automatic_retry_allowed": False,
            "automatic_code_write_allowed": False,
            "route": "EXISTING_REMEDIATION_OWNER",
            "owner_issue": 1156,
            "reason": "Prior derived incident history failed validation; retain loss marker until separate owner-verified restoration, never reconstruct deleted observations",
        }
        incidents.append(integrity_incident)
        history_by_key[integrity_fp] = integrity_incident

    has_red = any(x["severity"] == "RED" for x in incidents)
    has_amber = any(x["severity"] == "AMBER" for x in incidents)
    if census_empty or status_issues or not current:
        operational_verdict = "INSUFFICIENT_EVIDENCE"
    elif has_red:
        operational_verdict = "NEEDS_DIAGNOSIS"
    elif has_amber:
        operational_verdict = "ADVISORY_DEGRADED"
    else:
        operational_verdict = "NO_RED_HEALTH_INCIDENTS"
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
        "source_generated_at_utc": {"automation_health": source_timestamp},
        "health_live_coverage": round(live_coverage, 4),
        "health_consistency": "OK" if not status_issues else "DEGRADED",
        "source_observation_counted": trustworthy_new_receipt,
        "operational_verdict": operational_verdict,
        "workflow_census_count": len(workflows),
        "input_issues": (["EMPTY_WORKFLOW_CENSUS"] if census_empty else []) + status_issues +
                        (["PRIOR_INCIDENT_HISTORY_INTEGRITY_LOST"] if history_integrity_lost else []),
        "prior_status": prior_status,
        "incident_count": len(incidents),
        "incidents": sorted(incidents, key=lambda x: x["workflow"]),
        "incident_history": sorted(history_by_key.values(), key=lambda x: x["fingerprint"]),
        "scoreboard": {key: scoreboard[key] for key in VERDICTS},
        "candidate_count": len(candidates),
        "challengers": challengers,
        "existing_owners": {"self_healing": 1156, "adaptive_evolution": 1157},
        "promotion_policy": "NONE_BY_THIS_REPORT; prospective held-out evidence and independent governance required",
        "repair_policy": "NO_RETRIES_OR_AUTOMATIC_MERGE_BY_THIS_REPORT; existing remediation remains executor",
    }
    _safe_write(root, output, result)
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
