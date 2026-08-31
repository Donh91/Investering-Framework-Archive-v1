import pytest

from scripts.intraday_execution.intraday_execution_research import (
    classify,
    legacy_event_policy,
    research_context_eligibility,
)


def cfg(*, warmup=0):
    return {
        "warmup_observations": warmup,
        "research_eligibility": {
            "status": "ENTRY_LEDGER_FORWARD_ONLY_OBSERVATION_CONTEXT_v1",
            "eligibility_semantics": "COLLECTION_ELIGIBILITY_ONLY_NOT_MARKET_PERMISSION",
            "required_source_owner": "HOURLY_SEQUENCE_COMPLETED_UTC_1H",
            "required_entry_contract": "ENTRY_SIGNAL_LATEST_v1",
            "required_entry_state": "WAIT",
            "required_promotion_status": "FORWARD_ONLY_NOT_PROMOTION_READY",
            "required_permits_active_state": False,
            "required_breadth_entry_permission": "RETIRED_ZERO_WEIGHT",
            "entry_signal_role": "FORWARD_ONLY_OBSERVATION_CONTEXT_NO_ELIGIBILITY_FROM_LEGACY_ACTIVE",
            "breadth_role": "DESCRIPTIVE_RESEARCH_CONTEXT_ZERO_EXECUTION_WEIGHT",
            "direction_confidence_role": "SHADOW_DIAGNOSTIC_ONLY_NO_REGIME_OR_ENTRY_PERMISSION",
        },
        "legacy_execution_event_ledger": {
            "status": "FROZEN_PENDING_SEPARATE_REGISTERED_TEST",
            "new_event_creation": False,
            "outcome_maturation": False,
            "historical_rows_preserved": True,
            "reason": "LEGACY_EXECUTION_EVENT_OUTCOME_LANE_HAS_NO_SEPARATE_ACTIVE_TEST_REGISTRY_BINDING",
            "authority": "RESEARCH_TELEMETRY_ONLY_NO_NEW_PROSPECTIVE_EVENT_OUTCOMES",
        },
        "authority": {
            "research_only": True,
            "portfolio_execution": False,
            "canonical_market_state": False,
            "automatic_rule_changes": False,
        },
    }


def valid_obs(*, entry_state="WAIT", breadth=0.5):
    neutral_asset = {
        "close": 100.0,
        "vwap_deviation_pct": 0.0,
        "rolling_relative_quote_volume": 1.0,
        "return_4h_pct": 0.0,
        "momentum_acceleration_1h_vs_prior3h_pp": 0.0,
        "taker_buy_quote_share": 0.5,
    }
    return {
        "hourly_sequence_run_id": "HOURLY_SEQUENCE_TEST",
        "entry_state": entry_state,
        "entry_context": {
            "contract": "ENTRY_SIGNAL_LATEST_v1",
            "definition_version": "ENTRY_SIGNAL_DEFINITION_v1_2_CANONICAL_PROMOTION_GUARD",
            "state": entry_state,
            "observer_state": "NO_PATTERN",
            "promotion_status": "FORWARD_ONLY_NOT_PROMOTION_READY",
            "permits_active_state": False,
            "breadth_entry_permission": "RETIRED_ZERO_WEIGHT",
            "breadth_semantics": "DESCRIPTIVE_PARTICIPATION_ZERO_EXECUTION_WEIGHT",
            "entry_authority": {
                "portfolio_execution": False,
                "canonical_market_state": False,
                "market_rule_change": False,
            },
        },
        "pullback_research_state": "REGIME_NOT_ACTIVE",
        "btc": dict(neutral_asset),
        "eth": dict(neutral_asset),
        "ethbtc": {"close": 0.03, "return_1h_pct": 0.0, "return_4h_pct": 0.0},
        "breadth": {"advance_ratio": breadth},
    }


def test_legacy_active_entry_state_is_rejected_even_with_valid_hourly_source():
    obs = valid_obs(entry_state="GRADUATED_ALTCOIN_TOPUP_ACTIVE", breadth=1.0)
    eligibility = research_context_eligibility(cfg(), obs)
    assert eligibility["eligible"] is False
    assert eligibility["reason"] == "ENTRY_OWNER_NOT_FORWARD_ONLY_WAIT_CONTEXT"
    state, evidence = classify(cfg(), [], obs, None)
    assert state == "REGIME_NOT_ACTIVE"
    assert evidence["research_eligibility"]["canonical_market_permission"] is False


def test_reactivated_breadth_entry_permission_is_rejected():
    obs = valid_obs(entry_state="WAIT", breadth=1.0)
    obs["entry_context"]["breadth_entry_permission"] = "ACTIVE_GATE"
    state, evidence = classify(cfg(), [], obs, None)
    assert state == "REGIME_NOT_ACTIVE"
    assert evidence["research_eligibility"]["reason"] == "BREADTH_ENTRY_PERMISSION_NOT_RETIRED_ZERO_WEIGHT"
    assert evidence["research_eligibility"]["breadth_role"] == "DESCRIPTIVE_RESEARCH_CONTEXT_ZERO_EXECUTION_WEIGHT"


