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
    if principles.get("code_write_executor") != "CODEX_ONLY":
        raise ValueError("code_write_executor_must_be_codex_only")
    if principles.get("automatic_merge") is not False:
        raise ValueError("automatic_merge_forbidden")
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
    _runtime_models(runtime)
    if not isinstance(runtime.get("codex_available"), bool):
        raise ValueError("runtime_codex_available_required")
    if not isinstance(runtime.get("deterministic_available"), bool):
        raise ValueError("runtime_deterministic_available_required")


def validate_profile(profile: dict[str, Any]) -> None:
    if profile.get("contract") != "CAPABILITY_TASK_PROFILE_v1":
        raise ValueError("invalid_capability_task_profile_contract")
    units = profile.get("units")
    if not isinstance(units, list) or not units:
        raise ValueError("capability_task_units_required")
    seen: set[str] = set()
    for unit in units:
        if not isinstance(unit, dict):
            raise ValueError("invalid_capability_task_unit")
        unit_id = unit.get("unit_id")
        if not isinstance(unit_id, str) or not unit_id or unit_id in seen:
            raise ValueError("invalid_or_duplicate_unit_id")
        seen.add(unit_id)
        if unit.get("executor_class") not in {"MODEL", "CODE", "DETERMINISTIC"}:
            raise ValueError(f"invalid_executor_class:{unit_id}")
        if not isinstance(unit.get("write_required", False), bool):
            raise ValueError(f"invalid_write_required:{unit_id}")
        if not isinstance(unit.get("independent_review_required", False), bool):
            raise ValueError(f"invalid_independent_review_required:{unit_id}")
        if unit.get("write_required") and unit.get("executor_class") != "CODE":
            raise ValueError(f"write_requires_code_executor:{unit_id}")
        if FORBIDDEN_AUTHORITY_KEYS & set(unit):
            raise ValueError(f"authority_key_forbidden_in_unit:{unit_id}")


def estimate_model_cost(model_cfg: dict[str, Any], input_tokens: int, output_tokens: int) -> float:
    price = model_cfg["price_per_million"]
    return round((input_tokens * float(price["input"]) + output_tokens * float(price["output"])) / 1_000_000, 8)


def _select_api_model(policy: dict[str, Any], runtime: dict[str, Any], unit: dict[str, Any], *, exclude: set[str] | None = None) -> dict[str, Any] | None:
    exclude = exclude or set()
    available = _runtime_models(runtime)
    complexity = str(unit.get("complexity") or "ROUTINE")
    complexity_rank = policy.get("complexity_rank", {}).get(complexity)
    if not isinstance(complexity_rank, int):
        raise ValueError(f"invalid_complexity:{complexity}")
    required = set(unit.get("required_capabilities") or [])
    if any(not isinstance(x, str) for x in required):
        raise ValueError("invalid_required_capabilities")
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
        cost = estimate_model_cost(cfg, estimated_input, estimated_output)
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


def route_unit(policy: dict[str, Any], runtime: dict[str, Any], unit: dict[str, Any]) -> dict[str, Any]:
    unit_id = unit["unit_id"]
    executor_class = unit["executor_class"]
    base = {
        "unit_id": unit_id,
        "source_task": unit.get("source_task"),
        "write_required": bool(unit.get("write_required", False)),
        "allowed_write_scope": unit.get("allowed_write_scope", []),
    }
    if executor_class == "DETERMINISTIC":
        if runtime["deterministic_available"] is not True:
            return {**base, "status": "WAITING_FOR_CAPABILITY", "executor": "DETERMINISTIC", "reason": "DETERMINISTIC_RUNTIME_UNAVAILABLE"}
        return {**base, "status": "READY", "executor": policy["execution"]["deterministic_executor_name"], "runtime_confirmed": True}
    if executor_class == "CODE":
        if not unit.get("write_required"):
            return {**base, "status": "BLOCKED", "executor": policy["execution"]["code_executor_name"], "reason": "CODE_EXECUTOR_REQUIRES_EXPLICIT_WRITE_SCOPE"}
        scope = unit.get("allowed_write_scope")
        if not isinstance(scope, list) or not scope or any(not isinstance(x, str) or not x for x in scope):
            return {**base, "status": "BLOCKED", "executor": policy["execution"]["code_executor_name"], "reason": "CODE_WRITE_SCOPE_REQUIRED"}
        if runtime["codex_available"] is not True:
            return {**base, "status": "WAITING_FOR_CAPABILITY", "executor": policy["execution"]["code_executor_name"], "reason": "CODEX_RUNTIME_UNAVAILABLE"}
        return {
            **base,
            "status": "READY",
            "executor": policy["execution"]["code_executor_name"],
            "runtime_confirmed": True,
            "automatic_merge": False,
        }
    selected = _select_api_model(policy, runtime, unit)
    if selected is None:
        return {**base, "status": "WAITING_FOR_CAPABILITY", "executor": policy["execution"]["api_executor_name"], "reason": "NO_VERIFIED_MODEL_SATISFIES_PROFILE"}
    routed = {**base, "status": "READY", **selected}
    if unit.get("independent_review_required"):
        review_unit = {
            **unit,
            "required_capabilities": sorted(set(unit.get("review_capabilities") or policy["review"]["minimum_capabilities"])),
            "complexity": unit.get("review_complexity", unit.get("complexity", "DIFFICULT")),
            "reasoning_effort": unit.get("review_reasoning_effort", unit.get("reasoning_effort", "high")),
            "requires_astra": bool(unit.get("review_requires_astra", False)),
        }
        review = _select_api_model(policy, runtime, review_unit, exclude={selected["model"]} if policy["review"].get("prefer_different_model_from_worker") else set())
        if review is None:
            return {**routed, "status": "WAITING_FOR_CAPABILITY", "reason": "INDEPENDENT_REVIEW_MODEL_UNAVAILABLE", "review": None}
        routed["review"] = {**review, "read_only": True}
    return routed


def build_execution_plan(policy: dict[str, Any], runtime: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    validate_policy(policy)
    validate_runtime(runtime)
    validate_profile(profile)
    routes = [route_unit(policy, runtime, unit) for unit in profile["units"]]
    parent = None
    parent_profile = profile.get("parent")
    if parent_profile is not None:
        if not isinstance(parent_profile, dict):
            raise ValueError("invalid_parent_profile")
        parent_unit = {
            "unit_id": "__parent__",
            "executor_class": "MODEL",
            "write_required": False,
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
    parallel_ready = min(sum(1 for r in routes if r["status"] == "READY"), max_parallel)
    return {
        "contract": "CAPABILITY_EXECUTION_PLAN_v1",
        "status": status,
        "profile_task": profile.get("task_name"),
        "policy_sha256": sha256_json(policy),
        "runtime_capabilities_sha256": sha256_json(runtime),
        "parent": parent,
        "units": routes,
        "parallel_ready_units": parallel_ready,
        "max_parallel_units": max_parallel,
        "routing_rule": "DETERMINISTIC_FIRST_THEN_CHEAPEST_VERIFIED_QUALIFIED_EXECUTOR",
        "automatic_merge": False,
        "authority": {
            "creates_truth": False,
            "framework_state_change": False,
            "market_rule_change": False,
            "threshold_change": False,
            "weight_change": False,
            "portfolio_action": False,
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
        "codex_available": bool(codex_available),
        "deterministic_available": True,
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
