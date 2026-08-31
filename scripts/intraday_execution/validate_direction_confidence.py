#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    from scripts.intraday_execution import shadow_direction_confidence as owner
except ModuleNotFoundError:
    import shadow_direction_confidence as owner

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


def validate_registry(root: Path) -> str:
    path = root / REGISTRY
    require(path.exists(), "ACTIVE_TEST_REGISTRY_MISSING")
    text = path.read_text(encoding="utf-8")
    bindings = [block for block in re.findall(r"```yaml\s*\n(.*?)```", text, re.S)
                if re.search(rf"^test_id: {TEST_ID}\s*$", block, re.M)]
    require(len(bindings) == 1, "ACTIVE_TEST_REGISTRY_BINDING_MISSING_OR_AMBIGUOUS")
    text = bindings[0]
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
    return text


def registry_binding_hash(root: Path) -> str:
    return hashlib.sha256(validate_registry(root).encode()).hexdigest()


def validate_production_context(context: dict[str, Any]) -> None:
    require(context.get("repository") == owner.REPOSITORY, "PRODUCTION_REPOSITORY_INVALID")
    require(context.get("ref") == "refs/heads/main", "PRODUCTION_MAIN_REF_REQUIRED")
    require(context.get("event") in {"schedule", "workflow_dispatch"}, "PRODUCTION_EVENT_INVALID")
    require(str(context.get("run_id", "")).isdigit(), "PRODUCTION_RUN_ID_REQUIRED")
    require(bool(re.fullmatch(r"[0-9a-f]{40}", str(context.get("commit_sha", "")))), "PRODUCTION_COMMIT_REQUIRED")


def validate_registration(root: Path, cfg: dict[str, Any], now: datetime) -> dict[str, Any]:
    path = root / owner.REGISTRATION
    require(path.exists(), "REGISTRATION_RECEIPT_MISSING")
    row = read_json(path)
    require(row.get("contract") == "INTRADAY_DIRECTION_REGISTRATION_v1", "REGISTRATION_CONTRACT_INVALID")
    require(row.get("registered_test_id") == TEST_ID, "REGISTRATION_TEST_ID_INVALID")
    require(parse_utc(str(row.get("registered_at_utc"))) <= now, "REGISTRATION_IN_FUTURE")
    require(row.get("forward_eligibility") == "POST_REGISTRATION_CANONICAL_MAIN_ONLY", "REGISTRATION_FORWARD_RULE_INVALID")
    require(row.get("prior_rows_adopted") == 0, "REGISTRATION_PRIOR_ROWS_FORBIDDEN")
    validate_production_context(row.get("production_context") or {})
    require(row.get("registry_binding_sha256") == registry_binding_hash(root), "REGISTRATION_REGISTRY_HASH_MISMATCH")
    require(row.get("configuration_sha256") == owner.content_hash(cfg), "REGISTRATION_CONFIG_HASH_MISMATCH")
    require(row.get("receipt_sha256") == owner.content_hash({k: v for k, v in row.items() if k != "receipt_sha256"}), "REGISTRATION_RECEIPT_HASH_MISMATCH")
    return row


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


