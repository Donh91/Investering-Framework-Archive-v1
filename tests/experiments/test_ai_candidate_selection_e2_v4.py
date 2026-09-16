from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from scripts.experiments import ai_candidate_selection_e2 as v3
from scripts.experiments import ai_candidate_selection_e2_v4 as v4


V4_REQUEST_PATH = Path("research/experiment_lifecycle/e2/requests/AT-E2-CANDIDATE-SELECTION-v4.json")


def load_v4() -> dict:
    return json.loads(V4_REQUEST_PATH.read_text(encoding="utf-8"))


class CandidateSelectionE2V4Tests(unittest.TestCase):
    def test_v4_preregistration_and_v3_control_validate(self) -> None:
        request = v4.validate_request(load_v4())
        v3_baseline = v4.assert_v3_control(request, Path("."))
        self.assertEqual(request["selection_max_output_tokens"], 1000)
        self.assertEqual(v3_baseline["selection_max_output_tokens"], 200)
        self.assertEqual(request["candidate_set_sha256"], v3.CANDIDATE_SET_SHA256)
        self.assertEqual(request["candidate_set"], v3_baseline["candidate_set"])

    def test_only_declared_transport_field_differs_across_invariants(self) -> None:
        request = v4.validate_request(load_v4())
        baseline = v4.assert_v3_control(request, Path("."))
        for key in v4.INVARIANT_FIELDS:
            self.assertEqual(request[key], baseline[key], key)
        self.assertEqual(baseline["selection_max_output_tokens"], v4.V3_MAX_OUTPUT_TOKENS)
        self.assertEqual(request["selection_max_output_tokens"], v4.V4_MAX_OUTPUT_TOKENS)

    def test_v4_rejects_old_200_token_ceiling(self) -> None:
        request = load_v4()
        request["selection_max_output_tokens"] = 200
        with self.assertRaisesRegex(ValueError, "frozen_v4_transport_runtime_mismatch"):
            v4.validate_request(request)

    def test_candidate_mutation_still_fails_closed(self) -> None:
        request = load_v4()
        request["candidate_set"][0]["feature"] = "ret4_pct"
        with self.assertRaisesRegex(ValueError, "candidate_set_differs"):
            v4.validate_request(request)

    def test_parent_and_authority_are_immutable(self) -> None:
        request = load_v4()
        mutated = deepcopy(request)
        mutated["parent_result_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "parent_result_binding_mismatch"):
            v4.validate_request(mutated)
        mutated = deepcopy(request)
        mutated["authority"]["portfolio_execution"] = True
        with self.assertRaisesRegex(ValueError, "research_only_authority_required"):
            v4.validate_request(mutated)

    def test_v3_validator_remains_unchanged(self) -> None:
        v3_request = json.loads(v4.V3_REQUEST_REL.read_text(encoding="utf-8"))
        validated = v3.validate_request(v3_request)
        self.assertEqual(validated["issue"], 966)
        self.assertEqual(validated["selection_max_output_tokens"], 200)


if __name__ == "__main__":
    unittest.main()
