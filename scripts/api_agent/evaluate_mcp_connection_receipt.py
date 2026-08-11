from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PROGRAM_PATH = Path("research/api_agent/mcp/MCP_CONNECTION_EVALUATION_PROGRAM_v1.json")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return max(0.0, min(1.0, numerator / denominator))


def _crosscheck_points(status: str) -> float:
    return {"PASS": 10.0, "PARTIAL": 5.0, "NOT_APPLICABLE": 5.0, "NOT_RUN": 0.0, "FAIL": 0.0}.get(status, 0.0)


def detect_hard_blockers(receipt: dict[str, Any]) -> list[str]:
    blockers = list(receipt.get("hard_blockers") or [])
    if receipt.get("official_server_verified") is not True:
        blockers.append("UNOFFICIAL_OR_UNVERIFIED_SERVER")
    if receipt.get("auth_secret_persisted") is True:
        blockers.append("SECRET_VALUE_PERSISTED_OR_ECHOED")
    if receipt.get("mutating_tool_called") is True:
        blockers.append("MUTATING_TOOL_CALLED")
    if receipt.get("production_dependency") is True:
        blockers.append("PRODUCTION_DEPENDENCY_REQUIRED")
    if receipt.get("canonical_owner_replaced") is True:
        blockers.append("CANONICAL_OWNER_REPLACEMENT_REQUIRED")
    if receipt.get("provider_cost_status") == "OVER_BUDGET":
        blockers.append("UNBOUNDED_PROVIDER_COST_OR_PAYMENT")
    if int(receipt.get("mcp_call_count", 0) or 0) > 0 and receipt.get("provenance_complete") is not True:
        blockers.append("PROVENANCE_NOT_PRESERVABLE")
    if receipt.get("tool_discovery_status") == "PASS" and int(receipt.get("discovered_tool_count", 0) or 0) > 0 and int(receipt.get("allowed_read_only_tool_count", 0) or 0) == 0:
        blockers.append("READ_ONLY_ALLOWLIST_NOT_ENFORCEABLE")
    return sorted(set(blockers))


