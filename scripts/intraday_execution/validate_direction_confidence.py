#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

TEST_ID = "INTRADAY_DIRECTION_CONFIDENCE_V1"
REGISTRY = Path("06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md")
CONFIG = Path("04_MARKET_LEARNING/intraday_execution/config.json")
PREDICTIONS = Path("04_MARKET_LEARNING/intraday_execution/direction_predictions")
OUTCOMES = Path("04_MARKET_LEARNING/intraday_execution/direction_outcomes")
CALIBRATION = Path("04_MARKET_LEARNING/intraday_execution/DIRECTION_CALIBRATION.json")
VALIDATION = Path("04_MARKET_LEARNING/intraday_execution/DIRECTION_VALIDATION.json")
SCORER_PATH = "scripts/intraday_execution/shadow_direction_confidence.py"
VALIDATOR_PATH = "scripts/intraday_execution/validate_direction_confidence.py"
BENCHMARK = "NO_SKILL_DIRECTION_PROBABILITY_0_50_BRIER_0_25"


class ValidationError(RuntimeError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValidationError(f"JSON_READ_FAILED:{path}:{exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"JSON_OBJECT_REQUIRED:{path}")
    return value


def parse_utc(value: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception as exc:
        raise ValidationError(f"TIMESTAMP_INVALID:{value}") from exc
    if dt.tzinfo is None:
        raise ValidationError(f"TIMESTAMP_TIMEZONE_REQUIRED:{value}")
    return dt.astimezone(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ValidationError(code)


def iter_json(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*.json") if path.is_file())


def validate_registry(root: Path) -> None:
    path = root / REGISTRY
    require(path.exists(), "ACTIVE_TEST_REGISTRY_MISSING")
    text = path.read_text(encoding="utf-8")
    required = [
        f"test_id: {TEST_ID}",
        "status: ACTIVE_REGISTRATION_REPAIR_WARMUP",
        "start: FIRST_CANONICAL_MAIN_RUN_AFTER_REGISTRATION_MERGE_AND_VALIDATOR_PASS",
        f"benchmark: {BENCHMARK}",
        f"validator_path: {VALIDATOR_PATH}",
        f"scorer_path: {SCORER_PATH}",
        "authority: SHADOW_ONLY_RESEARCH_NON_CANONICAL",
        "prior_rows_status: PRE_REGISTRATION_QA_OR_INITIALIZATION_NOT_FORWARD_EVIDENCE",
    ]
    for token in required:
        require(token in text, f"ACTIVE_TEST_REGISTRY_BINDING_MISSING:{token}")


def validate_config(root: Path) -> dict[str, Any]:
    cfg = read_json(root / CONFIG)
    require(cfg.get("contract") == "INTRADAY_EXECUTION_RESEARCH_CONFIG_v1", "CONFIG_CONTRACT_INVALID")
    authority = cfg.get("authority") or {}
    require(authority.get("research_only") is True, "CONFIG_RESEARCH_ONLY_REQUIRED")
    require(authority.get("portfolio_execution") is False, "CONFIG_PORTFOLIO_AUTHORITY_FORBIDDEN")
    require(authority.get("canonical_market_state") is False, "CONFIG_CANONICAL_STATE_FORBIDDEN")
    require(authority.get("automatic_rule_changes") is False, "CONFIG_AUTOMATIC_RULE_CHANGE_FORBIDDEN")

    shadow = cfg.get("shadow_direction_confidence") or {}
    require(shadow.get("status") == "SHADOW_ONLY_PROSPECTIVE", "SHADOW_STATUS_INVALID")
    require(shadow.get("registered_test_id") == TEST_ID, "SHADOW_TEST_ID_UNBOUND")
    require(shadow.get("active_test_registry_path") == str(REGISTRY), "SHADOW_REGISTRY_PATH_UNBOUND")
    require(shadow.get("validator_path") == VALIDATOR_PATH, "SHADOW_VALIDATOR_PATH_UNBOUND")
    require(shadow.get("scorer_path") == SCORER_PATH, "SHADOW_SCORER_PATH_UNBOUND")
    require(shadow.get("benchmark") == BENCHMARK, "SHADOW_BENCHMARK_UNBOUND")
    require(shadow.get("forward_eligibility_rule") == "POST_REGISTRATION_CANONICAL_MAIN_ONLY", "SHADOW_FORWARD_ELIGIBILITY_UNBOUND")
    require(shadow.get("pre_registration_rows") == "INELIGIBLE_QA_OR_INITIALIZATION_ONLY", "SHADOW_PRE_REGISTRATION_RULE_UNBOUND")
    require(shadow.get("source_owner_required_cadence_hours") == 1, "SOURCE_OWNER_CADENCE_NOT_1H")
    require(shadow.get("source_owner_required_semantics") == "COMPLETED_UTC_1H_CANDLES", "SOURCE_OWNER_SEMANTICS_INVALID")
    require(
        shadow.get("forecast_horizon_semantics")
        == "CLOSED_1H_CANDLE_CLOSE_OBSERVATION_TO_EXACT_HORIZON_DUE",
        "FORECAST_HORIZON_SEMANTICS_INVALID",
    )
    require(
        shadow.get("outcome_evidence_rule")
        == "EXACT_DUE_CLOSED_1H_OWNER_CANDLE_ONLY_NO_LATER_PRICE_SUBSTITUTION",
        "OUTCOME_EVIDENCE_RULE_INVALID",
    )
    require(
        shadow.get("probability_rule") == "NO_NUMERIC_PROBABILITY_BEFORE_MINIMUM_INDEPENDENT_SAMPLE",
        "PROBABILITY_RULE_INVALID",
    )
    require(shadow.get("automatic_signal_reweighting") is False, "AUTOMATIC_REWEIGHTING_FORBIDDEN")
    require(shadow.get("microcap_direction") == "NO_EDGE_UNTIL_ELIGIBLE_OWNER_EXISTS", "MICROCAP_FAIL_CLOSED_REQUIRED")
    require(int(shadow.get("minimum_independent_calibration_samples", 0)) >= 20, "MINIMUM_CALIBRATION_SAMPLE_TOO_LOW")
    require(int(shadow.get("high_assurance_minimum_independent_samples", 0)) >= 300, "HIGH_ASSURANCE_SAMPLE_TOO_LOW")
    require(float(shadow.get("high_assurance_wilson_floor", 0.0)) >= 0.97, "HIGH_ASSURANCE_WILSON_TOO_LOW")
    return shadow


def validate_prediction(path: Path, cfg: dict[str, Any]) -> None:
    row = read_json(path)
    require(row.get("contract") == "INTRADAY_DIRECTION_PREDICTION_v1", f"PREDICTION_CONTRACT_INVALID:{path}")
    authority = row.get("authority") or {}
    require(authority.get("shadow_only") is True, f"PREDICTION_SHADOW_ONLY_REQUIRED:{path}")
    require(authority.get("candidate_is_portfolio_action") is False, f"PREDICTION_PORTFOLIO_AUTHORITY_FORBIDDEN:{path}")
    require(authority.get("canonical_market_state") is False, f"PREDICTION_CANONICAL_STATE_FORBIDDEN:{path}")
    require(authority.get("automatic_rule_changes") is False, f"PREDICTION_AUTOMATIC_RULE_CHANGE_FORBIDDEN:{path}")
    require(row.get("source_observation_semantics") == "CLOSED_1H_CANDLE_CLOSE_OBSERVABLE_TIME", f"PREDICTION_SOURCE_SEMANTICS_INVALID:{path}")

    issued = parse_utc(str(row.get("issued_at_utc")))
    candle_open = parse_utc(str(row.get("source_candle_open_utc")))
    observed = parse_utc(str(row.get("source_price_observation_utc")))
    require(observed - candle_open == timedelta(hours=1), f"PREDICTION_CANDLE_CLOSE_ANCHOR_INVALID:{path}")
    require(issued >= observed, f"PREDICTION_ISSUED_BEFORE_SOURCE_CLOSE:{path}")
    lag_minutes = (issued - observed).total_seconds() / 60.0
    require(lag_minutes <= float(cfg.get("max_prediction_issue_lag_minutes", 90)), f"PREDICTION_SOURCE_TOO_STALE:{path}")

    horizons = row.get("horizons") or {}
    require(isinstance(horizons, dict) and horizons, f"PREDICTION_HORIZONS_MISSING:{path}")
    allowed_horizons = {int(v) for v in cfg.get("direction_horizons_hours", [1, 4, 24])}
    for key, horizon_row in horizons.items():
        require(isinstance(horizon_row, dict), f"PREDICTION_HORIZON_ROW_INVALID:{path}:{key}")
        horizon = int(horizon_row.get("horizon_hours"))
        require(horizon in allowed_horizons, f"PREDICTION_HORIZON_UNREGISTERED:{path}:{horizon}")
        due = parse_utc(str(horizon_row.get("due_at_utc")))
        cutoff = parse_utc(str(horizon_row.get("source_cutoff_utc")))
        require(cutoff == observed, f"PREDICTION_SOURCE_CUTOFF_DRIFT:{path}:{key}")
        require(due - observed == timedelta(hours=horizon), f"PREDICTION_DUE_NOT_EXACT_HORIZON:{path}:{key}")
        targets = horizon_row.get("targets") or {}
        require(set(targets) == {"BTC", "ETH"}, f"PREDICTION_TARGET_SET_INVALID:{path}:{key}")
        for target, target_row in targets.items():
            direction = target_row.get("direction")
            require(direction in {"UP", "DOWN", "NO_EDGE"}, f"PREDICTION_DIRECTION_INVALID:{path}:{key}:{target}")
            require(isinstance(target_row.get("start_value"), (int, float)), f"PREDICTION_START_VALUE_MISSING:{path}:{key}:{target}")
            agreement = target_row.get("evidence_agreement_pct")
            require(agreement is None or (isinstance(agreement, (int, float)) and 0.0 <= float(agreement) <= 100.0), f"PREDICTION_AGREEMENT_INVALID:{path}:{key}:{target}")
            probability = target_row.get("frozen_calibrated_probability_pct")
            require(probability is None or (isinstance(probability, (int, float)) and 0.0 <= float(probability) <= 100.0), f"PREDICTION_PROBABILITY_INVALID:{path}:{key}:{target}")
            if direction == "NO_EDGE":
                require(probability is None, f"NO_EDGE_NUMERIC_PROBABILITY_FORBIDDEN:{path}:{key}:{target}")


def validate_outcome(path: Path, cfg: dict[str, Any]) -> None:
    row = read_json(path)
    require(row.get("contract") == "INTRADAY_DIRECTION_OUTCOME_v1", f"OUTCOME_CONTRACT_INVALID:{path}")
    authority = row.get("authority") or {}
    require(authority.get("shadow_only") is True, f"OUTCOME_SHADOW_ONLY_REQUIRED:{path}")
    require(authority.get("automatic_rule_changes") is False, f"OUTCOME_AUTOMATIC_RULE_CHANGE_FORBIDDEN:{path}")
    require(authority.get("portfolio_execution") is False, f"OUTCOME_PORTFOLIO_AUTHORITY_FORBIDDEN:{path}")

    observed = parse_utc(str(row.get("source_price_observation_utc")))
    due = parse_utc(str(row.get("due_at_utc")))
    horizon = int(row.get("horizon_hours"))
    require(horizon in {int(v) for v in cfg.get("direction_horizons_hours", [1, 4, 24])}, f"OUTCOME_HORIZON_UNREGISTERED:{path}")
    require(due - observed == timedelta(hours=horizon), f"OUTCOME_DUE_NOT_EXACT_HORIZON:{path}")
    predicted = row.get("predicted_direction")
    require(predicted in {"UP", "DOWN", "NO_EDGE"}, f"OUTCOME_PREDICTION_INVALID:{path}")

    status = row.get("status")
    require(status in {"MATURED", "CENSORED"}, f"OUTCOME_STATUS_INVALID:{path}")
    if status == "CENSORED":
        if row.get("reason") == "EXACT_DUE_OWNER_CANDLE_MISSING_AFTER_GRACE":
            require(row.get("substitute_later_price_forbidden") is True, f"OUTCOME_LATER_PRICE_GUARD_MISSING:{path}")
        return

    evidence_time = parse_utc(str(row.get("evidence_observation_utc")))
    require(evidence_time == due, f"OUTCOME_EVIDENCE_NOT_EXACT_DUE:{path}")
    require(float(row.get("evidence_horizon_error_hours", 999.0)) == 0.0, f"OUTCOME_HORIZON_ERROR_NONZERO:{path}")
    require(row.get("evidence_semantics") == "EXACT_DUE_CLOSED_1H_OWNER_CANDLE", f"OUTCOME_EVIDENCE_SEMANTICS_INVALID:{path}")
    require(isinstance(row.get("start_value"), (int, float)), f"OUTCOME_START_VALUE_MISSING:{path}")
    require(isinstance(row.get("end_value"), (int, float)), f"OUTCOME_END_VALUE_MISSING:{path}")
    actual = row.get("actual_direction")
    require(actual in {"UP", "DOWN", "FLAT"}, f"OUTCOME_ACTUAL_DIRECTION_INVALID:{path}")
    result = row.get("result")
    if predicted == "NO_EDGE":
        require(result == "ABSTAINED", f"NO_EDGE_MUST_ABSTAIN:{path}")
        require(row.get("brier_score") is None, f"NO_EDGE_BRIER_FORBIDDEN:{path}")
    else:
        require(result in {"HIT", "MISS"}, f"DIRECTIONAL_RESULT_INVALID:{path}")
        p = row.get("frozen_calibrated_probability_pct")
        if p is None:
            require(row.get("brier_score") is None, f"UNSCORED_PROBABILITY_HAS_BRIER:{path}")
        else:
            require(isinstance(p, (int, float)) and 0.0 <= float(p) <= 100.0, f"OUTCOME_PROBABILITY_INVALID:{path}")
            require(isinstance(row.get("brier_score"), (int, float)), f"CALIBRATED_OUTCOME_BRIER_MISSING:{path}")


def validate_calibration(root: Path, cfg: dict[str, Any]) -> None:
    path = root / CALIBRATION
    if not path.exists():
        return
    row = read_json(path)
    require(row.get("contract") == "INTRADAY_DIRECTION_CALIBRATION_v1", "CALIBRATION_CONTRACT_INVALID")
    governance = row.get("governance") or {}
    require(governance.get("shadow_only") is True, "CALIBRATION_SHADOW_ONLY_REQUIRED")
    require(governance.get("automatic_signal_reweighting") is False, "CALIBRATION_AUTOMATIC_REWEIGHTING_FORBIDDEN")
    require(governance.get("canonical_market_state") is False, "CALIBRATION_CANONICAL_STATE_FORBIDDEN")
    require(governance.get("portfolio_execution") is False, "CALIBRATION_PORTFOLIO_AUTHORITY_FORBIDDEN")
    minimum = int(cfg.get("minimum_independent_calibration_samples", 20))
    for group_id, group in (row.get("groups") or {}).items():
        count = int(group.get("independent_count", 0))
        display = group.get("display_probability")
        maturity = group.get("maturity")
        if count < minimum:
            require(display is None, f"CALIBRATION_PREMATURE_PROBABILITY:{group_id}")
            require(maturity == "WARMUP", f"CALIBRATION_PREMATURE_MATURITY:{group_id}")
        if display is not None:
            require(isinstance(display, (int, float)) and 0.0 <= float(display) <= 1.0, f"CALIBRATION_PROBABILITY_RANGE_INVALID:{group_id}")
        if maturity == "HIGH_ASSURANCE_99_ELIGIBLE":
            require(count >= int(cfg.get("high_assurance_minimum_independent_samples", 300)), f"HIGH_ASSURANCE_SAMPLE_GATE_BROKEN:{group_id}")
            require(float(group.get("wilson_lower_95", 0.0)) >= float(cfg.get("high_assurance_wilson_floor", 0.97)), f"HIGH_ASSURANCE_WILSON_GATE_BROKEN:{group_id}")


def validate_repository(root: Path, write_receipt: bool = False) -> dict[str, Any]:
    validate_registry(root)
    cfg = validate_config(root)
    prediction_paths = iter_json(root / PREDICTIONS)
    outcome_paths = iter_json(root / OUTCOMES)
    for path in prediction_paths:
        validate_prediction(path, cfg)
    for path in outcome_paths:
        validate_outcome(path, cfg)
    validate_calibration(root, cfg)

    receipt = {
        "contract": "INTRADAY_DIRECTION_VALIDATION_v1",
        "registered_test_id": TEST_ID,
        "generated_at_utc": iso(datetime.now(timezone.utc)),
        "status": "PASS",
        "prediction_rows_validated": len(prediction_paths),
        "outcome_rows_validated": len(outcome_paths),
        "benchmark": BENCHMARK,
        "row_validity": "PASS",
        "coverage_readiness": "SEPARATE_NOT_INFERRED",
        "promotion_status": "NOT_PROMOTED_SHADOW_ONLY",
        "authority": {
            "canonical_market_state": False,
            "portfolio_execution": False,
            "automatic_rule_changes": False,
        },
    }
    if write_receipt:
        target = root / VALIDATION
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    try:
        receipt = validate_repository(args.root.resolve(), write_receipt=args.write_receipt)
    except ValidationError as exc:
        print(json.dumps({"contract": "INTRADAY_DIRECTION_VALIDATION_v1", "status": "FAIL", "error": str(exc)}, sort_keys=True))
        raise SystemExit(1)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
