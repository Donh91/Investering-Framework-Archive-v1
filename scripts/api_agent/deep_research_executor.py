from __future__ import annotations

import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
from typing import Any

try:
    from scripts.api_agent import advance_deep_research_queue as queue_engine
    from scripts.api_agent import mcp_research_gateway as mcp
    from scripts.api_agent.mcp_transport_normalizer import normalize_mcp_contract
except ModuleNotFoundError:
    import advance_deep_research_queue as queue_engine
    import mcp_research_gateway as mcp
    from mcp_transport_normalizer import normalize_mcp_contract

MAX_EXECUTOR_COST_USD = 0.75
UNIVERSAL_FORBIDDEN_TOOL_FRAGMENTS = {
    "trade", "order", "execute", "transfer", "withdraw", "deposit", "wallet",
    "portfolio", "account", "delete", "update", "write", "create", "save",
}
RED_TEAM_VERDICTS = {
    "REJECT", "SOURCE_CONTEXT_ONLY", "EXPLANATORY_ONLY", "SHADOW_OBSERVATION",
    "MODIFY_EXISTING_TEST", "DATA_BLOCKED",
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object_required:{path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(mcp.canonical_bytes(value))


def zero_authority() -> dict[str, bool]:
    return {
        "framework_state_change": False,
        "portfolio_action": False,
        "market_rule_change": False,
        "threshold_change": False,
        "weight_change": False,
        "canonical_promotion": False,
        "new_sensor": False,
    }


def authority_is_zero(value: dict[str, Any]) -> bool:
    authority = value.get("authority") if isinstance(value.get("authority"), dict) else {}
    return bool(authority) and all(item is False for item in authority.values())


def provider_row(scorecard: dict[str, Any], provider: str) -> dict[str, Any] | None:
    for row in scorecard.get("providers", []):
        if isinstance(row, dict) and row.get("provider") == provider:
            return row
    return None


def provider_is_retained(scorecard: dict[str, Any], provider: str) -> bool:
    row = provider_row(scorecard, provider)
    return bool(row and row.get("state") in queue_engine.USABLE_PROVIDER_STATES)


def prepare_provider_contract(contract: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_mcp_contract(contract)
    forbidden = {str(item).lower() for item in normalized.get("forbidden_tool_name_fragments", [])}
    forbidden.update(UNIVERSAL_FORBIDDEN_TOOL_FRAGMENTS)
    normalized["forbidden_tool_name_fragments"] = sorted(forbidden)
    return normalized


def blocked_provider_evidence(provider: str, reason: str) -> dict[str, Any]:
    return {
        "contract": "DEEP_RESEARCH_PROVIDER_EVIDENCE_v1",
        "provider": provider,
        "status": "BLOCKED",
        "reason": reason,
        "provenance_complete": False,
        "calls": [],
        "openai_estimated_cost_usd": 0.0,
        "authority": zero_authority(),
    }


def acquire_provider_evidence(
    provider: str,
    task: dict[str, Any],
    scorecard: dict[str, Any],
    provider_contract_path: Path,
    openai_key: str | None,
) -> dict[str, Any]:
    if not provider_is_retained(scorecard, provider):
        return blocked_provider_evidence(provider, "PROVIDER_NOT_RETAINED")
    raw_contract = mcp.load_contract(provider_contract_path)
    contract = prepare_provider_contract(raw_contract)
    headers, auth_present = mcp.resolve_headers(contract)
    if not auth_present:
        return blocked_provider_evidence(provider, "AUTH_MISSING_EXTERNAL_DEPENDENCY")
    if not openai_key:
        return blocked_provider_evidence(provider, "OPENAI_API_KEY_MISSING")

    probe = mcp.call_openai(openai_key, mcp.build_probe_payload(contract, headers))
    inventory = mcp.extract_inventory(probe)
    allowed = mcp.select_allowed_tools(contract, inventory)
    probe_i, probe_o, probe_cost = mcp.usage_cost(probe)
    if not inventory:
        result = blocked_provider_evidence(provider, "MCP_TOOL_DISCOVERY_EMPTY")
        result["openai_estimated_cost_usd"] = probe_cost
        return result
    if not allowed:
        result = blocked_provider_evidence(provider, "READ_ONLY_ALLOWLIST_NOT_ENFORCEABLE")
        result["openai_estimated_cost_usd"] = probe_cost
        return result

    challenge = (
        f"Deep Research task {task.get('research_id')}: {task.get('question')}\n"
        f"Horizons: {json.dumps(task.get('horizons', []))}. "
        "Return only source-backed provider evidence relevant to the task. Preserve timestamps, missingness, conflicts and provenance."
    )
    response = mcp.call_openai(openai_key, mcp.build_research_payload(contract, headers, allowed, challenge))
    calls = mcp.extract_calls(response)
    if not calls:
        return blocked_provider_evidence(provider, "MCP_RESEARCH_CALL_MISSING")
    if any(call.get("name") not in allowed for call in calls):
        return blocked_provider_evidence(provider, "MCP_CALLED_TOOL_OUTSIDE_ALLOWLIST")
    output_text = mcp.extract_output_text(response)
    if not output_text:
        return blocked_provider_evidence(provider, "MCP_RESEARCH_OUTPUT_MISSING")
    try:
        parsed = json.loads(output_text)
    except json.JSONDecodeError:
        return blocked_provider_evidence(provider, "MCP_RESEARCH_OUTPUT_INVALID_JSON")
    research_i, research_o, research_cost = mcp.usage_cost(response)
    provenance = parsed.get("provenance") if isinstance(parsed, dict) else None
    return {
        "contract": "DEEP_RESEARCH_PROVIDER_EVIDENCE_v1",
        "provider": provider,
        "status": "READY" if provenance else "DEGRADED",
        "provider_state": provider_row(scorecard, provider).get("state") if provider_row(scorecard, provider) else None,
        "server_url": contract.get("transport", {}).get("server_url"),
        "tool_inventory_count": len(inventory),
        "allowed_tool_names": allowed,
        "calls": calls,
        "result": parsed,
        "provenance_complete": bool(provenance),
        "openai_usage": {
            "input_tokens": probe_i + research_i,
            "output_tokens": probe_o + research_o,
        },
        "openai_estimated_cost_usd": round(probe_cost + research_cost, 8),
        "authority": zero_authority(),
    }


def research_schema() -> dict[str, Any]:
    horizon_item = {
        "type": "object",
        "additionalProperties": False,
        "required": ["horizon", "supporting_evidence", "contrary_evidence", "conflicts", "unknowns", "provenance"],
        "properties": {
            "horizon": {"type": "string"},
            "supporting_evidence": {"type": "array", "items": {"type": "string"}},
            "contrary_evidence": {"type": "array", "items": {"type": "string"}},
            "conflicts": {"type": "array", "items": {"type": "string"}},
            "unknowns": {"type": "array", "items": {"type": "string"}},
            "provenance": {"type": "array", "items": {"type": "string"}},
        },
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "status", "research_id", "horizon_findings", "cross_horizon_agreement",
            "cross_horizon_conflicts", "horizon_conflict", "evidence_for_hypothesis",
            "evidence_against_hypothesis", "unknowns", "provider_provenance",
            "decision_divergence_assessment", "integration_recommendation",
        ],
        "properties": {
            "status": {"type": "string", "enum": ["READY", "DEGRADED", "BLOCKED"]},
            "research_id": {"type": "string"},
            "horizon_findings": {"type": "array", "items": horizon_item},
            "cross_horizon_agreement": {"type": "array", "items": {"type": "string"}},
            "cross_horizon_conflicts": {"type": "array", "items": {"type": "string"}},
            "horizon_conflict": {"type": "boolean"},
            "evidence_for_hypothesis": {"type": "array", "items": {"type": "string"}},
            "evidence_against_hypothesis": {"type": "array", "items": {"type": "string"}},
            "unknowns": {"type": "array", "items": {"type": "string"}},
            "provider_provenance": {"type": "array", "items": {"type": "string"}},
            "decision_divergence_assessment": {"type": "string"},
            "integration_recommendation": {
                "type": "string",
                "enum": [
                    "RESEARCH_CONTEXT_ONLY", "EXISTING_TEST_SUPPORT_ONLY", "SHADOW_OBSERVATION_ONLY",
                    "CROSSCHECK_ONLY", "CANDIDATE_DISCOVERY_CONTEXT_ONLY", "RESEARCH_INFRASTRUCTURE_ONLY", "NO_CHANGE",
                ],
            },
        },
    }


def red_team_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "verdict", "frozen_proposition", "decision_divergence", "evidence_class",
            "strongest_support", "strongest_falsification", "false_positive_cost",
            "false_negative_cost", "falsifier_status", "kill_condition_status",
            "governance_proposal_warranted", "next_action",
        ],
        "properties": {
            "verdict": {"type": "string", "enum": sorted(RED_TEAM_VERDICTS)},
            "frozen_proposition": {"type": "string"},
            "decision_divergence": {"type": "string"},
            "evidence_class": {"type": "string"},
            "strongest_support": {"type": "string"},
            "strongest_falsification": {"type": "string"},
            "false_positive_cost": {"type": "string"},
            "false_negative_cost": {"type": "string"},
            "falsifier_status": {"type": "string"},
            "kill_condition_status": {"type": "string"},
            "governance_proposal_warranted": {"type": "boolean"},
            "next_action": {"type": "string"},
        },
    }


