from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.api_agent import meme_alpha_runtime as base
from scripts.api_agent.meme_alpha_runtime_v1_2 import (
    _apply_output_compaction,
    _augmented_output_schema,
    _build_exact_plan,
)


POLICY = {
    "queue": {
        "intake_roots": ["private_research/memes_alpha/research_leads"],
        "eligible_status_tokens": [
            "QUEUED",
            "READY",
            "WATCH",
            "HIGH_PRIORITY_WATCH",
            "QUEUED_FOR_INDEPENDENT_REPLAY",
            "PROVISIONAL",
            "RESEARCH",
        ],
        "terminal_states": ["COMPLETE", "KILLED", "SUPERSEDED"],
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


class MemeAlphaRuntimeV12HardeningTests(unittest.TestCase):
    def write_json(self, root: Path, rel: str, value: dict) -> Path:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, sort_keys=True) + "\n")
        return path

    def test_exact_admission_rejects_not_activated_substring_and_selects_next(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            rejected = self.write_json(
                root,
                "private_research/memes_alpha/research_leads/a.json",
                {"status": "RESEARCH_CANDIDATE_NOT_ACTIVATED", "priority": "P0"},
            )
            valid = self.write_json(
                root,
                "private_research/memes_alpha/research_leads/b.json",
                {"status": "QUEUED", "priority": "P2"},
            )
            plan = _build_exact_plan(root, POLICY, {"processed_inputs": {}})
            self.assertFalse(plan["no_op"])
            self.assertEqual(plan["selected"]["path"], valid.relative_to(root).as_posix())
            self.assertEqual(plan["rejected_non_exact_status_count"], 1)
            self.assertEqual(plan["rejected_non_exact_statuses"][0]["path"], rejected.relative_to(root).as_posix())

    def test_exact_admission_returns_noop_when_only_not_activated_candidate_exists(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_json(
                root,
                "private_research/memes_alpha/research_leads/a.json",
                {"status": "RESEARCH_CANDIDATE_NOT_ACTIVATED", "priority": "P0"},
            )
            plan = _build_exact_plan(root, POLICY, {"processed_inputs": {}})
            self.assertTrue(plan["no_op"])
            self.assertEqual(plan["rejected_non_exact_status_count"], 1)

    def test_compaction_tightens_schema_without_raising_token_budget(self) -> None:
        schema = _augmented_output_schema(base.output_schema)
        payload = {
            "max_output_tokens": 3600,
            "instructions": "base instruction",
            "text": {"format": {"schema": schema}},
        }
        task = {
            "output_compaction": {
                "target_max_output_tokens": 3000,
                "max_verified_findings": 7,
                "max_disconfirming_evidence": 5,
                "max_uncertainties": 5,
                "max_network_connections": 8,
                "max_next_research_steps": 4,
                "max_development_candidates": 2,
                "instruction": "Do not repeat evidence.",
            }
        }
        self.assertTrue(_apply_output_compaction(payload, task))
        props = payload["text"]["format"]["schema"]["properties"]
        self.assertEqual(payload["max_output_tokens"], 3600)
        self.assertEqual(props["verified_findings"]["maxItems"], 7)
        self.assertEqual(props["disconfirming_evidence"]["maxItems"], 5)
        self.assertEqual(props["uncertainties"]["maxItems"], 5)
        self.assertEqual(props["network_connections"]["maxItems"], 8)
        self.assertEqual(props["next_research_steps"]["maxItems"], 4)
        self.assertEqual(props["development_candidates"]["maxItems"], 2)
        auth = props["source_authentication"]["properties"]
        self.assertLessEqual(auth["external_trust_anchors"]["maxItems"], 4)
        self.assertLessEqual(auth["repository_forensics"]["maxItems"], 4)
        self.assertLessEqual(auth["red_team_findings"]["maxItems"], 4)
        self.assertIn("OUTPUT_COMPACTION is binding", payload["instructions"])
        self.assertIn("3000", payload["instructions"])


if __name__ == "__main__":
    unittest.main()