def validate_prediction(path: Path, cfg: dict[str, Any], now: datetime | None = None) -> None:
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
    if now is not None:
        require(issued <= now, f"PREDICTION_ISSUED_IN_FUTURE:{path}")
    lag_minutes = (issued - observed).total_seconds() / 60.0
    require(lag_minutes <= float(cfg.get("max_prediction_issue_lag_minutes", 90)), f"PREDICTION_SOURCE_TOO_STALE:{path}")

    horizons = row.get("horizons") or {}
    require(isinstance(horizons, dict) and horizons, f"PREDICTION_HORIZONS_MISSING:{path}")
    allowed_horizons = {int(v) for v in cfg.get("direction_horizons_hours", [1, 4, 24])}
    for key, horizon_row in horizons.items():
        require(isinstance(horizon_row, dict), f"PREDICTION_HORIZON_ROW_INVALID:{path}:{key}")
        horizon = int(horizon_row.get("horizon_hours"))
        require(horizon in allowed_horizons, f"PREDICTION_HORIZON_UNREGISTERED:{path}:{horizon}")
        require(key == f"{horizon}H", f"PREDICTION_HORIZON_KEY_INVALID:{path}:{key}")
        due = parse_utc(str(horizon_row.get("due_at_utc")))
        cutoff = parse_utc(str(horizon_row.get("source_cutoff_utc")))
        require(cutoff == observed, f"PREDICTION_SOURCE_CUTOFF_DRIFT:{path}:{key}")
        require(due - observed == timedelta(hours=horizon), f"PREDICTION_DUE_NOT_EXACT_HORIZON:{path}:{key}")
        remaining = (due - issued).total_seconds() / 3600.0
        minimum = horizon * float(cfg.get("minimum_remaining_fraction_of_horizon", 0.5))
        require(remaining >= minimum, f"PREDICTION_INSUFFICIENT_FORWARD_SPAN:{path}:{key}")
        require(horizon_row.get("status") == "ELIGIBLE", f"PREDICTION_INELIGIBLE_HORIZON:{path}:{key}")
        targets = horizon_row.get("targets") or {}
        require(set(targets) == {"BTC", "ETH"}, f"PREDICTION_TARGET_SET_INVALID:{path}:{key}")
        for target, target_row in targets.items():
            direction = target_row.get("direction")
            require(direction in {"UP", "DOWN", "NO_EDGE"}, f"PREDICTION_DIRECTION_INVALID:{path}:{key}:{target}")
            start = target_row.get("start_value")
            require(owner.finite_number(start) and start > 0, f"PREDICTION_START_VALUE_MISSING_OR_INVALID:{path}:{key}:{target}")
            agreement = target_row.get("evidence_agreement_pct")
            require(agreement is None or (owner.finite_number(agreement) and 0.0 <= agreement <= 100.0), f"PREDICTION_AGREEMENT_INVALID:{path}:{key}:{target}")
            probability = target_row.get("frozen_calibrated_probability_pct")
            require(probability is None or (owner.finite_number(probability) and 0.0 <= probability <= 100.0), f"PREDICTION_PROBABILITY_INVALID:{path}:{key}:{target}")
            if direction == "NO_EDGE":
                require(probability is None, f"NO_EDGE_NUMERIC_PROBABILITY_FORBIDDEN:{path}:{key}:{target}")
            if probability is not None:
                require(target_row.get("confidence_status_at_issue") not in {None, "WARMUP", "ABSTAIN_NO_EDGE"}, f"PREDICTION_UNCALIBRATED_PROBABILITY:{path}:{key}:{target}")
                require(int(target_row.get("independent_calibration_samples_at_issue", 0)) >= int(cfg["minimum_independent_calibration_samples"]), f"PREDICTION_CALIBRATION_SAMPLE_MISSING:{path}:{key}:{target}")
                if probability >= 99:
                    require(target_row.get("confidence_status_at_issue") == "HIGH_ASSURANCE_99_ELIGIBLE", f"PREDICTION_99_WITHOUT_ASSURANCE:{path}:{key}:{target}")


