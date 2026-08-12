from __future__ import annotations

import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

try:
    from scripts.api_agent import mcp_research_gateway as gateway
    from scripts.api_agent.advance_mcp_connection_scorecard import CEILING_ALLOWED, apply_evaluation
    from scripts.api_agent.evaluate_mcp_connection_receipt import evaluate as evaluate_receipt
except ModuleNotFoundError:
    import mcp_research_gateway as gateway
    from advance_mcp_connection_scorecard import CEILING_ALLOWED, apply_evaluation
    from evaluate_mcp_connection_receipt import evaluate as evaluate_receipt


SUMMARY_FIELDS = [
    "official_server_verified", "auth_secret_present", "auth_secret_persisted",
    "tool_discovery_status", "discovered_tool_count", "allowed_read_only_tool_count",
    "mcp_call_count", "successful_mcp_call_count", "failed_mcp_call_count",
    "mutating_tool_called", "provenance_complete", "research_questions_total",
    "research_questions_answered", "unique_value_items", "overlap_items",
    "manual_intervention_count", "production_dependency", "canonical_owner_replaced",
    "provider_cost_status", "hard_blockers", "openai_estimated_cost_usd",
]


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object_required:{path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gateway.canonical_bytes(value))


def provider_contract_path(program: dict[str, Any], provider: str) -> str:
    for row in program.get("queue", []):
        if row.get("provider") == provider:
            path = row.get("contract_path")
            if path:
                return str(path)
    raise ValueError("provider_contract_not_found")


def compact_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    return {key: deepcopy(receipt.get(key)) for key in SUMMARY_FIELDS}


def aggregate_receipts(provider: str, contract_path: str, receipts: list[dict[str, Any]]) -> dict[str, Any]:
    if not receipts:
        raise ValueError("pilot_receipts_required")
    blockers = sorted({str(item) for receipt in receipts for item in (receipt.get("hard_blockers") or [])})
    return {
        "contract": "MCP_CONNECTION_PILOT_RECEIPT_v1",
        "provider": provider,
        "provider_contract": contract_path,
        "stage": "REDUNDANCY_AND_INCREMENTAL_VALUE_REVIEW",
        "status": "PASS" if not blockers and all(r.get("failed_mcp_call_count", 0) == 0 for r in receipts) else "PARTIAL",
        "created_at_utc": gateway.utc_now(),
        "official_server_verified": all(r.get("official_server_verified") is True for r in receipts),
        "auth_secret_present": all(r.get("auth_secret_present") is True for r in receipts),
        "auth_secret_persisted": any(r.get("auth_secret_persisted") is True for r in receipts),
        "tool_discovery_status": "PASS" if all(r.get("tool_discovery_status") == "PASS" for r in receipts) else "PARTIAL",
        "discovered_tool_count": max(int(r.get("discovered_tool_count", 0) or 0) for r in receipts),
        "allowed_read_only_tool_count": max(int(r.get("allowed_read_only_tool_count", 0) or 0) for r in receipts),
        "mcp_call_count": sum(int(r.get("mcp_call_count", 0) or 0) for r in receipts),
        "successful_mcp_call_count": sum(int(r.get("successful_mcp_call_count", 0) or 0) for r in receipts),
        "failed_mcp_call_count": sum(int(r.get("failed_mcp_call_count", 0) or 0) for r in receipts),
        "mutating_tool_called": any(r.get("mutating_tool_called") is True for r in receipts),
        "provenance_complete": all(r.get("provenance_complete") is True for r in receipts),
        "research_questions_total": sum(int(r.get("research_questions_total", 0) or 0) for r in receipts),
        "research_questions_answered": sum(int(r.get("research_questions_answered", 0) or 0) for r in receipts),
        "unique_value_items": sum(int(r.get("unique_value_items", 0) or 0) for r in receipts),
        "overlap_items": sum(int(r.get("overlap_items", 0) or 0) for r in receipts),
        "crosscheck_status": "NOT_RUN",
        "repeat_consistency_status": "NOT_RUN",
        "manual_intervention_count": sum(int(r.get("manual_intervention_count", 0) or 0) for r in receipts),
        "provider_cost_status": "UNKNOWN",
        "production_dependency": any(r.get("production_dependency") is True for r in receipts),
        "canonical_owner_replaced": any(r.get("canonical_owner_replaced") is True for r in receipts),
        "hard_blockers": blockers,
        "tool_inventory": [],
        "allowed_tool_names": [],
        "called_tool_names": [],
        "openai_estimated_cost_usd": round(sum(float(r.get("openai_estimated_cost_usd", 0.0) or 0.0) for r in receipts), 8),
        "research_output_hash": None,
        "notes": [f"Deterministic aggregate of {len(receipts)} bounded challenge receipts; raw provider outputs remain separately receipted."],
        "authority": {"framework_state_change": False, "portfolio_action": False, "market_rule_change": False, "canonical_promotion": False},
    }


