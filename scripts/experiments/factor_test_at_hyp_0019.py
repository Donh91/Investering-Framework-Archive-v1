#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

CONTRACT = "AUTO_TRADING_FACTOR_TEST_RESULT_v1"
EXPERIMENT_ID = "AT-E3-0019"
THEORY_ID = "AT-HYP-0019"
MISSION_ISSUE = 885
TRIAL_N = 2

FEATURE_FIELD = "score"
PRICE_FIELD = "real_price"
WINDOW_ROWS = 24
FORWARD_HOURS = 24
MAX_GAP_SECONDS = 2 * 60 * 60
FORWARD_TOLERANCE_SECONDS = 75 * 60
TRAIN_FRACTION = 0.60
MIN_TEST_ROWS_PER_SYMBOL = 20
MIN_IC_IMPROVEMENT = 0.02
TRANSFORMS = ("RAW", "ROLLING_PERCENTILE", "ZSCORE", "DISTANCE_FROM_EXTREMA")
SOURCE_COMMIT = "9844e392d8744a23c829ff68bae0080423527f1b"
SOURCE_PATH = "raw/CFGI_HISTORICAL_1H_EVENT_STAGE_V1/2026/08/21/searchable/cfgi_targeted.event_time_rows.jsonl"
SOURCE_GIT_BLOB_SHA = "1a927c25d4907f353a66bdf54e4fb8bf66b526d5"

UTC = timezone.utc


class FactorTestError(ValueError):
    pass


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def parse_time(value: Any) -> datetime:
    raw = str(value or "").strip()
    if not raw:
        raise FactorTestError("MISSING_TIMESTAMP")
    normalized = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise FactorTestError("INVALID_TIMESTAMP") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise FactorTestError("AMBIGUOUS_TIMESTAMP_TIMEZONE_REQUIRED")
    return parsed.astimezone(UTC)