def validate_receipt_shape(receipt: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if receipt.get("contract") != "MCP_CONNECTION_PILOT_RECEIPT_v1":
        errors.append("invalid_receipt_contract")
    total_calls = int(receipt.get("mcp_call_count", 0) or 0)
    succeeded = int(receipt.get("successful_mcp_call_count", 0) or 0)
    failed = int(receipt.get("failed_mcp_call_count", 0) or 0)
    if succeeded + failed != total_calls:
        errors.append("mcp_call_count_mismatch")
    q_total = int(receipt.get("research_questions_total", 0) or 0)
    q_answered = int(receipt.get("research_questions_answered", 0) or 0)
    if q_answered > q_total:
        errors.append("research_question_count_invalid")
    if int(receipt.get("allowed_read_only_tool_count", 0) or 0) > int(receipt.get("discovered_tool_count", 0) or 0):
        errors.append("allowed_tool_count_exceeds_discovered")
    authority = receipt.get("authority") if isinstance(receipt.get("authority"), dict) else {}
    for key in ("framework_state_change", "portfolio_action", "market_rule_change", "canonical_promotion"):
        if authority.get(key) is not False:
            errors.append(f"unsafe_receipt_authority:{key}")
    return errors


def score_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    shape_errors = validate_receipt_shape(receipt)
    blockers = detect_hard_blockers(receipt)
    total_calls = int(receipt.get("mcp_call_count", 0) or 0)
    successful_calls = int(receipt.get("successful_mcp_call_count", 0) or 0)
    q_total = int(receipt.get("research_questions_total", 0) or 0)
    q_answered = int(receipt.get("research_questions_answered", 0) or 0)
    unique = int(receipt.get("unique_value_items", 0) or 0)
    overlap = int(receipt.get("overlap_items", 0) or 0)
    manual = int(receipt.get("manual_intervention_count", 0) or 0)

    dimensions = {
        "connection_reliability": round(20.0 * _ratio(successful_calls, total_calls), 2),
        "research_question_coverage": round(20.0 * _ratio(q_answered, q_total), 2),
        "incremental_information_value": round(20.0 * _ratio(unique, unique + overlap), 2),
        "provenance_and_reproducibility": 15.0 if receipt.get("provenance_complete") is True and receipt.get("repeat_consistency_status") in {"PASS", "NOT_APPLICABLE"} else (8.0 if receipt.get("provenance_complete") is True else 0.0),
        "crosscheck_quality": _crosscheck_points(str(receipt.get("crosscheck_status"))),
        "operational_friction": max(0.0, 5.0 - min(5.0, manual * 2.0)),
        "cost_fit": 5.0 if receipt.get("provider_cost_status") in {"WITHIN_BUDGET", "NO_INCREMENTAL_COST"} else (2.5 if receipt.get("provider_cost_status") == "UNKNOWN" else 0.0),
        "failure_isolation": 5.0 if receipt.get("production_dependency") is False and receipt.get("canonical_owner_replaced") is False else 0.0,
    }
    score = round(sum(dimensions.values()), 2)
    return {"score": score, "dimensions": dimensions, "hard_blockers": blockers, "shape_errors": shape_errors}


def provider_ceiling(program: dict[str, Any], provider: str) -> str | None:
    if provider == program.get("baseline", {}).get("provider"):
        return "RESEARCH_ACTIVE"
    for item in program.get("queue", []):
        if item.get("provider") == provider:
            return item.get("promotion_ceiling")
    return None


def classify(score: float, blockers: list[str], shape_errors: list[str], ceiling: str | None) -> str:
    if shape_errors:
        return "KILL"
    if blockers:
        external_only = set(blockers) <= {"UNOFFICIAL_OR_UNVERIFIED_SERVER", "READ_ONLY_ALLOWLIST_NOT_ENFORCEABLE"}
        return "DATA_BLOCKED" if external_only else "KILL"
    if score < 50:
        return "KILL"
    if score < 65:
        return "HOLD"
    if score < 80:
        return "SHADOW_OBSERVATION"
    return {
        "RESEARCH_ACTIVE": "KEEP_RESEARCH_ACTIVE",
        "CROSSCHECK_ACTIVE": "KEEP_CROSSCHECK_ONLY",
        "SHADOW_OBSERVATION": "SHADOW_OBSERVATION",
        "CANDIDATE_DISCOVERY_ACTIVE": "CANDIDATE_DISCOVERY_ONLY",
        "DIAGNOSTICS_ACTIVE": "DIAGNOSTICS_ONLY",
    }.get(ceiling, "HOLD")


def evaluate(root: Path, receipt_path: Path) -> dict[str, Any]:
    program = load_json(root / PROGRAM_PATH)
    receipt = load_json(receipt_path)
    scored = score_receipt(receipt)
    ceiling = provider_ceiling(program, str(receipt.get("provider")))
    verdict = classify(scored["score"], scored["hard_blockers"], scored["shape_errors"], ceiling)
    return {
        "contract": "MCP_CONNECTION_DETERMINISTIC_EVALUATION_v1",
        "provider": receipt.get("provider"),
        "receipt": str(receipt_path),
        "deterministic_score": scored["score"],
        "dimensions": scored["dimensions"],
        "hard_blockers": scored["hard_blockers"],
        "shape_errors": scored["shape_errors"],
        "promotion_ceiling": ceiling,
        "deterministic_verdict": verdict,
        "ai_red_team_required": verdict not in {"KILL", "DATA_BLOCKED"},
        "authority": {
            "framework_state_change": False,
            "portfolio_action": False,
            "market_rule_change": False,
            "canonical_promotion": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    result = evaluate(args.root, args.receipt)
    print(json.dumps(result, sort_keys=True))
    if result["shape_errors"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
