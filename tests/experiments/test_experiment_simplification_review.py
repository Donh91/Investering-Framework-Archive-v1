from __future__ import annotations

import unittest

from scripts.experiments.experiment_simplification_review import build_review, strict_semantic_key


def candidate(cid: str, path: str, *, direction: str = "DOWN", horizon: int = 7, threshold: float = 5.0, hypothesis: str = "h") -> dict:
    return {
        "contract": "EXPERIMENT_CANDIDATE_v1",
        "candidate_id": cid,
        "spec": {
            "kind": "FORECAST_TEST",
            "title": cid,
            "hypothesis": hypothesis,
            "falsifier": "f",
            "horizon_days": horizon,
            "components": [],
            "target_metric_path": path,
            "target_direction": direction,
            "target_threshold_pct": threshold if direction in {"UP", "DOWN"} else None,
            "target_range_lower_pct": None,
            "target_range_upper_pct": None,
            "target_unit_contract_version": "FORECAST_TARGET_UNITS_v2",
            "regime_dependency": "CURRENT_OBSERVED_REGIME",
        },
    }


def registry_row(cid: str, *, state: str = "INCUBATING", obs: int = 10, outcomes: int = 0, admission: str = "QUALIFIED_FOR_FORWARD_TEST") -> dict:
    return {
        "candidate_id": cid,
        "kind": "FORECAST_TEST",
        "state": state,
        "observation_count": obs,
        "matured_outcome_count": outcomes,
        "scientific_admission_status": admission,
        "semantic_fingerprint": f"registry-{cid}",
    }


