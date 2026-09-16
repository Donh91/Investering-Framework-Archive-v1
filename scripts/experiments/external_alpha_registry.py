from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any

CONTRACT = "EXTERNAL_ALPHA_REGISTRY_V1"
SCORING_VERSION = "EXTERNAL_ALPHA_ADMISSION_V1"

SCORE_TABLES: dict[str, dict[str, int]] = {
    "identity_status": {
        "VERIFIED": 10,
        "PARTIAL": 5,
        "UNRESOLVED": 0,
        "AMBIGUOUS": 0,
    },
    "track_record_status": {
        "VERIFIED_PRIMARY": 15,
        "RECONSTRUCTABLE_PRIMARY": 12,
        "OPEN_SOURCE_REPLAY": 9,
        "PARTIAL": 5,
        "MARKETING_ONLY": 0,
    },
    "loser_coverage": {
        "FULL": 10,
        "PARTIAL": 5,
        "UNKNOWN": 0,
        "SELECTIVE": 0,
    },
    "timestamp_quality": {
        "IMMUTABLE": 10,
        "POINT_IN_TIME": 8,
        "RECONSTRUCTABLE": 6,
        "PARTIAL": 3,
        "UNKNOWN": 0,
    },
    "ledger_coverage": {
        "NEAR_COMPLETE": 10,
        "SUBSTANTIAL": 7,
        "PARTIAL": 4,
        "UNKNOWN": 0,
    },
    "opportunity_set_status": {
        "PROVEN": 15,
        "RECONSTRUCTABLE": 10,
        "PARTIAL": 5,
        "NONE": 0,
        "UNKNOWN": 0,
    },
    "execution_data_status": {
        "PRIMARY": 10,
        "RECONSTRUCTABLE": 7,
        "PARTIAL": 3,
        "NONE": 0,
        "UNKNOWN": 0,
    },
    "version_boundaries": {
        "KNOWN": 5,
        "PARTIAL": 3,
        "UNKNOWN": 0,
    },
    "transfer_value": {
        "HIGH": 10,
        "MEDIUM": 6,
        "LOW": 2,
        "NONE": 0,
    },
}

EVIDENCE_FIELDS = tuple(SCORE_TABLES)
BOOLEAN_EVIDENCE_FIELDS = (
    "falsifier_defined",
    "marketing_only",
    "selective_winners_only",
)

STAGES = (
    "DISCOVER",
    "VERIFY_IDENTITY",
    "VERIFY_TRACK_RECORD",
    "RECONSTRUCT_ACTIONS",
    "RECONSTRUCT_OPPORTUNITY_SET",
    "SOURCE_ALPHA",
    "OBSERVABLE_ALPHA",
    "COPYABLE_ALPHA",
    "SCALABLE_ALPHA",
    "TRANSFER_COMPONENT",
    "KILLED",
)

ADMISSION_DECISIONS = ("REJECT", "WATCH", "RESEARCH_QUEUE", "REVERSE_ENGINEER")
PROMOTION_STATES = (
    "RESEARCH_ONLY",
    "SOURCE_ALPHA_PENDING",
    "SOURCE_ALPHA_VERIFIED",
    "SOURCE_EDGE_NOT_COPYABLE",
    "COPYABLE_ALPHA_VERIFIED",
    "SCALABLE_ALPHA_VERIFIED",
    "TRANSFER_CANDIDATE",
    "TRANSFERRED_COMPONENT",
    "KILLED",
)

SOURCE_ALPHA_RULINGS = ("PENDING", "VERIFIED", "REJECTED", "INSUFFICIENT_EVIDENCE")
OBSERVABILITY_RULINGS = ("PENDING", "PARTIAL", "VERIFIED", "NOT_OBSERVABLE", "INSUFFICIENT_EVIDENCE")
COPYABILITY_RULINGS = ("PENDING", "PARTIAL", "VERIFIED", "NOT_COPYABLE", "INSUFFICIENT_EVIDENCE")
SCALABILITY_RULINGS = ("PENDING", "PARTIAL", "VERIFIED", "NOT_SCALABLE", "INSUFFICIENT_EVIDENCE")

CANDIDATE_ID_RE = re.compile(r"^EXT-ALPHA-[0-9]{4}$")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("registry must be a JSON object")
    return value


def decision_from_score(score: int) -> str:
    if score >= 75:
        return "REVERSE_ENGINEER"
    if score >= 50:
        return "RESEARCH_QUEUE"
    if score >= 30:
        return "WATCH"
    return "REJECT"