def validate_outcome(path: Path, cfg: dict[str, Any], now: datetime | None = None) -> None:
    row = read_json(path)
    require(row.get("contract") == "INTRADAY_DIRECTION_OUTCOME_v1", f"OUTCOME_CONTRACT_INVALID:{path}")
    authority = row.get("authority") or {}
    require(authority.get("shadow_only") is True, f"OUTCOME_SHADOW_ONLY_REQUIRED:{path}")
    require(authority.get("automatic_rule_changes") is False, f"OUTCOME_AUTOMATIC_RULE_CHANGE_FORBIDDEN:{path}")
    require(authority.get("portfolio_execution") is False, f"OUTCOME_PORTFOLIO_AUTHORITY_FORBIDDEN:{path}")

    observed = parse_utc(str(row.get("source_price_observation_utc")))
    due = parse_utc(str(row.get("due_at_utc")))
    issued = parse_utc(str(row.get("issued_at_utc")))
    measured = parse_utc(str(row.get("measured_at_utc")))
    require(observed <= issued < due, f"OUTCOME_FORECAST_TIME_INVALID:{path}")
    require(measured >= due, f"OUTCOME_MEASURED_BEFORE_DUE:{path}")
    if now is not None:
        require(measured <= now, f"OUTCOME_MEASURED_IN_FUTURE:{path}")
    horizon = int(row.get("horizon_hours"))
    require(horizon in {int(v) for v in cfg.get("direction_horizons_hours", [1, 4, 24])}, f"OUTCOME_HORIZON_UNREGISTERED:{path}")
    require(due - observed == timedelta(hours=horizon), f"OUTCOME_DUE_NOT_EXACT_HORIZON:{path}")
    predicted = row.get("predicted_direction")
    require(predicted in {"UP", "DOWN", "NO_EDGE"}, f"OUTCOME_PREDICTION_INVALID:{path}")

    status = row.get("status")
    require(status in {"MATURED", "CENSORED"}, f"OUTCOME_STATUS_INVALID:{path}")
    if status == "CENSORED":
        require(row.get("reason") == "EXACT_DUE_OWNER_CANDLE_MISSING_AFTER_GRACE", f"OUTCOME_CENSOR_REASON_INVALID:{path}")
        require(row.get("substitute_later_price_forbidden") is True, f"OUTCOME_LATER_PRICE_GUARD_MISSING:{path}")
        wait = (measured - due).total_seconds() / 3600.0
        require(wait > float(cfg.get("max_outcome_evidence_lag_hours", 1.5)), f"OUTCOME_CENSORED_BEFORE_GRACE:{path}")
        require(owner.finite_number(row.get("evidence_wait_hours")) and math.isclose(row["evidence_wait_hours"], wait, abs_tol=1e-6, rel_tol=0), f"OUTCOME_CENSOR_WAIT_MISMATCH:{path}")
        require(row.get("result") is None and row.get("brier_score") is None, f"CENSORED_OUTCOME_MUST_NOT_SCORE:{path}")
        require(all(row.get(key) is None for key in ("end_value", "return_pct", "actual_direction", "evidence_observation_utc", "evidence_source_path")), f"CENSORED_OUTCOME_HAS_MATURED_EVIDENCE:{path}")
        return

    evidence_time = parse_utc(str(row.get("evidence_observation_utc")))
    require(evidence_time == due, f"OUTCOME_EVIDENCE_NOT_EXACT_DUE:{path}")
    require(float(row.get("evidence_horizon_error_hours", 999.0)) == 0.0, f"OUTCOME_HORIZON_ERROR_NONZERO:{path}")
    require(row.get("evidence_semantics") == "EXACT_DUE_CLOSED_1H_OWNER_CANDLE", f"OUTCOME_EVIDENCE_SEMANTICS_INVALID:{path}")
    require(parse_utc(str(row.get("evidence_candle_open_utc"))) == due - timedelta(hours=1), f"OUTCOME_CANDLE_OPEN_INVALID:{path}")
    require(owner.finite_number(row.get("start_value")) and row["start_value"] > 0, f"OUTCOME_START_VALUE_MISSING:{path}")
    require(owner.finite_number(row.get("end_value")) and row["end_value"] > 0, f"OUTCOME_END_VALUE_MISSING:{path}")
    expected_return = (row["end_value"] / row["start_value"] - 1.0) * 100.0
    expected_actual = "UP" if expected_return > 0 else ("DOWN" if expected_return < 0 else "FLAT")
    actual = row.get("actual_direction")
    require(actual in {"UP", "DOWN", "FLAT"}, f"OUTCOME_ACTUAL_DIRECTION_INVALID:{path}")
    require(actual == expected_actual, f"OUTCOME_ACTUAL_DIRECTION_MISMATCH:{path}")
    require(owner.finite_number(row.get("return_pct")) and math.isclose(row["return_pct"], expected_return, abs_tol=1e-8, rel_tol=0), f"OUTCOME_RETURN_MISMATCH:{path}")
    result = row.get("result")
    if predicted == "NO_EDGE":
        require(result == "ABSTAINED", f"NO_EDGE_MUST_ABSTAIN:{path}")
        require(row.get("brier_score") is None, f"NO_EDGE_BRIER_FORBIDDEN:{path}")
    else:
        require(result in {"HIT", "MISS"}, f"DIRECTIONAL_RESULT_INVALID:{path}")
        require(result == ("HIT" if predicted == actual else "MISS"), f"OUTCOME_HIT_MISS_MISMATCH:{path}")
        p = row.get("frozen_calibrated_probability_pct")
        if p is None:
            require(row.get("brier_score") is None, f"UNSCORED_PROBABILITY_HAS_BRIER:{path}")
        else:
            require(owner.finite_number(p) and 0.0 <= p <= 100.0, f"OUTCOME_PROBABILITY_INVALID:{path}")
            require(owner.finite_number(row.get("brier_score")), f"CALIBRATED_OUTCOME_BRIER_MISSING:{path}")
            expected_brier = (p / 100.0 - (1.0 if result == "HIT" else 0.0)) ** 2
            require(math.isclose(row["brier_score"], expected_brier, abs_tol=1e-8, rel_tol=0), f"OUTCOME_BRIER_MISMATCH:{path}")


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
            require(owner.finite_number(display) and 0.0 <= display <= 1.0, f"CALIBRATION_PROBABILITY_RANGE_INVALID:{group_id}")
            if round(display * 100.0, 1) >= 99.0:
                require(maturity == "HIGH_ASSURANCE_99_ELIGIBLE", f"CALIBRATION_99_WITHOUT_ASSURANCE:{group_id}")
        if maturity == "HIGH_ASSURANCE_99_ELIGIBLE":
            require(count >= int(cfg.get("high_assurance_minimum_independent_samples", 300)), f"HIGH_ASSURANCE_SAMPLE_GATE_BROKEN:{group_id}")
            require(float(group.get("wilson_lower_95", 0.0)) >= float(cfg.get("high_assurance_wilson_floor", 0.97)), f"HIGH_ASSURANCE_WILSON_GATE_BROKEN:{group_id}")
            require(float(group.get("laplace_calibrated_estimate", 0.0)) >= 0.99, f"HIGH_ASSURANCE_ESTIMATE_GATE_BROKEN:{group_id}")


