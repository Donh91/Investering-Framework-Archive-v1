import json
from datetime import datetime, timezone
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
    validate_repository as _validate_repository,
)
from scripts.intraday_execution import shadow_direction_confidence as owner
from scripts.intraday_execution.validate_direction_confidence import registry_binding_hash


def validate_repository(root, **kwargs):
    # Explicit synthetic clock; the production CLI always uses actual UTC time.
    return _validate_repository(root, now=kwargs.pop("now", datetime(2026, 9, 1, tzinfo=timezone.utc)), **kwargs)


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


def complete_ledger_fixture(tmp_path, *, with_outcome=True):
    root = setup_root(tmp_path)
    context = {"repository": owner.REPOSITORY, "ref": "refs/heads/main", "event": "schedule", "run_id": "12345", "run_attempt": "1", "commit_sha": "a" * 40}
    registration = {
        "contract": "INTRADAY_DIRECTION_REGISTRATION_v1",
        "registered_test_id": TEST_ID,
        "registered_at_utc": "2026-08-31T08:00:00Z",
        "production_context": context,
        "registry_binding_sha256": registry_binding_hash(root),
        "configuration_sha256": owner.content_hash(base_config()["shadow_direction_confidence"]),
        "forward_eligibility": "POST_REGISTRATION_CANONICAL_MAIN_ONLY",
        "prior_rows_adopted": 0,
    }
    registration["receipt_sha256"] = owner.content_hash(registration)
    write_json(root / owner.REGISTRATION, registration)
    source = root / "03_DAILY_CAPTURE_LOGS/hourly/2026/08/2026-08-31.csv"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("timestamp_utc,btc_close,eth_close,spot_status\n2026-08-31T09:00:00Z,100,100,PASS\n2026-08-31T10:00:00Z,101,101,PASS\n")
    pred_path = root / PREDICTIONS / "2026/08/31/pred.json"
    pred = prediction()
    pred.update(registered_test_id=TEST_ID, registration_receipt_sha256=registration["receipt_sha256"], production_context=context)
    write_json(pred_path, pred)
    outcome_path = root / OUTCOMES / "2026/08/31/outcome.json"
    row = outcome()
    evidence = owner._exact_hourly_close(datetime(2026, 8, 31, 11, tzinfo=timezone.utc), "BTC", root=root)
    row.update(registered_test_id=TEST_ID, registration_receipt_sha256=registration["receipt_sha256"], production_context=context, prediction_path=pred_path.relative_to(root).as_posix(), prediction_sha256=owner.file_hash(pred_path), evidence_source_path=evidence["source_path"], evidence_source_binding_sha256=evidence["source_binding_sha256"])
    if with_outcome:
        write_json(outcome_path, row)
    return root, pred_path, outcome_path, row


def test_complete_prediction_outcome_source_chain_passes(tmp_path):
    root, _, _, _ = complete_ledger_fixture(tmp_path)
    receipt = validate_repository(root)
    assert receipt["prediction_rows_validated"] == 1
    assert receipt["outcome_rows_validated"] == 1
    assert receipt["promotion_status"] == "NOT_PROMOTED_SHADOW_ONLY"


@pytest.mark.parametrize("change,error", [
    ({"prediction_path": "missing.json"}, "OUTCOME_FROZEN_PREDICTION_MISSING"),
    ({"measured_at_utc": "2026-08-31T10:30:00Z"}, "OUTCOME_MEASURED_BEFORE_DUE"),
    ({"actual_direction": "DOWN", "end_value": 99.0, "return_pct": -1.0, "result": "HIT"}, "OUTCOME_HIT_MISS_MISMATCH"),
    ({"return_pct": 100.0}, "OUTCOME_RETURN_MISMATCH"),
    ({"prediction_sha256": "0" * 64}, "OUTCOME_PREDICTION_HASH_MISMATCH"),
    ({"evidence_source_binding_sha256": "0" * 64}, "OUTCOME_SOURCE_BINDING_MISMATCH"),
    ({"calibration_group": "ETH:24H:DOWN:8_of_8"}, "OUTCOME_CALIBRATION_GROUP_DRIFT"),
    ({"production_context": {}}, "PRODUCTION_REPOSITORY_INVALID"),
])
def test_invalid_outcome_cannot_enter_calibration(tmp_path, change, error):
    root, _, path, row = complete_ledger_fixture(tmp_path)
    row.update(change)
    write_json(path, row)
    with pytest.raises(ValidationError, match=error):
        validate_repository(root)


