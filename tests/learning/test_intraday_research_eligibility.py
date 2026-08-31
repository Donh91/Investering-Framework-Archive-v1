from scripts.intraday_execution.intraday_execution_research import (
    classify,
    legacy_event_policy,
    research_context_eligibility,
)


def cfg(*, warmup=0):
    return {
        "warmup_observations": warmup,
        "research_eligibility": {
            "status": "RESEARCH_ONLY_DATA_CONTEXT",
            "eligibility_semantics": "DATA_AVAILABLE_FOR_RESEARCH_NOT_MARKET_PERMISSION",
            "required_source_owner": "HOURLY_SEQUENCE_COMPLETED_UTC_1H",
            "entry_signal_role": "LEGACY_CONTEXT_ONLY_NO_ELIGIBILITY_OR_PERMISSION",
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
        "pullback_research_state": "REGIME_NOT_ACTIVE",
        "btc": dict(neutral_asset),
        "eth": dict(neutral_asset),
        "ethbtc": {"close": 0.03, "return_1h_pct": 0.0, "return_4h_pct": 0.0},
        "breadth": {"advance_ratio": breadth},
    }


def test_retired_entry_state_cannot_authorize_research_without_hourly_source():
    obs = valid_obs(entry_state="GRADUATED_ALTCOIN_TOPUP_ACTIVE", breadth=1.0)
    obs["hourly_sequence_run_id"] = None
    eligibility = research_context_eligibility(cfg(), obs)
    assert eligibility["eligible"] is False
    assert eligibility["reason"] == "COMPLETED_HOURLY_PRICE_CONTEXT_INSUFFICIENT"
    state, evidence = classify(cfg(), [], obs, None)
    assert state == "REGIME_NOT_ACTIVE"
    assert evidence["research_eligibility"]["canonical_market_permission"] is False


def test_proxy_or_extreme_breadth_cannot_authorize_research_without_hourly_source():
    obs = valid_obs(entry_state="WAIT", breadth=1.0)
    obs["hourly_sequence_run_id"] = None
    state, evidence = classify(cfg(), [], obs, None)
    assert state == "REGIME_NOT_ACTIVE"
    assert evidence["research_eligibility"]["breadth_role"] == "DESCRIPTIVE_RESEARCH_CONTEXT_ZERO_EXECUTION_WEIGHT"


def test_valid_nonbinding_hourly_context_keeps_research_owner_alive_with_wait_entry_state():
    obs = valid_obs(entry_state="WAIT", breadth=0.5)
    eligibility = research_context_eligibility(cfg(), obs)
    assert eligibility["eligible"] is True
    assert eligibility["entry_signal_role"] == "LEGACY_CONTEXT_ONLY_NO_ELIGIBILITY_OR_PERMISSION"
    assert eligibility["canonical_market_permission"] is False
    assert eligibility["portfolio_execution"] is False
    state, evidence = classify(cfg(), [], obs, None)
    assert state == "NORMAL"
    assert evidence["research_eligibility"]["status"] == "ELIGIBLE_RESEARCH_CONTEXT"


def test_direction_confidence_cannot_substitute_as_research_permission():
    obs = valid_obs(entry_state="WAIT")
    obs["hourly_sequence_run_id"] = None
    obs["shadow_direction_confidence"] = {"direction": "UP", "calibrated_probability": 99.0}
    eligibility = research_context_eligibility(cfg(), obs)
    assert eligibility["eligible"] is False
    assert eligibility["direction_confidence_role"] == "SHADOW_DIAGNOSTIC_ONLY_NO_REGIME_OR_ENTRY_PERMISSION"


def test_invalid_authority_fails_closed_even_with_valid_market_context():
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