def load_rows(path: Path) -> tuple[list[dict[str, Any]], str]:
    raw_bytes = path.read_bytes()
    digest = hashlib.sha256(raw_bytes).hexdigest()
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(raw_bytes.decode("utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise FactorTestError(f"INVALID_JSON_LINE:{line_no}") from exc
        if not isinstance(row, dict):
            raise FactorTestError(f"INVALID_ROW:{line_no}")
        symbol = str(row.get("symbol") or "").upper()
        if symbol not in {"BTC", "ETH"}:
            continue
        timestamp = parse_time(row.get("timestamp"))
        feature = row.get(FEATURE_FIELD)
        price = row.get(PRICE_FIELD)
        if not isinstance(feature, (int, float)) or isinstance(feature, bool) or not math.isfinite(float(feature)):
            raise FactorTestError(f"INVALID_FEATURE:{line_no}")
        if not isinstance(price, (int, float)) or isinstance(price, bool) or not math.isfinite(float(price)) or float(price) <= 0:
            raise FactorTestError(f"INVALID_PRICE:{line_no}")
        rows.append({
            "symbol": symbol,
            "timestamp": timestamp,
            "timestamp_utc": timestamp.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "feature": float(feature),
            "price": float(price),
        })
    if not rows:
        raise FactorTestError("NO_ELIGIBLE_ROWS")
    return rows, digest


def segment_rows(rows: list[dict[str, Any]]) -> dict[str, list[list[dict[str, Any]]]]:
    by_symbol: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_symbol.setdefault(row["symbol"], []).append(row)
    output: dict[str, list[list[dict[str, Any]]]] = {}
    for symbol, symbol_rows in by_symbol.items():
        symbol_rows.sort(key=lambda row: row["timestamp"])
        for idx in range(1, len(symbol_rows)):
            if symbol_rows[idx]["timestamp"] <= symbol_rows[idx - 1]["timestamp"]:
                raise FactorTestError(f"NON_MONOTONIC_TIMESTAMP:{symbol}")
        segments: list[list[dict[str, Any]]] = []
        current: list[dict[str, Any]] = []
        for row in symbol_rows:
            if current:
                gap = (row["timestamp"] - current[-1]["timestamp"]).total_seconds()
                if gap > MAX_GAP_SECONDS:
                    segments.append(current)
                    current = []
            current.append(row)
        if current:
            segments.append(current)
        output[symbol] = segments
    return output


def trailing_values(segment: list[dict[str, Any]], index: int, window: int) -> list[float] | None:
    if index < window - 1:
        return None
    return [float(row["feature"]) for row in segment[index - window + 1:index + 1]]


def transform_raw(segment: list[dict[str, Any]], index: int) -> float | None:
    return float(segment[index]["feature"])


def transform_percentile(segment: list[dict[str, Any]], index: int) -> float | None:
    window = trailing_values(segment, index, WINDOW_ROWS)
    if window is None:
        return None
    current = window[-1]
    less = sum(value < current for value in window)
    equal = sum(value == current for value in window)
    return (less + 0.5 * equal) / len(window)


def transform_zscore(segment: list[dict[str, Any]], index: int) -> float | None:
    window = trailing_values(segment, index, WINDOW_ROWS)
    if window is None:
        return None
    mean = sum(window) / len(window)
    variance = sum((value - mean) ** 2 for value in window) / len(window)
    std = math.sqrt(variance)
    return 0.0 if std == 0.0 else (window[-1] - mean) / std


def transform_distance(segment: list[dict[str, Any]], index: int) -> float | None:
    window = trailing_values(segment, index, WINDOW_ROWS)
    if window is None:
        return None
    low = min(window)
    high = max(window)
    if high == low:
        return 0.0
    return 2.0 * ((window[-1] - low) / (high - low)) - 1.0


BUILDERS: dict[str, Callable[[list[dict[str, Any]], int], float | None]] = {
    "RAW": transform_raw,
    "ROLLING_PERCENTILE": transform_percentile,
    "ZSCORE": transform_zscore,
    "DISTANCE_FROM_EXTREMA": transform_distance,
}


def future_return(segment: list[dict[str, Any]], index: int) -> float | None:
    target_time = segment[index]["timestamp"].timestamp() + FORWARD_HOURS * 3600
    best_index: int | None = None
    best_distance: float | None = None
    for candidate_index in range(index + 1, len(segment)):
        candidate_time = segment[candidate_index]["timestamp"].timestamp()
        distance = abs(candidate_time - target_time)
        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_index = candidate_index
        if candidate_time > target_time + FORWARD_TOLERANCE_SECONDS:
            break
    if best_index is None or best_distance is None or best_distance > FORWARD_TOLERANCE_SECONDS:
        return None
    start = float(segment[index]["price"])
    end = float(segment[best_index]["price"])
    return (end / start - 1.0) * 100.0


def right_truncation_check(segment: list[dict[str, Any]], builder: Callable[[list[dict[str, Any]], int], float | None]) -> bool:
    full = [builder(segment, index) for index in range(len(segment))]
    for cutoff in range(WINDOW_ROWS - 1, len(segment) - 1):
        prefix = segment[:cutoff + 1]
        observed = builder(prefix, len(prefix) - 1)
        expected = full[cutoff]
        if observed is None or expected is None:
            if observed is not expected:
                return False
        elif not math.isclose(float(observed), float(expected), rel_tol=0.0, abs_tol=1e-12):
            return False
    return True


def build_examples(segments: dict[str, list[list[dict[str, Any]]]]) -> tuple[list[dict[str, Any]], dict[str, bool]]:
    examples: list[dict[str, Any]] = []
    leakage: dict[str, bool] = {name: True for name in TRANSFORMS}
    for symbol, symbol_segments in segments.items():
        for segment_id, segment in enumerate(symbol_segments):
            if len(segment) < WINDOW_ROWS + FORWARD_HOURS + 2:
                continue
            for name, builder in BUILDERS.items():
                if not right_truncation_check(segment, builder):
                    leakage[name] = False
            for index in range(len(segment)):
                label = future_return(segment, index)
                if label is None:
                    continue
                transformed = {name: BUILDERS[name](segment, index) for name in TRANSFORMS}
                if any(value is None for value in transformed.values()):
                    continue
                examples.append({
                    "symbol": symbol,
                    "segment_id": segment_id,
                    "timestamp": segment[index]["timestamp"],
                    "future_return_pct": label,
                    "features": transformed,
                })
    return examples, leakage


def average_ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda idx: values[idx])
    ranks = [0.0] * len(values)
    cursor = 0
    while cursor < len(order):
        end = cursor + 1
        while end < len(order) and values[order[end]] == values[order[cursor]]:
            end += 1
        average_rank = (cursor + 1 + end) / 2.0
        for position in range(cursor, end):
            ranks[order[position]] = average_rank
        cursor = end
    return ranks


def pearson(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or len(left) < 3:
        return 0.0
    mean_left = sum(left) / len(left)
    mean_right = sum(right) / len(right)
    numerator = sum((x - mean_left) * (y - mean_right) for x, y in zip(left, right))
    left_ss = sum((x - mean_left) ** 2 for x in left)
    right_ss = sum((y - mean_right) ** 2 for y in right)
    denominator = math.sqrt(left_ss * right_ss)
    return 0.0 if denominator == 0.0 else numerator / denominator


def spearman(left: list[float], right: list[float]) -> float:
    return pearson(average_ranks(left), average_ranks(right))


def split_examples(examples: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    train: list[dict[str, Any]] = []
    test: list[dict[str, Any]] = []
    groups: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for row in examples:
        groups.setdefault((row["symbol"], row["segment_id"]), []).append(row)
    for rows in groups.values():
        rows.sort(key=lambda row: row["timestamp"])
        split = max(1, min(len(rows) - 1, int(len(rows) * TRAIN_FRACTION)))
        train.extend(rows[:split])
        test.extend(rows[split:])
    return train, test


def metric_block(rows: list[dict[str, Any]], transform: str, orientation: float) -> dict[str, Any]:
    if len(rows) < 4:
        return {"n": len(rows), "spearman_ic": None, "top_bottom_quartile_spread_pct": None}
    factor = [orientation * float(row["features"][transform]) for row in rows]
    outcome = [float(row["future_return_pct"]) for row in rows]
    ic = spearman(factor, outcome)
    ordered = sorted(range(len(rows)), key=lambda idx: factor[idx])
    quartile = max(1, len(rows) // 4)
    bottom = [outcome[idx] for idx in ordered[:quartile]]
    top = [outcome[idx] for idx in ordered[-quartile:]]
    spread = sum(top) / len(top) - sum(bottom) / len(bottom)
    return {
        "n": len(rows),
        "spearman_ic": round(ic, 8),
        "top_bottom_quartile_spread_pct": round(spread, 8),
    }


def evaluate(examples: list[dict[str, Any]]) -> dict[str, Any]:
    train, test = split_examples(examples)
    output: dict[str, Any] = {}
    for transform in TRANSFORMS:
        train_ic = spearman(
            [float(row["features"][transform]) for row in train],
            [float(row["future_return_pct"]) for row in train],
        ) if len(train) >= 3 else 0.0
        orientation = 1.0 if train_ic >= 0 else -1.0
        by_symbol = {}
        for symbol in ("BTC", "ETH"):
            symbol_rows = [row for row in test if row["symbol"] == symbol]
            by_symbol[symbol] = metric_block(symbol_rows, transform, orientation)
        output[transform] = {
            "training_n": len(train),
            "training_raw_spearman_ic": round(train_ic, 8),
            "orientation_frozen_from_training": int(orientation),
            "oos_combined": metric_block(test, transform, orientation),
            "oos_by_symbol": by_symbol,
        }
    return {"train_n": len(train), "test_n": len(test), "transforms": output}


def adjudicate(metrics: dict[str, Any], leakage: dict[str, bool]) -> dict[str, Any]:
    if not all(leakage.values()):
        return {"status": "BLOCKED_TEMPORAL_LEAKAGE", "historical_support": False, "promotion_authorized": False, "reason": "At least one feature transform failed right-truncation invariance."}
    transforms = metrics["transforms"]
    raw_ic = transforms["RAW"]["oos_combined"]["spearman_ic"]
    if raw_ic is None:
        return {"status": "INCONCLUSIVE_INSUFFICIENT_DATA", "historical_support": False, "promotion_authorized": False, "reason": "Raw baseline has insufficient OOS rows."}
    eligible: list[tuple[str, float]] = []
    for name in ("ROLLING_PERCENTILE", "ZSCORE", "DISTANCE_FROM_EXTREMA"):
        combined_ic = transforms[name]["oos_combined"]["spearman_ic"]
        btc_ic = transforms[name]["oos_by_symbol"]["BTC"]["spearman_ic"]
        eth_ic = transforms[name]["oos_by_symbol"]["ETH"]["spearman_ic"]
        raw_btc = transforms["RAW"]["oos_by_symbol"]["BTC"]["spearman_ic"]
        raw_eth = transforms["RAW"]["oos_by_symbol"]["ETH"]["spearman_ic"]
        if None in (combined_ic, btc_ic, eth_ic, raw_btc, raw_eth):
            continue
        if combined_ic >= raw_ic + MIN_IC_IMPROVEMENT and btc_ic >= raw_btc and eth_ic >= raw_eth:
            eligible.append((name, combined_ic))
    if eligible:
        winner = max(eligible, key=lambda item: item[1])
        return {"status": "HISTORICAL_SUPPORT_ONLY", "historical_support": True, "promotion_authorized": False, "best_normalized_transform": winner[0], "reason": "A pre-registered normalized transform beat raw OOS IC by the minimum margin without degrading either BTC or ETH OOS IC. Historical evidence may rank/falsify only."}
    return {"status": "NOT_SUPPORTED_ON_FROZEN_DATASET", "historical_support": False, "promotion_authorized": False, "reason": "No normalized transform met the pre-registered cross-symbol OOS improvement rule versus raw."}


def run(path: Path) -> dict[str, Any]:
    rows, input_sha256 = load_rows(path)
    segments = segment_rows(rows)
    examples, leakage = build_examples(segments)
    metrics = evaluate(examples)
    symbol_test_counts = {symbol: int(metrics["transforms"]["RAW"]["oos_by_symbol"][symbol]["n"] or 0) for symbol in ("BTC", "ETH")}
    insufficient_symbols = [symbol for symbol, count in symbol_test_counts.items() if count < MIN_TEST_ROWS_PER_SYMBOL]
    adjudication = adjudicate(metrics, leakage) if not insufficient_symbols else {"status": "INCONCLUSIVE_INSUFFICIENT_DATA", "historical_support": False, "promotion_authorized": False, "reason": f"Insufficient OOS rows for symbols: {','.join(insufficient_symbols)}"}
    return {
        "contract": CONTRACT,
        "experiment_id": EXPERIMENT_ID,
        "theory_id": THEORY_ID,
        "mission_issue": MISSION_ISSUE,
        "trial_accounting": {"proposal_trial_n": TRIAL_N, "monotonic_trial_n_required": True, "abandoned_and_failed_attempts_remain_counted": True, "transform_family_size": len(TRANSFORMS), "normalized_variants_compared": len(TRANSFORMS) - 1, "multiple_testing_note": "No p-value promotion. Historical test may falsify or rank only; forward evidence is required for promotion."},
        "pre_registered_design": {
            "feature_field": FEATURE_FIELD,
            "label_price_field": PRICE_FIELD,
            "rolling_window_rows": WINDOW_ROWS,
            "forward_horizon_hours": FORWARD_HOURS,
            "segment_gap_fail_boundary_seconds": MAX_GAP_SECONDS,
            "forward_match_tolerance_seconds": FORWARD_TOLERANCE_SECONDS,
            "chronological_train_fraction": TRAIN_FRACTION,
            "transforms": list(TRANSFORMS),
            "primary_metric": "OOS_ORIENTED_SPEARMAN_IC",
            "secondary_metric": "OOS_TOP_BOTTOM_QUARTILE_RETURN_SPREAD",
            "orientation_rule": "Freeze each transform sign from chronological training rows only.",
            "support_rule": {"combined_oos_ic_improvement_min": MIN_IC_IMPROVEMENT, "cross_symbol_non_degradation_required": True},
        },
        "source_binding": {"repository": "Donh91/secrets", "commit_sha": SOURCE_COMMIT, "path": SOURCE_PATH, "git_blob_sha": SOURCE_GIT_BLOB_SHA, "input_sha256": input_sha256, "raw_values_exported_to_public_result": False},
        "data_summary": {"eligible_input_rows": len(rows), "segments_by_symbol": {symbol: len(value) for symbol, value in segments.items()}, "analysis_examples": len(examples), "train_rows": metrics["train_n"], "oos_rows": metrics["test_n"], "oos_rows_by_symbol": symbol_test_counts},
        "temporal_integrity": {"right_truncation_invariance": leakage, "all_transforms_clean": all(leakage.values()), "features_use_current_and_past_only": True, "future_price_used_only_as_outcome_label": True, "cross_gap_windows_forbidden": True},
        "metrics": metrics["transforms"],
        "adjudication": adjudication,
        "authority": {"research_only": True, "portfolio_execution": False, "automatic_promotion": False, "canonical_effect": False, "framework_state_change": False},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run(args.input)
    encoded = canon(report)
    if args.output:
        if args.output.exists():
            raise SystemExit(f"immutable_output_exists:{args.output}")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(encoded)
    print(encoded.decode().rstrip())


if __name__ == "__main__":
    main()
