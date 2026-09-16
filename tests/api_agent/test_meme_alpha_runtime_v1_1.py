from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.api_agent.meme_alpha_runtime_v1_1 import analyze


POLICY = {
    "contract": "MEME_ALPHA_RUNTIME_POLICY_v1",
    "model_policy": {
        "default_model": "gpt-5.6-luna",
        "default_reasoning_effort": "medium",
        "max_output_tokens": 3600,
    },
    "budget": {
        "single_task_hard_cap_usd": 0.75,
        "max_web_search_calls_per_task": 4,
        "provider_web_search_overrun_tolerance": 1,
        "web_search_tool_call_cost_usd_snapshot": 0.01,
    },
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


def valid_output() -> dict:
    return {
        "status": "DEGRADED",
        "task_id": "model-task-id",
        "summary": "bounded research result",
        "verified_findings": [],
        "disconfirming_evidence": [],
        "uncertainties": [],
        "wallet_candidates": [],
        "network_connections": [],
        "next_research_steps": [],
        "development_candidates": [],
        "source_urls": [],
        "priority_after_run": "HIGH",
    }


def response_with_web_calls(count: int) -> dict:
    output = [
        {
            "type": "web_search_call",
            "action": {"query": f"bounded query {idx}", "sources": []},
        }
        for idx in range(count)
    ]
    output.append({"type": "message", "content": [{"type": "output_text", "text": json.dumps(valid_output())}]})
    return {
        "id": "resp-test",
        "model": "gpt-5.6-luna-2026-09-14",
        "status": "completed",
        "usage": {"input_tokens": 1000, "output_tokens": 500},
        "output": output,
    }


class MemeAlphaRuntimeV11Tests(unittest.TestCase):
    def run_analyze(self, web_calls: int):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            task = root / "task.json"
            task.write_text(json.dumps({
                "status": "QUEUED",
                "subject": "test",
                "method_version": "1.1-scientific-hardening",
                "method_sha256": "a" * 64,
            }) + "\n")
            out = root / "out"
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
                with patch("scripts.api_agent.meme_alpha_runtime_v1_1.base.call_api", return_value=response_with_web_calls(web_calls)):
                    receipt = analyze(task, POLICY, out, dry_run=False, enable_web=True, model=None)
                    persisted = json.loads((out / "output.json").read_text())
                    queries = json.loads((out / "web_queries.json").read_text())
                    sources = json.loads((out / "web_sources.json").read_text())
                    return receipt, persisted, queries, sources

    def test_one_provider_call_overshoot_is_accepted_costed_and_recorded(self) -> None:
        receipt, output, _, _ = self.run_analyze(5)
        self.assertEqual(receipt["web_search_call_limit_requested"], 4)
        self.assertEqual(receipt["web_search_call_count"], 5)
        self.assertEqual(receipt["web_search_call_overrun"], 1)
        self.assertEqual(receipt["estimated_web_tool_cost_usd"], 0.05)
        self.assertTrue(any("provider overrun" in item for item in output["uncertainties"]))

    def test_more_than_one_provider_call_overshoot_remains_fatal(self) -> None:
        with self.assertRaisesRegex(SystemExit, "web_search_call_limit_exceeded:6"):
            self.run_analyze(6)

    def test_receipt_freezes_required_runtime_lineage(self) -> None:
        receipt, _, queries, sources = self.run_analyze(2)
        for key in (
            "input_sha256",
            "output_sha256",
            "policy_sha256",
            "prompt_sha256",
            "query_manifest_sha256",
            "retrieval_manifest_sha256",
        ):
            self.assertEqual(len(receipt[key]), 64)
        self.assertEqual(receipt["method_version"], "1.1-scientific-hardening")
        self.assertEqual(receipt["method_sha256"], "a" * 64)
        self.assertEqual(receipt["model"], "gpt-5.6-luna")
        self.assertEqual(receipt["model_snapshot_or_version"], "gpt-5.6-luna-2026-09-14")
        self.assertEqual(receipt["web_query_count"], 2)
        self.assertEqual(queries["queries"], ["bounded query 0", "bounded query 1"])
        self.assertEqual(sources["urls"], [])


if __name__ == "__main__":
    unittest.main()
