from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = {
    "specialist_id",
    "run_id",
    "as_of_utc",
    "owner_inputs",
    "owner_receipts",
    "freshness_status",
    "state",
    "direction",
    "confidence_0_100",
    "persistence_status",
    "evidence_for",
    "evidence_against",
    "missing_required_inputs",
    "conflicts",
    "no_action_reason",
    "authority",
}


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: list[str]


def validate_specialist(payload: dict[str, Any], registry: dict[str, Any]) -> ValidationResult:
    errors: list[str] = []
    missing = sorted(REQUIRED_FIELDS - set(payload))
    if missing:
        errors.append(f"missing_fields:{','.join(missing)}")
        return ValidationResult(False, errors)

    by_id = {item["specialist_id"]: item for item in registry["specialists"]}
    spec = by_id.get(payload["specialist_id"])
    if spec is None:
        errors.append("unknown_specialist")
        return ValidationResult(False, errors)

    if payload["state"] not in spec["allowed_states"]:
        errors.append("invalid_state")
    confidence = payload["confidence_0_100"]
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 100:
        errors.append("invalid_confidence")
    if payload["freshness_status"] not in {"PASS", "STALE", "UNKNOWN"}:
        errors.append("invalid_freshness")
    if payload["freshness_status"] != "PASS" and payload["confidence_0_100"] > 50:
        errors.append("stale_confidence_above_50")
    authority = payload["authority"]
    for forbidden in ("creates_truth", "framework_state_change", "model_weight_change", "portfolio_action"):
        if authority.get(forbidden) is not False:
            errors.append(f"forbidden_authority:{forbidden}")
    if not payload["owner_inputs"] or not payload["owner_receipts"]:
        errors.append("owner_lineage_missing")
    return ValidationResult(not errors, errors)


def synthesize(payloads: list[dict[str, Any]], registry: dict[str, Any]) -> dict[str, Any]:
    valid: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    spec_by_id = {item["specialist_id"]: item for item in registry["specialists"]}

    for payload in payloads:
        result = validate_specialist(payload, registry)
        if result.valid:
            valid.append(payload)
        else:
            rejected.append({"specialist_id": payload.get("specialist_id"), "errors": result.errors})

    families = sorted({spec_by_id[p["specialist_id"]]["causal_family"] for p in valid})
    minimum = registry["director"]["minimum_distinct_causal_families"]
    if len(families) >= minimum:
        status = "READY"
    elif valid:
        status = "DEGRADED"
    else:
        status = "BLOCKED"

    directions = sorted({p["direction"] for p in valid if p["direction"] != "UNKNOWN"})
    disagreement = len(directions) > 1
    confidence = round(sum(float(p["confidence_0_100"]) for p in valid) / len(valid), 2) if valid else None

    return {
        "contract": "SPECIALIST_DIRECTOR_SYNTHESIS_v1",
        "status": status,
        "valid_specialists": [p["specialist_id"] for p in valid],
        "rejected_specialists": rejected,
        "distinct_causal_families": families,
        "coverage": {"observed": len(families), "required": minimum},
        "directions_present": directions,
        "disagreement_preserved": disagreement,
        "mean_confidence_descriptive_only": confidence,
        "market_truth_created": False,
        "framework_state_change": False,
        "model_weight_change": False,
        "portfolio_action": False,
        "outcome_access": False,
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--inputs", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    registry = json.loads(args.registry.read_text())
    payloads = json.loads(args.inputs.read_text())
    result = synthesize(payloads, registry)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