def score_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    evidence = candidate.get("evidence")
    if not isinstance(evidence, dict):
        raise ValueError("candidate.evidence must be an object")

    components: dict[str, int] = {}
    raw = 0
    for field, table in SCORE_TABLES.items():
        value = evidence.get(field)
        if value not in table:
            raise ValueError(f"invalid {field}: {value!r}")
        points = table[value]
        components[field] = points
        raw += points

    falsifier_points = 5 if evidence.get("falsifier_defined") is True else 0
    components["falsifier_defined"] = falsifier_points
    raw += falsifier_points

    caps: list[dict[str, Any]] = []
    cap = 100

    if evidence.get("marketing_only") is True:
        cap = min(cap, 24)
        caps.append({"reason": "MARKETING_ONLY", "cap": 24})

    if evidence.get("selective_winners_only") is True or evidence.get("loser_coverage") == "SELECTIVE":
        cap = min(cap, 29)
        caps.append({"reason": "SELECTIVE_WINNERS", "cap": 29})

    if evidence.get("identity_status") == "AMBIGUOUS":
        cap = min(cap, 29)
        caps.append({"reason": "AMBIGUOUS_IDENTITY", "cap": 29})

    if evidence.get("falsifier_defined") is not True:
        cap = min(cap, 49)
        caps.append({"reason": "NO_FALSIFIER", "cap": 49})

    score = min(raw, cap)
    return {
        "raw_score": raw,
        "score": score,
        "decision": decision_from_score(score),
        "components": components,
        "caps": caps,
    }


