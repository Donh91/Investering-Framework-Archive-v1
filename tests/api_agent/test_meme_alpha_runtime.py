from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.api_agent.meme_alpha_runtime import analyze, build_plan, load_object, validate_output


POLICY = {
    "contract": "MEME_ALPHA_RUNTIME_POLICY_v1",
    "queue": {
        "intake_roots": ["private_research/memes_alpha/research_leads", "private_research/memes_alpha/cases"],
        "eligible_status_tokens": ["QUEUED", "READY", "WATCH", "QUEUED_FOR_INDEPENDENT_REPLAY"],
        "terminal_states": ["COMPLETE", "KILLED", "SUPERSEDED"],
    },
    "model_policy": {"default_model": "gpt-5.6-luna", "default_reasoning_effort": "medium"},
    "budget": {"single_task_hard_cap_usd": 0.75},
    "authority": {
        "portfolio_action": False,
        "automatic_trading": False,
        "canonical_promotion": False,
        "framework_state_change": False,
        "market_rule_change": False,
        "model_weight_change": False,
        "automatic_merge": False,
    },
}


class MemeAlphaRuntimeTests(unittest.TestCase):
    def write_json(self, root: Path, rel: str, value: dict) -> Path:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, sort_keys=True) + "\n")
        return path

    def test_plan_prefers_high_priority_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            low = self.write_json(root, "private_research/memes_alpha/cases/a.json", {"status": "WATCH", "priority": "P2"})
            high = self.write_json(root, "private_research/memes_alpha/research_leads/b.json", {"status": "QUEUED_FOR_INDEPENDENT_REPLAY", "priority": "P0"})
            plan = build_plan(root, POLICY, {"processed_inputs": {}})
            self.assertFalse(plan["no_op"])
            self.assertEqual(plan["selected"]["path"], high.relative_to(root).as_posix())
            processed = {plan["selected"]["path"]: plan["selected"]["input_sha256"]}
            plan2 = build_plan(root, POLICY, {"processed_inputs": processed})
            self.assertEqual(plan2["selected"]["path"], low.relative_to(root).as_posix())
            processed[plan2["selected"]["path"]] = plan2["selected"]["input_sha256"]
            plan3 = build_plan(root, POLICY, {"processed_inputs": processed})
            self.assertTrue(plan3["no_op"])

    def test_changed_source_becomes_eligible_again(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = self.write_json(root, "private_research/memes_alpha/research_leads/a.json", {"status": "QUEUED", "priority": "P1", "v": 1})
            plan = build_plan(root, POLICY, {"processed_inputs": {}})
            processed = {plan["selected"]["path"]: plan["selected"]["input_sha256"]}
            path.write_text(json.dumps({"status": "QUEUED", "priority": "P1", "v": 2}) + "\n")
            plan2 = build_plan(root, POLICY, {"processed_inputs": processed})
            self.assertFalse(plan2["no_op"])
            self.assertNotEqual(plan2["selected"]["input_sha256"], processed[plan2["selected"]["path"]])

    def test_terminal_item_is_not_selected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_json(root, "private_research/memes_alpha/research_leads/a.json", {"status": "COMPLETE", "priority": "P0"})
            plan = build_plan(root, POLICY, {"processed_inputs": {}})
            self.assertTrue(plan["no_op"])

    def test_dry_run_writes_bounded_receipt_without_api_key(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            task = self.write_json(root, "task.json", {"status": "QUEUED", "subject": "wallet provenance"})
            policy_path = self.write_json(root, "policy.json", POLICY)
            out = root / "out"
            receipt = analyze(task, load_object(policy_path), out, dry_run=True, enable_web=True, model=None)
            self.assertEqual(receipt["response_id"], "dry-run")
            self.assertEqual(receipt["estimated_model_cost_usd"], 0.0)
            self.assertFalse(receipt["authority"]["portfolio_action"])
            self.assertTrue((out / "output.json").exists())
            self.assertTrue((out / "receipt.json").exists())

    def test_forbidden_authority_output_is_rejected(self) -> None:
        value = {
            "status": "READY", "task_id": "x", "summary": "x", "verified_findings": [],
            "disconfirming_evidence": [], "uncertainties": [], "wallet_candidates": [],
            "network_connections": [], "next_research_steps": [], "development_candidates": [],
            "source_urls": [], "priority_after_run": "LOW", "buy": "yes",
        }
        with self.assertRaises(ValueError):
            validate_output(value)


if __name__ == "__main__":
    unittest.main()
