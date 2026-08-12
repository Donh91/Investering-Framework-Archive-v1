from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.api_agent.forward_evidence_observer import coverage_health, mature, observe
from scripts.api_agent.research_execution_coordinator import build_plan


def base_check(**overrides):
    value = {
        "test_id": "GATE_BTC_PARTIAL_FT_1",
        "check_id": "CHECK-001",
        "timestamp_utc": "2026-08-12T06:00:00Z",
        "source_run_id": "run-1",
        "source_hash": "a" * 64,
        "eligible_check": True,
        "missing_fields": [],
        "framework_state": "OWNER_FROZEN_STATE",
        "benchmark_action_WAIT": "WAIT",
        "experimental_action_BTC_PARTIAL": "WAIT",
        "actual_decision_divergence": False,
        "entry_reference_price": 64000.0,
        "position_fraction_assumed": 0.25,
    }
    value.update(overrides)
    return value


def test_no_divergence_is_observable_but_not_outcome_evidence():
    receipt = observe(base_check())
    assert receipt["status"] == "CHECKED_NO_DIVERGENCE"
    assert receipt["counts_as_outcome_row"] is False
    assert receipt["divergence_source_row"] is None
    assert not any(receipt["authority"].values())


def test_trigger_candidate_or_missing_explicit_assertion_cannot_create_row():
    receipt = observe(base_check(actual_decision_divergence=None, experimental_action_BTC_PARTIAL="TRIGGER_CANDIDATE"))
    assert receipt["status"] == "NOT_EVALUABLE_DATA_BLOCKED"
    assert "ACTUAL_DECISION_DIVERGENCE_NOT_EXPLICIT" in receipt["reasons"]
    assert receipt["divergence_source_row"] is None


def test_action_assertion_contradiction_blocks_instead_of_inference():
    receipt = observe(base_check(actual_decision_divergence=False, experimental_action_BTC_PARTIAL="BTC_PARTIAL"))
    assert receipt["status"] == "NOT_EVALUABLE_DATA_BLOCKED"
    assert "ACTION_DIVERGENCE_CONTRADICTS_EXPLICIT_ASSERTION" in receipt["reasons"]


def test_true_wait_vs_partial_divergence_freezes_t0_without_outcome_count():
    receipt = observe(base_check(actual_decision_divergence=True, experimental_action_BTC_PARTIAL="BTC_PARTIAL"))
    assert receipt["status"] == "DIVERGENCE_CAPTURED"
    assert receipt["counts_as_outcome_row"] is False
    row = receipt["divergence_source_row"]
    assert row["benchmark_action_WAIT"] == "WAIT"
    assert row["experimental_action_BTC_PARTIAL"] == "BTC_PARTIAL"
    assert row["frozen_horizon_24h"] == "2026-08-13T06:00:00Z"
    assert row["frozen_horizon_72h"] == "2026-08-15T06:00:00Z"
    assert row["frozen_horizon_7d"] == "2026-08-19T06:00:00Z"
    assert row["return_at_horizon_pct"] is None
    assert row["framework_acceptance"] == "PENDING_OUTCOME_MATURITY"


def test_maturity_rejects_mutated_frozen_input():
    receipt = observe(base_check(actual_decision_divergence=True, experimental_action_BTC_PARTIAL="BTC_PARTIAL"))
    mutated = deepcopy(receipt)
    mutated["divergence_source_row"]["entry_reference_price"] = 1.0
    with pytest.raises(ValueError, match="frozen_input_mutation_detected"):
        mature(mutated, [], "2026-08-20T06:00:00Z")


def test_maturity_preserves_pending_and_missing_due_separately():
    receipt = observe(base_check(actual_decision_divergence=True, experimental_action_BTC_PARTIAL="BTC_PARTIAL"))
    observation_24h = {
        "horizon": "24H",
        "observed_at_utc": "2026-08-13T06:00:00Z",
        "return_pct": 1.2,
        "max_favorable_excursion_pct": 1.8,
        "max_adverse_excursion_pct": -0.7,
        "benchmark_return_pct": 0.0,
        "source_hash": "b" * 64,
        "source_provider": "OWNER_MARKET_DATA",
        "data_quality": "VERIFIED",
    }
    result = mature(receipt, [observation_24h], "2026-08-16T06:00:00Z")
    assert set(result["matured_horizons"]) == {"24H"}
    assert result["missing_due_horizons"] == ["72H"]
    assert result["pending_horizons"] == ["7D"]
    assert result["counts_as_outcome_row"] is False
    assert result["owner_attach_required_before_outcome_row_count"] is True


def test_coverage_gap_is_not_silently_counted_as_no_divergence():
    r1 = observe(base_check(check_id="A"))
    r2 = observe(base_check(check_id="B", actual_decision_divergence=True, experimental_action_BTC_PARTIAL="BTC_PARTIAL"))
    row_id = r2["divergence_source_row"]["row_id"]
    health = coverage_health(["A", "B", "C"], [r1, r2], [row_id])
    assert health["checks_total"] == 2
    assert health["no_divergence_checks"] == 1
    assert health["divergence_source_rows"] == 1
    assert health["matured_outcome_rows"] == 1
    assert health["coverage_gaps"] == 1
    assert health["coverage_gap_ids"] == ["C"]
    assert health["coverage_status"] == "GAP"
    assert health["coverage_receipts_are_outcome_evidence"] is False


def provider_scorecard():
    return {
        "active_provider": "Dune",
        "providers": [{"provider": "Dune", "state": "READY_FOR_TOOL_DISCOVERY"}],
    }


def deep_state():
    return {
        "active_research_id": "DRQ-001",
        "item_states": {"DRQ-001": {"state": "ACTIVE_READY_FOR_RESEARCH"}},
    }


def test_coordinator_uses_one_heavy_slot_and_keeps_passive_lane_independent():
    plan = build_plan(provider_scorecard(), deep_state())
    assert plan["heavy_execution"]["max_active_total"] == 1
    assert plan["heavy_execution"]["selected_next_lane"] == "deep_research"
    assert plan["passive_forward_evidence"]["allowed"] is True
    assert plan["passive_forward_evidence"]["consumes_heavy_slot"] is False
    assert not any(plan["authority"].values())


def test_coordinator_alternates_when_both_heavy_lanes_are_ready():
    after_deep = build_plan(provider_scorecard(), deep_state(), last_heavy_lane="deep_research")
    after_provider = build_plan(provider_scorecard(), deep_state(), last_heavy_lane="provider_evaluation")
    assert after_deep["heavy_execution"]["selected_next_lane"] == "provider_evaluation"
    assert after_provider["heavy_execution"]["selected_next_lane"] == "deep_research"


def test_active_heavy_lease_blocks_second_heavy_job_only():
    plan = build_plan(provider_scorecard(), deep_state(), active_heavy_lane="provider_evaluation")
    assert plan["heavy_execution"]["selected_next_lane"] is None
    assert plan["passive_forward_evidence"]["allowed"] is True
