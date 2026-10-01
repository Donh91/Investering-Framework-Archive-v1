#!/usr/bin/env python3
"""Mature immutable Official Daily Compass freezes without rewriting forecasts."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

CONTRACT = "OFFICIAL_DAILY_COMPASS_OUTCOME_v1"
SCORING_CONTRACT = "OFFICIAL_DAILY_COMPASS_SCORING_v2"
DEFAULT_ROOT = Path("04_MARKET_LEARNING/handlekompas/official")
HANDLEKOMPAS_RUNS = Path("04_MARKET_LEARNING/handlekompas/runs")
HOURLY_ROOT = Path("03_DAILY_CAPTURE_LOGS/hourly")
HORIZONS = {"12h": 12, "72h": 72, "168h": 168}
DIRECTION_KEY = {"12h": "NEXT_12H", "72h": "NEXT_1_3D", "168h": "NEXT_5_7D"}
SIDEWAYS_TOLERANCE_PCT = {"12h": 1.5, "72h": 3.0, "168h": 5.0}
TARGET_TOLERANCE = timedelta(hours=1)
HOURLY_CLOSE_OFFSET = timedelta(hours=1)


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def parse_utc(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.utcoffset() is None:
        return None
    return dt.astimezone(timezone.utc)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def pct_change(start: Any, end: Any) -> float | None:
    if not isinstance(start, (int, float)) or not isinstance(end, (int, float)) or isinstance(start, bool) or isinstance(end, bool):
        return None
    if float(start) == 0:
        return None
    return (float(end) / float(start) - 1.0) * 100.0


def hourly_paths(start: datetime, end: datetime) -> Iterable[Path]:
    day = start.date()
    stop = end.date()
    while day <= stop:
        yield HOURLY_ROOT / f"{day:%Y/%m}/{day:%Y-%m-%d}.csv"
        day += timedelta(days=1)


def reference_close_time(reference: Mapping[str, Any]) -> datetime | None:
    explicit = parse_utc(reference.get("source_window_end_utc"))
    if explicit is not None:
        return explicit
    opened = parse_utc(reference.get("observation_open_utc"))
    return opened + HOURLY_CLOSE_OFFSET if opened is not None else None


def row_close_time(row: Mapping[str, Any]) -> datetime | None:
    close = row.get("observation_close_utc")
    if isinstance(close, datetime):
        return close
    stamp = row.get("timestamp_utc")
    return stamp + HOURLY_CLOSE_OFFSET if isinstance(stamp, datetime) else None


def load_hourly(repo_root: Path, start: datetime, end: datetime) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rel in hourly_paths(start, end):
        path = repo_root / rel
        if not path.exists():
            continue
        try:
            raw = path.read_text(encoding="utf-8-sig")
            for row in csv.DictReader(io.StringIO(raw)):
                stamp = parse_utc(row.get("timestamp_utc"))
                if stamp is None:
                    continue
                close_stamp = parse_utc(row.get("source_window_end_utc")) or (stamp + HOURLY_CLOSE_OFFSET)
                if close_stamp < start - TARGET_TOLERANCE or close_stamp > end + TARGET_TOLERANCE:
                    continue
                def f(key: str) -> float | None:
                    try:
                        return float(row[key]) if row.get(key) not in (None, "") else None
                    except (TypeError, ValueError):
                        return None
                rows.append({
                    "timestamp_utc": stamp,
                    "observation_close_utc": close_stamp,
                    "btc": f("btc_close"),
                    "eth": f("eth_close"),
                    "ethbtc": f("ethbtc_close"),
                })
        except Exception:
            continue
    return sorted(rows, key=lambda row: row["timestamp_utc"])


def closest_target(rows: list[dict[str, Any]], target: datetime, tolerance: timedelta = TARGET_TOLERANCE) -> dict[str, Any] | None:
    eligible: list[tuple[float, bool, datetime, dict[str, Any]]] = []
    for row in rows:
        close = row_close_time(row)
        if close is None:
            continue
        distance = abs((close - target).total_seconds())
        if distance <= tolerance.total_seconds():
            eligible.append((distance, close > target, close, row))
    return min(eligible, key=lambda item: (item[0], item[1], item[2]))[3] if eligible else None


def excursion(start_value: float | None, values: list[float]) -> dict[str, float | None]:
    if start_value is None or not values:
        return {"mfe_pct": None, "mae_pct": None}
    changes = [pct_change(start_value, value) for value in values]
    finite = [value for value in changes if value is not None]
    return {"mfe_pct": max(finite) if finite else None, "mae_pct": min(finite) if finite else None}


def native_runs(repo_root: Path, start: datetime, end: datetime) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    day = start.date()
    while day <= end.date():
        directory = repo_root / HANDLEKOMPAS_RUNS / f"{day:%Y/%m/%d}"
        if directory.exists():
            for path in sorted(directory.glob("*.json")):
                try:
                    value = read_json(path)
                    stamp = parse_utc(value.get("generated_at_utc"))
                    if stamp is not None and start <= stamp <= end:
                        rows.append({
                            "timestamp_utc": stamp,
                            "action": ((value.get("action") or {}).get("NOW")),
                            "path": path.relative_to(repo_root).as_posix(),
                            "sha256": sha256(path.read_bytes()),
                        })
                except Exception:
                    continue
        day += timedelta(days=1)
    return sorted(rows, key=lambda row: row["timestamp_utc"])


def first_action_event(rows: list[dict[str, Any]], states: set[str]) -> dict[str, Any]:
    for row in rows:
        if row.get("action") in states:
            return {
                "fired": True,
                "first_fired_at_utc": row["timestamp_utc"].isoformat().replace("+00:00", "Z"),
                "state": row.get("action"),
                "source_path": row.get("path"),
                "source_sha256": row.get("sha256"),
            }
    return {"fired": False, "first_fired_at_utc": None, "state": None, "source_path": None, "source_sha256": None}


def direction_score(predicted: Any, realized_pct: float | None, horizon: str) -> dict[str, Any]:
    if predicted in {None, "MIXED", "NO_EDGE", "UNAVAILABLE"}:
        return {"result": "ABSTAINED", "correct": None, "predicted": predicted, "realized_pct": realized_pct}
    if realized_pct is None:
        return {"result": "UNAVAILABLE", "correct": None, "predicted": predicted, "realized_pct": None}
    tol = SIDEWAYS_TOLERANCE_PCT[horizon]
    if predicted == "UP":
        correct = realized_pct > 0
    elif predicted == "DOWN":
        correct = realized_pct < 0
    elif predicted == "SIDEWAYS":
        correct = abs(realized_pct) <= tol
    else:
        return {"result": "UNSUPPORTED_PREDICTION", "correct": None, "predicted": predicted, "realized_pct": realized_pct}
    return {"result": "CORRECT" if correct else "INCORRECT", "correct": correct, "predicted": predicted, "realized_pct": realized_pct, "sideways_tolerance_pct": tol if predicted == "SIDEWAYS" else None}


def feature_value(freeze: Mapping[str, Any], feature_id: str) -> Any:
    rows = ((freeze.get("evidence_snapshot") or {}).get("selected_features") or [])
    for row in rows:
        if isinstance(row, Mapping) and row.get("feature_id") == feature_id:
            return row.get("value")
    return None


def persistence_baseline(freeze: Mapping[str, Any], realized_pct: float | None) -> dict[str, Any]:
    prior = feature_value(freeze, "btc_delta_since_prior_packet_pct")
    if not isinstance(prior, (int, float)) or realized_pct is None or prior == 0:
        return {"status": "UNAVAILABLE", "reason": "NO_NONZERO_PRE_FREEZE_BTC_DELTA"}
    predicted = "UP" if prior > 0 else "DOWN"
    correct = (realized_pct > 0) if predicted == "UP" else (realized_pct < 0)
    return {"status": "SCORED", "prediction": predicted, "correct": correct, "realized_pct": realized_pct}


def action_quality(action: Any, btc_return: float | None, btc_mae: float | None) -> dict[str, Any]:
    action_name = str(action or "NO_EDGE")
    if btc_return is None:
        return {"status": "UNAVAILABLE", "action": action_name}
    if action_name in {"DEPLOY", "PREPARE"}:
        result = "FAVORED" if btc_return > 0 else "NOT_FAVORED"
    elif action_name in {"WAIT", "HARD_WAIT", "HOLD"}:
        result = "PROTECTIVE" if btc_return < 0 else "OPPORTUNITY_COST_OR_NEUTRAL"
    else:
        result = "ABSTAINED"
    return {"status": "PROXY_ONLY", "action": action_name, "result": result, "btc_return_pct": btc_return, "btc_mae_pct": btc_mae, "note": "Navigation-quality proxy only; not portfolio PnL or execution evidence."}


def mature_one(repo_root: Path, freeze_path: Path, horizon: str, now: datetime, output_root: Path) -> dict[str, Any] | None:
    freeze = read_json(freeze_path)
    issued = parse_utc(freeze.get("issued_at_utc"))
    if issued is None:
        return None
    hours = HORIZONS[horizon]
    ref = freeze.get("market_reference") or {}
    start_reference = reference_close_time(ref)
    if start_reference is None:
        return {
            "status": "PENDING_REFERENCE_TIME",
            "horizon": horizon,
            "compass_id": freeze.get("compass_id"),
            "reason": "MARKET_REFERENCE_OBSERVATION_TIME_MISSING",
        }
    target = start_reference + timedelta(hours=hours)
    if now < target:
        return None

    outcome_rel = output_root / "outcomes" / issued.strftime("%Y/%m/%d") / f"{freeze.get('compass_id')}_{horizon}.json"
    outcome_path = repo_root / outcome_rel
    if outcome_path.exists():
        return {"status": "ALREADY_MATURED", "path": outcome_rel.as_posix()}

    rows = load_hourly(repo_root, start_reference, target + TARGET_TOLERANCE)
    target_row = closest_target(rows, target)
    if target_row is None:
        return {
            "status": "PENDING_TARGET_EVIDENCE",
            "path": outcome_rel.as_posix(),
            "horizon": horizon,
            "compass_id": freeze.get("compass_id"),
            "target_at_utc": target.isoformat().replace("+00:00", "Z"),
            "reason": "NO_ELIGIBLE_TARGET_OBSERVATION_WITHIN_TOLERANCE",
        }
    btc_start = ref.get("btc_usdt") if isinstance(ref.get("btc_usdt"), (int, float)) else None
    eth_start = ref.get("eth_usdt") if isinstance(ref.get("eth_usdt"), (int, float)) else None
    ethbtc_start = ref.get("ethbtc") if isinstance(ref.get("ethbtc"), (int, float)) else None
    btc_end = target_row.get("btc") if target_row else None
    eth_end = target_row.get("eth") if target_row else None
    ethbtc_end = target_row.get("ethbtc") if target_row else None
    btc_return = pct_change(btc_start, btc_end)
    eth_return = pct_change(eth_start, eth_end)
    ethbtc_return = pct_change(ethbtc_start, ethbtc_end)

    interval = [row for row in rows if (row_close_time(row) is not None and start_reference <= row_close_time(row) <= target)]
    btc_exc = excursion(btc_start, [row["btc"] for row in interval if isinstance(row.get("btc"), (int, float))])
    eth_exc = excursion(eth_start, [row["eth"] for row in interval if isinstance(row.get("eth"), (int, float))])

    action_rows = native_runs(repo_root, issued, target)
    key = DIRECTION_KEY[horizon]
    horizon_call = ((freeze.get("horizons") or {}).get(key) or {})
    confirm_states = set((((horizon_call.get("confirmation_trigger") or {}).get("states")) or []))
    deteriorate_states = set((((horizon_call.get("invalidation_trigger") or {}).get("states")) or []))
    predicted = horizon_call.get("expected_direction")
    confirmation_event = first_action_event(action_rows, confirm_states) if confirm_states else {"fired": None, "reason": "NO_MACHINE_TRIGGER"}
    deterioration_event = first_action_event(action_rows, deteriorate_states) if deteriorate_states else {"fired": None, "reason": "NO_MACHINE_TRIGGER"}

    target_close = row_close_time(target_row)
    effective_window_hours = ((target_close - start_reference).total_seconds() / 3600.0) if target_close else None
    window_deviation_hours = abs(effective_window_hours - hours) if effective_window_hours is not None else None
    if window_deviation_hours is None or window_deviation_hours > 1.0:
        return {
            "status": "PENDING_TARGET_EVIDENCE",
            "path": outcome_rel.as_posix(),
            "horizon": horizon,
            "compass_id": freeze.get("compass_id"),
            "target_at_utc": target.isoformat().replace("+00:00", "Z"),
            "reason": "WINDOW_OUT_OF_TOLERANCE",
            "effective_window_hours": effective_window_hours,
        }

    outcome = {
        "contract": CONTRACT,
        "scoring_contract": SCORING_CONTRACT,
        "compass_id": freeze.get("compass_id"),
        "compass_sha256": freeze.get("compass_sha256"),
        "forecast_path": freeze_path.relative_to(repo_root).as_posix(),
        "issued_at_utc": freeze.get("issued_at_utc"),
        "horizon": horizon,
        "target_at_utc": target.isoformat().replace("+00:00", "Z"),
        "matured_at_utc": now.isoformat().replace("+00:00", "Z"),
        "target_observation_at_utc": target_close.isoformat().replace("+00:00", "Z") if target_close else None,
        "target_observation_open_at_utc": target_row["timestamp_utc"].isoformat().replace("+00:00", "Z") if target_row else None,
        "time_basis": {
            "status": "PASS",
            "nominal_horizon_hours": hours,
            "start_reference_at_utc": start_reference.isoformat().replace("+00:00", "Z"),
            "start_reference_age_hours": round((issued - start_reference).total_seconds() / 3600.0, 6),
            "effective_window_hours": round(effective_window_hours, 6),
            "window_deviation_hours": round(window_deviation_hours, 6),
            "endpoint_semantics": "HOURLY_CLOSE_TIME_NEAREST_TO_REFERENCE_PLUS_HORIZON",
        },
        "realized": {
            "btc_return_pct": btc_return,
            "eth_return_pct": eth_return,
            "ethbtc_return_pct": ethbtc_return,
            "btc_mfe_pct": btc_exc["mfe_pct"],
            "btc_mae_pct": btc_exc["mae_pct"],
            "eth_mfe_pct": eth_exc["mfe_pct"],
            "eth_mae_pct": eth_exc["mae_pct"],
        },
        "direction_accuracy": {
            "btc": direction_score(predicted, btc_return, horizon),
            "eth": direction_score(predicted, eth_return, horizon),
        },
        "triggers": {
            "confirmation": confirmation_event,
            "deterioration": deterioration_event,
        },
        "timing_accuracy": {
            "status": "PARTIAL",
            "eta_window": horizon_call.get("eta"),
            "confirmation_first_fired_at_utc": confirmation_event.get("first_fired_at_utc"),
            "note": "V1 scores event timing only when the registered native action-state trigger is observable; otherwise timing remains missing.",
        },
        "action_utility": action_quality(horizon_call.get("action_posture"), btc_return, btc_exc["mae_pct"]),
        "rotation_ladder_accuracy": {
            "status": "UNAVAILABLE_NO_GOVERNED_CAP_BUCKET_RETURN_SERIES",
            "note": "BTC/ETH outcomes are measured. Large/mid/small/micro tiers are not proxy-scored from unrelated assets.",
        },
        "baselines": {
            "persistence": persistence_baseline(freeze, btc_return),
            "always_hold_btc_return_pct": btc_return,
            "no_edge": {"status": "REFERENCE_ONLY", "return_assumption_pct": 0.0},
        },
        "missingness": {
            "target_hourly_row_missing": target_row is None,
            "btc_reference_missing": btc_start is None,
            "eth_reference_missing": eth_start is None,
            "ethbtc_reference_missing": ethbtc_start is None,
        },
        "authority": {
            "portfolio_execution": False,
            "forecast_rewrite": False,
            "source_override": False,
            "purpose": "POST_MATURITY_ACCOUNTABILITY_ONLY",
        },
    }
    outcome["outcome_sha256"] = sha256(canon({k: v for k, v in outcome.items() if k != "outcome_sha256"}))
    outcome_path.parent.mkdir(parents=True, exist_ok=True)
    outcome_path.write_bytes(canon(outcome))
    return {"status": "MATURED", "path": outcome_rel.as_posix(), "horizon": horizon, "compass_id": freeze.get("compass_id"), "outcome_sha256": outcome["outcome_sha256"]}


def find_freezes(repo_root: Path, output_root: Path) -> list[Path]:
    root = repo_root / output_root / "daily"
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("CMP-*.json") if path.is_file())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--now-utc")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    now = parse_utc(args.now_utc) if args.now_utc else datetime.now(timezone.utc).replace(microsecond=0)
    if now is None:
        raise ValueError("INVALID_NOW_UTC")

    results: list[dict[str, Any]] = []
    for freeze_path in find_freezes(args.repo_root, args.output_root):
        for horizon in HORIZONS:
            if args.dry_run:
                freeze = read_json(freeze_path)
                issued = parse_utc(freeze.get("issued_at_utc"))
                ref = freeze.get("market_reference") or {}
                start_reference = reference_close_time(ref) if issued else None
                target = start_reference + timedelta(hours=HORIZONS[horizon]) if start_reference else None
                results.append({
                    "compass_id": freeze.get("compass_id"),
                    "horizon": horizon,
                    "eligible": bool(target and now >= target),
                    "target_at_utc": target.isoformat().replace("+00:00", "Z") if target else None,
                })
            else:
                result = mature_one(args.repo_root, freeze_path, horizon, now, args.output_root)
                if result:
                    results.append(result)
    print(json.dumps({"contract": "OFFICIAL_DAILY_COMPASS_MATURITY_RUN_v1", "generated_at_utc": now.isoformat().replace("+00:00", "Z"), "results": results}, sort_keys=True))


if __name__ == "__main__":
    main()
