from __future__ import annotations

from typing import Iterable, Mapping

PROFILES = ("FULL_STACK", "REDUCED_EXECUTION_STACK", "MINIMAL_CORE_STACK")


def validate_shadow_run(rows: Iterable[Mapping]) -> list[str]:
    material = list(rows)
    errors: list[str] = []
    if len(material) != len(PROFILES):
        errors.append("exactly one row per profile required")
        return errors
    run_ids = {row.get("run_id") for row in material}
    snapshots = {row.get("snapshot_utc") for row in material}
    profiles = {row.get("profile_id") for row in material}
    if len(run_ids) != 1:
        errors.append("run_id mismatch")
    if len(snapshots) != 1:
        errors.append("snapshot mismatch")
    if profiles != set(PROFILES):
        errors.append("profile set mismatch")
    required = {
        "available_sensors",
        "available_clusters",
        "source_failures",
        "state_output",
        "transition_output",
        "veto_output",
        "payload_bytes",
        "runtime_seconds",
        "explanation_tokens",
        "warnings_emitted",
    }
    for row in material:
        missing = required - set(row)
        if missing:
            errors.append(f"{row.get('profile_id')}: missing {sorted(missing)}")
        for numeric in ("payload_bytes", "runtime_seconds", "explanation_tokens"):
            if numeric in row and float(row[numeric]) < 0:
                errors.append(f"{row.get('profile_id')}: {numeric} cannot be negative")
    return errors


def score_shadow_period(runs: Iterable[Iterable[Mapping]]) -> dict:
    material = [list(run) for run in runs]
    valid_runs = []
    invalid_runs = []
    for run in material:
        errors = validate_shadow_run(run)
        if errors:
            invalid_runs.append({"run_id": run[0].get("run_id") if run else None, "errors": errors})
        else:
            valid_runs.append({row["profile_id"]: row for row in run})

    result = {
        "status": "PASS" if not invalid_runs else "PARTIAL",
        "valid_runs": len(valid_runs),
        "invalid_runs": invalid_runs,
        "profiles": {},
    }
    if not valid_runs:
        return result

    for challenger in ("REDUCED_EXECUTION_STACK", "MINIMAL_CORE_STACK"):
        state_hits = 0
        transition_hits = 0
        veto_hits = 0
        missed_warnings = 0
        false_transitions = 0
        payload_reductions = []
        runtime_reductions = []
        explanation_reductions = []
        for run in valid_runs:
            full = run["FULL_STACK"]
            candidate = run[challenger]
            state_hits += candidate["state_output"] == full["state_output"]
            transition_hits += candidate["transition_output"] == full["transition_output"]
            veto_hits += candidate["veto_output"] == full["veto_output"]
            missed_warnings += len(set(full["warnings_emitted"]) - set(candidate["warnings_emitted"]))
            false_transitions += int(candidate["transition_output"] != "NONE" and full["transition_output"] == "NONE")
            if full["payload_bytes"]:
                payload_reductions.append(1 - candidate["payload_bytes"] / full["payload_bytes"])
            if full["runtime_seconds"]:
                runtime_reductions.append(1 - candidate["runtime_seconds"] / full["runtime_seconds"])
            if full["explanation_tokens"]:
                explanation_reductions.append(1 - candidate["explanation_tokens"] / full["explanation_tokens"])

        n = len(valid_runs)
        result["profiles"][challenger] = {
            "state_agreement_rate": state_hits / n,
            "transition_agreement_rate": transition_hits / n,
            "veto_agreement_rate": veto_hits / n,
            "missed_warning_count": missed_warnings,
            "false_transition_count": false_transitions,
            "mean_payload_reduction_pct": 100 * sum(payload_reductions) / len(payload_reductions) if payload_reductions else None,
            "mean_runtime_reduction_pct": 100 * sum(runtime_reductions) / len(runtime_reductions) if runtime_reductions else None,
            "mean_explanation_reduction_pct": 100 * sum(explanation_reductions) / len(explanation_reductions) if explanation_reductions else None,
        }
    return result
