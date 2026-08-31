import json
from pathlib import Path

import pytest

from scripts.intraday_execution.validate_direction_confidence import (
    BENCHMARK,
    CONFIG,
    OUTCOMES,
    PREDICTIONS,
    REGISTRY,
    TEST_ID,
    ValidationError,
    validate_repository,
)


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def base_config() -> dict:
    return {
        "contract": "INTRADAY_EXECUTION_RESEARCH_CONFIG_v1",
        "shadow_direction_confidence": {
            "status": "SHADOW_ONLY_PROSPECTIVE",
            "registered_test_id": TEST_ID,
            "active_test_registry_path": str(REGISTRY),
            "validator_path": "scripts/intraday_execution/validate_direction_confidence.py",
            "scorer_path": "scripts/intraday_execution/shadow_direction_confidence.py",
            "benchmark": BENCHMARK,
            "forward_eligibility_rule": "POST_REGISTRATION_CANONICAL_MAIN_ONLY",
            "pre_registration_rows": "INELIGIBLE_QA_OR_INITIALIZATION_ONLY",
            "direction_horizons_hours": [1, 4, 24],
            "source_owner_required_cadence_hours": 1,
            "source_owner_required_semantics": "COMPLETED_UTC_1H_CANDLES",
            "minimum_direction_families": 4,
            "minimum_vote_margin": 2,
            "max_prediction_issue_lag_minutes": 90,
            "minimum_remaining_fraction_of_horizon": 0.5,
            "max_outcome_evidence_lag_hours": 1.5,
            "minimum_independent_calibration_samples": 20,
            "strong_calibration_samples": 50,
            "high_assurance_minimum_independent_samples": 300,
            "high_assurance_wilson_floor": 0.97,
            "probability_rule": "NO_NUMERIC_PROBABILITY_BEFORE_MINIMUM_INDEPENDENT_SAMPLE",
            "forecast_horizon_semantics": "CLOSED_1H_CANDLE_CLOSE_OBSERVATION_TO_EXACT_HORIZON_DUE",
            "outcome_evidence_rule": "EXACT_DUE_CLOSED_1H_OWNER_CANDLE_ONLY_NO_LATER_PRICE_SUBSTITUTION",
            "automatic_signal_reweighting": False,
            "microcap_direction": "NO_EDGE_UNTIL_ELIGIBLE_OWNER_EXISTS",
        },
        "authority": {
            "research_only": True,
            "portfolio_execution": False,
            "canonical_market_state": False,
            "automatic_rule_changes": False,
        },
    }


def registry_text() -> str:
    return f"""
## T12 - Intraday Direction Confidence Calibration
```yaml
test_id: {TEST_ID}
status: ACTIVE_REGISTRATION_REPAIR_WARMUP
start: FIRST_CANONICAL_MAIN_RUN_AFTER_REGISTRATION_MERGE_AND_VALIDATOR_PASS
prior_rows_status: PRE_REGISTRATION_QA_OR_INITIALIZATION_NOT_FORWARD_EVIDENCE
benchmark: {BENCHMARK}
validator_path: scripts/intraday_execution/validate_direction_confidence.py
scorer_path: scripts/intraday_execution/shadow_direction_confidence.py
authority: SHADOW_ONLY_RESEARCH_NON_CANONICAL
```
"""


def setup_root(tmp_path: Path) -> Path:
    registry = tmp_path / REGISTRY
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(registry_text(), encoding="utf-8")
    write_json(tmp_path / CONFIG, base_config())
    return tmp_path


def prediction(direction: str = "UP", probability=None) -> dict:
    target = {
        "direction": direction,
        "start_value": 100.0,
        "evidence_agreement_pct": 66.67,
        "calibration_key": "4_of_6",
        "votes": [],
        "frozen_calibrated_probability_pct": probability,
        "confidence_status_at_issue": "WARMUP" if probability is None else "CALIBRATED",
    }
    return {
        "contract": "INTRADAY_DIRECTION_PREDICTION_v1",
        "issued_at_utc": "2026-08-31T10:10:00Z",
        "source_candle_open_utc": "2026-08-31T09:00:00Z",
        "source_price_observation_utc": "2026-08-31T10:00:00Z",
        "source_observation_semantics": "CLOSED_1H_CANDLE_CLOSE_OBSERVABLE_TIME",
        "source_lag_minutes": 10.0,
        "hourly_sequence_run_id": "fixture",
        "horizons": {
            "1H": {
                "horizon_hours": 1,
                "status": "ELIGIBLE",
                "source_cutoff_utc": "2026-08-31T10:00:00Z",
                "due_at_utc": "2026-08-31T11:00:00Z",
                "remaining_forward_hours_at_issue": 0.833333,
                "minimum_remaining_forward_hours": 0.5,
                "targets": {"BTC": dict(target), "ETH": dict(target)},
            }
        },
        "authority": {
            "shadow_only": True,
            "candidate_is_portfolio_action": False,
            "canonical_market_state": False,
            "automatic_rule_changes": False,
        },
    }


