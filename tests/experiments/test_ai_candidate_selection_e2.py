from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from scripts.experiments import ai_candidate_selection_e2 as v3


REQUEST_PATH = Path("research/experiment_lifecycle/e2/requests/AT-E2-CANDIDATE-SELECTION-v3.json")


def load_request() -> dict:
    return json.loads(REQUEST_PATH.read_text(encoding="utf-8"))


def capability() -> dict:
    schema = v3.selection_schema(v3.FIXED_CANDIDATES)
    return {
        "tools": ["openai.responses", "deterministic_candidate_validation", "agent_handoff_contract"],
        "schemas": {
            "selection_output": v3.base.sha(schema),
            "candidate_set": v3.CANDIDATE_SET_SHA256,
        },
        "runtime": "AUTO_TRADING_E2_CANDIDATE_SELECTION_v3",
    }


def record(candidate_id: str | None, repeat: int) -> dict:
    output = {"candidate_id": candidate_id} if candidate_id is not None else {"bad": "shape"}
    return {
        "arm": "AI_CANDIDATE_SELECTION",
        "repeat": repeat,
        "request_hash": "same-request-hash",
        "response_id": f"r{repeat}",
        "output": output,
        "input_tokens": 1,
        "output_tokens": 1,
        "cost_usd": 0.0,
        "error": None,
        "response_hash": v3.base.sha(output),
    }


class CandidateSelectionE2Tests(unittest.TestCase):
    def test_preregistered_request_and_candidate_set_validate(self) -> None:
        request = v3.validate_request(load_request())
        self.assertEqual(v3.base.sha(request["candidate_set"]), v3.CANDIDATE_SET_SHA256)
        self.assertEqual(len(v3.validate_candidates(request["candidate_set"])), 10)

    def test_candidate_mutation_fails_closed(self) -> None:
        request = load_request()
        request["candidate_set"][0]["feature"] = "ret4_pct"
        with self.assertRaisesRegex(ValueError, "candidate_set_differs"):
            v3.validate_request(request)

    def test_seven_of_ten_modal_selection_passes_gate(self) -> None:
        request = v3.validate_request(load_request())
        records = [record("C03", i) for i in range(1, 8)] + [record("C04", i) for i in range(8, 11)]
        result = v3.evaluate_records(records, request=request, design_summary={"frozen": True}, capability=capability())
        self.assertEqual(result["modal_candidate_id"], "C03")
        self.assertEqual(result["modal_candidate_share"], 0.7)
        self.assertEqual(result["candidate_admission_rate"], 1.0)
        self.assertEqual(result["structured_selection_success_rate"], 1.0)
        self.assertTrue(result["economic_successor_eligible"])
        self.assertEqual(result["conclusion"], "CANDIDATE_SELECTION_CONVERGENCE_SUPPORTED_FOR_ECONOMIC_SUCCESSOR")

    def test_distributed_selection_fails_convergence(self) -> None:
        request = v3.validate_request(load_request())
        ids = ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10"]
        records = [record(candidate_id, i) for i, candidate_id in enumerate(ids, start=1)]
        result = v3.evaluate_records(records, request=request, design_summary={"frozen": True}, capability=capability())
        self.assertEqual(result["modal_candidate_share"], 0.1)
        self.assertFalse(result["economic_successor_eligible"])
        self.assertEqual(result["conclusion"], "CANDIDATE_SELECTION_CONVERGENCE_NOT_SUPPORTED")

    def test_invalid_output_remains_counted(self) -> None:
        request = v3.validate_request(load_request())
        records = [record("C03", i) for i in range(1, 10)] + [record(None, 10)]
        result = v3.evaluate_records(records, request=request, design_summary={"frozen": True}, capability=capability())
        self.assertEqual(result["structured_selection_success_rate"], 0.9)
        self.assertEqual(result["candidate_admission_rate"], 0.9)
        self.assertEqual(result["failed_call_count"], 1)
        self.assertEqual(result["failure_taxonomy"], {"STRICT_SELECTION_SCHEMA_INVALID": 1})

    def test_parent_binding_and_authority_cannot_be_rewritten(self) -> None:
        request = load_request()
        mutated = deepcopy(request)
        mutated["parent_result_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "parent_result_binding_mismatch"):
            v3.validate_request(mutated)
        mutated = deepcopy(request)
        mutated["authority"]["portfolio_execution"] = True
        with self.assertRaisesRegex(ValueError, "research_only_authority_required"):
            v3.validate_request(mutated)


if __name__ == "__main__":
    unittest.main()