class ExperimentSimplificationReviewTests(unittest.TestCase):
    def test_namespace_aliases_with_same_full_semantics_group_for_merge_review(self) -> None:
        a = candidate("EC-a", "derivatives.BTC-USDT-SWAP.mark_price.mark_price")
        b = candidate("EC-b", "latest_capture.market_metrics.derivatives.BTC-USDT-SWAP.mark_price.mark_price")
        self.assertEqual(strict_semantic_key(a), strict_semantic_key(b))
        registry = {"generated_at_utc": "2026-09-24T00:00:00Z", "candidates": [registry_row("EC-a"), registry_row("EC-b")]}
        out = build_review(registry, {"EC-a": a, "EC-b": b})
        self.assertEqual(len(out["exact_semantic_alias_groups"]), 1)
        self.assertEqual(out["exact_semantic_alias_groups"][0]["candidate_ids"], ["EC-a", "EC-b"])
        self.assertEqual(out["exact_semantic_alias_groups"][0]["recommendation"], "MERGE_REVIEW")
        self.assertFalse(out["exact_semantic_alias_groups"][0]["automatic_merge"])

    def test_same_target_path_but_distinct_thresholds_are_not_exactly_collapsed(self) -> None:
        a = candidate("EC-a", "derivatives.BTC-USDT-SWAP.mark_price.mark_price", threshold=3.0)
        b = candidate("EC-b", "market.derivatives.BTC-USDT-SWAP.mark_price.mark_price", threshold=7.0)
        self.assertNotEqual(strict_semantic_key(a), strict_semantic_key(b))
        registry = {"generated_at_utc": "2026-09-24T00:00:00Z", "candidates": [registry_row("EC-a"), registry_row("EC-b")]}
        out = build_review(registry, {"EC-a": a, "EC-b": b})
        self.assertEqual(out["exact_semantic_alias_groups"], [])
        self.assertEqual(len(out["target_family_inspection_groups"]), 1)
        self.assertTrue(out["target_family_inspection_groups"][0]["same_target_is_not_merge_authority"])
        self.assertTrue(out["target_family_inspection_groups"][0]["distinct_hypotheses_preserved"])

    def test_waiting_states_remain_waiting_review_only(self) -> None:
        rows = [
            registry_row("EC-data", state="WAITING_FOR_DATA"),
            registry_row("EC-map", state="WAITING_FOR_MAPPING"),
        ]
        cands = {
            "EC-data": candidate("EC-data", "spot.BTCUSDT.close"),
            "EC-map": candidate("EC-map", "spot.ETHUSDT.close"),
        }
        out = build_review({"generated_at_utc": "x", "candidates": rows}, cands)
        by_id = {row["candidate_id"]: row for row in out["candidates"]}
        self.assertEqual(by_id["EC-data"]["recommendation"], "WAIT_FOR_DATA")
        self.assertEqual(by_id["EC-map"]["recommendation"], "WAIT_FOR_MAPPING")

    def test_repeated_matured_inconclusive_distinct_semantics_are_not_merge_authority(self) -> None:
        a = candidate("EC-a", "spot.BTCUSDT.close", threshold=3.0)
        b = candidate("EC-b", "market_metrics.spot.BTCUSDT.close", threshold=7.0)
        rows = [
            registry_row("EC-a", state="MATURED_INCONCLUSIVE", obs=100, outcomes=3),
            registry_row("EC-b", state="MATURED_INCONCLUSIVE", obs=100, outcomes=4),
        ]
        out = build_review({"generated_at_utc": "x", "candidates": rows}, {"EC-a": a, "EC-b": b})
        self.assertEqual(len(out["repeated_matured_inconclusive_families"]), 1)
        self.assertEqual(out["repeated_matured_inconclusive_families"][0]["recommendation"], "NEEDS_MORE_OUTCOMES")
        self.assertFalse(out["repeated_matured_inconclusive_families"][0]["automatic_action"])

    def test_high_observation_zero_outcome_flag_is_descriptive_and_non_mutating(self) -> None:
        rows = [
            registry_row("EC-low", obs=10),
            registry_row("EC-mid", obs=20),
            registry_row("EC-high", obs=100),
        ]
        cands = {
            cid: candidate(cid, f"spot.{cid}.close")
            for cid in ("EC-low", "EC-mid", "EC-high")
        }
        out = build_review({"generated_at_utc": "x", "candidates": rows}, cands)
        flagged = {row["candidate_id"] for row in out["high_observation_zero_outcome_incubating"]}
        self.assertIn("EC-high", flagged)
        self.assertEqual(out["high_observation_zero_outcome_definition"]["authority"], "DESCRIPTIVE_REVIEW_ONLY")
        self.assertFalse(out["authority"]["automatic_retirement"])
        self.assertFalse(out["authority"]["candidate_history_mutation"])


    def test_current_registry_readback_is_deterministic_and_candidate_bytes_are_unchanged(self) -> None:
        from pathlib import Path
        import hashlib
        import json

        from scripts.experiments.experiment_simplification_review import load_candidates

        repo = Path(__file__).resolve().parents[2]
        registry_path = repo / "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json"
        candidate_root = repo / "research/experiment_lifecycle/candidates"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))

        before = {
            path.relative_to(repo).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(candidate_root.rglob("*.json"))
        }
        candidates = load_candidates(candidate_root)
        first = build_review(registry, candidates)
        second = build_review(registry, candidates)
        after = {
            path.relative_to(repo).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(candidate_root.rglob("*.json"))
        }

        self.assertEqual(before, after)
        self.assertEqual(first, second)
        registry_rows = registry.get("candidates", [])
        unique_ids = {row.get("candidate_id") for row in registry_rows if isinstance(row, dict) and row.get("candidate_id")}
        self.assertEqual(first["registry_row_count"], len(registry_rows))
        self.assertEqual(first["candidate_count"], len(unique_ids))
        self.assertEqual(first["unique_candidate_count"], len(unique_ids))
        duplicate_ids = {
            cid for cid in unique_ids
            if sum(1 for row in registry_rows if isinstance(row, dict) and row.get("candidate_id") == cid) > 1
        }
        self.assertEqual({row["candidate_id"] for row in first["duplicate_candidate_id_rows"]}, duplicate_ids)
        for row in first["duplicate_candidate_id_rows"]:
            self.assertGreater(row["row_count"], 1)
            self.assertEqual(row["review"], "REGISTRY_DUPLICATE_ID_READ_ONLY_REVIEW")
            self.assertFalse(row["automatic_action"])
        self.assertFalse(first["authority"]["candidate_history_mutation"])
        self.assertFalse(first["authority"]["automatic_merge"])
        self.assertFalse(first["authority"]["automatic_retirement"])
        self.assertFalse(first["authority"]["automatic_promotion"])
        self.assertFalse(first["authority"]["model_weight_change"])
        self.assertFalse(first["authority"]["market_gate_change"])
        self.assertFalse(first["authority"]["portfolio_action"])
        self.assertFalse(first["rules"]["same_metric_path_alone_can_merge"])
        for group in first["exact_semantic_alias_groups"]:
            self.assertEqual(group["recommendation"], "MERGE_REVIEW")
            self.assertFalse(group["automatic_merge"])
            self.assertFalse(group["automatic_retirement"])

    def test_not_supported_only_routes_to_retire_review_never_auto_retires(self) -> None:
        row = registry_row("EC-x", state="MATURED_NOT_SUPPORTED", obs=50, outcomes=5)
        out = build_review({"generated_at_utc": "x", "candidates": [row]}, {"EC-x": candidate("EC-x", "spot.BTCUSDT.close")})
        self.assertEqual(out["candidates"][0]["recommendation"], "RETIRE_REVIEW")
        self.assertFalse(out["authority"]["automatic_retirement"])
        self.assertFalse(out["rules"]["review_can_delete_candidate"])
        self.assertFalse(out["rules"]["review_can_rewrite_history"])
        self.assertFalse(out["rules"]["review_can_promote_candidate"])
        self.assertFalse(out["rules"]["review_can_change_weight"])


if __name__ == "__main__":
    unittest.main()
