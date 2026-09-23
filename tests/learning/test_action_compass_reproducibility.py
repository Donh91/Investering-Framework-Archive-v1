from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from scripts.learning.action_compass_reproducibility import compare_replays, validate_fixture


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "tests/fixtures/action_compass_reproducibility/T9_SYNTHETIC_BASE_v1.json"


def output(replay_id: str, *, model: str = "MODEL_A", wording: str = "same decision", quality=None):
    if quality is None:
        quality = ["COMPLETE"]
    return {
        "replay_id": replay_id,
        "interpreted_at_utc": "2026-09-01T12:05:00Z",
        "producer_model": model,
        "wording": wording,
        "data_quality_tags": quality,
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
    }


class ActionCompassReproducibilityTests(unittest.TestCase):
    def fixture(self):
        return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_frozen_synthetic_fixture_hash_is_valid_and_noneligible(self):
        info = validate_fixture(self.fixture())
        self.assertEqual(info["fixture_class"], "SYNTHETIC_CONTROLLED")
        self.assertFalse(info["eligible_replay"])

    def test_identical_semantics_allow_model_and_wording_variance(self):
        result = compare_replays(
            self.fixture(),
            [
                output("REPLAY_A", model="MODEL_A", wording="first wording"),
                output("REPLAY_B", model="MODEL_B", wording="different human wording"),
            ],
        )
        self.assertEqual(result["status"], "SEMANTIC_MATCH")
        self.assertTrue(result["metadata_or_wording_variance_observed"])
        self.assertEqual(result["semantic_disagreements"], [])
        self.assertEqual(result["eligible_replay_count"], 0)
        self.assertEqual(result["synthetic_replay_count"], 2)
        self.assertFalse(result["prospective_action_compass_receipt_created"])
        self.assertFalse(result["reproducibility_conclusion_authorized"])

    def test_data_quality_order_is_nonsemantic_but_classification_set_is_semantic(self):
        a = output("REPLAY_A", quality=["COMPLETE", "PARTIAL"])
        b = output("REPLAY_B", quality=["PARTIAL", "COMPLETE"])
        self.assertEqual(compare_replays(self.fixture(), [a, b])["status"], "SEMANTIC_MATCH")
        c = output("REPLAY_C", quality=["SOURCE_DEGRADED"])
        result = compare_replays(self.fixture(), [a, c])
        self.assertEqual(result["status"], "SEMANTIC_DISAGREEMENT")
        self.assertTrue(any("data_quality_tags" in path for row in result["semantic_disagreements"] for path in row["paths"]))

    def test_changed_action_is_semantic_disagreement(self):
        a = output("REPLAY_A")
        b = output("REPLAY_B")
        b["action_compass"]["near_term"]["action"] = "REDUCE"
        result = compare_replays(self.fixture(), [a, b])
        self.assertEqual(result["status"], "SEMANTIC_DISAGREEMENT")
        self.assertIn("action_compass.near_term.action", result["semantic_disagreements"][0]["paths"])

    def test_changed_lane3_state_is_semantic_disagreement(self):
        a = output("REPLAY_A")
        b = output("REPLAY_B")
        b["action_compass"]["altcoin_compass"]["state"] = "ROTATION"
        result = compare_replays(self.fixture(), [a, b])
        self.assertEqual(result["status"], "SEMANTIC_DISAGREEMENT")
        self.assertIn("action_compass.altcoin_compass.state", result["semantic_disagreements"][0]["paths"])

    def test_changed_warning_is_semantic_disagreement(self):
        a = output("REPLAY_A")
        b = output("REPLAY_B")
        b["action_compass"]["altcoin_compass"]["warning"] = "DISTRIBUTION_WARNING"
        result = compare_replays(self.fixture(), [a, b])
        self.assertEqual(result["status"], "SEMANTIC_DISAGREEMENT")
        self.assertIn("action_compass.altcoin_compass.warning", result["semantic_disagreements"][0]["paths"])

    def test_invalid_controlled_vocabulary_is_invalid_output(self):
        a = output("REPLAY_A")
        b = output("REPLAY_B")
        b["action_compass"]["near_term"]["action"] = "MAYBE_BUY"
        result = compare_replays(self.fixture(), [a, b])
        self.assertEqual(result["status"], "INVALID_OUTPUT")
        self.assertEqual(result["valid_replay_count"], 1)
        self.assertTrue(result["invalid_outputs"])

    def test_pre_activation_fixture_fails_closed(self):
        fixture = self.fixture()
        fixture["frozen_at_utc"] = "2026-08-25T23:59:59Z"
        with self.assertRaisesRegex(ValueError, "pre_activation_fixture_forbidden"):
            validate_fixture(fixture)

    def test_mutable_latest_and_historical_chat_sources_fail_closed(self):
        fixture = self.fixture()
        fixture["source_reference"] = "tests/fixtures/action_compass_reproducibility/LATEST.json"
        with self.assertRaisesRegex(ValueError, "mutable_latest_fixture_forbidden"):
            validate_fixture(fixture)
        fixture = self.fixture()
        fixture["source_reference"] = "tests/fixtures/action_compass_reproducibility/historical_chat_export.json"
        with self.assertRaisesRegex(ValueError, "historical_chat_fixture_forbidden"):
            validate_fixture(fixture)

    def test_post_activation_receipt_replays_are_eligible_but_never_auto_conclude(self):
        fixture = self.fixture()
        fixture["fixture_class"] = "POST_ACTIVATION_FROZEN_RECEIPT"
        fixture["source_reference"] = "research/framework_memory/action_compass_receipts/2026/09/01/receipt.json"
        result = compare_replays(fixture, [output("REPLAY_A"), output("REPLAY_B")])
        self.assertEqual(result["status"], "SEMANTIC_MATCH")
        self.assertEqual(result["eligible_replay_count"], 2)
        self.assertEqual(result["synthetic_replay_count"], 0)
        self.assertEqual(result["reproducibility_conclusion_minimum_eligible_replays"], 10)
        self.assertFalse(result["reproducibility_conclusion_authorized"])

    def test_comparator_is_pure_and_does_not_mutate_fixture_or_outputs(self):
        fixture = self.fixture()
        outputs = [output("REPLAY_A"), output("REPLAY_B")]
        before_fixture = copy.deepcopy(fixture)
        before_outputs = copy.deepcopy(outputs)
        compare_replays(fixture, outputs)
        self.assertEqual(fixture, before_fixture)
        self.assertEqual(outputs, before_outputs)


if __name__ == "__main__":
    unittest.main()