def test_promotion_ready_or_permitted_active_state_is_not_silently_accepted():
    obs = valid_obs(entry_state="WAIT")
    obs["entry_context"]["promotion_status"] = "PROMOTED"
    obs["entry_context"]["permits_active_state"] = True
    eligibility = research_context_eligibility(cfg(), obs)
    assert eligibility["eligible"] is False
    assert eligibility["reason"] == "ENTRY_PROMOTION_CONTEXT_INCOMPATIBLE"


def test_missing_entry_owner_evidence_fails_closed():
    obs = valid_obs(entry_state="WAIT")
    obs["entry_context"] = {}
    eligibility = research_context_eligibility(cfg(), obs)
    assert eligibility["eligible"] is False
    assert eligibility["reason"] == "ENTRY_OWNER_CONTRACT_MISSING_OR_INCOMPATIBLE"


def test_missing_hourly_source_fails_closed_despite_valid_wait_context():
    obs = valid_obs(entry_state="WAIT")
    obs["hourly_sequence_run_id"] = None
    eligibility = research_context_eligibility(cfg(), obs)
    assert eligibility["eligible"] is False
    assert eligibility["reason"] == "COMPLETED_HOURLY_PRICE_CONTEXT_INSUFFICIENT"


@pytest.mark.parametrize("asset", ["btc", "eth", "ethbtc"])
@pytest.mark.parametrize("invalid_close", [True, float("nan"), float("inf"), -float("inf"), 0, -1, "100"])
def test_invalid_owner_price_cannot_authorize_research_collection(asset, invalid_close):
    obs = valid_obs(entry_state="WAIT")
    obs[asset]["close"] = invalid_close
    eligibility = research_context_eligibility(cfg(), obs)
    assert eligibility["eligible"] is False
    assert eligibility["reason"] == "COMPLETED_HOURLY_PRICE_CONTEXT_INSUFFICIENT"
    state, _ = classify(cfg(), [], obs, None)
    assert state == "REGIME_NOT_ACTIVE"


def test_valid_forward_only_wait_context_keeps_research_owner_alive():
    obs = valid_obs(entry_state="WAIT", breadth=0.5)
    eligibility = research_context_eligibility(cfg(), obs)
    assert eligibility["eligible"] is True
    assert eligibility["entry_signal_role"] == "FORWARD_ONLY_OBSERVATION_CONTEXT_NO_ELIGIBILITY_FROM_LEGACY_ACTIVE"
    assert eligibility["entry_promotion_status"] == "FORWARD_ONLY_NOT_PROMOTION_READY"
    assert eligibility["entry_permits_active_state"] is False
    assert eligibility["breadth_entry_permission"] == "RETIRED_ZERO_WEIGHT"
    assert eligibility["canonical_market_permission"] is False
    assert eligibility["portfolio_execution"] is False
    state, evidence = classify(cfg(), [], obs, None)
    assert state == "NORMAL"
    assert evidence["research_eligibility"]["status"] == "ELIGIBLE_RESEARCH_CONTEXT"


def test_direction_confidence_cannot_substitute_as_research_permission():
    obs = valid_obs(entry_state="WAIT")
    obs["entry_context"] = {}
    obs["shadow_direction_confidence"] = {"direction": "UP", "calibrated_probability": 99.0}
    eligibility = research_context_eligibility(cfg(), obs)
    assert eligibility["eligible"] is False
    assert eligibility["direction_confidence_role"] == "SHADOW_DIAGNOSTIC_ONLY_NO_REGIME_OR_ENTRY_PERMISSION"


def test_invalid_authority_fails_closed_even_with_valid_owner_context():
    local_cfg = cfg()
    local_cfg["authority"]["portfolio_execution"] = True
    eligibility = research_context_eligibility(local_cfg, valid_obs())
    assert eligibility["eligible"] is False
    assert eligibility["reason"] == "RESEARCH_AUTHORITY_BOUNDARY_INVALID"


def test_legacy_execution_event_lane_remains_frozen_without_separate_registered_test():
    policy = legacy_event_policy(cfg())
    assert policy["status"] == "FROZEN_PENDING_SEPARATE_REGISTERED_TEST"
    assert policy["new_event_creation"] is False
    assert policy["outcome_maturation"] is False
    assert policy["historical_rows_preserved"] is True


def test_readme_and_cowork_addendum_preserve_current_authority_contract():
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    for relative in (
        "04_MARKET_LEARNING/intraday_execution/README.md",
        "06_RESEARCH_LAB/historical_altseason_pullback_v1/INTRADAY_EXECUTION_COWORK_ADDENDUM.md",
    ):
        text = (root / relative).read_text()
        for token in (
            "ENTRY_SIGNAL_LATEST_v1", "WAIT", "FORWARD_ONLY_NOT_PROMOTION_READY",
            "permits_active_state: false", "RETIRED_ZERO_WEIGHT",
            "GRADUATED_ALTCOIN_TOPUP_ACTIVE", "zero execution weight",
            "FROZEN_PENDING_SEPARATE_REGISTERED_TEST", "new_event_creation: false",
            "outcome_maturation: false", "historical_rows_preserved: true",
            "INTRADAY_DIRECTION_CONFIDENCE_V1", "NO_EDGE",
        ):
            assert token in text, (relative, token)
        for retired_claim in ("inside an active regime", "once risk ownership is already permitted"):
            assert retired_claim not in text.lower(), (relative, retired_claim)