def auth_missing_evaluation(provider: str, receipt_path: Path, ceiling: str | None) -> dict[str, Any]:
    return {
        "contract": "MCP_CONNECTION_DETERMINISTIC_EVALUATION_v1",
        "provider": provider,
        "receipt": str(receipt_path),
        "deterministic_score": 0.0,
        "dimensions": {},
        "hard_blockers": ["AUTH_MISSING_EXTERNAL_DEPENDENCY"],
        "shape_errors": [],
        "promotion_ceiling": ceiling,
        "deterministic_verdict": "DATA_BLOCKED",
        "ai_red_team_required": False,
        "authority": {"framework_state_change": False, "portfolio_action": False, "market_rule_change": False, "canonical_promotion": False},
    }


def ceiling_for(program: dict[str, Any], provider: str) -> str | None:
    for row in program.get("queue", []):
        if row.get("provider") == provider:
            return row.get("promotion_ceiling")
    return None


def ai_red_team(api_key: str, program: dict[str, Any], evaluation: dict[str, Any], aggregate: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    ceiling = str(evaluation.get("promotion_ceiling"))
    allowed = sorted(set(CEILING_ALLOWED.get(ceiling, {"HOLD", "KILL", "DATA_BLOCKED"})) & set(program.get("ai_review", {}).get("allowed_verdicts", [])))
    schema = {
        "type": "object", "additionalProperties": False,
        "required": ["verdict", "incremental_value_assessment", "redundancy_risk", "provenance_assessment", "reason"],
        "properties": {
            "verdict": {"type": "string", "enum": allowed},
            "incremental_value_assessment": {"type": "string"},
            "redundancy_risk": {"type": "string"},
            "provenance_assessment": {"type": "string"},
            "reason": {"type": "string"},
        },
    }
    payload = {
        "model": "gpt-5.6-luna",
        "reasoning": {"effort": "medium", "context": "current_turn"},
        "store": False,
        "max_output_tokens": 900,
        "instructions": "Act as the Research Lab Red Team for an MCP provider pilot. Do not infer market direction or portfolio action. Judge only research utility, redundancy, provenance, reliability and safety. Respect the supplied promotion ceiling and deterministic hard blockers.",
        "input": json.dumps({"evaluation": evaluation, "aggregate_receipt": aggregate}, sort_keys=True),
        "text": {"format": {"type": "json_schema", "name": "mcp_provider_red_team_v1", "strict": True, "schema": schema}},
    }
    response = gateway.call_openai(api_key, payload)
    text = gateway.extract_output_text(response)
    value = json.loads(text)
    verdict = str(value.get("verdict"))
    if verdict not in allowed:
        raise ValueError("ai_verdict_outside_ceiling")
    _, _, cost = gateway.usage_cost(response)
    value["openai_estimated_cost_usd"] = cost
    return verdict, value


def run_gateway(contract_path: str, challenge_index: int, output_dir: Path) -> dict[str, Any]:
    cmd = [
        sys.executable, "scripts/api_agent/mcp_research_gateway.py",
        "--provider-contract", contract_path,
        "--challenge-index", str(challenge_index),
        "--output-dir", str(output_dir),
    ]
    result = subprocess.run(cmd, check=False, text=True, capture_output=True)
    receipt_path = output_dir / "receipt.json"
    if not receipt_path.exists():
        raise RuntimeError(f"gateway_receipt_missing:exit={result.returncode}:{result.stderr[-400:]}")
    return load_json(receipt_path)


def execute(program_path: Path, scorecard_path: Path, automation_state_path: Path, output_dir: Path) -> dict[str, Any]:
    program = load_json(program_path)
    scorecard = load_json(scorecard_path)
    state = load_json(automation_state_path)
    provider = scorecard.get("active_provider")
    if not provider:
        return {"status": "NO_ACTIVE_PROVIDER", "scorecard_updated": False}
    contract_path = provider_contract_path(program, str(provider))
    contract = load_json(Path(contract_path))
    challenges = contract.get("pilot_research_challenges") if isinstance(contract.get("pilot_research_challenges"), list) else []
    if not challenges:
        raise ValueError("provider_has_no_pilot_challenges")
    progress = state.setdefault("provider_progress", {}).setdefault(str(provider), {"next_challenge_index": 0, "receipt_summaries": []})
    challenge_index = int(progress.get("next_challenge_index", 0) or 0)
    if challenge_index >= len(challenges):
        challenge_index = len(challenges) - 1

    challenge_dir = output_dir / f"challenge_{challenge_index + 1}"
    receipt = run_gateway(contract_path, challenge_index, challenge_dir)
    blockers = set(receipt.get("hard_blockers") or [])
    if "OPENAI_API_KEY_MISSING" in blockers:
        result = {"status": "BLOCKED_SHARED_OPENAI_DEPENDENCY", "provider": provider, "scorecard_updated": False, "receipt": receipt}
        write_json(output_dir / "automation_result.json", result)
        write_json(output_dir / "next_automation_state.json", state)
        return result
    if blockers == {"AUTH_MISSING_EXTERNAL_DEPENDENCY"}:
        evaluation = auth_missing_evaluation(str(provider), challenge_dir / "receipt.json", ceiling_for(program, str(provider)))
        updated = apply_evaluation(program, scorecard, evaluation, None)
        state["provider_progress"].pop(str(provider), None)
        result = {"status": "DATA_BLOCKED_PROVIDER_ADVANCED", "provider": provider, "scorecard_updated": True, "evaluation": evaluation}
        write_json(output_dir / "evaluation.json", evaluation)
        write_json(output_dir / "next_scorecard.json", updated)
        write_json(output_dir / "next_automation_state.json", state)
        write_json(output_dir / "automation_result.json", result)
        return result

    summary = compact_receipt(receipt)
    progress.setdefault("receipt_summaries", []).append(summary)
    progress["next_challenge_index"] = challenge_index + 1
    if progress["next_challenge_index"] < len(challenges):
        result = {"status": "CHALLENGE_RECORDED", "provider": provider, "challenge_index": challenge_index, "remaining": len(challenges) - progress["next_challenge_index"], "scorecard_updated": False}
        write_json(output_dir / "next_automation_state.json", state)
        write_json(output_dir / "automation_result.json", result)
        return result

    aggregate = aggregate_receipts(str(provider), contract_path, list(progress.get("receipt_summaries", [])))
    aggregate_path = output_dir / "aggregate_receipt.json"
    write_json(aggregate_path, aggregate)
    evaluation = evaluate_receipt(Path("."), aggregate_path)
    write_json(output_dir / "evaluation.json", evaluation)
    ai_verdict = None
    red_team = None
    if evaluation.get("ai_red_team_required") is True:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            result = {"status": "BLOCKED_SHARED_OPENAI_DEPENDENCY", "provider": provider, "scorecard_updated": False, "evaluation": evaluation}
            write_json(output_dir / "next_automation_state.json", state)
            write_json(output_dir / "automation_result.json", result)
            return result
        ai_verdict, red_team = ai_red_team(api_key, program, evaluation, aggregate)
        write_json(output_dir / "red_team_receipt.json", red_team)
    updated = apply_evaluation(program, scorecard, evaluation, ai_verdict)
    state["provider_progress"].pop(str(provider), None)
    result = {"status": "PROVIDER_TERMINAL_CLASSIFICATION", "provider": provider, "scorecard_updated": True, "deterministic_verdict": evaluation.get("deterministic_verdict"), "ai_verdict": ai_verdict}
    write_json(output_dir / "next_scorecard.json", updated)
    write_json(output_dir / "next_automation_state.json", state)
    write_json(output_dir / "automation_result.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run exactly one staged MCP provider pilot unit and advance only when evidence is sufficient or an external provider dependency is blocked.")
    parser.add_argument("--program", type=Path, required=True)
    parser.add_argument("--scorecard", type=Path, required=True)
    parser.add_argument("--automation-state", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = execute(args.program, args.scorecard, args.automation_state, args.output_dir)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