def structured_payload(model: str, name: str, schema: dict[str, Any], instructions: str, data: Any, max_output_tokens: int) -> dict[str, Any]:
    return {
        "model": model,
        "reasoning": {"effort": "medium", "context": "current_turn"},
        "store": False,
        "max_output_tokens": max_output_tokens,
        "instructions": instructions,
        "input": json.dumps(data, sort_keys=True),
        "text": {"format": {"type": "json_schema", "name": name, "strict": True, "schema": schema}},
    }


def call_structured_with_one_retry(api_key: str, payload: dict[str, Any]) -> tuple[dict[str, Any], float, int]:
    last_error: Exception | None = None
    cost = 0.0
    for attempt in (1, 2):
        response = mcp.call_openai(api_key, payload)
        _, _, attempt_cost = mcp.usage_cost(response)
        cost += attempt_cost
        text = mcp.extract_output_text(response)
        try:
            value = json.loads(text)
            if isinstance(value, dict):
                return value, round(cost, 8), attempt
            last_error = ValueError("structured_object_required")
        except Exception as exc:
            last_error = exc
    raise ValueError(f"structured_output_invalid_after_bounded_retry:{last_error}")


def coverage_gate_passes(coverage: dict[str, Any] | None, policy: dict[str, Any]) -> bool:
    gate = policy.get("coverage_gate", {})
    if not isinstance(coverage, dict):
        return False
    return (
        coverage.get("contract") == gate.get("required_coverage_contract")
        and coverage.get("coverage_status") == gate.get("required_coverage_status")
        and int(coverage.get("checks_total", 0) or 0) >= int(gate.get("minimum_checks_total", 1))
    )


