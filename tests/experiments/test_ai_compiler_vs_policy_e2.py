import csv
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.experiments import agent_handoff_contract as handoff
from scripts.experiments import ai_compiler_vs_policy_e2 as e2


class AiCompilerVsPolicyE2Tests(unittest.TestCase):
    def make_root(self, *, mutate_derived=False):
        root = Path(tempfile.mkdtemp())
        path = root / "03_DAILY_CAPTURE_LOGS/hourly/2026/01/2026-01-01.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        fields = [
            "timestamp", "spot_status", "btc_close", "eth_close",
            "btc_return_1h_pct", "eth_return_1h_pct", "btc_oi_change_1h_pct", "price_oi_state",
        ]
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for i in range(96):
                writer.writerow({
                    "timestamp": (start + timedelta(hours=i)).isoformat().replace("+00:00", "Z"),
                    "spot_status": "PASS",
                    "btc_close": 100000 + i * 37 + (i % 5) * 11,
                    "eth_close": 4000 + i * 2.1 + (i % 7) * 0.7,
                    "btc_return_1h_pct": 999999 if mutate_derived else -999999,
                    "eth_return_1h_pct": -888888 if mutate_derived else 888888,
                    "btc_oi_change_1h_pct": 777777 if mutate_derived else -777777,
                    "price_oi_state": "CORRUPTED_A" if mutate_derived else "CORRUPTED_B",
                })
        return root

    def request(self):
        return {
            "authority": {
                "automatic_promotion": False,
                "canonical_effect": False,
                "exchange_signing": False,
                "framework_state_change": False,
                "model_weight_change": False,
                "order_routing": False,
                "portfolio_execution": False,
                "threshold_change": False,
            },
            "compiler_max_output_tokens": 500,
            "compiler_repeats": 3,
            "consumed_columns": ["btc_close", "eth_close", "spot_status", "timestamp"],
            "contract": e2.REQUEST_CONTRACT,
            "cutoff_utc": "2026-01-04T23:00:00Z",
            "design_rows": 24,
            "evaluation_points": 6,
            "evaluation_stride_hours": 2,
            "experiment_id": "AT-E2-911-test",
            "failed_and_abandoned_attempts_remain_counted": True,
            "frozen_at_utc": "2026-01-05T00:00:00Z",
            "hard_cost_stop_usd": 0.75,
            "issue": 911,
            "model": "gpt-5.6-luna",
            "no_post_result_prompt_tuning": True,
            "policy_max_output_tokens": 300,
            "policy_repeats": 3,
            "pre_registered_thresholds": {
                "compiler_min_replay_agreement": 0.95,
                "direct_min_action_agreement": 0.9,
                "economic_noninferiority_bps_per_decision": 5.0,
                "material_reproducibility_gap": 0.05,
            },
            "proposal_trial_n": 1,
            "reasoning_effort": "medium",
            "round_trip_cost_bps": 10.0,
            "source_root": "03_DAILY_CAPTURE_LOGS/hourly",
            "status": "APPROVED_RESEARCH_ONLY",
            "theory_ids": ["AT-HYP-0004", "AT-HYP-0008"],
        }

    def test_request_rejects_quarantined_column_contract(self):
        request = self.request()
        request["consumed_columns"].append("btc_return_1h_pct")
        with self.assertRaisesRegex(ValueError, "raw_column_firewall_mismatch"):
            e2.validate_request(request)

    def test_raw_loader_is_invariant_to_corrupted_derived_columns(self):
        first, _ = e2.load_raw_close_rows(self.make_root(mutate_derived=False) / "03_DAILY_CAPTURE_LOGS/hourly", self.request()["cutoff_utc"])
        second, _ = e2.load_raw_close_rows(self.make_root(mutate_derived=True) / "03_DAILY_CAPTURE_LOGS/hourly", self.request()["cutoff_utc"])
        self.assertEqual(first, second)

    def test_evaluation_labels_are_separate_from_model_point(self):
        root = self.make_root()
        rows, _ = e2.load_raw_close_rows(root / "03_DAILY_CAPTURE_LOGS/hourly", self.request()["cutoff_utc"])
        design, points = e2.build_frozen_sample(rows, self.request())
        self.assertTrue(design["assets"]["BTC"]["features"])
        self.assertIn("_evaluation_label_next_1h_pct", points[0])
        public = {k: v for k, v in points[0].items() if not k.startswith("_evaluation_")}
        self.assertNotIn("evaluation_label", json.dumps(public))

    def test_compiler_handoff_rejects_rule_mutation(self):
        mission = {"experiment_id": "AT-E2-911-test"}
        design = {"frozen": True}
        rule = {"feature": "ret4_pct", "long_trigger": "GT_Q75", "short_trigger": "LT_Q25", "rationale": "x"}
        capability = {"tools": ["openai.responses", "deterministic_replay"], "schemas": {"compiler": "abc"}, "runtime": "test"}
        contract = handoff.build_contract(
            stage_id="E2_COMPILER_RUN_1", mission=mission, input_artifact=design,
            capability_snapshot=capability, output_artifact=rule, repair_scope="E2_COMPILER_RUN_1",
            owner_candidate_id="AT-E2-911-test", created_at="2026-01-05T00:00:00Z",
        )
        self.assertTrue(handoff.assert_downstream_input(contract, rule))
        mutated = dict(rule)
        mutated["feature"] = "ret1_pct"
        with self.assertRaisesRegex(ValueError, "downstream_input_not_pinned"):
            handoff.assert_downstream_input(contract, mutated)

    def test_pairwise_agreement_counts_disagreement(self):
        score = e2.pairwise_agreement([
            ["LONG", "FLAT", "SHORT"],
            ["LONG", "FLAT", "SHORT"],
            ["LONG", "SHORT", "SHORT"],
        ])
        self.assertAlmostEqual(score, 7 / 9)

    def test_dry_run_is_complete_reproducible_and_research_only(self):
        root = self.make_root()
        output = root / "out"
        result = e2.run_trial(self.request(), root, output, dry_run=True)
        self.assertEqual(result["status"], "COMPLETE")
        self.assertEqual(result["reproducibility"]["compiler_replay_pairwise_agreement"], 1.0)
        self.assertEqual(result["reproducibility"]["direct_policy_pairwise_action_agreement"], 1.0)
        self.assertFalse(result["data_firewall"]["quarantined_derived_history_used"])
        self.assertFalse(result["capital_ready"])
        self.assertTrue(all(v is False for v in result["authority"].values()))
        self.assertEqual(result["api"]["failed_calls"], 0)
        self.assertEqual(result["api"]["total_cost_usd"], 0.0)
        self.assertTrue((output / "result.json").is_file())
        self.assertTrue((output / "calls.jsonl").is_file())


if __name__ == "__main__":
    unittest.main()
