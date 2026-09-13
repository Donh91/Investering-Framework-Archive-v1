#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc
CONTRACT = "AUTO_TRADING_FACTOR_TEST_RESULT_v2"
EXPERIMENT_ID = "AT-E3-0019"
THEORY_ID = "AT-HYP-0019"
TRIAL_N = 5

SOURCE_REPOSITORY = "Donh91/Investering-Framework-Archive-v1"
SOURCE_COMMIT = "5851b0ca2927caba0cbb62ac2170431023cf73cc"
SOURCE_ROOT = "03_DAILY_CAPTURE_LOGS/captures"
SOURCE_TREE_SHA1 = "b37ee316bab2536425ba01640d19e01c21a27c59"
SOURCE_BINDING_SHA256 = "7c0ef4d9f9917e0a2d7702a70a8c9f039c12ea4478da1af64464c9d1e85ff1a2"
CAPTURE_START = "2026-08-01T00:00:00Z"
CAPTURE_CUTOFF = "2026-09-13T04:48:56Z"
ALLOWED_CAPTURE_CONTRACTS = {"DAILY_LIVE_ANCHOR_INDEX_v3"}
CFGI_TIMEFRAME = "4h"

ROLLING_WINDOW_HOURS = 24
FORWARD_HORIZON_HOURS = 24
FORWARD_MATCH_TOLERANCE_SECONDS = 9000
MIN_WINDOW_OBSERVATIONS = 5
MIN_WINDOW_SPAN_HOURS = 16
MAX_WINDOW_GAP_HOURS = 8
TRAIN_FRACTION = 0.60
PURGE_HOURS = 24
MIN_COMBINED_IC_IMPROVEMENT = 0.02
TRANSFORMS = ("RAW", "ROLLING_PERCENTILE", "ZSCORE", "DISTANCE_FROM_EXTREMA")
NORMALIZED = TRANSFORMS[1:]


class N5IntegrityError(ValueError):
    pass


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def parse_ts(value: Any) -> datetime:
    raw = str(value or "").strip()
    if not raw:
        raise N5IntegrityError("MISSING_TIMESTAMP")
    raw = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise N5IntegrityError("INVALID_TIMESTAMP") from exc
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise N5IntegrityError("TIMEZONE_REQUIRED")
    return dt.astimezone(UTC)