def select_followup(
    queue: dict[str, Any],
    state: dict[str, Any],
    scorecard: dict[str, Any],
    policy: dict[str, Any],
    current_task: dict[str, Any],
    result: dict[str, Any] | None,
    supplemental_task: dict[str, Any],
    coverage: dict[str, Any] | None,
    terminal_state: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    updated = deepcopy(state)
    current_id = str(current_task.get("research_id"))
    updated.setdefault("item_states", {})[current_id] = {"state": terminal_state, "missing_required_providers": []}
    updated["active_research_id"] = None
    bucket_name = "completed_research_ids" if terminal_state == "COMPLETE" else "held_research_ids"
    bucket = updated.setdefault(bucket_name, [])
    if current_id not in bucket:
        bucket.append(current_id)

    available = queue_engine.retained_providers(scorecard)
    updated = queue_engine.refresh_item_states(queue, updated, available)
    updated["active_research_id"] = None

    event = policy.get("event_priority", {})
    event_target = str(event.get("priority_target"))
    if (
        terminal_state == "COMPLETE"
        and current_id == event.get("source_research_id")
        and isinstance(result, dict)
        and result.get(event.get("condition_field")) is event.get("condition_value")
        and updated.get("item_states", {}).get(event_target, {}).get("state") == "READY"
    ):
        item = next(item for item in queue.get("items", []) if item.get("id") == event_target)
        updated["active_research_id"] = event_target
        updated["item_states"][event_target] = {"state": "ACTIVE_READY_FOR_RESEARCH", "missing_required_providers": []}
        return updated, queue_engine.build_task_packet(item, updated)

    supplemental_id = supplemental_task.get("research_id")
    completed = set(updated.get("completed_research_ids", []))
    if "DRQ-001" in completed and supplemental_id not in completed and current_id != supplemental_id:
        updated["active_research_id"] = supplemental_id
        updated["item_states"][supplemental_id] = {"state": "ACTIVE_READY_FOR_RESEARCH", "missing_required_providers": []}
        task = deepcopy(supplemental_task)
        task["status"] = "READY"
        return updated, task

    queue_for_selection = deepcopy(queue)
    if not coverage_gate_passes(coverage, policy):
        queue_for_selection["items"] = [item for item in queue_for_selection.get("items", []) if item.get("id") != "DRQ-018"]
    updated, item = queue_engine.select_next(queue_for_selection, updated, scorecard)
    if not coverage_gate_passes(coverage, policy):
        updated.setdefault("item_states", {})["DRQ-018"] = {
            "state": "WAIT_PROSPECTIVE_COVERAGE",
            "missing_required_providers": [],
        }
    return updated, queue_engine.build_task_packet(item, updated)


def execute(
    task: dict[str, Any],
    queue: dict[str, Any],
    state: dict[str, Any],
    scorecard: dict[str, Any],
    policy: dict[str, Any],
    supplemental_task: dict[str, Any],
    output_dir: Path,
    owner_context: dict[str, Any] | None = None,
    coverage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if task.get("status") not in {"READY", "PREREGISTERED_SUPPLEMENTAL_RESEARCH"}:
        raise ValueError("ready_task_required")
    if not authority_is_zero(task):
        raise ValueError("task_authority_not_zero")
    output_dir.mkdir(parents=True, exist_ok=True)
    openai_key = os.environ.get("OPENAI_API_KEY")

    provider_paths = policy.get("provider_contracts", {})
    required = list(task.get("required_providers", []))
    optional = list(task.get("optional_retained_providers", []))
    evidence: list[dict[str, Any]] = []
    for provider in required + optional:
        if provider in {row.get("provider") for row in scorecard.get("providers", []) if isinstance(row, dict)} and provider_is_retained(scorecard, provider):
            path = provider_paths.get(provider)
            if not path:
                evidence.append(blocked_provider_evidence(provider, "PROVIDER_CONTRACT_MAPPING_MISSING"))
            else:
                evidence.append(acquire_provider_evidence(provider, task, scorecard, Path(path), openai_key))

    total_cost = round(sum(float(item.get("openai_estimated_cost_usd", 0.0) or 0.0) for item in evidence), 8)
    for item in evidence:
        write_json(output_dir / "provider_evidence" / f"{item.get('provider')}.json", item)

    required_blocked = [item for item in evidence if item.get("provider") in required and item.get("status") == "BLOCKED"]
    if required and (len(evidence) < len(required) or required_blocked):
        completion = {
            "contract": "DEEP_RESEARCH_COMPLETION_RECEIPT_v1",
            "research_id": task.get("research_id"),
            "status": "BLOCKED",
            "reason": "REQUIRED_PROVIDER_EVIDENCE_UNAVAILABLE",
            "provider_evidence": [item.get("provider") for item in evidence],
            "openai_estimated_cost_usd": total_cost,
            "authority": zero_authority(),
        }
        next_state, next_task = select_followup(queue, state, scorecard, policy, task, None, supplemental_task, coverage, "HOLD")
        write_json(output_dir / "completion_receipt.json", completion)
        write_json(output_dir / "next_state.json", next_state)
        write_json(output_dir / "next_task.json", next_task)
        return completion
    if not openai_key:
        completion = {
            "contract": "DEEP_RESEARCH_COMPLETION_RECEIPT_v1",
            "research_id": task.get("research_id"),
            "status": "BLOCKED",
            "reason": "OPENAI_API_KEY_MISSING",
            "openai_estimated_cost_usd": total_cost,
            "authority": zero_authority(),
        }
        write_json(output_dir / "completion_receipt.json", completion)
        return completion

    synthesis_input = {
        "task": task,
        "owner_context": owner_context or {"status": "NOT_SUPPLIED", "missing_data": "UNKNOWN"},
        "provider_evidence": evidence,
        "rules": [
            "Research evidence only; do not output BUY, SELL or position sizing.",
            "Missing data is unknown, not negative evidence.",
            "Model agreement is not independent evidence.",
            "Preserve horizon conflict instead of forcing one direction.",
            "Do not change framework state, thresholds, weights, sensors or policy semantics.",
        ],
    }
    synthesis_instructions = (
        "Perform the bounded Deep Research task from the supplied immutable context. Separate supporting and contrary evidence, preserve provenance and unknowns, and explicitly identify cross-horizon conflict. "
        "The result is research evidence only and cannot create a market state, portfolio action, threshold, weight, sensor or canonical promotion."
    )
    try:
        result, synth_cost, synth_attempts = call_structured_with_one_retry(
            openai_key,
            structured_payload("gpt-5.6-luna", "deep_research_result_v1", research_schema(), synthesis_instructions, synthesis_input, 2600),
        )
    except Exception as exc:
        completion = {
            "contract": "DEEP_RESEARCH_COMPLETION_RECEIPT_v1",
            "research_id": task.get("research_id"),
            "status": "BLOCKED",
            "reason": f"RESEARCH_OUTPUT_INVALID:{str(exc)[:240]}",
            "openai_estimated_cost_usd": total_cost,
            "authority": zero_authority(),
        }
        write_json(output_dir / "completion_receipt.json", completion)
        return completion
    total_cost = round(total_cost + synth_cost, 8)
    if total_cost > MAX_EXECUTOR_COST_USD:
        raise ValueError("deep_research_cost_ceiling_exceeded")
    write_json(output_dir / "research_result.json", result)

    red_team_input = {
        "task": task,
        "research_result": result,
        "provider_evidence": evidence,
        "authority_boundary": zero_authority(),
    }
    red_team_instructions = (
        "Act as the framework Research Lab Red Team. Assume the research claim is wrong until it survives falsification. Separate source context from outcome evidence, demand measurable decision divergence, state false-positive and false-negative costs, and enforce the task integration ceiling. "
        "You may recommend a governance proposal, but you may not promote, integrate or change live market or portfolio state."
    )
    red_team, red_cost, red_attempts = call_structured_with_one_retry(
        openai_key,
        structured_payload("gpt-5.6-luna", "deep_research_red_team_v1", red_team_schema(), red_team_instructions, red_team_input, 1800),
    )
    total_cost = round(total_cost + red_cost, 8)
    if total_cost > MAX_EXECUTOR_COST_USD:
        raise ValueError("deep_research_cost_ceiling_exceeded")
    write_json(output_dir / "red_team_receipt.json", red_team)

    completion = {
        "contract": "DEEP_RESEARCH_COMPLETION_RECEIPT_v1",
        "research_id": task.get("research_id"),
        "status": "COMPLETE",
        "research_status": result.get("status"),
        "red_team_verdict": red_team.get("verdict"),
        "governance_proposal_warranted": red_team.get("governance_proposal_warranted") is True,
        "automatic_integration_performed": False,
        "provider_provenance_complete": all(item.get("provenance_complete") for item in evidence) if evidence else True,
        "research_attempts": synth_attempts,
        "red_team_attempts": red_attempts,
        "openai_estimated_cost_usd": total_cost,
        "authority": zero_authority(),
    }
    next_state, next_task = select_followup(queue, state, scorecard, policy, task, result, supplemental_task, coverage, "COMPLETE")
    write_json(output_dir / "completion_receipt.json", completion)
    write_json(output_dir / "next_state.json", next_state)
    write_json(output_dir / "next_task.json", next_task)
    return completion


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute one bounded Deep Research queue item through provider evidence, synthesis, red-team and queue advancement.")
    parser.add_argument("--task", type=Path, required=True)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--provider-scorecard", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--supplemental-task", type=Path, required=True)
    parser.add_argument("--owner-context", type=Path)
    parser.add_argument("--coverage-health", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    completion = execute(
        load_json(args.task),
        load_json(args.queue),
        load_json(args.state),
        load_json(args.provider_scorecard),
        load_json(args.policy),
        load_json(args.supplemental_task),
        args.output_dir,
        load_json(args.owner_context) if args.owner_context else None,
        load_json(args.coverage_health) if args.coverage_health else None,
    )
    print(json.dumps(completion, sort_keys=True))
    return 0 if completion.get("status") == "COMPLETE" else 78


if __name__ == "__main__":
    raise SystemExit(main())
