#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
import experiment_lifecycle as lifecycle  # noqa: E402

UTC = timezone.utc
CONTRACT = "AUTO_TRADING_E1_LEAKAGE_VALIDATION_v1"
EXPERIMENT_ID = "AT-E1-0001"
MISSION_ISSUE = 885
WINDOW = 4


class TemporalIntegrityError(ValueError):
    pass


def parse_timestamp(value: Any) -> datetime:
    raw = str(value or "").strip()
    if not raw:
        raise TemporalIntegrityError("MISSING_TIMESTAMP")
    normalized = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise TemporalIntegrityError("INVALID_TIMESTAMP") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise TemporalIntegrityError("AMBIGUOUS_TIMESTAMP_TIMEZONE_REQUIRED")
    return parsed.astimezone(UTC)


def normalize_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(rows, list) or len(rows) < WINDOW + 2:
        raise TemporalIntegrityError("INSUFFICIENT_ROWS")
    normalized: list[dict[str, Any]] = []
    previous: datetime | None = None
    for row in rows:
        if not isinstance(row, dict):
            raise TemporalIntegrityError("INVALID_ROW")
        timestamp = parse_timestamp(row.get("timestamp"))
        value = row.get("value")
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)):
            raise TemporalIntegrityError("INVALID_VALUE")
        if previous is not None and timestamp <= previous:
            raise TemporalIntegrityError("NON_MONOTONIC_OR_DUPLICATE_TIMESTAMP")
        previous = timestamp
        normalized.append({
            "timestamp": timestamp.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "value": float(value),
        })
    return normalized


FeatureBuilder = Callable[[list[dict[str, Any]], int], list[float | None]]


def trailing_mean(rows: list[dict[str, Any]], window: int) -> list[float | None]:
    values = [float(row["value"]) for row in rows]
    output: list[float | None] = [None] * len(values)
    for index in range(window - 1, len(values)):
        chunk = values[index - window + 1:index + 1]
        output[index] = sum(chunk) / float(window)
    return output


def trailing_zscore(rows: list[dict[str, Any]], window: int) -> list[float | None]:
    values = [float(row["value"]) for row in rows]
    output: list[float | None] = [None] * len(values)
    for index in range(window - 1, len(values)):
        chunk = values[index - window + 1:index + 1]
        mean = sum(chunk) / float(window)
        variance = sum((item - mean) ** 2 for item in chunk) / float(window)
        std = math.sqrt(variance)
        output[index] = 0.0 if std == 0.0 else (values[index] - mean) / std
    return output


def planted_next_value_leak(rows: list[dict[str, Any]], window: int) -> list[float | None]:
    del window
    output: list[float | None] = [None] * len(rows)
    for index in range(len(rows) - 1):
        output[index] = float(rows[index + 1]["value"])
    return output


def planted_centered_mean_leak(rows: list[dict[str, Any]], window: int) -> list[float | None]:
    del window
    values = [float(row["value"]) for row in rows]
    output: list[float | None] = [None] * len(values)
    for index in range(1, len(values) - 1):
        output[index] = (values[index - 1] + values[index] + values[index + 1]) / 3.0
    return output


def same(left: float | None, right: float | None, tolerance: float = 1e-12) -> bool:
    if left is None or right is None:
        return left is right
    return math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=tolerance)


def right_truncation_invariance(rows: list[dict[str, Any]], builder: FeatureBuilder, window: int) -> dict[str, Any]:
    normalized = normalize_rows(rows)
    full = builder(normalized, window)
    mismatches: list[int] = []
    for cutoff in range(window - 1, len(normalized) - 1):
        prefix = normalized[:cutoff + 1]
        prefix_features = builder(prefix, window)
        if not same(prefix_features[-1], full[cutoff]):
            mismatches.append(cutoff)
    return {
        "invariant": not mismatches,
        "mismatch_indices": mismatches,
        "tested_cutoffs": len(normalized) - window,
    }


