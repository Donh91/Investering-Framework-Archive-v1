from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.api_agent.meme_alpha_runtime_v1_2 import analyze
from scripts.api_agent.meme_alpha_source_auth import (
    apply_source_authentication_gate,
    default_source_authentication,
    task_requires_source_authentication,
)


POLICY = {
    "contract": "MEME_ALPHA_RUNTIME_POLICY_v1",
    "queue": {"intake_roots": [], "eligible_status_tokens": [], "terminal_states": []},
    "model_policy": {
        "default_model": "gpt-5.6-luna",
        "default_reasoning_effort": "medium",
        "max_output_tokens": 3600,
    },
    "budget": {
        "single_task_hard_cap_usd": 0.75,
        "max_web_search_calls_per_task": 2,
        "provider_web_search_overrun_tolerance": 1,
        "web_search_tool_call_cost_usd_snapshot": 0.01,
    },
    "source_authentication": {
        "enabled": True,
        "minimum_external_trust_anchors": 2,
        "minimum_independent_anchor_categories": 2,
        "require_high_confidence_onchain_binding_for_token_ca_claim": True,
        "block_on_unresolved_red_team": True,
        "block_on_repo_forensics_blocker": True,
        "sanitize_unauthenticated_first_party_findings": True,
        "sanitize_unauthenticated_summary": True,
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


def base_output(packet: dict) -> dict:
    return {
        "status": "READY",
        "task_id": "MAL-test",
        "summary": "test",
        "verified_findings": [],
        "disconfirming_evidence": [],
        "uncertainties": [],
        "wallet_candidates": [],
        "network_connections": [],
        "next_research_steps": [],
        "development_candidates": [],
        "source_urls": [],
        "priority_after_run": "LOW",
        "source_authentication": packet,
    }


def anchor(category: str, locator: str) -> dict:
    return {
        "category": category,
        "locator": locator,
        "evidence": "project-controlled external link",
        "external_to_subject": True,
        "source_controlled": True,
        "independent": True,
    }


class MemeAlphaSourceAuthTests(unittest.TestCase):
    def test_github_or_verified_commit_alone_cannot_authenticate(self) -> None:
        packet = default_source_authentication()
        packet.update({
            "scope": "PROJECT_SOURCE",
            "state": "AUTHENTICATED_FIRST_PARTY",
            "claimed_entity": "Example Project",
            "subject": "github.com/example/project",
            "repository_forensics": [{"signal": "verified_commit", "severity": "INFO", "evidence": "GitHub signature valid"}],
        })
        output = base_output(packet)
        output["summary"] = "The official project repository passed authentication and proves the mascot is canonical."
        output["verified_findings"] = ["The official project repository proves the mascot is canonical."]
        result = apply_source_authentication_gate(output, {"subject": "official GitHub mascot provenance"}, POLICY)
        self.assertFalse(result["source_authentication"]["first_party_claim_allowed"])
        self.assertEqual(result["status"], "DEGRADED")
        self.assertEqual(result["verified_findings"], [])
        self.assertTrue(result["summary"].startswith("Source authentication did not admit first-party provenance"))
        self.assertNotIn("passed authentication", result["summary"])
        self.assertTrue(any(item.startswith("MODEL_SUMMARY_PRE_GATE_UNTRUSTED:") for item in result["uncertainties"]))
        self.assertTrue(any("AUTH_GATED" in item for item in result["uncertainties"]))

    def test_two_external_categories_can_authenticate_project_source(self) -> None:
        packet = default_source_authentication()
        packet.update({
            "scope": "PROJECT_SOURCE",
            "state": "AUTHENTICATED_FIRST_PARTY",
            "claimed_entity": "Example Project",
            "subject": "github.com/example/project",
            "external_trust_anchors": [
                anchor("OFFICIAL_WEBSITE", "https://example.org/developers"),
                anchor("OFFICIAL_SOCIAL", "https://x.com/example/status/1"),
            ],
            "red_team_findings": [{"hypothesis": "lookalike repo", "status": "CLEAR", "evidence": "official links converge"}],
        })
        output = base_output(packet)
        output["summary"] = "Authenticated summary remains intact."
        result = apply_source_authentication_gate(output, {"subject": "official repository provenance"}, POLICY)
        self.assertTrue(result["source_authentication"]["first_party_claim_allowed"])
        self.assertEqual(result["source_authentication"]["gate_reasons"], [])
        self.assertEqual(result["summary"], "Authenticated summary remains intact.")

    def test_token_ca_binding_requires_high_onchain_binding(self) -> None:
        packet = default_source_authentication()
        packet.update({
            "scope": "TOKEN_CA_BINDING",
            "state": "AUTHENTICATED_FIRST_PARTY",
            "claimed_entity": "Example Project",
            "subject": "token 0xabc",
            "external_trust_anchors": [
                anchor("OFFICIAL_WEBSITE", "https://example.org/token"),
                anchor("OFFICIAL_SOCIAL", "https://x.com/example/status/2"),
            ],
            "onchain_bindings": [{"relation": "factory deploy", "confidence": "MEDIUM", "evidence": "plausible factory"}],
        })
        result = apply_source_authentication_gate(base_output(packet), {"subject": "official token CA provenance"}, POLICY)
        self.assertFalse(result["source_authentication"]["first_party_claim_allowed"])
        self.assertIn("HIGH_CONFIDENCE_ONCHAIN_BINDING_REQUIRED", result["source_authentication"]["gate_reasons"])
        self.assertTrue(result["summary"].startswith("Source authentication did not admit first-party provenance"))

    def test_red_team_unresolved_blocks_even_with_anchors(self) -> None:
        packet = default_source_authentication()
        packet.update({
            "scope": "PROJECT_SOURCE",
            "state": "AUTHENTICATED_FIRST_PARTY",
            "claimed_entity": "Example Project",
            "subject": "github.com/example/project",
            "external_trust_anchors": [
                anchor("OFFICIAL_WEBSITE", "https://example.org/dev"),
                anchor("OFFICIAL_DOCS", "https://docs.example.org/source"),
            ],
            "red_team_findings": [{"hypothesis": "spoofed domain redirect", "status": "UNRESOLVED", "evidence": "ownership not proven"}],
        })
        result = apply_source_authentication_gate(base_output(packet), {"subject": "official GitHub source"}, POLICY)
        self.assertFalse(result["source_authentication"]["first_party_claim_allowed"])
        self.assertIn("RED_TEAM_UNRESOLVED_OR_BLOCKING", result["source_authentication"]["gate_reasons"])

    def test_cto_scope_does_not_inherit_false_first_party_status(self) -> None:
        packet = default_source_authentication()
        packet.update({"scope": "CTO_COMMUNITY", "state": "CANDIDATE", "claimed_entity": "community CTO", "subject": "token"})
        result = apply_source_authentication_gate(base_output(packet), {"subject": "community CTO survival"}, POLICY)
        self.assertFalse(result["source_authentication"]["first_party_claim_allowed"])
        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["summary"], "test")

    def test_runtime_hydration_noise_does_not_force_auth(self) -> None:
        task = {"subject": "wallet cohort", "runtime_hydration": {"context_files": [{"content": "github official repository"}]}}
        self.assertFalse(task_requires_source_authentication(task))

    def test_v12_dry_run_persists_gate_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            task = root / "task.json"
            task.write_text(json.dumps({"status": "QUEUED", "subject": "official GitHub provenance"}))
            out = root / "out"
            receipt = analyze(task, POLICY, out, dry_run=True, enable_web=True, model=None)
            output = json.loads((out / "output.json").read_text())
            self.assertEqual(receipt["runtime_contract"], "MEME_ALPHA_RUNTIME_v1_2_SOURCE_AUTH")
            self.assertFalse(receipt["first_party_claim_allowed"])
            self.assertEqual(output["source_authentication"]["state"], "CANDIDATE")
            self.assertEqual(output["status"], "BLOCKED")
            self.assertTrue(output["summary"].startswith("Source authentication did not admit first-party provenance"))


if __name__ == "__main__":
    unittest.main()
