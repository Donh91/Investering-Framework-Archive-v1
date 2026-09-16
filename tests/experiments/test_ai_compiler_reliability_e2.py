import csv
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.experiments import ai_compiler_reliability_e2 as v2


class AiCompilerReliabilityE2Tests(unittest.TestCase):
    def make_root(self, *, mutate_derived=False):
        root = Path(tempfile.mkdtemp())
        path = root / "03_DAILY_CAPTURE_LOGS/hourly/2026/01/2026-01-01.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        fields = [
            "timestamp_utc", "spot_status", "btc_close", "eth_close",
            "btc_return_1h_pct", "eth_return_1h_pct", "price_oi_state",
        ]
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for i in range(96):
                writer.writerow({
                    "timestamp_utc": (start + timedelta(hours=i)).isoformat().replace("+00:00", "Z"),
                    "spot_status": "PASS",
                    "btc_close": 100000 + i * 37 + (i % 5) * 11,
                    "eth_close": 4000 + i * 2.1 + (i % 7) * 0.7,
                    "btc_return_1h_pct": 999999 if mutate_derived else -999999,
                    "eth_return_1h_pct": -888888 if mutate_derived else 888888,
                    "price_oi_state": "CORRUPTED_A" if mutate_derived else "CORRUPTED_B",
                })
        return root

    def request(self):
        return {
            "authority": dict(v2.AUTHORITY),
            "compiler_max_output_tokens": 1000,
            "compiler_repeats": 10,
            "consumed_columns": ["btc_close", "eth_close", "spot_status", "timestamp_utc"],
            "contract": v2.REQUEST_CONTRACT,
            "cutoff_utc": "2026-01-04T23:00:00Z",
            "design_rows": 24,
            "direct_policy_arm_enabled": False,
            "economic_scoring_enabled": False,
            "evaluation_outcomes_hidden_from_ai": True,
            "evaluation_points": 6,
            "evaluation_stride_hours": 2,
            "experiment_id": v2.EXPERIMENT_ID,
            "failed_and_abandoned_attempts_remain_counted": True,
            "frozen_at_utc": "2026-09-14T10:30:00Z",
            "hard_cost_stop_usd": 0.1,
            "identical_primary_payload_required": True,
            "issue": v2.ISSUE,
            "modal_rule_may_only_seed_new_preregistered_successor": True,
            "model": "gpt-5.6-luna",
            "no_post_result_prompt_tuning": True,
            "no_retroactive_rescore": True,
            "parent_experiment_id": "AT-E2-911-v1",
            "parent_result_sha256": "53ad7e6b56a9ed24df2ca2285090c8d0967b3836d85a28f2c9e6779628a24168",
            "pre_registered_thresholds": {
                "structured_output_success_rate": 0.9,
                "replayable_rule_admission_rate": 0.9,
                "modal_normalized_rule_share": 0.7,
            },
            "reasoning_effort": "medium",
            "source_root": "03_DAILY_CAPTURE_LOGS/hourly",
            "status": "APPROVED_RESEARCH_ONLY",
            "theory_ids": ["AT-HYP-0004", "AT-HYP-0008"],
        }

    @staticmethod
    def record(output, repeat, error=None):
        return {
            "arm": "AI_COMPILER_RELIABILITY",
            "repeat": repeat,
            "request_hash": "same-request-hash",
            "response_id": f"r{repeat}",
            "output": output,
            "input_tokens": 100,
            "output_tokens": 20,
            "cost_usd": 0.0001,
            "error": error,
            "response_hash": f"response-{repeat}",
        }

    def design(self):
        return {"window": {"first_design_timestamp": "2026-01-01T12:00:00Z", "last_design_timestamp": "2026-01-02T11:00:00Z"}}

    def capability(self):
        return {
            "tools": ["openai.responses", "deterministic_rule_validation", "agent_handoff_contract"],
            "schemas": {"compiler_output": "abc"},
            "runtime": "AUTO_TRADING_E2_COMPILER_RELIABILITY_v2",
        }

    def test_request_rejects_economic_or_direct_policy_phase(self):
        request = self.request()
        request["economic_scoring_enabled"] = True
        with self.assertRaisesRegex(ValueError, "exclude_economics_and_direct_policy"):
            v2.validate_request(request)

    def test_structured_but_flat_rule_is_not_replayable(self):
        output = {"feature": "ret4_pct", "long_trigger": "DISABLED", "short_trigger": "DISABLED"}
        self.assertIsNotNone(v2.structured_rule(output))
        self.assertIsNone(v2.replayable_rule(output))

    def test_all_primary_gates_pass_for_stable_replayable_rule(self):
        output = {"feature": "ret4_pct", "long_trigger": "GT_Q75", "short_trigger": "LT_Q25"}
        records = [self.record(output, i) for i in range(1, 11)]
        result = v2.evaluate_records(records, request=self.request(), design_summary=self.design(), capability=self.capability())
        self.assertEqual(result["structured_output_success_rate"], 1.0)
        self.assertEqual(result["replayable_rule_admission_rate"], 1.0)
        self.assertEqual(result["modal_normalized_rule_share"], 1.0)
        self.assertTrue(result["economic_successor_eligible"])
        self.assertEqual(result["conclusion"], "COMPILER_RELIABILITY_SUPPORTED_FOR_ECONOMIC_SUCCESSOR")

    def test_failed_calls_remain_counted_and_fail_ninety_percent_gate(self):
        good = {"feature": "ret4_pct", "long_trigger": "GT_Q75", "short_trigger": "LT_Q25"}
        records = [self.record(good, i) for i in range(1, 9)]
        records.append(self.record(None, 9, "ValueError:missing_output_text"))
        records.append(self.record(None, 10, "JSONDecodeError:unterminated"))
        result = v2.evaluate_records(records, request=self.request(), design_summary=self.design(), capability=self.capability())
        self.assertEqual(result["structured_output_success_rate"], 0.8)
        self.assertEqual(result["replayable_rule_admission_rate"], 0.8)
        self.assertEqual(result["failed_call_count"], 2)
        self.assertEqual(result["failure_taxonomy"]["MISSING_OUTPUT_TEXT"], 1)
        self.assertEqual(result["failure_taxonomy"]["MALFORMED_JSON"], 1)
        self.assertFalse(result["economic_successor_eligible"])

    def test_valid_but_split_rules_fail_modal_convergence_gate(self):
        first = {"feature": "ret4_pct", "long_trigger": "GT_Q75", "short_trigger": "LT_Q25"}
        second = {"feature": "ret12_pct", "long_trigger": "GT_Q75", "short_trigger": "LT_Q25"}
        records = [self.record(first if i <= 5 else second, i) for i in range(1, 11)]
        result = v2.evaluate_records(records, request=self.request(), design_summary=self.design(), capability=self.capability())
        self.assertEqual(result["structured_output_success_rate"], 1.0)
        self.assertEqual(result["replayable_rule_admission_rate"], 1.0)
        self.assertEqual(result["modal_normalized_rule_share"], 0.5)
        self.assertFalse(result["gates"]["modal_normalized_rule_convergence"])
        self.assertFalse(result["economic_successor_eligible"])

    def test_raw_loader_ignores_corrupted_derived_columns(self):
        first, _ = v2.hourly.load_raw_close_rows(self.make_root(mutate_derived=False) / "03_DAILY_CAPTURE_LOGS/hourly", self.request()["cutoff_utc"])
        second, _ = v2.hourly.load_raw_close_rows(self.make_root(mutate_derived=True) / "03_DAILY_CAPTURE_LOGS/hourly", self.request()["cutoff_utc"])
        self.assertEqual(first, second)

    def test_dry_run_is_reliability_only_and_research_only(self):
        root = self.make_root()
        output = root / "out"
        result = v2.run_trial(self.request(), root, output, dry_run=True)
        self.assertEqual(result["status"], "COMPLETE")
        self.assertEqual(result["conclusion"], "COMPILER_RELIABILITY_SUPPORTED_FOR_ECONOMIC_SUCCESSOR")
        self.assertEqual(result["reliability"]["structured_output_success_rate"], 1.0)
        self.assertEqual(result["reliability"]["replayable_rule_admission_rate"], 1.0)
        self.assertEqual(result["reliability"]["modal_normalized_rule_share"], 1.0)
        self.assertFalse(result["economic_scoring_performed"])
        self.assertFalse(result["direct_policy_arm_performed"])
        self.assertFalse(result["capital_ready"])
        self.assertTrue(all(value is False for value in result["authority"].values()))
        self.assertEqual(result["api"]["failed_calls"], 0)
        self.assertEqual(result["api"]["total_cost_usd"], 0.0)
        calls = (output / "calls.jsonl").read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(calls), 10)
        hashes = {json.loads(line)["request_hash"] for line in calls}
        self.assertEqual(len(hashes), 1)
        self.assertTrue((output / "result.json").is_file())
        self.assertTrue((output / "design_summary.json").is_file())


if __name__ == "__main__":
    unittest.main()