def left_truncation_convergence(
    rows: list[dict[str, Any]],
    builder: FeatureBuilder,
    window: int,
    drop_rows: int,
) -> dict[str, Any]:
    normalized = normalize_rows(rows)
    if not 0 < drop_rows < len(normalized) - window:
        raise ValueError("invalid_drop_rows")
    full = builder(normalized, window)
    truncated = normalized[drop_rows:]
    truncated_features = builder(truncated, window)
    mismatches: list[int] = []
    first_comparable_original_index = drop_rows + window - 1
    for original_index in range(first_comparable_original_index, len(normalized)):
        truncated_index = original_index - drop_rows
        if not same(full[original_index], truncated_features[truncated_index]):
            mismatches.append(original_index)
    return {
        "converged": not mismatches,
        "mismatch_indices": mismatches,
        "drop_rows": drop_rows,
        "warmup_rows_required": window - 1,
        "first_comparable_original_index": first_comparable_original_index,
    }


def synthetic_rows() -> list[dict[str, Any]]:
    values = [100, 103, 101, 108, 104, 111, 107, 115, 109, 120, 112, 125]
    return [
        {"timestamp": f"2026-01-01T{index:02d}:00:00Z", "value": value}
        for index, value in enumerate(values)
    ]


def timestamp_fail_closed_checks(rows: list[dict[str, Any]]) -> dict[str, Any]:
    naive = [dict(row) for row in rows]
    naive[3]["timestamp"] = "2026-01-01T03:00:00"
    duplicate = [dict(row) for row in rows]
    duplicate[4]["timestamp"] = duplicate[3]["timestamp"]

    failures: dict[str, str] = {}
    for label, candidate in (("naive_timezone", naive), ("duplicate_timestamp", duplicate)):
        try:
            normalize_rows(candidate)
        except TemporalIntegrityError as exc:
            failures[label] = str(exc)
        else:
            failures[label] = "NOT_REJECTED"
    return {
        "fail_closed": all(value != "NOT_REJECTED" for value in failures.values()),
        "rejections": failures,
    }


def experiment_owner_spec() -> dict[str, Any]:
    return lifecycle.normalize({
        "kind": "DATA_QUALITY_TEST",
        "title": "Auto Trading E1 temporal leakage detector validation",
        "hypothesis": "Point-in-time feature builders remain invariant to appended future observations and converge after sufficient warm-up.",
        "falsifier": "Any causal reference feature changes at time t when observations after t are appended, or a planted future leak is not detected.",
        "horizon_days": 1,
        "components": [],
        "target_direction": "NONE",
        "regime_dependency": "REGIME_AGNOSTIC",
        "novelty_reason": "MISSION_885_E1_TEMPORAL_INTEGRITY",
        "revisit_conditions": ["Re-run before any new strategy/factor lane is trusted."],
        "evidence_basis": ["GitHub issue #885"],
    })