def validate_linkage(root: Path, cfg: dict[str, Any], prediction_paths: list[Path], outcome_paths: list[Path], now: datetime) -> None:
    if not prediction_paths and not outcome_paths:
        if (root / owner.REGISTRATION).exists():
            validate_registration(root, cfg, now)
        return
    registration = validate_registration(root, cfg, now)
    registered = parse_utc(registration["registered_at_utc"])
    predictions = {path.relative_to(root).as_posix(): (path, read_json(path)) for path in prediction_paths}
    cutoffs: set[datetime] = set()
    for path, row in predictions.values():
        require(row.get("registered_test_id") == TEST_ID, f"PREDICTION_TEST_UNBOUND:{path}")
        require(row.get("registration_receipt_sha256") == registration["receipt_sha256"], f"PREDICTION_REGISTRATION_UNBOUND:{path}")
        require(parse_utc(row["issued_at_utc"]) >= registered, f"PREDICTION_PRE_REGISTRATION:{path}")
        validate_production_context(row.get("production_context") or {})
        cutoff = parse_utc(row["source_price_observation_utc"])
        require(cutoff not in cutoffs, f"DUPLICATE_SOURCE_CANDLE_PREDICTION:{path}")
        cutoffs.add(cutoff)
        for horizon in row["horizons"].values():
            for target, target_row in horizon["targets"].items():
                evidence = owner._exact_hourly_close(cutoff, target, root=root)
                require(evidence is not None and evidence["close"] == target_row["start_value"], f"PREDICTION_SOURCE_PRICE_UNVERIFIED:{path}:{target}")
    seen: set[tuple[str, int, str]] = set()
    outcomes = [read_json(path) for path in outcome_paths]
    for path, row in zip(outcome_paths, outcomes):
        prediction_path = row.get("prediction_path")
        require(prediction_path in predictions, f"OUTCOME_FROZEN_PREDICTION_MISSING:{path}")
        pred_path, pred = predictions[prediction_path]
        require(row.get("prediction_sha256") == owner.file_hash(pred_path), f"OUTCOME_PREDICTION_HASH_MISMATCH:{path}")
        require(row.get("registered_test_id") == TEST_ID and row.get("registration_receipt_sha256") == registration["receipt_sha256"], f"OUTCOME_REGISTRATION_UNBOUND:{path}")
        validate_production_context(row.get("production_context") or {})
        for key in ("issued_at_utc", "source_candle_open_utc", "source_price_observation_utc"):
            require(row.get(key) == pred.get(key), f"OUTCOME_FROZEN_FIELD_DRIFT:{path}:{key}")
        key = (prediction_path, row["horizon_hours"], row.get("target"))
        require(key not in seen, f"DUPLICATE_OUTCOME:{path}")
        seen.add(key)
        horizon = pred["horizons"].get(f"{row['horizon_hours']}H") or {}
        target = (horizon.get("targets") or {}).get(row.get("target"))
        require(target is not None and row["due_at_utc"] == horizon.get("due_at_utc"), f"OUTCOME_HORIZON_OR_TARGET_UNBOUND:{path}")
        for outcome_key, prediction_key in (("predicted_direction", "direction"), ("calibration_key", "calibration_key"), ("votes", "votes"), ("frozen_calibrated_probability_pct", "frozen_calibrated_probability_pct")):
            require(row.get(outcome_key) == target.get(prediction_key), f"OUTCOME_FROZEN_FIELD_DRIFT:{path}:{outcome_key}")
        require(row.get("calibration_group") == owner._group_id(row["target"], row["horizon_hours"], target["direction"], target["calibration_key"]), f"OUTCOME_CALIBRATION_GROUP_DRIFT:{path}")
        require(row.get("start_value") == target["start_value"], f"OUTCOME_START_PRICE_DRIFT:{path}")
        due = parse_utc(row["due_at_utc"])
        deadline = due + timedelta(hours=float(cfg.get("max_outcome_evidence_lag_hours", 1.5)))
        require(row.get("evidence_deadline_utc") == iso(deadline), f"OUTCOME_EVIDENCE_DEADLINE_DRIFT:{path}")
        try:
            evidence = owner.exact_hourly_close_at_commit(
                root, row["production_context"]["commit_sha"], due, row["target"],
                available_by=min(parse_utc(row["measured_at_utc"]), deadline),
                observed_at=parse_utc(row["measured_at_utc"]),
            )
        except RuntimeError as exc:
            raise ValidationError(f"OUTCOME_SOURCE_HISTORY_UNVERIFIED:{path}:{exc}") from exc
        if row["status"] == "MATURED":
            require(evidence is not None, f"OUTCOME_SOURCE_NOT_AVAILABLE_WITHIN_GRACE:{path}")
            require(row["end_value"] == evidence["close"], f"OUTCOME_SOURCE_PRICE_UNVERIFIED:{path}")
            require(row.get("evidence_source_path") == evidence["source_path"] and row.get("evidence_source_binding_sha256") == evidence["source_binding_sha256"], f"OUTCOME_SOURCE_BINDING_MISMATCH:{path}")
            require(row.get("evidence_source_commit_sha") == evidence["source_commit_sha"] and row.get("evidence_source_snapshot_utc") == evidence["source_snapshot_utc"], f"OUTCOME_SOURCE_PUBLICATION_BINDING_MISMATCH:{path}")
        else:
            require(evidence is None, f"OUTCOME_CENSORED_DESPITE_EXACT_SOURCE:{path}")
    # Reconstruct only the outcomes observable when each probability was frozen.
    for path, pred in predictions.values():
        issued = parse_utc(pred["issued_at_utc"])
        known = [row for row in outcomes if parse_utc(row["measured_at_utc"]) <= issued]
        summary = owner.calibration_summary_from_rows(known, cfg, issued)
        for horizon in pred["horizons"].values():
            for target_name, target in horizon["targets"].items():
                if target.get("frozen_calibrated_probability_pct") is None:
                    continue
                expected = owner._calibration_view(summary, target_name, horizon["horizon_hours"], target)
                require(target["frozen_calibrated_probability_pct"] == expected["calibrated_probability"], f"PREDICTION_PROBABILITY_WITHOUT_PRIOR_CALIBRATION:{path}")
                require(target.get("independent_calibration_samples_at_issue") == expected["independent_calibration_samples"], f"PREDICTION_CALIBRATION_COUNT_DRIFT:{path}")
                require(target.get("confidence_status_at_issue") == expected["confidence_status"], f"PREDICTION_CALIBRATION_STATUS_DRIFT:{path}")


