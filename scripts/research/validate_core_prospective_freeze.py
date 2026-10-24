#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

from shared_row_activation_phase_gate import validate_activation_phase, validate_owner_matrix_floor

ROOT = Path("06_RESEARCH_LAB/shared_row_model_tournament_v1")
TEST = Path("tests/research/test_shared_row_p0_integrity.py")


def main() -> None:
    contract = json.loads((ROOT / "CORE_FAMILY_PROSPECTIVE_CONTRACT_v1.json").read_text())
    outcome = json.loads((ROOT / "OUTCOME_CONTRACT_v1.json").read_text())
    freeze = json.loads((ROOT / "TRANSFORM_FREEZE_REGISTRY.json").read_text())
    runtime = json.loads((ROOT / "RUNTIME_STATUS.json").read_text())
    owner_matrix = json.loads((ROOT / "OWNER_BINDING_MATRIX.json").read_text())
    schema = json.loads((ROOT / "04_SHARED_ROW_SCHEMA.json").read_text())
    assert contract["authority"] == "RESEARCH_ONLY_NON_CANONICAL"
    assert contract["legacy_equivalence"] is False and contract["no_backdating"] is True
    assert contract["candidate_decision_contract"]["complete_core_set_required"] is True
    assert contract["family_contracts"]["ETHBTC_PERSISTENCE"]["definition"]["lookback_rows"] == 168
    assert contract["source_binding_contract"]["contract"] == "SHARED_ROW_SOURCE_BINDING_MANIFEST_v1"
    # Phase-aware control: current repo remains quarantined; ACTIVE requires
    # an independently reviewed, future-floor activation PR and source replay.
    phase = validate_activation_phase(contract, freeze, runtime)
    owner_floor_gate = validate_owner_matrix_floor(contract, freeze, owner_matrix)
    activation = contract["prospective_activation"]
    implementation_commit = activation.get("implementation_merge_commit")
    boundary = activation.get("post_repair_source_capture_not_before_utc")
    if implementation_commit is None:
        assert boundary is None
    else:
        assert len(implementation_commit) == 40
        assert boundary == activation.get("implementation_merged_at_utc")
        assert activation.get("readiness_must_be_reproduced_from_actual_bound_sources") is True
    assert all(
        item.get("repair_state") == "P0_REPAIRED_AWAITING_ACTIVATION_OR_ACTIVE"
        for item in freeze["families"]
        if item["family_id"] in {"ETHBTC_PERSISTENCE", "BREADTH_SURVIVAL", "BTCD_PATH_RECLAIM"}
    )
    assert outcome["freeze_before_first_eligible_row"] is True
    assert outcome["immutability"]["baseline_reconstructed_from_row_source_commit"] is True
    assert outcome["path_metrics"]["complete_hourly_path_required"] is True
    assert outcome["primary_classification"]["horizons_hours"] == {"24h": 24, "72h": 72, "7d": 168}
    assert schema["row_integrity_contract"] == "SHARED_ROW_P0_BINDING_v1"

    spec = importlib.util.spec_from_file_location("shared_row_p0_tests", TEST)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    phase_tests = unittest.defaultTestLoader.discover(
        start_dir=str(TEST.parent), pattern="test_shared_row_activation_phase_gate.py"
    )
    suite.addTests(phase_tests)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    print(
        json.dumps(
            {
                "status": "PASS",
                "contract": "CORE_PROSPECTIVE_P0_INTEGRITY_GATE_v1",
                "activation_phase": phase,
                "owner_matrix_floor_gate": owner_floor_gate,
                "tests_run": result.testsRun,
                "checks": [
                    "quarantine_fail_closed",
                    "phase_aware_activation_fail_closed",
                    "production_breadth_bundle_replay",
                    "same_cutoff_enforced",
                    "missing_is_not_zero",
                    "premature_outcome_rejected",
                    "exact_168_unique_continuous_hours",
                    "strict_btcd_chronology",
                    "provider_and_version_continuity",
                    "reachable_git_path_hash_bindings",
                    "candidate_label_permutation_rejected",
                    "row_time_baseline_reconciled",
                    "complete_outcome_path_required",
                    "outcome_idempotence",
                    "outcome_independent_context_blocks",
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
