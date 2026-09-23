from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.learning.action_compass_reproducibility import (
    compare_replays,
    output_is_inside_receipt_root,
    validate_fixture,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "tests/fixtures/action_compass_reproducibility/T9_SYNTHETIC_BASE_v1.json"


def candidate(*, model="MODEL_A", rationale=None, quality=None):
    if rationale is None:
        rationale = ["NO_EXIT_AUTHORITY"]
    if quality is None:
        quality = ["COMPLETE"]
    return {
        "contract": "THREE_HORIZON_ACTION_COMPASS_RECEIPT_CANDIDATE_v1_1",
        "input_packet_sha256": "7777777777777777777777777777777777777777777777777777777777777777",
        "input_binding_status": "OPAQUE_SOURCE_HASH_ASSERTED",
        "input_contract": "T9_SYNTHETIC_FIXTURE_INPUT_v1",
        "source_reference": "OPAQUE:t9-synthetic-fixture-001",
        "source_timestamp_utc": "2026-09-01T12:00:00Z",
        "canonical_repository": "Donh91/Investering-Framework-Archive-v1",
        "canonical_commit_sha": "0000000000000000000000000000000000000000",
        "owner_contract": "02_DATA_PING/protocols/2026-08-25__three-horizon-action-compass-output-contract-v1__canonical.md",
        "interpreted_at_utc": "2026-09-01T12:05:00Z",
        "producer_model": model,
        "action_compass": {
            "contract": "THREE_HORIZON_ACTION_COMPASS_v1_1",
            "as_of_utc": "2026-09-01T12:00:00Z",
            "near_term": {
                "horizon_hours": 24,
                "valid_from_utc": "2026-09-01T12:00:00Z",
                "valid_until_utc": "2026-09-02T12:00:00Z",
                "action": "HOLD",
            },
            "next_window": {
                "window_start_date": "2026-09-06",
                "window_end_date": "2026-09-08",
                "action": "PREPARE_BUY",
            },
            "altcoin_compass": {
                "horizon_days": 28,
                "through_date": "2026-09-29",
                "state": "PRE_ROTATION",
                "action": "HOLD",
                "warning": "NONE",
            },
        },
        "data_quality_tags": quality,
        "rationale_tags": rationale,
        "baseline_observer": {"status": "UNAVAILABLE", "reason": "BASELINE_DATA_MISSING"},
        "portfolio_execution": False,
    }


class ActionCompassReproducibilityTests(unittest.TestCase):
    def fixture(self):
        return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_frozen_synthetic_fixture_hash_is_valid_and_noneligible(self):
        info = validate_fixture(self.fixture())
        self.assertFalse(info["eligible_replay"])

    def test_identical_machine_semantics_allow_model_and_rationale_variance(self):
        a = candidate(model="MODEL_A", rationale=["NO_EXIT_AUTHORITY"])
        b = candidate(model="MODEL_B", rationale=["BREADTH_CONFLICT"])
        result = compare_replays(self.fixture(), [a, b])
        self.assertEqual(result["status"], "SEMANTIC_MATCH")
        self.assertTrue(result["metadata_variance_observed"])
        self.assertEqual(result["eligible_replay_count"], 0)

    def test_changed_action_state_warning_horizon_or_quality_is_disagreement(self):
        mutations = [
            ("action_compass", "near_term", "action", "REDUCE"),
            ("action_compass", "altcoin_compass", "state", "ROTATION"),
            ("action_compass", "altcoin_compass", "warning", "DISTRIBUTION_WARNING"),
            ("action_compass", "near_term", "horizon_hours", 48),
        ]
        for path in mutations:
            a = candidate()
            b = candidate()
            node = b
            for key in path[:-2]:
                node = node[key]
            node[path[-2]] = path[-1]
            self.assertEqual(compare_replays(self.fixture(), [a, b])["status"], "SEMANTIC_DISAGREEMENT")
        a = candidate(quality=["COMPLETE"])
        b = candidate(quality=["SOURCE_DEGRADED"])
        self.assertEqual(compare_replays(self.fixture(), [a, b])["status"], "SEMANTIC_DISAGREEMENT")

    def test_quality_order_is_not_semantic(self):
        a = candidate(quality=["COMPLETE", "PARTIAL"])
        b = candidate(quality=["PARTIAL", "COMPLETE"])
        self.assertEqual(compare_replays(self.fixture(), [a, b])["status"], "SEMANTIC_MATCH")

    def test_replay_bound_to_different_input_fails_closed(self):
        a = candidate()
        b = candidate()
        b["input_packet_sha256"] = "8" * 64
        result = compare_replays(self.fixture(), [a, b])
        self.assertEqual(result["status"], "INVALID_OUTPUT")
        self.assertIn("replay_input_binding_mismatch", result["invalid_outputs"][0]["error"])

    def test_owner_validator_rejection_fails_closed(self):
        a = candidate()
        b = candidate()
        b["action_compass"]["near_term"]["action"] = "MAYBE_BUY"
        result = compare_replays(self.fixture(), [a, b])
        self.assertEqual(result["status"], "INVALID_OUTPUT")

    def test_pre_activation_input_and_interpretation_fail_closed(self):
        fixture = self.fixture()
        fixture["frozen_input"]["source_timestamp_utc"] = "2026-08-25T23:59:59Z"
        from scripts.learning import action_compass_accountability as owner
        fixture["frozen_input_sha256"] = owner.digest(fixture["frozen_input"])
        with self.assertRaisesRegex(ValueError, "pre_activation_input_forbidden"):
            validate_fixture(fixture)
        a = candidate()
        b = candidate()
        b["interpreted_at_utc"] = "2026-08-25T23:59:59Z"
        self.assertEqual(compare_replays(self.fixture(), [a, b])["status"], "INVALID_OUTPUT")

    def test_mutable_latest_and_historical_chat_fixture_sources_fail_closed(self):
        fixture = self.fixture()
        fixture["source_reference"] = "tests/fixtures/action_compass_reproducibility/LATEST.json"
        with self.assertRaisesRegex(ValueError, "mutable_latest_fixture_forbidden"):
            validate_fixture(fixture)
        fixture = self.fixture()
        fixture["source_reference"] = "tests/fixtures/action_compass_reproducibility/historical_chat_export.json"
        with self.assertRaisesRegex(ValueError, "historical_chat_fixture_forbidden"):
            validate_fixture(fixture)

    def test_post_activation_verified_receipt_replays_are_eligible_but_never_auto_conclude(self):
        fixture = self.fixture()
        fixture["fixture_class"] = "POST_ACTIVATION_FROZEN_RECEIPT"
        fixture["source_reference"] = "research/framework_memory/action_compass_receipts/2026/09/01/receipt.json"
        fixture["frozen_input"]["input_binding_status"] = "VERIFIED_REPO_FILE"
        fixture["frozen_input"]["source_reference"] = "03_DAILY_CAPTURE_LOGS/captures/example.json"
        from scripts.learning import action_compass_accountability as owner
        fixture["frozen_input_sha256"] = owner.digest(fixture["frozen_input"])
        a = candidate()
        b = candidate()
        for row in (a, b):
            row["input_binding_status"] = "VERIFIED_REPO_FILE"
            row["source_reference"] = "03_DAILY_CAPTURE_LOGS/captures/example.json"
        result = compare_replays(fixture, [a, b])
        self.assertEqual(result["status"], "SEMANTIC_MATCH")
        self.assertEqual(result["eligible_replay_count"], 2)
        self.assertFalse(result["reproducibility_conclusion_authorized"])
        self.assertEqual(result["reproducibility_conclusion_minimum_eligible_replays"], 10)

    def test_comparator_is_pure(self):
        fixture = self.fixture()
        outputs = [candidate(), candidate()]
        f0, o0 = copy.deepcopy(fixture), copy.deepcopy(outputs)
        compare_replays(fixture, outputs)
        self.assertEqual(fixture, f0)
        self.assertEqual(outputs, o0)

    def test_receipt_root_output_is_forbidden(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            target = repo / "research/framework_memory/action_compass_receipts/out.json"
            self.assertTrue(output_is_inside_receipt_root(target, repo))
            safe = repo / "research/t9/out.json"
            self.assertFalse(output_is_inside_receipt_root(safe, repo))


if __name__ == "__main__":
    unittest.main()