def validate_repository(root: Path, write_receipt: bool = False, *, now: datetime | None = None) -> dict[str, Any]:
    root = root.resolve()
    now = now or datetime.now(timezone.utc)
    validate_registry(root)
    cfg = validate_config(root)
    prediction_paths = iter_json(root / PREDICTIONS)
    outcome_paths = iter_json(root / OUTCOMES)
    for path in prediction_paths:
        validate_prediction(path, cfg, now)
    for path in outcome_paths:
        validate_outcome(path, cfg, now)
    validate_calibration(root, cfg)
    validate_linkage(root, cfg, prediction_paths, outcome_paths, now)
    if (root / CALIBRATION).exists():
        calibration = read_json(root / CALIBRATION)
        generated = parse_utc(calibration["generated_at_utc"])
        require(generated <= now, "CALIBRATION_GENERATED_IN_FUTURE")
        known = [read_json(path) for path in outcome_paths]
        require(all(parse_utc(row["measured_at_utc"]) <= generated for row in known), "CALIBRATION_PRECEDES_ITS_OUTCOMES")
        require(calibration == owner.calibration_summary_from_rows(known, cfg, generated), "CALIBRATION_NOT_REPRODUCIBLE_FROM_VALIDATED_OUTCOMES")

    receipt = {
        "contract": "INTRADAY_DIRECTION_VALIDATION_v1",
        "registered_test_id": TEST_ID,
        "generated_at_utc": iso(now),
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
