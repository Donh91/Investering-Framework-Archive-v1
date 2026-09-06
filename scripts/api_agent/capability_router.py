from __future__ import annotations

import argparse
import hashlib
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FORBIDDEN_AUTHORITY_KEYS = {
    "portfolio_action",
    "trade_action",
    "framework_state_change",
    "market_rule_change",
    "threshold_change",
    "weight_change",
    "canonical_promotion",
    "automatic_merge",
}


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"object_required:{path}")
    return value


def _runtime_models(runtime: dict[str, Any]) -> set[str]:
    models = runtime.get("available_models", [])
    if not isinstance(models, list) or any(not isinstance(x, str) for x in models):
        raise ValueError("invalid_runtime_available_models")
    return set(models)


def _require_nonempty_string(value: Any, error: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(error)
    return value.strip()


def _require_string_list(value: Any, error: str, *, allow_empty: bool = True) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
        raise ValueError(error)
    if not allow_empty and not value:
        raise ValueError(error)
    return [x.strip() for x in value]


def _delegation_policy(policy: dict[str, Any]) -> dict[str, Any]:
    delegation = policy.get("delegation")
    if not isinstance(delegation, dict):
        raise ValueError("delegation_policy_required")
    return delegation


def _is_hardened_profile(policy: dict[str, Any], profile: dict[str, Any]) -> bool:
    return profile.get("contract") == _delegation_policy(policy).get("hardened_profile_contract")


def validate_policy(policy: dict[str, Any]) -> None:
    if policy.get("contract") != "CAPABILITY_ROUTING_POLICY_v1":
        raise ValueError("invalid_capability_routing_policy_contract")
    if policy.get("status") not in {"ACTIVE_SHADOW_FIRST", "ACTIVE_QUALIFIED"}:
        raise ValueError("invalid_capability_routing_policy_status")
    authority = policy.get("authority")
    if not isinstance(authority, dict) or any(authority.get(key) is not False for key in FORBIDDEN_AUTHORITY_KEYS):
        raise ValueError("capability_policy_authority_must_be_false")
    principles = policy.get("principles")
    if not isinstance(principles, dict):
        raise ValueError("capability_policy_principles_required")
    if principles.get("model_identity_never_grants_authority") is not True:
        raise ValueError("model_identity_authority_separation_required")
    if principles.get("api_models_have_repository_write_authority") is not False:
        raise ValueError("api_repository_write_authority_forbidden")
    if principles.get("profile_write_scope_is_request_not_authority") is not True:
        raise ValueError("profile_write_scope_must_not_grant_authority")
    if principles.get("code_write_executor") != "CODEX_ONLY":
        raise ValueError("code_write_executor_must_be_codex_only")
    if principles.get("automatic_merge") is not False:
        raise ValueError("automatic_merge_forbidden")
    for key in (
        "contract_first_decomposition",
        "responsibility_before_capability",
        "least_privilege_context",
        "delegation_lineage_required_for_hardened_profiles",
        "bounded_redelegation_only",
    ):
        if principles.get(key) is not True:
            raise ValueError(f"delegation_principle_required:{key}")

    delegation = _delegation_policy(policy)
    if delegation.get("legacy_profile_contract") != "CAPABILITY_TASK_PROFILE_v1":
        raise ValueError("invalid_legacy_profile_contract")
    if delegation.get("hardened_profile_contract") != "CAPABILITY_TASK_PROFILE_v1_1":
        raise ValueError("invalid_hardened_profile_contract")
    if delegation.get("lineage_receipt_contract") != "DELEGATION_LINEAGE_RECEIPT_v1_1":
        raise ValueError("invalid_delegation_lineage_contract")
    if delegation.get("production_requires_hardened_profile") is not True:
        raise ValueError("production_must_require_hardened_profile")
    max_depth = delegation.get("max_delegation_depth")
    if not isinstance(max_depth, int) or not 0 <= max_depth <= 4:
        raise ValueError("invalid_max_delegation_depth")
    max_redelegations = delegation.get("max_redelegations_per_unit")
    if not isinstance(max_redelegations, int) or not 0 <= max_redelegations <= 1:
        raise ValueError("invalid_max_redelegations_per_unit")
    if delegation.get("require_unique_responsibility_scope") is not True:
        raise ValueError("unique_responsibility_scope_required")
    if delegation.get("context_policy") != "LEAST_PRIVILEGE_EXPLICIT_REFS":
        raise ValueError("invalid_context_policy")
    _require_string_list(delegation.get("forbidden_unbounded_refs"), "invalid_forbidden_unbounded_refs", allow_empty=False)
    _require_string_list(delegation.get("verification_types"), "invalid_verification_types", allow_empty=False)
    _require_string_list(delegation.get("failure_modes"), "invalid_failure_modes", allow_empty=False)
    _require_string_list(delegation.get("escalation_modes"), "invalid_escalation_modes", allow_empty=False)
    bindings = delegation.get("executor_tool_bindings")
    if not isinstance(bindings, dict) or set(bindings) != {"MODEL", "CODE", "DETERMINISTIC"}:
        raise ValueError("invalid_executor_tool_bindings")
    if any(not isinstance(value, str) or not value for value in bindings.values()):
        raise ValueError("invalid_executor_tool_binding_value")

    pricing = policy.get("pricing_snapshot")
    if not isinstance(pricing, dict):
        raise ValueError("pricing_snapshot_required")
    threshold = pricing.get("long_context_threshold_tokens")
    if not isinstance(threshold, int) or threshold < 1:
        raise ValueError("invalid_long_context_threshold")
    for key in ("long_context_input_multiplier", "long_context_output_multiplier"):
        if not isinstance(pricing.get(key), (int, float)) or float(pricing[key]) < 1:
            raise ValueError(f"invalid_pricing_multiplier:{key}")
    models = policy.get("models")
    if not isinstance(models, dict) or not models:
        raise ValueError("capability_policy_models_required")
    for model_id, cfg in models.items():
        if not isinstance(model_id, str) or not isinstance(cfg, dict):
            raise ValueError("invalid_capability_model")
        if not isinstance(cfg.get("rank"), int) or cfg["rank"] < 1:
            raise ValueError(f"invalid_model_rank:{model_id}")
        if not isinstance(cfg.get("capabilities"), list):
            raise ValueError(f"invalid_model_capabilities:{model_id}")
        if not isinstance(cfg.get("reasoning_efforts"), list):
            raise ValueError(f"invalid_model_reasoning_efforts:{model_id}")
        price = cfg.get("price_per_million")
        if not isinstance(price, dict) or not isinstance(price.get("input"), (int, float)) or not isinstance(price.get("output"), (int, float)):
            raise ValueError(f"invalid_model_price:{model_id}")


def validate_runtime(runtime: dict[str, Any]) -> None:
    if runtime.get("contract") != "RUNTIME_CAPABILITIES_v1":
        raise ValueError("invalid_runtime_capabilities_contract")
    available = _runtime_models(runtime)
    if not isinstance(runtime.get("codex_available"), bool):
        raise ValueError("runtime_codex_available_required")
    if not isinstance(runtime.get("deterministic_available"), bool):
        raise ValueError("runtime_deterministic_available_required")
    if "qualified_models" in runtime:
        qualified = runtime["qualified_models"]
        if not isinstance(qualified, list) or any(not isinstance(x, str) for x in qualified):
            raise ValueError("invalid_runtime_qualified_models")
        if not set(qualified).issubset(available):
            raise ValueError("qualified_model_not_available")


def _validate_hardened_unit(
    policy: dict[str, Any],
    profile: dict[str, Any],
    unit: dict[str, Any],
    responsibility_scopes: set[str],
) -> None:
    delegation = _delegation_policy(policy)
    unit_id = str(unit["unit_id"])
    owner = _require_nonempty_string(unit.get("responsibility_owner"), f"responsibility_owner_required:{unit_id}")
    scope = _require_nonempty_string(unit.get("responsibility_scope"), f"responsibility_scope_required:{unit_id}")
    if delegation.get("require_unique_responsibility_scope") and scope in responsibility_scopes:
        raise ValueError(f"duplicate_responsibility_scope:{scope}")
    responsibility_scopes.add(scope)
    _require_nonempty_string(unit.get("expected_output"), f"expected_output_required:{unit_id}")

    verification = unit.get("verification_method")
    if not isinstance(verification, dict):
        raise ValueError(f"verification_method_required:{unit_id}")
    if verification.get("type") not in set(delegation["verification_types"]):
        raise ValueError(f"invalid_verification_type:{unit_id}")
    _require_string_list(verification.get("success_criteria"), f"verification_success_criteria_required:{unit_id}", allow_empty=False)

    allowed_context = _require_string_list(unit.get("allowed_context"), f"allowed_context_required:{unit_id}")
    allowed_tools = _require_string_list(unit.get("allowed_tools"), f"allowed_tools_required:{unit_id}")
    forbidden_refs = set(delegation["forbidden_unbounded_refs"])
    if forbidden_refs & set(allowed_context):
        raise ValueError(f"unbounded_context_forbidden:{unit_id}")
    if forbidden_refs & set(allowed_tools):
        raise ValueError(f"unbounded_tool_scope_forbidden:{unit_id}")
    required_tool = delegation["executor_tool_bindings"][unit["executor_class"]]
    if required_tool not in allowed_tools:
        raise ValueError(f"executor_tool_not_allowed:{unit_id}:{required_tool}")

    authority_scope = unit.get("authority_scope")
    if not isinstance(authority_scope, dict):
        raise ValueError(f"authority_scope_required:{unit_id}")
    if not isinstance(authority_scope.get("repository_write_requested"), bool):
        raise ValueError(f"repository_write_request_required:{unit_id}")
    if authority_scope["repository_write_requested"] is not bool(unit.get("write_required", False)):
        raise ValueError(f"repository_write_request_mismatch:{unit_id}")
    if any(authority_scope.get(key) is not False for key in FORBIDDEN_AUTHORITY_KEYS):
        raise ValueError(f"delegated_authority_must_be_false:{unit_id}")

    budget = unit.get("budget")
    if not isinstance(budget, dict):
        raise ValueError(f"budget_required:{unit_id}")
    max_cost = budget.get("max_estimated_cost_usd")
    max_input = budget.get("max_input_tokens")
    max_output = budget.get("max_output_tokens")
    if not isinstance(max_cost, (int, float)) or float(max_cost) < 0:
        raise ValueError(f"invalid_cost_budget:{unit_id}")
    if not isinstance(max_input, int) or max_input < 0:
        raise ValueError(f"invalid_input_token_budget:{unit_id}")
    if not isinstance(max_output, int) or max_output < 0:
        raise ValueError(f"invalid_output_token_budget:{unit_id}")
    estimated_input = int(unit.get("estimated_input_tokens", 0) or 0)
    estimated_output = int(unit.get("estimated_output_tokens", 0) or 0)
    if estimated_input < 0 or estimated_output < 0:
        raise ValueError(f"negative_token_estimate:{unit_id}")
    if estimated_input > max_input:
        raise ValueError(f"estimated_input_exceeds_budget:{unit_id}")
    if estimated_output > max_output:
        raise ValueError(f"estimated_output_exceeds_budget:{unit_id}")

    failure_mode = unit.get("failure_mode")
    if failure_mode not in set(delegation["failure_modes"]):
        raise ValueError(f"invalid_failure_mode:{unit_id}")
    escalation = unit.get("escalation_rule")
    if not isinstance(escalation, dict):
        raise ValueError(f"escalation_rule_required:{unit_id}")
    mode = escalation.get("mode")
    if mode not in set(delegation["escalation_modes"]):
        raise ValueError(f"invalid_escalation_mode:{unit_id}")
    max_redelegations = escalation.get("max_redelegations")
    if not isinstance(max_redelegations, int) or not 0 <= max_redelegations <= int(delegation["max_redelegations_per_unit"]):
        raise ValueError(f"invalid_unit_redelegation_limit:{unit_id}")
    target = escalation.get("target")
    if mode == "STOP":
        if max_redelegations != 0:
            raise ValueError(f"stop_cannot_redelegate:{unit_id}")
        if target not in {None, ""}:
            raise ValueError(f"stop_target_must_be_empty:{unit_id}")
    else:
        _require_nonempty_string(target, f"escalation_target_required:{unit_id}")
    if failure_mode == "FAIL_CLOSED" and mode != "STOP":
        raise ValueError(f"fail_closed_requires_stop:{unit_id}")
    if mode == "REDELEGATE_ONCE":
        if failure_mode != "REDELEGATE_ONCE_THEN_ESCALATE" or max_redelegations != 1:
            raise ValueError(f"redelegation_contract_mismatch:{unit_id}")
        if int(profile["delegation_depth"]) >= int(delegation["max_delegation_depth"]):
            raise ValueError(f"redelegation_depth_exhausted:{unit_id}")
    if failure_mode == "REDELEGATE_ONCE_THEN_ESCALATE" and mode != "REDELEGATE_ONCE":
        raise ValueError(f"redelegation_failure_mode_requires_redelegation:{unit_id}")
    if failure_mode == "ESCALATE" and mode != "ESCALATE_TO_PARENT":
        raise ValueError(f"escalate_failure_mode_requires_parent:{unit_id}")

    # Read the values so the contract cannot silently accept blank ownership metadata.
    if owner == scope:
        pass


def validate_profile(profile: dict[str, Any], policy: dict[str, Any] | None = None) -> None:
    contract = profile.get("contract")
    if policy is None:
        accepted = {"CAPABILITY_TASK_PROFILE_v1", "CAPABILITY_TASK_PROFILE_v1_1"}
    else:
        delegation = _delegation_policy(policy)
        accepted = {delegation["legacy_profile_contract"], delegation["hardened_profile_contract"]}
    if contract not in accepted:
        raise ValueError("invalid_capability_task_profile_contract")
    units = profile.get("units")
    if not isinstance(units, list) or not units:
        raise ValueError("capability_task_units_required")

    hardened = bool(policy is not None and _is_hardened_profile(policy, profile))
    responsibility_scopes: set[str] = set()
    if hardened:
        delegation = _delegation_policy(policy)
        _require_nonempty_string(profile.get("task_id"), "hardened_task_id_required")
        _require_nonempty_string(profile.get("delegator"), "hardened_delegator_required")
        depth = profile.get("delegation_depth")
        if not isinstance(depth, int) or not 0 <= depth <= int(delegation["max_delegation_depth"]):
            raise ValueError("invalid_delegation_depth")
        parent_task_id = profile.get("parent_task_id")
        if depth > 0:
            _require_nonempty_string(parent_task_id, "parent_task_id_required_for_delegation")
        elif parent_task_id not in {None, ""}:
            raise ValueError("root_profile_parent_task_id_must_be_empty")

    seen: set[str] = set()
    for unit in units:
        if not isinstance(unit, dict):
            raise ValueError("invalid_capability_task_unit")
        unit_id = unit.get("unit_id")
        if not isinstance(unit_id, str) or not unit_id or unit_id in seen:
            raise ValueError("invalid_or_duplicate_unit_id")
        seen.add(unit_id)
        executor_class = unit.get("executor_class")
        if executor_class not in {"MODEL", "CODE", "DETERMINISTIC"}:
            raise ValueError(f"invalid_executor_class:{unit_id}")
        if not isinstance(unit.get("write_required", False), bool):
            raise ValueError(f"invalid_write_required:{unit_id}")
        if not isinstance(unit.get("independent_review_required", False), bool):
            raise ValueError(f"invalid_independent_review_required:{unit_id}")
        if unit.get("write_required") and executor_class != "CODE":
            raise ValueError(f"write_requires_code_executor:{unit_id}")
        requested_scope = unit.get("requested_write_scope", [])
        if not isinstance(requested_scope, list) or any(not isinstance(x, str) or not x for x in requested_scope):
            raise ValueError(f"invalid_requested_write_scope:{unit_id}")
        if requested_scope and executor_class != "CODE":
            raise ValueError(f"write_scope_requires_code_executor:{unit_id}")
        if FORBIDDEN_AUTHORITY_KEYS & set(unit):
            raise ValueError(f"authority_key_forbidden_in_unit:{unit_id}")
        if hardened:
            _validate_hardened_unit(policy, profile, unit, responsibility_scopes)


def estimate_model_cost(policy: dict[str, Any], model_cfg: dict[str, Any], input_tokens: int, output_tokens: int) -> float:
    if input_tokens < 0 or output_tokens < 0:
        raise ValueError("negative_token_estimate")
    price = model_cfg["price_per_million"]
    input_rate = float(price["input"])
    output_rate = float(price["output"])
    pricing = policy["pricing_snapshot"]
    if input_tokens > int(pricing["long_context_threshold_tokens"]):
        input_rate *= float(pricing["long_context_input_multiplier"])
        output_rate *= float(pricing["long_context_output_multiplier"])
    return round((input_tokens * input_rate + output_tokens * output_rate) / 1_000_000, 8)


def _select_api_model(
    policy: dict[str, Any],
    runtime: dict[str, Any],
    unit: dict[str, Any],
    *,
    exclude: set[str] | None = None,
) -> dict[str, Any] | None:
    exclude = exclude or set()
    available = _runtime_models(runtime)
    complexity = str(unit.get("complexity") or "ROUTINE")
    complexity_rank = policy.get("complexity_rank", {}).get(complexity)
    if not isinstance(complexity_rank, int):
        raise ValueError(f"invalid_complexity:{complexity}")
    required_values = unit.get("required_capabilities") or []
    if not isinstance(required_values, list) or any(not isinstance(x, str) for x in required_values):
        raise ValueError("invalid_required_capabilities")
    required = set(required_values)
    requested_effort = str(unit.get("reasoning_effort") or "low")
    requires_astra = bool(unit.get("requires_astra", False))
    estimated_input = int(unit.get("estimated_input_tokens", 0) or 0)
    estimated_output = int(unit.get("estimated_output_tokens", 0) or 0)
    candidates: list[tuple[float, int, str, dict[str, Any]]] = []
    for model_id, cfg in policy["models"].items():
        if model_id in exclude or model_id not in available or cfg.get("api_eligible") is not True:
            continue
        if cfg.get("rank", 0) < complexity_rank:
            continue
        if requires_astra and model_id != "gpt-6-astra":
            continue
        if requested_effort not in set(cfg.get("reasoning_efforts", [])):
            continue
        if not required.issubset(set(cfg.get("capabilities", []))):
            continue
        cost = estimate_model_cost(policy, cfg, estimated_input, estimated_output)
        candidates.append((cost, int(cfg["rank"]), model_id, cfg))
    if not candidates:
        return None
    cost, _, model_id, cfg = sorted(candidates, key=lambda x: (x[0], x[1], x[2]))[0]
    return {
        "executor": policy["execution"]["api_executor_name"],
        "model": model_id,
        "reasoning_effort": requested_effort,
        "estimated_cost_usd": cost,
        "runtime_confirmed": True,
        "model_rank": cfg["rank"],
    }


def _delegation_input(profile: dict[str, Any], unit: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": profile.get("task_id"),
        "parent_task_id": profile.get("parent_task_id"),
        "delegator": profile.get("delegator"),
        "delegation_depth": profile.get("delegation_depth"),
        "unit_id": unit.get("unit_id"),
        "source_task": unit.get("source_task"),
        "responsibility_owner": unit.get("responsibility_owner"),
        "responsibility_scope": unit.get("responsibility_scope"),
        "expected_output": unit.get("expected_output"),
        "verification_method": unit.get("verification_method"),
        "allowed_context": unit.get("allowed_context"),
        "allowed_tools": unit.get("allowed_tools"),
        "authority_scope": unit.get("authority_scope"),
        "budget": unit.get("budget"),
        "failure_mode": unit.get("failure_mode"),
        "escalation_rule": unit.get("escalation_rule"),
    }


def _delegation_metadata(policy: dict[str, Any], profile: dict[str, Any] | None, unit: dict[str, Any]) -> dict[str, Any]:
    if not profile or not _is_hardened_profile(policy, profile):
        return {"delegation_contract_status": "LEGACY_UNHARDENED"}
    delegation = _delegation_policy(policy)
    escalation = unit["escalation_rule"]
    remaining = int(escalation.get("max_redelegations", 0))
    if int(profile["delegation_depth"]) >= int(delegation["max_delegation_depth"]):
        remaining = 0
    return {
        "delegation_contract_status": "HARDENED_V1_1",
        "delegation_lineage_contract": delegation["lineage_receipt_contract"],
        "task_id": profile["task_id"],
        "parent_task_id": profile.get("parent_task_id"),
        "delegator": profile["delegator"],
        "delegation_depth": profile["delegation_depth"],
        "responsibility_owner": unit["responsibility_owner"],
        "responsibility_scope": unit["responsibility_scope"],
        "expected_output": unit["expected_output"],
        "verification_method": unit["verification_method"],
        "allowed_context": unit["allowed_context"],
        "allowed_tools": unit["allowed_tools"],
        "authority_scope": unit["authority_scope"],
        "budget": unit["budget"],
        "failure_mode": unit["failure_mode"],
        "escalation_rule": unit["escalation_rule"],
        "redelegation_remaining": remaining,
        "delegation_input_sha256": sha256_json(_delegation_input(profile, unit)),
    }


def route_unit(
    policy: dict[str, Any],
    runtime: dict[str, Any],
    unit: dict[str, Any],
    *,
    profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    unit_id = unit["unit_id"]
    executor_class = unit["executor_class"]
    base = {
        "unit_id": unit_id,
        "source_task": unit.get("source_task"),
        "write_required": bool(unit.get("write_required", False)),
        "requested_write_scope": unit.get("requested_write_scope", []),
        "router_grants_write_authority": False,
        **_delegation_metadata(policy, profile, unit),
    }
    if executor_class == "DETERMINISTIC":
        if runtime["deterministic_available"] is not True:
            return {**base, "status": "WAITING_FOR_CAPABILITY", "executor": "DETERMINISTIC", "reason": "DETERMINISTIC_RUNTIME_UNAVAILABLE"}
        return {**base, "status": "READY", "executor": policy["execution"]["deterministic_executor_name"], "runtime_confirmed": True}
    if executor_class == "CODE":
        if not unit.get("write_required"):
            return {**base, "status": "BLOCKED", "executor": policy["execution"]["code_executor_name"], "reason": "CODE_EXECUTOR_REQUIRES_EXPLICIT_WRITE_SCOPE"}
        scope = unit.get("requested_write_scope")
        if not isinstance(scope, list) or not scope or any(not isinstance(x, str) or not x for x in scope):
            return {**base, "status": "BLOCKED", "executor": policy["execution"]["code_executor_name"], "reason": "CODE_WRITE_SCOPE_REQUIRED"}
        if runtime["codex_available"] is not True:
            return {**base, "status": "WAITING_FOR_CAPABILITY", "executor": policy["execution"]["code_executor_name"], "reason": "CODEX_RUNTIME_UNAVAILABLE"}
        return {
            **base,
            "status": "READY",
            "executor": policy["execution"]["code_executor_name"],
            "runtime_confirmed": True,
            "write_authority_source": "EXISTING_CODEX_TASK_CONTRACT_REQUIRED",
            "review_owner": policy["review"]["code_review_owner"],
            "independent_review_required": True,
            "automatic_merge": False,
        }
    selected = _select_api_model(policy, runtime, unit)
    if selected is None:
        return {**base, "status": "WAITING_FOR_CAPABILITY", "executor": policy["execution"]["api_executor_name"], "reason": "NO_VERIFIED_MODEL_SATISFIES_PROFILE"}
    if profile and _is_hardened_profile(policy, profile):
        max_cost = float(unit["budget"]["max_estimated_cost_usd"])
        if float(selected["estimated_cost_usd"]) > max_cost:
            return {
                **base,
                "status": "BLOCKED",
                "executor": policy["execution"]["api_executor_name"],
                "reason": "UNIT_COST_BUDGET_EXCEEDED",
                "estimated_cost_usd": selected["estimated_cost_usd"],
                "max_estimated_cost_usd": max_cost,
            }
    routed = {**base, "status": "READY", **selected}
    if unit.get("independent_review_required"):
        review_unit = {
            **unit,
            "required_capabilities": sorted(set(unit.get("review_capabilities") or policy["review"]["minimum_capabilities"])),
            "complexity": unit.get("review_complexity", unit.get("complexity", "DIFFICULT")),
            "reasoning_effort": unit.get("review_reasoning_effort", unit.get("reasoning_effort", "high")),
            "requires_astra": bool(unit.get("review_requires_astra", False)),
        }
        review = _select_api_model(
            policy,
            runtime,
            review_unit,
            exclude={selected["model"]} if policy["review"].get("prefer_different_model_from_worker") else set(),
        )
        if review is None:
            return {**routed, "status": "WAITING_FOR_CAPABILITY", "reason": "INDEPENDENT_REVIEW_MODEL_UNAVAILABLE", "review": None}
        routed["review"] = {**review, "read_only": True, "repository_write_authority": False}
    return routed


def build_execution_plan(policy: dict[str, Any], runtime: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    validate_policy(policy)
    validate_runtime(runtime)
    validate_profile(profile, policy)
    routes = [route_unit(policy, runtime, unit, profile=profile) for unit in profile["units"]]
    parent = None
    parent_profile = profile.get("parent")
    if parent_profile is not None:
        if not isinstance(parent_profile, dict):
            raise ValueError("invalid_parent_profile")
        parent_unit = {
            "unit_id": "__parent__",
            "executor_class": "MODEL",
            "write_required": False,
            "requested_write_scope": [],
            "independent_review_required": False,
            "complexity": parent_profile.get("complexity", "ARCHITECTURE"),
            "required_capabilities": parent_profile.get("required_capabilities", ["orchestration"]),
            "reasoning_effort": parent_profile.get("reasoning_effort", "high"),
            "requires_astra": bool(parent_profile.get("requires_astra", False)),
            "estimated_input_tokens": parent_profile.get("estimated_input_tokens", 0),
            "estimated_output_tokens": parent_profile.get("estimated_output_tokens", 0),
        }
        parent = route_unit(policy, runtime, parent_unit)
    statuses = [r["status"] for r in routes] + ([parent["status"]] if parent else [])
    if any(status == "BLOCKED" for status in statuses):
        status = "BLOCKED"
    elif any(status == "WAITING_FOR_CAPABILITY" for status in statuses):
        status = "WAITING_FOR_CAPABILITY"
    else:
        status = "READY"
    max_parallel = int(policy.get("execution", {}).get("max_parallel_units", 1))
    if not 1 <= max_parallel <= 16:
        raise ValueError("invalid_max_parallel_units")
    parallel_ready = min(sum(1 for r in routes if r["status"] == "READY"), max_parallel)
    hardened = _is_hardened_profile(policy, profile)
    return {
        "contract": "CAPABILITY_EXECUTION_PLAN_v1",
        "status": status,
        "profile_task": profile.get("task_name"),
        "profile_contract": profile.get("contract"),
        "delegation_contract_status": "HARDENED_V1_1" if hardened else "LEGACY_UNHARDENED",
        "task_id": profile.get("task_id"),
        "parent_task_id": profile.get("parent_task_id"),
        "delegator": profile.get("delegator"),
        "delegation_depth": profile.get("delegation_depth"),
        "policy_sha256": sha256_json(policy),
        "runtime_capabilities_sha256": sha256_json(runtime),
        "profile_sha256": sha256_json(profile),
        "parent": parent,
        "units": routes,
        "parallel_ready_units": parallel_ready,
        "max_parallel_units": max_parallel,
        "max_delegation_depth": policy["delegation"]["max_delegation_depth"],
        "routing_rule": "CONTRACT_FIRST_THEN_DETERMINISTIC_OR_CHEAPEST_VERIFIED_QUALIFIED_EXECUTOR",
        "automatic_merge": False,
        "router_grants_write_authority": False,
        "authority": {
            "creates_truth": False,
            "framework_state_change": False,
            "market_rule_change": False,
            "threshold_change": False,
            "weight_change": False,
            "portfolio_action": False,
            "trade_action": False,
            "canonical_promotion": False,
            "automatic_merge": False,
        },
    }


def probe_openai_runtime(api_key: str, *, codex_available: bool = False) -> dict[str, Any]:
    request = urllib.request.Request(
        "https://api.openai.com/v1/models",
        headers={"Authorization": f"Bearer {api_key}"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.loads(response.read())
    ids = sorted({item.get("id") for item in payload.get("data", []) if isinstance(item, dict) and isinstance(item.get("id"), str)})
    return {
        "contract": "RUNTIME_CAPABILITIES_v1",
        "source": "OPENAI_MODELS_API",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "available_models": ids,
        "qualified_models": [],
        "codex_available": bool(codex_available),
        "deterministic_available": True,
        "qualification_note": "MODEL_LISTING_PROVES_DISCOVERY_ONLY_NOT_ROUTING_QUALIFICATION",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a fail-closed capability routing plan without changing framework authority.")
    parser.add_argument("--policy", type=Path, default=Path("research/api_agent/CAPABILITY_ROUTING_POLICY_v1.json"))
    parser.add_argument("--profile", type=Path, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--runtime-capabilities", type=Path)
    group.add_argument("--probe-openai", action="store_true")
    parser.add_argument("--codex-available", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    policy = load_json(args.policy)
    profile = load_json(args.profile)
    if args.probe_openai:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise SystemExit("OPENAI_API_KEY_missing")
        runtime = probe_openai_runtime(api_key, codex_available=args.codex_available)
    else:
        runtime = load_json(args.runtime_capabilities)
    plan = build_execution_plan(policy, runtime, profile)
    text = json.dumps(plan, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    else:
        print(text, end="")
    return 0 if plan["status"] == "READY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
