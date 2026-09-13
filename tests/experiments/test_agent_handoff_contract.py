import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[2]
SCRIPT = ROOT / "scripts" / "experiments" / "agent_handoff_contract.py"


def load_module():
    spec = importlib.util.spec_from_file_location("agent_handoff_contract", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def capabilities():
    return {
        "tools": ["point_in_time_loader", "factor_compiler", "deterministic_replay"],
        "schemas": {
            "factor_rule": "FACTOR_RULE_v1",
            "market_data": "PIT_MARKET_DATA_v1",
        },
        "runtime": "AUTO_TRADING_E2_FROZEN",
    }


class AgentHandoffContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()
        cls.mission = {
            "issue": 911,
            "question": "AI compiler versus direct per-bar policy reproducibility",
            "authority": "RESEARCH_ONLY",
        }
        cls.input_artifact = {
            "dataset": "frozen-e2-sample",
            "sha256": "data-sha",
            "evaluation_context_visible": False,
        }
        cls.compiled_rule = {
            "contract": "FACTOR_RULE_v1",
            "expression": "zscore_24h > 1.0",
            "position": "LONG_IF_TRUE_ELSE_FLAT",
        }

    def build(self, output=None, caps=None, created_at="2026-09-13T13:45:00Z"):
        return self.mod.build_contract(
            stage_id="E2_AI_COMPILER",
            mission=self.mission,
            input_artifact=self.input_artifact,
            capability_snapshot=caps or capabilities(),
            output_artifact=output or self.compiled_rule,
            repair_scope="E2_AI_COMPILER",
            owner_candidate_id="EC-E2-911",
            created_at=created_at,
        )

    def test_exact_pinned_artifacts_verify(self):
        contract = self.build()
        self.assertTrue(self.mod.verify_contract(
            contract,
            mission=self.mission,
            input_artifact=self.input_artifact,
            capability_snapshot=capabilities(),
            output_artifact=self.compiled_rule,
        ))
        self.assertFalse(contract["authority"]["portfolio_execution"])
        self.assertEqual(contract["owner"], "EXPERIMENT_LIFECYCLE_v1")

    def test_changed_artifact_hash_is_rejected(self):
        contract = self.build()
        changed = dict(self.compiled_rule)
        changed["expression"] = "zscore_24h > 0.5"
        with self.assertRaisesRegex(ValueError, "handoff_lock_mismatch:output_artifact_lock"):
            self.mod.verify_contract(
                contract,
                mission=self.mission,
                input_artifact=self.input_artifact,
                capability_snapshot=capabilities(),
                output_artifact=changed,
            )

    def test_911_compiler_output_is_exact_replay_input(self):
        compiler_handoff = self.build()
        self.assertTrue(self.mod.assert_downstream_input(compiler_handoff, self.compiled_rule))
        mutated_for_replay = dict(self.compiled_rule)
        mutated_for_replay["position"] = "LONG_OR_SHORT"
        with self.assertRaisesRegex(ValueError, "downstream_input_not_pinned_to_upstream_output"):
            self.mod.assert_downstream_input(compiler_handoff, mutated_for_replay)

    def test_local_repair_may_change_output_but_not_upstream_state(self):
        previous = self.build()
        repaired_output = dict(self.compiled_rule)
        repaired_output["expression"] = "zscore_24h >= 1.0"
        replacement = self.build(output=repaired_output, created_at="2026-09-13T13:46:00Z")
        self.assertTrue(self.mod.validate_local_repair(previous, replacement))
        self.assertNotEqual(
            previous["locks"]["output_artifact_lock"]["sha256"],
            replacement["locks"]["output_artifact_lock"]["sha256"],
        )

        changed_input = dict(self.input_artifact)
        changed_input["dataset"] = "different-sample"
        illegal = self.mod.build_contract(
            stage_id="E2_AI_COMPILER",
            mission=self.mission,
            input_artifact=changed_input,
            capability_snapshot=capabilities(),
            output_artifact=repaired_output,
            repair_scope="E2_AI_COMPILER",
            owner_candidate_id="EC-E2-911",
            created_at="2026-09-13T13:47:00Z",
        )
        with self.assertRaisesRegex(ValueError, "upstream_mutation_forbidden:input_artifact_lock"):
            self.mod.validate_local_repair(previous, illegal)

    def test_capability_drift_or_missing_schema_fails_closed(self):
        contract = self.build()
        drifted = capabilities()
        drifted["schemas"] = dict(drifted["schemas"])
        drifted["schemas"]["factor_rule"] = "FACTOR_RULE_v2"
        with self.assertRaisesRegex(ValueError, "handoff_lock_mismatch:capability_lock"):
            self.mod.verify_contract(
                contract,
                mission=self.mission,
                input_artifact=self.input_artifact,
                capability_snapshot=drifted,
                output_artifact=self.compiled_rule,
            )
        missing = capabilities()
        missing["schemas"] = {}
        with self.assertRaisesRegex(ValueError, "capability_schemas_required"):
            self.mod.verify_contract(
                contract,
                mission=self.mission,
                input_artifact=self.input_artifact,
                capability_snapshot=missing,
                output_artifact=self.compiled_rule,
            )

    def test_repair_scope_cannot_escape_stage(self):
        with self.assertRaisesRegex(ValueError, "repair_scope_must_equal_stage"):
            self.mod.build_contract(
                stage_id="E2_AI_COMPILER",
                mission=self.mission,
                input_artifact=self.input_artifact,
                capability_snapshot=capabilities(),
                output_artifact=self.compiled_rule,
                repair_scope="E1_DATA_FREEZE",
                owner_candidate_id="EC-E2-911",
            )

    def test_contract_is_immutable_on_disk(self):
        contract = self.build()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = self.mod.write_contract(root, contract)
            self.assertTrue(path.exists())
            with self.assertRaises(FileExistsError):
                self.mod.write_contract(root, contract)


if __name__ == "__main__":
    unittest.main()
