import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from scripts.api_agent import api_gateway
from scripts.api_agent.capability_router import build_execution_plan, estimate_model_cost, load_json
from scripts.api_agent.capability_routed_api_gateway import (
    _bind_delegation_execution,
    run_gateway_with_effective_registry,
    select_execution,
)


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
    hardened=False,
    task_id="TEST-TASK-1",
    parent_task_id=None,
    delegation_depth=0,
    responsibility_scope="test.scope",
    context_refs=None,
    allowed_tools=None,
    max_cost=10.0,
    failure_mode="FAIL_CLOSED",
    escalation_rule=None,
):
    unit = {
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
    value = {
        "contract": "CAPABILITY_TASK_PROFILE_v1_1" if hardened else "CAPABILITY_TASK_PROFILE_v1",
        "task_name": task,
        "units": [unit],
    }
    if hardened:
        binding = {
            "MODEL": "OPENAI_RESPONSES_API",
            "CODE": "CODEX",
            "DETERMINISTIC": "DETERMINISTIC",
        }[executor_class]
        unit.update(
            {
                "responsibility_owner": "TEST_OWNER",
                "responsibility_scope": responsibility_scope,
                "expected_output": "Produce the declared bounded test result.",
                "verification_method": {
                    "type": "SCHEMA_VALIDATION",
                    "success_criteria": ["Output passes the declared schema and receipt checks."],
                },
                "allowed_context": list(context_refs if context_refs is not None else ["ctx:test"]),
                "allowed_tools": list(allowed_tools if allowed_tools is not None else [binding]),
                "authority_scope": {
                    "repository_write_requested": bool(write),
                    "portfolio_action": False,
                    "trade_action": False,
                    "framework_state_change": False,
                    "market_rule_change": False,
                    "threshold_change": False,
                    "weight_change": False,
                    "canonical_promotion": False,
                    "automatic_merge": False,
                },
                "budget": {
                    "max_estimated_cost_usd": max_cost,
                    "max_input_tokens": 20000,
                    "max_output_tokens": 5000,
                },
                "failure_mode": failure_mode,
                "escalation_rule": escalation_rule or {
                    "mode": "STOP",
                    "target": None,
                    "max_redelegations": 0,
                },
            }
        )
        value.update(
            {
                "task_id": task_id,
                "parent_task_id": parent_task_id,
                "delegator": "ASTRA_PARENT",
                "delegation_depth": delegation_depth,
            }
        )
    return value


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

    def test_legacy_profile_remains_shadow_compatible_but_marked_unhardened(self):
        plan = build_execution_plan(self.policy, runtime("gpt-5.6-luna"), profile())
        self.assertEqual(plan["status"], "READY")
        self.assertEqual(plan["delegation_contract_status"], "LEGACY_UNHARDENED")
        self.assertEqual(plan["units"][0]["delegation_contract_status"], "LEGACY_UNHARDENED")

    def test_hardened_plan_emits_explicit_responsibility_and_lineage_hash(self):
        plan = build_execution_plan(
            self.policy,
            runtime("gpt-5.6-luna"),
            profile(hardened=True, capabilities=["structured_output"]),
        )
        route = plan["units"][0]
        self.assertEqual(plan["delegation_contract_status"], "HARDENED_V1_1")
        self.assertEqual(route["responsibility_owner"], "TEST_OWNER")
        self.assertEqual(route["responsibility_scope"], "test.scope")
        self.assertEqual(len(route["delegation_input_sha256"]), 64)
        self.assertEqual(route["allowed_context"], ["ctx:test"])
        self.assertEqual(route["allowed_tools"], ["OPENAI_RESPONSES_API"])
        self.assertEqual(route["redelegation_remaining"], 0)

    def test_hardened_profile_fails_closed_without_verification_contract(self):
        p = profile(hardened=True)
        del p["units"][0]["verification_method"]
        with self.assertRaisesRegex(ValueError, "verification_method_required"):
            build_execution_plan(self.policy, runtime("gpt-5.6-luna"), p)

    def test_hardened_profile_rejects_duplicate_responsibility_scope(self):
        p = profile(hardened=True)
        second = deepcopy(p["units"][0])
        second["unit_id"] = "u2"
        p["units"].append(second)
        with self.assertRaisesRegex(ValueError, "duplicate_responsibility_scope"):
            build_execution_plan(self.policy, runtime("gpt-5.6-luna"), p)

    def test_hardened_profile_rejects_unbounded_context(self):
        p = profile(hardened=True, context_refs=["*"])
        with self.assertRaisesRegex(ValueError, "unbounded_context_forbidden"):
            build_execution_plan(self.policy, runtime("gpt-5.6-luna"), p)

    def test_hardened_profile_rejects_unbounded_tool_scope(self):
        p = profile(hardened=True, allowed_tools=["OPENAI_RESPONSES_API", "ALL_TOOLS"])
        with self.assertRaisesRegex(ValueError, "unbounded_tool_scope_forbidden"):
            build_execution_plan(self.policy, runtime("gpt-5.6-luna"), p)

    def test_hardened_profile_rejects_depth_above_policy_limit(self):
        p = profile(hardened=True, delegation_depth=3, parent_task_id="PARENT")
        with self.assertRaisesRegex(ValueError, "invalid_delegation_depth"):
            build_execution_plan(self.policy, runtime("gpt-5.6-luna"), p)

    def test_redelegation_is_one_hop_and_cannot_start_at_depth_ceiling(self):
        escalation = {"mode": "REDELEGATE_ONCE", "target": "CAPABILITY_ROUTER", "max_redelegations": 1}
        ready = build_execution_plan(
            self.policy,
            runtime("gpt-5.6-luna"),
            profile(
                hardened=True,
                delegation_depth=1,
                parent_task_id="PARENT",
                failure_mode="REDELEGATE_ONCE_THEN_ESCALATE",
                escalation_rule=escalation,
            ),
        )
        self.assertEqual(ready["units"][0]["redelegation_remaining"], 1)
        p = profile(
            hardened=True,
            delegation_depth=2,
            parent_task_id="PARENT",
            failure_mode="REDELEGATE_ONCE_THEN_ESCALATE",
            escalation_rule=escalation,
        )
        with self.assertRaisesRegex(ValueError, "redelegation_depth_exhausted"):
            build_execution_plan(self.policy, runtime("gpt-5.6-luna"), p)

    def test_hardened_route_blocks_when_estimated_model_cost_exceeds_unit_budget(self):
        plan = build_execution_plan(
            self.policy,
            runtime("gpt-5.6-sol"),
            profile(
                hardened=True,
                complexity="DIFFICULT",
                capabilities=["difficult_reasoning"],
                effort="high",
                max_cost=0.000001,
            ),
        )
        self.assertEqual(plan["status"], "BLOCKED")
        self.assertEqual(plan["units"][0]["reason"], "UNIT_COST_BUDGET_EXCEEDED")

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
        self.assertIsNone(receipt["delegation_lineage"])

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

    def test_live_routing_rejects_legacy_profile_even_after_policy_qualification(self):
        registry = api_gateway.load_registry(REGISTRY)
        task = "DAILY_CONFLICT_REVIEW"
        qualified_policy = deepcopy(self.policy)
        qualified_policy["status"] = "ACTIVE_QUALIFIED"
        with self.assertRaisesRegex(ValueError, "hardened_delegation_profile_required_for_live_routing"):
            select_execution(
                task=task,
                task_cfg=registry["tasks"][task],
                policy=qualified_policy,
                runtime=runtime("gpt-5.6-luna", "gpt-5.6-terra", qualified=["gpt-5.6-luna"]),
                profile=profile(task=task, capabilities=["structured_output"], effort="low"),
                activate_routing=True,
            )

    def test_gateway_activation_requires_nonempty_runtime_qualification_after_policy_qualification(self):
        registry = api_gateway.load_registry(REGISTRY)
        task = "DAILY_CONFLICT_REVIEW"
        p = profile(task=task, capabilities=["structured_output"], effort="low", hardened=True)
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
        self.assertEqual(receipt["delegation_contract_status"], "HARDENED_V1_1")
        self.assertEqual(receipt["delegation_lineage"]["responsibility_scope"], "test.scope")

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
            profile=profile(task=task, complexity="SYNTHESIS", capabilities=["synthesis"], effort="medium", hardened=True),
            activate_routing=True,
        )
        self.assertEqual(effective["model"], "gpt-5.6-terra")
        self.assertEqual(receipt["recommended"]["model"], "gpt-5.6-terra")
        self.assertEqual(receipt["selection_pool"], "QUALIFIED_MODELS_ONLY")

    def test_hardened_context_attenuation_rejects_context_outside_allowlist(self):
        registry = api_gateway.load_registry(REGISTRY)
        task = "DAILY_CONFLICT_REVIEW"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            prompt_file = root / "prompt.txt"
            context_file = root / "context.json"
            output_dir = root / "out"
            prompt_file.write_text("test")
            context_file.write_text(json.dumps({"source_refs": ["ctx:extra"]}))
            with self.assertRaisesRegex(ValueError, "context_ref_not_allowed"):
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
                    allowed_context_refs=["ctx:test"],
                )

    def test_hardened_context_attenuation_binds_actual_context_hash(self):
        registry = api_gateway.load_registry(REGISTRY)
        task = "DAILY_CONFLICT_REVIEW"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            prompt_file = root / "prompt.txt"
            context_file = root / "context.json"
            output_dir = root / "out"
            prompt_file.write_text("test")
            context_file.write_text(json.dumps({"source_refs": ["ctx:test"], "payload": {"x": 1}}))
            binding = run_gateway_with_effective_registry(
                task=task,
                registry=registry,
                effective={"model": "gpt-5.6-luna", "reasoning_effort": "low"},
                policy=self.policy,
                prompt_file=prompt_file,
                context_file=context_file,
                output_dir=output_dir,
                intended_write_prefix=registry["tasks"][task]["allowed_write_prefix"],
                dry_run=True,
                allowed_context_refs=["ctx:test"],
            )
            self.assertEqual(binding["actual_context_refs"], ["ctx:test"])
            self.assertEqual(len(binding["actual_context_sha256"]), 64)

    def test_delegation_lineage_binds_output_and_verification_receipt(self):
        registry = api_gateway.load_registry(REGISTRY)
        task = "DAILY_CONFLICT_REVIEW"
        effective, plan, receipt = select_execution(
            task=task,
            task_cfg=registry["tasks"][task],
            policy=self.policy,
            runtime=runtime("gpt-5.6-luna", "gpt-5.6-terra"),
            profile=profile(task=task, capabilities=["structured_output"], effort="low", hardened=True),
            activate_routing=False,
        )
        self.assertEqual(effective["model"], registry["tasks"][task]["model"])
        self.assertEqual(plan["delegation_contract_status"], "HARDENED_V1_1")
        gateway_receipt = {
            "contract": "API_AGENT_RECEIPT_v3",
            "status": "PASS",
            "output_hash": "a" * 64,
            "context_hash": "b" * 64,
        }
        _bind_delegation_execution(
            receipt,
            gateway_receipt,
            {"actual_context_refs": ["ctx:test"], "actual_context_sha256": "c" * 64},
        )
        lineage = receipt["delegation_lineage"]
        self.assertEqual(lineage["execution_output_sha256"], "a" * 64)
        self.assertEqual(lineage["actual_context_refs"], ["ctx:test"])
        self.assertEqual(lineage["verification_status"], "VERIFIED_BY_EXECUTION_RECEIPT")
        self.assertEqual(len(lineage["verification_receipt_sha256"]), 64)

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