def outcome(evidence_time: str = "2026-08-31T11:00:00Z") -> dict:
    return {
        "contract": "INTRADAY_DIRECTION_OUTCOME_v1",
        "issued_at_utc": "2026-08-31T10:10:00Z",
        "source_price_observation_utc": "2026-08-31T10:00:00Z",
        "source_candle_open_utc": "2026-08-31T09:00:00Z",
        "due_at_utc": "2026-08-31T11:00:00Z",
        "measured_at_utc": "2026-08-31T11:15:00Z",
        "target": "BTC",
        "horizon_hours": 1,
        "predicted_direction": "UP",
        "calibration_key": "4_of_6",
        "calibration_group": "BTC:1H:UP:4_of_6",
        "votes": [],
        "frozen_calibrated_probability_pct": None,
        "status": "MATURED",
        "result": "HIT",
        "start_value": 100.0,
        "end_value": 101.0,
        "return_pct": 1.0,
        "actual_direction": "UP",
        "evidence_observation_utc": evidence_time,
        "evidence_candle_open_utc": "2026-08-31T10:00:00Z",
        "evidence_source_path": "03_DAILY_CAPTURE_LOGS/hourly/fixture.csv",
        "evidence_semantics": "EXACT_DUE_CLOSED_1H_OWNER_CANDLE",
        "evidence_horizon_error_hours": 0.0,
        "adjudication_delay_hours": 0.25,
        "brier_score": None,
        "miss_analysis": {"families_aligned_with_actual": [], "families_opposed_to_actual": []},
        "authority": {
            "shadow_only": True,
            "automatic_rule_changes": False,
            "portfolio_execution": False,
        },
    }


def test_registered_empty_repository_passes(tmp_path):
    root = setup_root(tmp_path)
    receipt = validate_repository(root)
    assert receipt["status"] == "PASS"
    assert receipt["registered_test_id"] == TEST_ID
    assert receipt["prediction_rows_validated"] == 0
    assert receipt["outcome_rows_validated"] == 0


def test_missing_registration_fails_closed(tmp_path):
    root = setup_root(tmp_path)
    (root / REGISTRY).write_text("# Active Test Registry\n", encoding="utf-8")
    with pytest.raises(ValidationError, match="ACTIVE_TEST_REGISTRY_BINDING_MISSING"):
        validate_repository(root)


def test_candle_open_used_as_observation_is_rejected(tmp_path):
    root = setup_root(tmp_path)
    row = prediction()
    row["source_price_observation_utc"] = row["source_candle_open_utc"]
    row["horizons"]["1H"]["source_cutoff_utc"] = row["source_candle_open_utc"]
    row["horizons"]["1H"]["due_at_utc"] = "2026-08-31T10:00:00Z"
    write_json(root / PREDICTIONS / "2026/08/31/pred.json", row)
    with pytest.raises(ValidationError, match="PREDICTION_CANDLE_CLOSE_ANCHOR_INVALID"):
        validate_repository(root)


def test_no_edge_numeric_probability_is_rejected(tmp_path):
    root = setup_root(tmp_path)
    row = prediction(direction="NO_EDGE", probability=88.0)
    write_json(root / PREDICTIONS / "2026/08/31/pred.json", row)
    with pytest.raises(ValidationError, match="NO_EDGE_NUMERIC_PROBABILITY_FORBIDDEN"):
        validate_repository(root)


def test_later_price_cannot_substitute_for_exact_due_outcome(tmp_path):
    root = setup_root(tmp_path)
    write_json(root / OUTCOMES / "2026/08/31/outcome.json", outcome("2026-08-31T12:00:00Z"))
    with pytest.raises(ValidationError, match="OUTCOME_EVIDENCE_NOT_EXACT_DUE"):
        validate_repository(root)


def test_probability_before_minimum_calibration_sample_is_rejected(tmp_path):
    root = setup_root(tmp_path)
    write_json(
        root / "04_MARKET_LEARNING/intraday_execution/DIRECTION_CALIBRATION.json",
        {
            "contract": "INTRADAY_DIRECTION_CALIBRATION_v1",
            "generated_at_utc": "2026-08-31T10:15:00Z",
            "scored_outcome_count": 19,
            "groups": {
                "BTC:1H:UP:4_of_6": {
                    "independent_count": 19,
                    "display_probability": 0.8,
                    "maturity": "EARLY_CALIBRATION",
                    "wilson_lower_95": 0.6,
                }
            },
            "family_reliability": {},
            "governance": {
                "shadow_only": True,
                "automatic_signal_reweighting": False,
                "canonical_market_state": False,
                "portfolio_execution": False,
            },
        },
    )
    with pytest.raises(ValidationError, match="CALIBRATION_PREMATURE_PROBABILITY"):
        validate_repository(root)


def test_censored_missing_exact_due_requires_substitution_guard(tmp_path):
    root = setup_root(tmp_path)
    row = outcome()
    row = {
        key: value
        for key, value in row.items()
        if key
        not in {
            "result",
            "start_value",
            "end_value",
            "return_pct",
            "actual_direction",
            "evidence_observation_utc",
            "evidence_candle_open_utc",
            "evidence_source_path",
            "evidence_semantics",
            "evidence_horizon_error_hours",
            "adjudication_delay_hours",
            "brier_score",
            "miss_analysis",
        }
    }
    row["status"] = "CENSORED"
    row["reason"] = "EXACT_DUE_OWNER_CANDLE_MISSING_AFTER_GRACE"
    row["substitute_later_price_forbidden"] = False
    write_json(root / OUTCOMES / "2026/08/31/outcome.json", row)
    with pytest.raises(ValidationError, match="OUTCOME_LATER_PRICE_GUARD_MISSING"):
        validate_repository(root)