def validate_candidate(candidate: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    candidate_id = candidate.get("candidate_id")
    if not isinstance(candidate_id, str) or not CANDIDATE_ID_RE.match(candidate_id):
        errors.append("invalid candidate_id")

    if not isinstance(candidate.get("name"), str) or not candidate.get("name", "").strip():
        errors.append("missing name")

    if candidate.get("current_stage") not in STAGES:
        errors.append(f"invalid current_stage: {candidate.get('current_stage')!r}")

    if candidate.get("promotion_state") not in PROMOTION_STATES:
        errors.append(f"invalid promotion_state: {candidate.get('promotion_state')!r}")

    evidence = candidate.get("evidence")
    if not isinstance(evidence, dict):
        errors.append("evidence must be an object")
        return errors

    for field, table in SCORE_TABLES.items():
        if evidence.get(field) not in table:
            errors.append(f"invalid {field}: {evidence.get(field)!r}")
    for field in BOOLEAN_EVIDENCE_FIELDS:
        if not isinstance(evidence.get(field), bool):
            errors.append(f"{field} must be boolean")

    admission = candidate.get("admission")
    try:
        scored = score_candidate(candidate)
    except ValueError as exc:
        errors.append(str(exc))
        scored = None

    if not isinstance(admission, dict):
        errors.append("admission must be an object")
    elif scored is not None:
        if admission.get("expected_score") != scored["score"]:
            errors.append(
                f"expected_score {admission.get('expected_score')!r} != computed {scored['score']}"
            )
        if admission.get("expected_decision") != scored["decision"]:
            errors.append(
                f"expected_decision {admission.get('expected_decision')!r} != computed {scored['decision']}"
            )
        if admission.get("expected_decision") not in ADMISSION_DECISIONS:
            errors.append("invalid expected_decision")

    rulings = candidate.get("rulings")
    if not isinstance(rulings, dict):
        errors.append("rulings must be an object")
        return errors

    allowed_rulings = {
        "source_alpha": SOURCE_ALPHA_RULINGS,
        "observability": OBSERVABILITY_RULINGS,
        "copyability": COPYABILITY_RULINGS,
        "scalability": SCALABILITY_RULINGS,
    }
    for field, allowed in allowed_rulings.items():
        if rulings.get(field) not in allowed:
            errors.append(f"invalid ruling {field}: {rulings.get(field)!r}")

    if rulings.get("copyability") == "VERIFIED" and rulings.get("source_alpha") != "VERIFIED":
        errors.append("copyability VERIFIED requires source_alpha VERIFIED")
    if rulings.get("scalability") == "VERIFIED" and rulings.get("copyability") != "VERIFIED":
        errors.append("scalability VERIFIED requires copyability VERIFIED")

    promotion_state = candidate.get("promotion_state")
    if promotion_state in {"SOURCE_ALPHA_VERIFIED", "COPYABLE_ALPHA_VERIFIED", "SCALABLE_ALPHA_VERIFIED", "TRANSFER_CANDIDATE", "TRANSFERRED_COMPONENT"} and rulings.get("source_alpha") != "VERIFIED":
        errors.append(f"{promotion_state} requires source_alpha VERIFIED")
    if promotion_state in {"COPYABLE_ALPHA_VERIFIED", "SCALABLE_ALPHA_VERIFIED", "TRANSFER_CANDIDATE", "TRANSFERRED_COMPONENT"} and rulings.get("copyability") != "VERIFIED":
        errors.append(f"{promotion_state} requires copyability VERIFIED")
    if promotion_state in {"SCALABLE_ALPHA_VERIFIED", "TRANSFERRED_COMPONENT"} and rulings.get("scalability") != "VERIFIED":
        errors.append(f"{promotion_state} requires scalability VERIFIED")

    primitives = candidate.get("candidate_primitives")
    if not isinstance(primitives, list) or not primitives or not all(isinstance(v, str) and v for v in primitives):
        errors.append("candidate_primitives must be a non-empty string list")
    elif len(primitives) != len(set(primitives)):
        errors.append("candidate_primitives must be unique")

    refs = candidate.get("references")
    if not isinstance(refs, list) or not refs or not all(isinstance(v, str) and v for v in refs):
        errors.append("references must be a non-empty string list")

    if not isinstance(candidate.get("next_falsifiable_action"), str) or not candidate.get("next_falsifiable_action", "").strip():
        errors.append("missing next_falsifiable_action")

    return errors


def validate_registry(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if registry.get("contract") != CONTRACT:
        errors.append(f"contract must be {CONTRACT}")
    if registry.get("scoring_version") != SCORING_VERSION:
        errors.append(f"scoring_version must be {SCORING_VERSION}")

    candidates = registry.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        errors.append("candidates must be a non-empty list")
        return errors

    seen: set[str] = set()
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            errors.append(f"candidate[{index}] must be an object")
            continue
        candidate_id = candidate.get("candidate_id")
        if isinstance(candidate_id, str):
            if candidate_id in seen:
                errors.append(f"duplicate candidate_id: {candidate_id}")
            seen.add(candidate_id)
        for error in validate_candidate(candidate):
            errors.append(f"{candidate_id or index}: {error}")

    gate = registry.get("meta_learning_gate")
    if not isinstance(gate, dict):
        errors.append("meta_learning_gate must be an object")
    else:
        for field in (
            "min_candidates_at_source_alpha_stage",
            "min_settled_source_alpha_rulings",
            "min_settled_copyability_rulings",
        ):
            value = gate.get(field)
            if not isinstance(value, int) or value < 1:
                errors.append(f"meta_learning_gate.{field} must be a positive integer")

    return errors


def meta_learning_gate(registry: dict[str, Any]) -> dict[str, Any]:
    candidates = registry.get("candidates", [])
    thresholds = registry.get("meta_learning_gate", {})
    source_stage_names = {"SOURCE_ALPHA", "OBSERVABLE_ALPHA", "COPYABLE_ALPHA", "SCALABLE_ALPHA", "TRANSFER_COMPONENT", "KILLED"}
    settled_source = {"VERIFIED", "REJECTED"}
    settled_copy = {"VERIFIED", "NOT_COPYABLE"}

    at_source_stage = 0
    settled_source_count = 0
    settled_copy_count = 0

    for candidate in candidates if isinstance(candidates, list) else []:
        if not isinstance(candidate, dict):
            continue
        rulings = candidate.get("rulings") if isinstance(candidate.get("rulings"), dict) else {}
        if candidate.get("current_stage") in source_stage_names or rulings.get("source_alpha") in settled_source:
            at_source_stage += 1
        if rulings.get("source_alpha") in settled_source:
            settled_source_count += 1
        if rulings.get("copyability") in settled_copy:
            settled_copy_count += 1

    required_source_stage = int(thresholds.get("min_candidates_at_source_alpha_stage", 5))
    required_source_rulings = int(thresholds.get("min_settled_source_alpha_rulings", 3))
    required_copy_rulings = int(thresholds.get("min_settled_copyability_rulings", 2))

    unlocked = (
        at_source_stage >= required_source_stage
        and settled_source_count >= required_source_rulings
        and settled_copy_count >= required_copy_rulings
    )

    return {
        "status": "UNLOCKED" if unlocked else "LOCKED",
        "counts": {
            "candidates_at_source_alpha_stage": at_source_stage,
            "settled_source_alpha_rulings": settled_source_count,
            "settled_copyability_rulings": settled_copy_count,
        },
        "required": {
            "candidates_at_source_alpha_stage": required_source_stage,
            "settled_source_alpha_rulings": required_source_rulings,
            "settled_copyability_rulings": required_copy_rulings,
        },
    }


def scored_registry(registry: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(registry)
    for candidate in result.get("candidates", []):
        candidate["computed_admission"] = score_candidate(candidate)
    result["computed_meta_learning_gate"] = meta_learning_gate(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and score the external alpha registry")
    parser.add_argument("registry", type=Path)
    parser.add_argument("--mode", choices=("validate", "score", "meta-gate"), default="validate")
    args = parser.parse_args()

    registry = load_json(args.registry)
    errors = validate_registry(registry)

    if args.mode == "validate":
        payload = {
            "status": "PASS" if not errors else "FAIL",
            "errors": errors,
            "candidate_count": len(registry.get("candidates", [])),
            "meta_learning_gate": meta_learning_gate(registry),
        }
    elif args.mode == "score":
        payload = scored_registry(registry)
        payload["validation_errors"] = errors
    else:
        payload = meta_learning_gate(registry)
        payload["validation_errors"] = errors

    print(json.dumps(payload, sort_keys=True, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
