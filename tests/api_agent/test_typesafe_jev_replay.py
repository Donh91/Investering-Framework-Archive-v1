from __future__ import annotations

import unittest

from scripts.api_agent.meme_alpha_prospective import freeze_shadow_observation, stable_hash
from scripts.api_agent.typesafe_jev_replay import (
    build_blind_state,
    counterfactual_route,
    freeze_challenger_prediction,
    validate_counterfactual_route,
)


def feature(name: str, value: object) -> dict:
    return {
        "feature_name": name,
        "feature_value_at_cutoff": value,
        "feature_effective_at_utc": "2026-09-19T09:04:00Z",
        "source_observed_at_utc": "2026-09-19T09:04:30Z",
        "source_or_schema_version": "fixture-v1",
        "source_record_or_event_identity": f"fixture:{name}",
        "mutability_class": "SNAPSHOT_PINNED",
    }


def observation() -> dict:
    return freeze_shadow_observation(
        identity={
            "chain": "solana",
            "token_id": "BlindReplayMint11111111111111111111111111111111",
            "token_origin_utc": "2026-09-19T09:00:00Z",
        },
        cutoff_minutes=5,
        cutoff_utc="2026-09-19T09:05:00Z",
        features=[feature("liquidity_usd", 75000), feature("source_conflict", "UNKNOWN")],
        wallet_roles=["UNKNOWN"],
    )


class JevBlindReplayTests(unittest.TestCase):
    def test_blind_state_is_stable_and_has_no_authority(self) -> None:
        state = build_blind_state(observation())
        self.assertEqual(state, build_blind_state(observation()))
        self.assertNotIn("authority", state)
        self.assertTrue(state["blind_state_sha256"])

    def test_outcome_leakage_is_rejected_recursively(self) -> None:
        packet = observation()
        packet["nested"] = {"mfe_after_discovery": 12.0}
        with self.assertRaisesRegex(ValueError, "OUTCOME_LEAKAGE_DETECTED"):
            build_blind_state(packet)

    def test_prediction_is_frozen_before_outcome_and_has_zero_authority(self) -> None:
        state = build_blind_state(observation())
        record = freeze_challenger_prediction(
            blind_state=state,
            challenger="JEV_1_13_0",
            question_contract_version="JEV_ALPHA_QUESTIONS_V1",
            model_version="jev-1.13.0",
            predictions={"material_evidence": 0.81, "deep_dive_value": 0.73},
        )
        self.assertTrue(record["prediction_sha256"])
        self.assertFalse(record["authority"]["automatic_trading"])
        self.assertFalse(record["authority"]["production_routing"])

    def test_prediction_cannot_smuggle_outcome(self) -> None:
        state = build_blind_state(observation())
        with self.assertRaisesRegex(ValueError, "PREDICTION_CONTAINS_OUTCOME_FIELD"):
            freeze_challenger_prediction(
                blind_state=state,
                challenger="JEV_1_13_0",
                question_contract_version="JEV_ALPHA_QUESTIONS_V1",
                predictions={"outcome_class": "WINNER"},
            )

    def test_replay_has_no_drop_route(self) -> None:
        self.assertEqual(counterfactual_route({}), "RETAIN")
        self.assertEqual(counterfactual_route({"deep_dive_value": 0.75}), "DEEP_DIVE")
        self.assertEqual(counterfactual_route({"evidence_conflict": 0.91}), "FRONTIER_REVIEW")
        with self.assertRaisesRegex(ValueError, "FORBIDDEN_REPLAY_ROUTE"):
            validate_counterfactual_route("DROP")


if __name__ == "__main__":
    unittest.main()
