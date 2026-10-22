"""Research-only phase-gate tests. Synthetic ACTIVE examples are NOT source admission.

The repository itself stays QUARANTINED; no activation, floor, model weight,
source data, historical row, portfolio or market state is changed by these tests.
"""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
ROOT = PROJECT / "06_RESEARCH_LAB/shared_row_model_tournament_v1"
sys.path.insert(0, str(PROJECT / "scripts/research"))
from shared_row_activation_phase_gate import validate_activation_phase, ACTIVE, QUARANTINED


def original_contracts():
    contract = json.loads((ROOT / "CORE_FAMILY_PROSPECTIVE_CONTRACT_v1.json").read_text())
    freeze = json.loads((ROOT / "TRANSFORM_FREEZE_REGISTRY.json").read_text())
    return contract, freeze


def runtime_for(contract):
    """Synthetic runtime snapshot for schema tests only; never changes repository."""
    state = json.loads((ROOT / "RUNTIME_STATUS.json").read_text())
    state["collection_state"] = contract["prospective_activation"]["collection_state"]
    state["core_prospective_eligibility_start"] = contract["prospective_eligibility_start"]
    state["core_prospective_eligibility_status"] = contract["prospective_eligibility_status"]
    return state


def synthetic_future_phase():
    contract, freeze = original_contracts()
    floor = "2026-11-05T00:00:00Z"  # SYNTHETIC; not a proposal for a real floor.
    contract["prospective_eligibility_start"] = floor
    contract["prospective_eligibility_status"] = "ACTIVE_POST_REPAIR_FLOOR"
    contract["prospective_activation"].update(
        collection_state=ACTIVE,
        activation_pr="https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1841",
        activation_evidence={
            # A syntactically valid synthetic identifier is NOT a real source receipt.
            "source_readiness_commit_sha": "a" * 40,
            "source_readiness_path": (
                "06_RESEARCH_LAB/shared_row_model_tournament_v1/"
                "ACTIVATION_READINESS_REVIEW_2026-10-05.md"
            ),
            "latest_source_capture_at_utc": "2026-11-04T18:00:00Z",
            "readiness_evidence_cutoff_utc": "2026-11-04T19:00:00Z",
            "activation_reviewed_at_utc": "2026-11-04T20:00:00Z",
            "activation_freeze_time_utc": "2026-11-04T21:00:00Z",
            "activation_adjudication_path": (
                "06_RESEARCH_LAB/shared_row_model_tournament_v1/"
                "ACTIVATION_ADJUDICATION_2026-10-05.md"
            ),
            "validator_repair_version": "SHARED_ROW_ACTIVATION_PHASE_GATE_v1_1",
        },
    )
    freeze["core_activation_rule"].update(
        collection_state=ACTIVE,
        containment_floor_sentinel=False,
        prospective_eligibility_start=floor,
    )
    for family in freeze["families"]:
        if family["family_id"] in {"ETHBTC_PERSISTENCE", "BREADTH_SURVIVAL", "BTCD_PATH_RECLAIM"}:
            family["prospective_eligibility_start"] = floor
    return contract, freeze


