from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

# Support both module import and direct CLI execution from the repository root.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.api_agent import api_gateway
from scripts.api_agent.capability_router import (
    build_execution_plan,
    canonical_bytes,
    estimate_model_cost,
    load_json,
    sha256_json,
)


POLICY_DEFAULT = Path("research/api_agent/CAPABILITY_ROUTING_POLICY_v1.json")


def _matching_unit(plan: dict[str, Any], task: str) -> dict[str, Any]:
    matches = [
        unit
        for unit in plan.get("units", [])
        if isinstance(unit, dict) and unit.get("source_task") == task
    ]
    if len(matches) != 1:
        raise ValueError(f"routing_plan_requires_exactly_one_matching_unit:{task}:{len(matches)}")
    return matches[0]


def select_execution(
    *,
    task: str,
    task_cfg: dict[str, Any],
    policy: dict[str, Any],
    runtime: dict[str, Any],
    profile: dict[str, Any],
    activate_routing: bool,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    plan = build_execution_plan(policy, runtime, profile)
    if plan.get("status") != "READY":
        raise ValueError(f"routing_plan_not_ready:{plan.get('status')}")
    unit = _matching_unit(plan, task)
    if unit.get("status") != "READY" or unit.get("executor") != policy["execution"]["api_executor_name"]:
        raise ValueError(f"task_not_routable_to_api:{task}:{unit.get('status')}:{unit.get('executor')}")
    if unit.get("write_required") is not False:
        raise ValueError("api_route_cannot_require_repository_write")
    if unit.get("runtime_confirmed") is not True:
        raise ValueError("selected_model_runtime_not_confirmed")

    baseline = {
        "model": task_cfg["model"],
        "reasoning_effort": task_cfg["reasoning_effort"],
    }
    recommended = {
        "model": unit["model"],
        "reasoning_effort": unit["reasoning_effort"],
    }
    effective = dict(baseline)
    mode = "SHADOW_RECOMMENDATION"

    if activate_routing:
        if policy.get("status") != "ACTIVE_QUALIFIED":
            raise ValueError("routing_policy_not_qualified")
        if policy.get("production_activation") != "EXPLICIT_RUNTIME_FLAG_AFTER_QUALIFICATION":
            raise ValueError("policy_does_not_allow_runtime_activation")
        qualified_models = runtime.get("qualified_models")
        if not isinstance(qualified_models, list) or recommended["model"] not in qualified_models:
            raise ValueError(f"selected_model_not_qualified:{recommended['model']}")
        if recommended["model"] not in policy.get("models", {}):
            raise ValueError("selected_model_not_in_policy")
        effective = dict(recommended)
        mode = "QUALIFIED_OVERRIDE"

    routing_receipt = {
        "contract": "CAPABILITY_ROUTING_RECEIPT_v1",
        "task": task,
        "mode": mode,
        "baseline": baseline,
        "recommended": recommended,
        "effective": effective,
        "plan_sha256": sha256_json(plan),
        "policy_sha256": sha256_json(policy),
        "runtime_capabilities_sha256": sha256_json(runtime),
        "profile_sha256": sha256_json(profile),
        "runtime_confirmed": True,
        "router_grants_write_authority": False,
        "automatic_merge": False,
        "repository_write_authority": False,
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
    return effective, plan, routing_receipt


def run_gateway_with_effective_registry(
    *,
    task: str,
    registry: dict[str, Any],
    effective: dict[str, Any],
    policy: dict[str, Any],
    prompt_file: Path,
    context_file: Path,
    output_dir: Path,
    intended_write_prefix: str,
    dry_run: bool,
) -> None:
    routed_registry = deepcopy(registry)
    task_cfg = routed_registry["tasks"][task]
    task_cfg["model"] = effective["model"]
    task_cfg["reasoning_effort"] = effective["reasoning_effort"]

    model_cfg = policy.get("models", {}).get(effective["model"])
    if not isinstance(model_cfg, dict) or not isinstance(model_cfg.get("price_per_million"), dict):
        raise ValueError(f"routing_price_missing:{effective['model']}")

    output_dir.mkdir(parents=True, exist_ok=True)
    temp_registry = output_dir / ".capability_routed_registry.tmp.json"
    temp_registry.write_bytes(canonical_bytes(routed_registry))

    argv = [
        "api_gateway.py",
        "--task",
        task,
        "--registry",
        str(temp_registry),
        "--prompt-file",
        str(prompt_file),
        "--context-file",
        str(context_file),
        "--output-dir",
        str(output_dir),
        "--intended-write-prefix",
        intended_write_prefix,
    ]
    if dry_run:
        argv.append("--dry-run")

    model_id = effective["model"]
    old_argv = sys.argv
    old_estimate_cost = api_gateway.estimate_cost
    old_price = api_gateway.PRICES_PER_MILLION.get(model_id)

    def routed_estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
        cfg = policy.get("models", {}).get(model)
        if isinstance(cfg, dict):
            return estimate_model_cost(policy, cfg, input_tokens, output_tokens)
        return old_estimate_cost(model, input_tokens, output_tokens)

    api_gateway.PRICES_PER_MILLION[model_id] = {
        "input": float(model_cfg["price_per_million"]["input"]),
        "output": float(model_cfg["price_per_million"]["output"]),
    }
    api_gateway.estimate_cost = routed_estimate_cost
    try:
        sys.argv = argv
        api_gateway.main()
    finally:
        sys.argv = old_argv
        api_gateway.estimate_cost = old_estimate_cost
        if old_price is None:
            api_gateway.PRICES_PER_MILLION.pop(model_id, None)
        else:
            api_gateway.PRICES_PER_MILLION[model_id] = old_price
        if temp_registry.exists():
            temp_registry.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Capability-routing adapter for the existing API Gateway. It never grants repository or framework authority."
    )
    parser.add_argument("--task", required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--policy", type=Path, default=POLICY_DEFAULT)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--runtime-capabilities", type=Path, required=True)
    parser.add_argument("--prompt-file", type=Path, required=True)
    parser.add_argument("--context-file", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--intended-write-prefix", required=True)
    parser.add_argument("--activate-routing", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    registry = api_gateway.load_registry(args.registry)
    task_cfg = registry["tasks"].get(args.task)
    if not task_cfg:
        raise SystemExit("unknown_task")
    policy = load_json(args.policy)
    runtime = load_json(args.runtime_capabilities)
    profile = load_json(args.profile)

    effective, plan, routing_receipt = select_execution(
        task=args.task,
        task_cfg=task_cfg,
        policy=policy,
        runtime=runtime,
        profile=profile,
        activate_routing=args.activate_routing,
    )

    run_gateway_with_effective_registry(
        task=args.task,
        registry=registry,
        effective=effective,
        policy=policy,
        prompt_file=args.prompt_file,
        context_file=args.context_file,
        output_dir=args.output_dir,
        intended_write_prefix=args.intended_write_prefix,
        dry_run=args.dry_run,
    )

    gateway_receipt_path = args.output_dir / "receipt.json"
    if not gateway_receipt_path.exists():
        raise SystemExit("api_gateway_receipt_missing")
    gateway_receipt = json.loads(gateway_receipt_path.read_text())
    if gateway_receipt.get("model") != effective["model"]:
        raise SystemExit("effective_model_readback_mismatch")
    if gateway_receipt.get("reasoning_effort") != effective["reasoning_effort"]:
        raise SystemExit("effective_reasoning_readback_mismatch")

    routing_receipt["gateway_receipt_sha256"] = sha256_json(gateway_receipt)
    routing_receipt["gateway_status"] = gateway_receipt.get("status")
    routing_receipt["gateway_estimated_cost_usd"] = gateway_receipt.get("estimated_cost_usd")
    (args.output_dir / "routing_receipt.json").write_bytes(canonical_bytes(routing_receipt))
    print(json.dumps({"routing": routing_receipt, "plan": plan}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