def iso(dt: datetime) -> str:
    return dt.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def rankdata(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    result = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            result[indexed[k][0]] = avg_rank
        i = j
    return result


def spearman(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or len(xs) < 3:
        return None
    rx, ry = rankdata(xs), rankdata(ys)
    mx = sum(rx) / len(rx)
    my = sum(ry) / len(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = sum((a - mx) ** 2 for a in rx)
    vy = sum((b - my) ** 2 for b in ry)
    if vx == 0.0 or vy == 0.0:
        return 0.0
    return cov / math.sqrt(vx * vy)


def quartile_spread(features: list[float], returns: list[float]) -> float | None:
    if len(features) != len(returns) or len(features) < 8:
        return None
    ordered = sorted(zip(features, returns), key=lambda item: item[0])
    q = max(1, len(ordered) // 4)
    bottom = [r for _, r in ordered[:q]]
    top = [r for _, r in ordered[-q:]]
    return (sum(top) / len(top) - sum(bottom) / len(bottom)) * 100.0


def window_transform(scores: list[float]) -> dict[str, float]:
    current = scores[-1]
    n = len(scores)
    less = sum(1 for x in scores if x < current)
    equal = sum(1 for x in scores if x == current)
    percentile = 0.5 if n <= 1 else (less + (equal - 1) / 2.0) / (n - 1)
    mean = sum(scores) / n
    variance = sum((x - mean) ** 2 for x in scores) / n
    std = math.sqrt(variance)
    z = 0.0 if std == 0 else (current - mean) / std
    low, high = min(scores), max(scores)
    half = (high - low) / 2.0
    midpoint = (high + low) / 2.0
    distance = 0.0 if half == 0 else (current - midpoint) / half
    return {
        "RAW": current,
        "ROLLING_PERCENTILE": percentile,
        "ZSCORE": z,
        "DISTANCE_FROM_EXTREMA": distance,
    }


def window_is_eligible(rows: list[dict[str, Any]]) -> bool:
    if len(rows) < MIN_WINDOW_OBSERVATIONS:
        return False
    times = [row["event_dt"] for row in rows]
    span = (times[-1] - times[0]).total_seconds() / 3600.0
    if span < MIN_WINDOW_SPAN_HOURS:
        return False
    gaps = [(b - a).total_seconds() / 3600.0 for a, b in zip(times, times[1:])]
    return not gaps or max(gaps) <= MAX_WINDOW_GAP_HOURS


def extract_rows(capture_root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    start, cutoff = parse_ts(CAPTURE_START), parse_ts(CAPTURE_CUTOFF)
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    files: list[dict[str, Any]] = []
    skipped_contracts: dict[str, int] = {}
    eligible_files = 0

    for path in sorted(capture_root.rglob("*.json")):
        if path.name == "LATEST.json":
            continue
        raw = path.read_bytes()
        try:
            obj = json.loads(raw)
        except Exception:
            continue
        contract = str(obj.get("contract") or "UNKNOWN")
        captured_raw = obj.get("captured_at_utc")
        try:
            captured = parse_ts(captured_raw)
        except N5IntegrityError:
            continue
        if captured < start or captured > cutoff:
            continue
        if contract not in ALLOWED_CAPTURE_CONTRACTS:
            skipped_contracts[contract] = skipped_contracts.get(contract, 0) + 1
            continue
        cfgi = (((obj.get("market_metrics") or {}).get("sentiment") or {}).get("cfgi") or {})
        if cfgi.get("timeframe") != CFGI_TIMEFRAME:
            continue
        symbols = cfgi.get("symbols") or {}
        file_used = False
        for symbol in ("BTC", "ETH"):
            entry = symbols.get(symbol) or {}
            if entry.get("owner_status") != "PASS" or entry.get("stale") is True:
                continue
            if not finite_number(entry.get("score")) or not finite_number(entry.get("price")) or float(entry["price"]) <= 0:
                continue
            event = parse_ts(entry.get("timestamp"))
            if event > captured + timedelta(minutes=10):
                raise N5IntegrityError("EVENT_TIMESTAMP_AFTER_CAPTURE")
            key = (symbol, iso(event))
            row = {
                "symbol": symbol,
                "event_dt": event,
                "event_timestamp": iso(event),
                "capture_dt": captured,
                "capture_timestamp": iso(captured),
                "score": float(entry["score"]),
                "price": float(entry["price"]),
                "source_path": f"{SOURCE_ROOT}/{path.relative_to(capture_root).as_posix()}",
            }
            existing = rows.get(key)
            if existing:
                if not (math.isclose(existing["score"], row["score"], abs_tol=1e-12) and
                        math.isclose(existing["price"], row["price"], abs_tol=1e-12)):
                    raise N5IntegrityError("CONFLICTING_DUPLICATE_EVENT_TIMESTAMP")
                if row["capture_dt"] < existing["capture_dt"]:
                    rows[key] = row
            else:
                rows[key] = row
            file_used = True
        if file_used:
            eligible_files += 1
            files.append({
                "path": f"{SOURCE_ROOT}/{path.relative_to(capture_root).as_posix()}",
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "captured_at_utc": iso(captured),
            })

    output = sorted(rows.values(), key=lambda r: (r["symbol"], r["event_dt"]))
    for symbol in ("BTC", "ETH"):
        last = None
        for row in [r for r in output if r["symbol"] == symbol]:
            if last is not None and row["event_dt"] <= last:
                raise N5IntegrityError("NON_MONOTONIC_DEDUPED_EVENT_TIME")
            last = row["event_dt"]
    manifest = {
        "eligible_capture_file_count": eligible_files,
        "file_manifest_sha256": digest(files),
        "files": files,
        "skipped_contract_counts": skipped_contracts,
    }
    return output, manifest


def nearest_future(rows: list[dict[str, Any]], index: int) -> dict[str, Any] | None:
    current = rows[index]
    target = current["event_dt"] + timedelta(hours=FORWARD_HORIZON_HOURS)
    best = None
    best_delta = None
    for candidate in rows[index + 1:]:
        delta = abs((candidate["event_dt"] - target).total_seconds())
        if best_delta is None or delta < best_delta:
            best, best_delta = candidate, delta
        if candidate["event_dt"] > target + timedelta(seconds=FORWARD_MATCH_TOLERANCE_SECONDS):
            break
    if best is None or best_delta is None or best_delta > FORWARD_MATCH_TOLERANCE_SECONDS:
        return None
    return best


def build_examples(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    horizon = timedelta(hours=ROLLING_WINDOW_HOURS)
    for symbol in ("BTC", "ETH"):
        series = [row for row in rows if row["symbol"] == symbol]
        for i, current in enumerate(series):
            left = current["event_dt"] - horizon
            window = [row for row in series[:i + 1] if row["event_dt"] > left]
            if not window_is_eligible(window):
                continue
            future = nearest_future(series, i)
            if future is None:
                continue
            transforms = window_transform([row["score"] for row in window])
            ret = future["price"] / current["price"] - 1.0
            examples.append({
                "symbol": symbol,
                "event_dt": current["event_dt"],
                "event_timestamp": current["event_timestamp"],
                "outcome_dt": future["event_dt"],
                "outcome_timestamp": future["event_timestamp"],
                "future_return": ret,
                "features": transforms,
                "window_observations": len(window),
                "window_span_hours": (window[-1]["event_dt"] - window[0]["event_dt"]).total_seconds() / 3600.0,
            })
    return sorted(examples, key=lambda r: (r["symbol"], r["event_dt"]))


def split_purged(examples: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, str]]:
    train: list[dict[str, Any]] = []
    oos: list[dict[str, Any]] = []
    boundaries: dict[str, str] = {}
    for symbol in ("BTC", "ETH"):
        series = [r for r in examples if r["symbol"] == symbol]
        if len(series) < 20:
            raise N5IntegrityError(f"INSUFFICIENT_EXAMPLES_{symbol}:{len(series)}")
        split = max(1, min(len(series) - 1, int(len(series) * TRAIN_FRACTION)))
        oos_start = series[split]["event_dt"]
        boundaries[symbol] = iso(oos_start)
        train.extend(r for r in series[:split] if r["outcome_dt"] <= oos_start - timedelta(hours=PURGE_HOURS))
        oos.extend(series[split:])
    if len(train) < 20 or len(oos) < 16:
        raise N5IntegrityError(f"INSUFFICIENT_PURGED_SPLIT:train={len(train)}:oos={len(oos)}")
    return train, oos, boundaries


def metric_row(rows: list[dict[str, Any]], transform: str, orientation: int) -> dict[str, Any]:
    features = [orientation * float(r["features"][transform]) for r in rows]
    returns = [float(r["future_return"]) for r in rows]
    ic = spearman(features, returns)
    spread = quartile_spread(features, returns)
    return {
        "n": len(rows),
        "spearman_ic": round(ic, 8) if ic is not None else None,
        "top_bottom_quartile_spread_pct": round(spread, 8) if spread is not None else None,
    }


def positive(value: Any) -> bool:
    return finite_number(value) and float(value) > 0.0


def adjudicate(metrics: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    raw = metrics["RAW"]
    raw_combined = raw["oos_combined"]["spearman_ic"]
    raw_btc = raw["oos_by_symbol"]["BTC"]["spearman_ic"]
    raw_eth = raw["oos_by_symbol"]["ETH"]["spearman_ic"]
    eligible: list[str] = []
    checks: dict[str, Any] = {}
    for name in NORMALIZED:
        row = metrics[name]
        combined = row["oos_combined"]
        btc = row["oos_by_symbol"]["BTC"]
        eth = row["oos_by_symbol"]["ETH"]
        rules = {
            "combined_oos_ic_positive": positive(combined["spearman_ic"]),
            "btc_oos_ic_positive": positive(btc["spearman_ic"]),
            "eth_oos_ic_positive": positive(eth["spearman_ic"]),
            "combined_quartile_spread_positive": positive(combined["top_bottom_quartile_spread_pct"]),
            "btc_quartile_spread_positive": positive(btc["top_bottom_quartile_spread_pct"]),
            "eth_quartile_spread_positive": positive(eth["top_bottom_quartile_spread_pct"]),
            "combined_ic_beats_raw_by_min_margin": (
                finite_number(combined["spearman_ic"]) and finite_number(raw_combined)
                and float(combined["spearman_ic"]) >= float(raw_combined) + MIN_COMBINED_IC_IMPROVEMENT
            ),
            "btc_ic_not_worse_than_raw": (
                finite_number(btc["spearman_ic"]) and finite_number(raw_btc)
                and float(btc["spearman_ic"]) >= float(raw_btc)
            ),
            "eth_ic_not_worse_than_raw": (
                finite_number(eth["spearman_ic"]) and finite_number(raw_eth)
                and float(eth["spearman_ic"]) >= float(raw_eth)
            ),
        }
        checks[name] = {"passed": all(rules.values()), "rules": rules}
        if checks[name]["passed"]:
            eligible.append(name)
    return eligible, checks


def evaluate(repo_root: Path) -> dict[str, Any]:
    capture_root = repo_root / SOURCE_ROOT
    rows, manifest = extract_rows(capture_root)
    by_symbol = {symbol: len([r for r in rows if r["symbol"] == symbol]) for symbol in ("BTC", "ETH")}
    if min(by_symbol.values(), default=0) < 20:
        raise N5IntegrityError(f"INSUFFICIENT_ELIGIBLE_SOURCE_ROWS:{by_symbol}")
    if rows and min(r["event_dt"] for r in rows) < datetime(2026, 7, 1, tzinfo=UTC):
        raise N5IntegrityError("INDEPENDENCE_BOUNDARY_VIOLATION")
    examples = build_examples(rows)
    train, oos, boundaries = split_purged(examples)

    metrics: dict[str, Any] = {}
    for transform in TRANSFORMS:
        train_x = [float(r["features"][transform]) for r in train]
        train_y = [float(r["future_return"]) for r in train]
        train_ic = spearman(train_x, train_y)
        orientation = -1 if train_ic is not None and train_ic < 0 else 1
        metrics[transform] = {
            "orientation_frozen_from_training": orientation,
            "training_n": len(train),
            "training_spearman_ic": round(train_ic, 8) if train_ic is not None else None,
            "oos_combined": metric_row(oos, transform, orientation),
            "oos_by_symbol": {
                symbol: metric_row([r for r in oos if r["symbol"] == symbol], transform, orientation)
                for symbol in ("BTC", "ETH")
            },
        }

    eligible, checks = adjudicate(metrics)
    event_times = [r["event_dt"] for r in rows]
    result = {
        "contract": CONTRACT,
        "experiment_id": EXPERIMENT_ID,
        "theory_id": THEORY_ID,
        "mission_issue": 885,
        "trial_accounting": {
            "proposal_trial_n": TRIAL_N,
            "monotonic_trial_n_required": True,
            "abandoned_and_failed_attempts_remain_counted": True,
            "prior_trials": {
                "1": "E1_LEAKAGE_VALIDATION_PASS",
                "2": "METHOD_ADJUDICATION_DEFECT_RETAINED",
                "3": "METHOD_CORRECTION_REPLAY_SAME_DATA_NOT_EVIDENCE",
                "4": "SOURCE_BINDING_BLOCKED_RETAINED",
            },
        },
        "source_binding": {
            "repository": SOURCE_REPOSITORY,
            "commit_sha": SOURCE_COMMIT,
            "path": SOURCE_ROOT,
            "git_tree_sha1": SOURCE_TREE_SHA1,
            "preregistered_source_binding_sha256": SOURCE_BINDING_SHA256,
            "capture_start_utc": CAPTURE_START,
            "capture_cutoff_utc": CAPTURE_CUTOFF,
            "capture_contracts_allowed": sorted(ALLOWED_CAPTURE_CONTRACTS),
            "cfgi_timeframe": CFGI_TIMEFRAME,
            "eligible_capture_file_count": manifest["eligible_capture_file_count"],
            "eligible_file_manifest_sha256": manifest["file_manifest_sha256"],
            "raw_values_exported_to_result": False,
        },
        "data_summary": {
            "eligible_source_rows": len(rows),
            "eligible_source_rows_by_symbol": by_symbol,
            "event_time_start_utc": iso(min(event_times)) if event_times else None,
            "event_time_end_utc": iso(max(event_times)) if event_times else None,
            "analysis_examples": len(examples),
            "train_rows_after_purge": len(train),
            "oos_rows": len(oos),
            "oos_rows_by_symbol": {symbol: len([r for r in oos if r["symbol"] == symbol]) for symbol in ("BTC", "ETH")},
            "oos_start_by_symbol": boundaries,
        },
        "pre_registered_design": {
            "feature_field": "score",
            "label_price_field": "price",
            "rolling_window_hours": ROLLING_WINDOW_HOURS,
            "minimum_window_observations": MIN_WINDOW_OBSERVATIONS,
            "minimum_window_span_hours": MIN_WINDOW_SPAN_HOURS,
            "maximum_window_gap_hours": MAX_WINDOW_GAP_HOURS,
            "forward_horizon_hours": FORWARD_HORIZON_HOURS,
            "forward_match_tolerance_seconds": FORWARD_MATCH_TOLERANCE_SECONDS,
            "chronological_train_fraction": TRAIN_FRACTION,
            "purge_hours": PURGE_HOURS,
            "orientation_rule": "Freeze each transform sign from purged chronological training rows only.",
            "primary_metric": "OOS_ORIENTED_SPEARMAN_IC",
            "secondary_metric": "OOS_TOP_BOTTOM_QUARTILE_RETURN_SPREAD",
            "transforms": list(TRANSFORMS),
            "support_rule": {
                "combined_oos_ic_positive": True,
                "btc_oos_ic_positive": True,
                "eth_oos_ic_positive": True,
                "combined_quartile_spread_positive": True,
                "btc_quartile_spread_positive": True,
                "eth_quartile_spread_positive": True,
                "min_combined_ic_improvement_over_raw": MIN_COMBINED_IC_IMPROVEMENT,
                "cross_symbol_non_degradation_vs_raw": True,
            },
        },
        "metrics": metrics,
        "adjudication": {
            "eligible_normalized_transforms": eligible,
            "transform_checks": checks,
            "status": "INDEPENDENT_SUPPORT" if eligible else "INDEPENDENT_NOT_SUPPORTED",
            "promotion_authorized": False,
            "reason": (
                "At least one pre-registered normalized transform satisfied the frozen positive-OOS gate on independent prospective capture history."
                if eligible else
                "No pre-registered normalized transform satisfied the frozen positive-OOS gate on independent prospective capture history."
            ),
        },
        "temporal_integrity": {
            "feature_windows_use_current_and_past_only": True,
            "future_price_used_only_as_outcome_label": True,
            "time_based_window_not_row_count_window": True,
            "purged_train_oos_overlap_prevented": True,
            "conflicting_duplicate_timestamps_fail_closed": True,
            "source_cutoff_frozen_before_outcome_replay": True,
        },
        "authority": {
            "research_only": True,
            "portfolio_execution": False,
            "automatic_promotion": False,
            "canonical_effect": False,
            "framework_state_change": False,
            "model_weight_change": False,
            "threshold_change": False,
        },
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = evaluate(args.repo_root)
    encoded = canonical(result)
    if args.verify and args.verify.read_bytes() != encoded:
        raise SystemExit("N5_RESULT_MISMATCH")
    if args.output:
        if args.output.exists():
            raise SystemExit(f"immutable_output_exists:{args.output}")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(encoded)
    print(encoded.decode().rstrip())


if __name__ == "__main__":
    main()