def test_frozen_prediction_mutation_is_rejected(tmp_path):
    root, pred_path, _, _ = complete_ledger_fixture(tmp_path)
    pred = json.loads(pred_path.read_text())
    pred["horizons"]["1H"]["targets"]["BTC"]["calibration_key"] = "5_of_6"
    write_json(pred_path, pred)
    with pytest.raises(ValidationError, match="OUTCOME_PREDICTION_HASH_MISMATCH"):
        validate_repository(root)


def test_duplicate_source_candle_prediction_is_rejected(tmp_path):
    root, path, _, _ = complete_ledger_fixture(tmp_path, with_outcome=False)
    write_json(path.with_name("retry.json"), json.loads(path.read_text()))
    with pytest.raises(ValidationError, match="DUPLICATE_SOURCE_CANDLE_PREDICTION"):
        validate_repository(root)


def test_duplicate_outcome_is_rejected(tmp_path):
    root, _, path, row = complete_ledger_fixture(tmp_path)
    write_json(path.with_name("duplicate.json"), row)
    with pytest.raises(ValidationError, match="DUPLICATE_OUTCOME"):
        validate_repository(root)


def test_prior_registration_and_branch_qa_rows_are_rejected(tmp_path):
    root, path, _, _ = complete_ledger_fixture(tmp_path, with_outcome=False)
    row = json.loads(path.read_text())
    row["production_context"]["ref"] = "refs/heads/agent/task-fixture"
    write_json(path, row)
    with pytest.raises(ValidationError, match="PRODUCTION_MAIN_REF_REQUIRED"):
        validate_repository(root)


def test_no_registration_cannot_adopt_qa_rows(tmp_path):
    root = setup_root(tmp_path)
    write_json(root / PREDICTIONS / "qa.json", prediction())
    with pytest.raises(ValidationError, match="REGISTRATION_RECEIPT_MISSING"):
        validate_repository(root)


def test_claimed_probability_requires_observable_prior_outcomes(tmp_path):
    root, path, _, _ = complete_ledger_fixture(tmp_path, with_outcome=False)
    row = json.loads(path.read_text())
    row["horizons"]["1H"]["targets"]["BTC"].update(frozen_calibrated_probability_pct=73.0, confidence_status_at_issue="EARLY_CALIBRATION", independent_calibration_samples_at_issue=20)
    write_json(path, row)
    with pytest.raises(ValidationError, match="PREDICTION_PROBABILITY_WITHOUT_PRIOR_CALIBRATION"):
        validate_repository(root)


def test_validator_rejects_insufficient_forward_span(tmp_path):
    root, path, _, _ = complete_ledger_fixture(tmp_path, with_outcome=False)
    row = json.loads(path.read_text())
    row["issued_at_utc"] = "2026-08-31T10:40:00Z"
    write_json(path, row)
    with pytest.raises(ValidationError, match="PREDICTION_INSUFFICIENT_FORWARD_SPAN"):
        validate_repository(root)


def test_outcome_cannot_be_asserted_from_a_future_clock(tmp_path):
    root, _, _, _ = complete_ledger_fixture(tmp_path)
    with pytest.raises(ValidationError, match="OUTCOME_MEASURED_IN_FUTURE"):
        validate_repository(root, now=datetime(2026, 8, 31, 10, 30, tzinfo=timezone.utc))
