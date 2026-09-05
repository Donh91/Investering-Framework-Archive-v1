import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from scripts.api_agent import api_gateway
from scripts.api_agent.capability_router import build_execution_plan, estimate_model_cost, load_json
from scripts.api_agent.capability_routed_api_gateway import run_gateway_with_effective_registry, select_execution


POLICY = Path("research/api_agent/CAPABILITY_ROUTING_POLICY_v1.json")
REGISTRY = Path("research/api_agent/API_TASK_REGISTRY_v1.json")


def runtime(*models, codex=False, qualified=None):
    return {
        "contract": "RUNTIME_CAPABILITIES_v1",
        "source": "TEST_FIXTURE",
        "available_models": list(models),
        "qualified_models": list(qualified or []),
        "codex_available": bool(codex),
        "deterministic_available": True,
    }


def profile(
    *,
    task="TEST_TASK",
    complexity="ROUTINE",
    capabilities=None,
    effort="low",
    executor_class="MODEL",
    write=False,
    scope=None,
    requires_astra=False,
    review=False,
):
    return {
        "contract": "CAPABILITY_TASK_PROFILE_v1",
        "task_name": task,
        "units": [
            {
                "unit_id": "u1",
                "source_task": task,
                "executor_class": executor_class,
                "complexity": complexity,
                "required_capabilities": capabilities or [],
                "reasoning_effort": effort,
                "estimated_input_tokens": 10000,
                "estimated_output_tokens": 1000,
                "write_required": write,
                "requested_write_scope": scope or [],
                "requires_astra": requires_astra,
                "independent_review_required": review,
            }
        ],
    }


class CapabilityRouterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = load_json(POLICY)

    def test_routine_uses_cheapest_available_model_for_shadow_recommendation(self):
        plan = build_execution_plan(
            self.policy,
            runtime("gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.6-sol"),
            profile(capabilities=["structured_output"]),
        )
        self.assertEqual(plan["status"], "READY")
        self.assertEqual(plan["units"][0]["model"], "gpt-5.6-luna")

    def test_synthesis_routes_to_terra_not_sol(self):
        plan = build_execution_plan(
            self.policy,
            runtime("gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.6-sol"),
            profile(complexity="SYNTHESIS", capabilities=["synthesis"], effort="medium"),
        )
        self.assertEqual(plan["units"][0]["model"], "gpt-5.6-terra")

    def test_difficult_reasoning_routes_to_sol_when_astra_not_required(self):
        plan = build_execution_plan(
            self.policy,
            runtime("gpt-5.6-sol", "gpt-6-astra"),
            profile(complexity="DIFFICULT", capabilities=["difficult_reasoning"], effort="high"),
        )
        self.assertEqual(plan["units"][0]["model"], "gpt-5.6-sol")

    def test_required_astra_fails_closed_when_runtime_does_not_have_it(self):
        plan = build_execution_plan(
            self.policy,
            runtime("gpt-5.6-sol"),
            profile(complexity="ARCHITECTURE", capabilities=["architecture"], effort="high", requires_astra=True),
        )
        self.assertEqual(plan["status"], "WAITING_FOR_CAPABILITY")
        self.assertEqual(plan["units"][0]["reason"], "NO_VERIFIED_MODEL_SATISFIES_PROFILE")

    def test_required_astra_routes_only_when_runtime_confirms_it(self):
        plan = build_execution_plan(
            self.policy,
            runtime("gpt-5.6-sol", "gpt-6-astra"),
            profile(complexity="ARCHITECTURE", capabilities=["architecture"], effort="xhigh", requires_astra=True),
        )
        self.assertEqual(plan["status"], "READY")
        self.assertEqual(plan["units"][0]["model"], "gpt-6-astra")
        self.assertTrue(plan["units"][0]["runtime_confirmed"])

    def test_repository_write_is_codex_only_and_router_grants_no_authority(self):
        p = profile(executor_class="CODE", write=True, scope=["scripts/example.py"])
        waiting = build_execution_plan(self.policy, runtime("gpt-6-astra", codex=False), p)
        self.assertEqual(waiting["status"], "WAITING_FOR_CAPABILITY")
        self.assertEqual(waiting["units"][0]["executor"], "CODEX")
        ready = build_execution_plan(self.policy, runtime("gpt-6-astra", codex=True), p)
        route = ready["units"][0]
        self.assertEqual(ready["status"], "READY")
        self.assertEqual(route["executor"], "CODEX")
        self.assertEqual(route["requested_write_scope"], ["scripts/example.py"])
        self.assertFalse(route["router_grants_write_authority"])
        self.assertEqual(route["write_authority_source"], "EXISTING_CODEX_TASK_CONTRACT_REQUIRED")
        self.assertEqual(route["review_owner"], "EXISTING_PR_REVIEW_GOVERNANCE")
        self.assertTrue(route["independent_review_required"])
        self.assertFalse(route["automatic_merge"])

    def test_model_unit_cannot_request_repository_write(self):
        p = profile(write=True, scope=["x"])
        with self.assertRaisesRegex(ValueError, "write_requires_code_executor"):
            build_execution_plan(self.policy, runtime("gpt-5.6-luna"), p)

    def test_model_unit_cannot_carry_requested_write_scope_without_code_executor(self):
        p = profile(scope=["x"])
        with self.assertRaisesRegex(ValueError, "write_scope_requires_code_executor"):
            build_execution_plan(self.policy, runtime("gpt-5.6-luna"), p)

    def test_independent_review_uses_different_model_when_available(self):
        plan = build_execution_plan(
            self.policy,
            runtime("gpt-5.6-sol", "gpt-6-astra"),
            profile(complexity="DIFFICULT", capabilities=["difficult_reasoning"], effort="high", review=True),
        )
        route = plan["units"][0]
        self.assertEqual(route["model"], "gpt-5.6-sol")
        self.assertEqual(route["review"]["model"], "gpt-6-astra")
        self.assertTrue(route["review"]["read_only"])
        self.assertFalse(route["review"]["repository_write_authority"])

    def test_plan_never_grants_framework_or_merge_authority(self):
        plan = build_execution_plan(self.policy, runtime("gpt-5.6-luna"), profile())
        self.assertFalse(plan["automatic_merge"])
        self.assertFalse(plan["router_grants_write_authority"])
        self.assertTrue(all(value is False for value in plan["authority"].values()))

    def test_cost_snapshot_uses_current_luna_rate_below_long_context_threshold(self):
        luna = self.policy["models"]["gpt-5.6-luna"]
        self.assertEqual(estimate_model_cost(self.policy, luna, 100_000, 100_000), 0.14)

    def test_long_context_cost_multiplier_is_applied(self):
        astra = self.policy["models"]["gpt-6-astra"]
        self.assertEqual(estimate_model_cost(self.policy, astra, 300_000, 10_000), 6.75)

    def test_gateway_shadow_route_does_not_change_baseline_model(self):
        registry = api_gateway.load_registry(REGISTRY)
        task = "DAILY_CONFLICT_REVIEW"
        effective, _, receipt = select_execution(
            task=task,
            task_cfg=registry["tasks"][task],
            policy=self.policy,
            runtime=runtime("gpt-5.6-luna", "gpt-5.6-terra", qualified=["gpt-5.6-luna"]),
            profile=profile(task=task, capabilities=["structured_output"], effort="low"),
            activate_routing=False,
        )
        self.assertEqual(receipt["recommended"]["model"], "gpt-5.6-luna")
        self.assertEqual(effective["model"], "gpt-5.6-terra")
        self.assertEqual(receipt["mode"], "SHADOW_RECOMMENDATION")
        self.assertEqual(receipt["selection_pool"], "AVAILABLE_MODELS_SHADOW")

    def test_shadow_policy_blocks_live_override_even_if_runtime_model_is_qualified(self):
        registry = api_gateway.load_registry(REGISTRY)
        task = "DAILY_CONFLICT_REVIEW"
        with self.assertRaisesRegex(ValueError, "routing_policy_not_qualified"):
            select_execution(
                task=task,
                task_cfg=registry["tasks"][task],
                policy=self.policy,
                runtime=runtime("gpt-5.6-luna", "gpt-5.6-terra", qualified=["gpt-5.6-luna"]),
                profile=profile(task=task, capabilities=["structured_output"], effort="low"),
                activate_routing=True,
            )

    def test_gateway_activation_requires_nonempty_runtime_qualification_after_policy_qualification(self):
        registry = api_gateway.load_registry(REGISTRY)
        task = "DAILY_CONFLICT_REVIEW"
        p = profile(task=task, capabilities=["structured_output"], effort="low")
        qualified_policy = deepcopy(self.policy)
        qualified_policy["status"] = "ACTIVE_QUALIFIED"
        with self.assertRaisesRegex(ValueError, "no_runtime_qualified_models"):
            select_execution(
                task=task,
                task_cfg=registry["tasks"][task],
                policy=qualified_policy,
                runtime=runtime("gpt-5.6-luna", "gpt-5.6-terra"),
                profile=p,
                activate_routing=True,
            )
        effective, _, receipt = select_execution(
            task=task,
            task_cfg=registry["tasks"][task],
            policy=qualified_policy,
            runtime=runtime("gpt-5.6-luna", "gpt-5.6-terra", qualified=["gpt-5.6-luna"]),
            profile=p,
            activate_routing=True,
        )
        self.assertEqual(effective["model"], "gpt-5.6-luna")
        self.assertEqual(receipt["mode"], "QUALIFIED_OVERRIDE")
        self.assertEqual(receipt["selection_pool"], "QUALIFIED_MODELS_ONLY")

    def test_live_routing_selects_cheapest_qualified_not_cheapest_merely_available(self):
        registry = api_gateway.load_registry(REGISTRY)
        task = "DAILY_CONFLICT_REVIEW"
        qualified_policy = deepcopy(self.policy)
        qualified_policy["status"] = "ACTIVE_QUALIFIED"
        effective, _, receipt = select_execution(
            task=task,
            task_cfg=registry["tasks"][task],
            policy=qualified_policy,
            runtime=runtime("gpt-5.6-luna", "gpt-5.6-terra", qualified=["gpt-5.6-terra"]),
            profile=profile(task=task, complexity="SYNTHESIS", capabilities=["synthesis"], effort="medium"),
            activate_routing=True,
        )
        self.assertEqual(effective["model"], "gpt-5.6-terra")
        self.assertEqual(receipt["recommended"]["model"], "gpt-5.6-terra")
        self.assertEqual(receipt["selection_pool"], "QUALIFIED_MODELS_ONLY")

    def test_routed_adapter_still_uses_existing_gateway_and_receipt_contract(self):
        registry = api_gateway.load_registry(REGISTRY)
        task = "DAILY_CONFLICT_REVIEW"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            prompt_file = root / "prompt.txt"
            context_file = root / "context.json"
            output_dir = root / "out"
            prompt_file.write_text("test")
            context_file.write_text("{}")
            original_price = dict(api_gateway.PRICES_PER_MILLION["gpt-5.6-luna"])
            original_estimator = api_gateway.estimate_cost
            run_gateway_with_effective_registry(
                task=task,
                registry=registry,
                effective={"model": "gpt-5.6-luna", "reasoning_effort": "low"},
                policy=self.policy,
                prompt_file=prompt_file,
                context_file=context_file,
                output_dir=output_dir,
                intended_write_prefix=registry["tasks"][task]["allowed_write_prefix"],
                dry_run=True,
            )
            receipt = json.loads((output_dir / "receipt.json").read_text())
            self.assertEqual(receipt["contract"], "API_AGENT_RECEIPT_v3")
            self.assertEqual(receipt["model"], "gpt-5.6-luna")
            self.assertEqual(api_gateway.PRICES_PER_MILLION["gpt-5.6-luna"], original_price)
            self.assertIs(api_gateway.estimate_cost, original_estimator)
            self.assertFalse((output_dir / ".capability_routed_registry.tmp.json").exists())


if __name__ == "__main__":
    unittest.main()