class ActivationPhaseGateTests(unittest.TestCase):
    def reject(self, contract, freeze):
        with self.assertRaises((AssertionError, ValueError, KeyError)):
            validate_activation_phase(contract, freeze, runtime_for(contract))

    def test_actual_quarantine_remains_valid(self):
        c, f = original_contracts()
        self.assertEqual(c["prospective_activation"]["collection_state"], QUARANTINED)
        self.assertEqual(validate_activation_phase(c, f, runtime_for(c)), "QUARANTINED_VALID")

    def test_synthetic_active_schema_only(self):
        c, f = synthetic_future_phase()
        self.assertEqual(
            validate_activation_phase(c, f, runtime_for(c)),
            "ACTIVE_SCHEMA_VALID_SOURCE_REVIEW_STILL_REQUIRED",
        )

    def test_mixed_activation_and_freeze_states_rejected(self):
        c, f = synthetic_future_phase()
        f["core_activation_rule"]["collection_state"] = QUARANTINED
        self.reject(c, f)

    def test_sentinel_cannot_become_an_active_floor(self):
        c, f = synthetic_future_phase()
        f["core_activation_rule"]["containment_floor_sentinel"] = True
        self.reject(c, f)

    def test_old_2026_09_30_containment_floor_cannot_be_reused(self):
        c, f = synthetic_future_phase()
        c["prospective_eligibility_start"] = "2026-09-30T00:00:00Z"
        f["core_activation_rule"]["prospective_eligibility_start"] = c["prospective_eligibility_start"]
        for family in f["families"]:
            if family["family_id"] in {"ETHBTC_PERSISTENCE", "BREADTH_SURVIVAL", "BTCD_PATH_RECLAIM"}:
                family["prospective_eligibility_start"] = c["prospective_eligibility_start"]
        self.reject(c, f)

    def test_missing_evidence_rejected(self):
        c, f = synthetic_future_phase()
        del c["prospective_activation"]["activation_evidence"]
        self.reject(c, f)

    def test_unverified_pr_reference_rejected(self):
        c, f = synthetic_future_phase()
        c["prospective_activation"]["activation_pr"] = "#1841"
        self.reject(c, f)

    def test_activation_review_after_floor_rejected(self):
        c, f = synthetic_future_phase()
        c["prospective_activation"]["activation_evidence"]["activation_reviewed_at_utc"] = "2026-11-05T01:00:00Z"
        self.reject(c, f)

    def test_unqualified_capture_after_review_rejected(self):
        c, f = synthetic_future_phase()
        c["prospective_activation"]["activation_evidence"]["latest_source_capture_at_utc"] = "2026-11-04T21:00:00Z"
        self.reject(c, f)

    def test_core_family_floor_drift_rejected(self):
        c, f = synthetic_future_phase()
        f["families"][0]["prospective_eligibility_start"] = "2026-11-03T00:00:00Z"
        self.reject(c, f)

    def test_unrecognized_state_rejected(self):
        c, f = synthetic_future_phase()
        c["prospective_activation"]["collection_state"] = "RUN_ANYWAY"
        f["core_activation_rule"]["collection_state"] = "RUN_ANYWAY"
        self.reject(c, f)

    def test_blocked_optional_family_must_not_inherit_core_floor(self):
        c, f = synthetic_future_phase()
        next(item for item in f["families"] if item["family_id"] == "ETF_FLOW_QUALITY")[
            "prospective_eligibility_start"
        ] = c["prospective_eligibility_start"]
        self.reject(c, f)

    def test_quarantine_cannot_falsely_claim_activation(self):
        c, f = original_contracts()
        c["prospective_activation"]["activation_pr"] = (
            "https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1841"
        )
        self.reject(c, f)

    def test_original_p0_anchor_must_match(self):
        c, f = synthetic_future_phase()
        c["prospective_activation"]["implementation_merge_commit"] = "0" * 40
        self.reject(c, f)

    def test_ambiguous_local_clock_rejected(self):
        c, f = synthetic_future_phase()
        c["prospective_activation"]["activation_evidence"]["activation_reviewed_at_utc"] = "2026-11-04T20:00:00+01:00"
        self.reject(c, f)

    def test_runtime_state_mismatch_rejected(self):
        c, f = synthetic_future_phase()
        runtime = runtime_for(c)
        runtime["collection_state"] = QUARANTINED
        with self.assertRaises(AssertionError):
            validate_activation_phase(c, f, runtime)

    def test_runtime_floor_mismatch_rejected(self):
        c, f = synthetic_future_phase()
        runtime = runtime_for(c)
        runtime["core_prospective_eligibility_start"] = "2026-09-30T00:00:00Z"
        with self.assertRaises(AssertionError):
            validate_activation_phase(c, f, runtime)

    def test_frozen_candidate_definition_mutation_rejected(self):
        c, f = synthetic_future_phase()
        c["candidate_decision_contract"]["C07_SIMPLE_3"] = "C01_ETHBTC OR C03_BTCD"
        self.reject(c, f)

    def test_duplicate_family_definition_rejected(self):
        c, f = synthetic_future_phase()
        f["families"].append(copy.deepcopy(f["families"][0]))
        self.reject(c, f)

    def test_missing_frozen_readiness_cutoff_rejected(self):
        c, f = synthetic_future_phase()
        del c["prospective_activation"]["activation_evidence"]["readiness_evidence_cutoff_utc"]
        self.reject(c, f)

    def test_activation_freeze_at_or_after_floor_rejected(self):
        c, f = synthetic_future_phase()
        c["prospective_activation"]["activation_evidence"]["activation_freeze_time_utc"] = c["prospective_eligibility_start"]
        self.reject(c, f)

    def test_readiness_cutoff_after_review_rejected(self):
        c, f = synthetic_future_phase()
        c["prospective_activation"]["activation_evidence"]["readiness_evidence_cutoff_utc"] = "2026-11-04T20:30:00Z"
        self.reject(c, f)

    def test_missing_adjudication_path_rejected(self):
        c, f = synthetic_future_phase()
        del c["prospective_activation"]["activation_evidence"]["activation_adjudication_path"]
        self.reject(c, f)

    def test_wrong_validator_repair_version_rejected(self):
        c, f = synthetic_future_phase()
        c["prospective_activation"]["activation_evidence"]["validator_repair_version"] = "UNVERIFIED"
        self.reject(c, f)

    def test_missing_runtime_rejected(self):
        c, f = synthetic_future_phase()
        with self.assertRaises(AssertionError):
            validate_activation_phase(c, f)

    def test_actual_repository_has_no_synthetic_activation_fields(self):
        c, f = original_contracts()
        self.assertIsNone(c["prospective_activation"].get("activation_evidence"))
        self.assertTrue(f["core_activation_rule"]["containment_floor_sentinel"])


if __name__ == "__main__":
    unittest.main()