def run_e1_validation() -> dict[str, Any]:
    rows = synthetic_rows()
    owner_spec = experiment_owner_spec()
    reference_sha = lifecycle.sha(rows)

    mean_right = right_truncation_invariance(rows, trailing_mean, WINDOW)
    zscore_right = right_truncation_invariance(rows, trailing_zscore, WINDOW)
    mean_left = left_truncation_convergence(rows, trailing_mean, WINDOW, drop_rows=2)
    zscore_left = left_truncation_convergence(rows, trailing_zscore, WINDOW, drop_rows=2)
    next_leak = right_truncation_invariance(rows, planted_next_value_leak, WINDOW)
    centered_leak = right_truncation_invariance(rows, planted_centered_mean_leak, WINDOW)
    timestamps = timestamp_fail_closed_checks(rows)

    checks = [
        {
            "check": "CAUSAL_TRAILING_MEAN_RIGHT_TRUNCATION",
            "expected": "PASS",
            "observed": "PASS" if mean_right["invariant"] else "FAIL",
            "detail": mean_right,
        },
        {
            "check": "CAUSAL_TRAILING_ZSCORE_RIGHT_TRUNCATION",
            "expected": "PASS",
            "observed": "PASS" if zscore_right["invariant"] else "FAIL",
            "detail": zscore_right,
        },
        {
            "check": "TRAILING_MEAN_LEFT_TRUNCATION_WARMUP",
            "expected": "PASS",
            "observed": "PASS" if mean_left["converged"] else "FAIL",
            "detail": mean_left,
        },
        {
            "check": "TRAILING_ZSCORE_LEFT_TRUNCATION_WARMUP",
            "expected": "PASS",
            "observed": "PASS" if zscore_left["converged"] else "FAIL",
            "detail": zscore_left,
        },
        {
            "check": "PLANTED_NEXT_VALUE_FUTURE_LEAK",
            "expected": "DETECTED",
            "observed": "DETECTED" if not next_leak["invariant"] else "MISSED",
            "detail": next_leak,
        },
        {
            "check": "PLANTED_CENTERED_WINDOW_FUTURE_LEAK",
            "expected": "DETECTED",
            "observed": "DETECTED" if not centered_leak["invariant"] else "MISSED",
            "detail": centered_leak,
        },
        {
            "check": "AMBIGUOUS_TIMESTAMP_FAIL_CLOSED",
            "expected": "PASS",
            "observed": "PASS" if timestamps["fail_closed"] else "FAIL",
            "detail": timestamps,
        },
    ]
    passed = all(row["expected"] == row["observed"] for row in checks)
    candidate_identity_sha = lifecycle.sha(lifecycle.identity_spec(owner_spec))

    return {
        "contract": CONTRACT,
        "experiment_id": EXPERIMENT_ID,
        "mission_issue": MISSION_ISSUE,
        "existing_owner": {
            "script": "scripts/experiments/experiment_lifecycle.py",
            "kind": owner_spec["kind"],
            "candidate_identity_sha256": candidate_identity_sha,
            "parallel_engine_created": False,
        },
        "reference_fixture_sha256": reference_sha,
        "method": {
            "right_truncation": "Feature value at t must be invariant when observations after t are appended.",
            "left_truncation": "Fixed-window causal features must converge after window-1 warm-up rows following left truncation.",
            "planted_defects": ["NEXT_VALUE_PASSTHROUGH", "CENTERED_WINDOW_MEAN"],
            "timestamp_semantics": "Timezone-aware, unique, strictly increasing timestamps required; otherwise fail closed.",
            "window_rows": WINDOW,
        },
        "checks": checks,
        "verdict": "PASS" if passed else "FAIL",
        "trial_accounting": {
            "proposal_trial_n": 1,
            "monotonic_trial_n_required": True,
            "failures_and_abandoned_attempts_remain_counted": True,
            "broad_strategy_search_authorized": False,
        },
        "authority": {
            "canonical_effect": False,
            "portfolio_execution": False,
            "framework_state_change": False,
            "threshold_change": False,
            "weight_change": False,
            "automatic_promotion": False,
            "research_only": True,
        },
        "gate": {
            "e1_required_before_strategy_factor_research": True,
            "e3_may_begin_only_if_verdict_pass": passed,
            "live_trading_authorized": False,
        },
    }


def write_immutable(path: Path, report: dict[str, Any]) -> None:
    if not lifecycle.write_new(path, report):
        raise FileExistsError(f"immutable_artifact_exists:{path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify-artifact", type=Path)
    args = parser.parse_args()

    report = run_e1_validation()
    if args.verify_artifact:
        expected = args.verify_artifact.read_bytes()
        actual = lifecycle.canon(report)
        if expected != actual:
            raise SystemExit("E1_ARTIFACT_MISMATCH")
    if args.output:
        write_immutable(args.output, report)
    sys.stdout.buffer.write(lifecycle.canon(report))
    if report["verdict"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
