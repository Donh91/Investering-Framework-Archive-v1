from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def at_path(value: Any, path: str) -> Any:
    current = value
    for part in path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def parse_dt(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        result = result.replace(tzinfo=timezone.utc)
    return result.astimezone(timezone.utc)


def validate_forecast(forecast: dict[str, Any]) -> None:
    frozen = parse_dt(forecast["frozen_at_utc"])
    due = parse_dt(forecast["outcome_due_utc"])
    if frozen >= due:
        raise ValueError("invalid_horizon")
    direction = forecast.get("direction")
    if direction not in {"UP", "DOWN", "RANGE"}:
        raise ValueError("invalid_direction")
    if forecast.get("unit_contract") not in {None, "PERCENT_MOVE_FROM_FROZEN_BASELINE"}:
        raise ValueError("unsupported_unit_contract")
    if direction in {"UP", "DOWN"}:
        threshold = forecast.get("threshold_pct")
        if not isinstance(threshold, (int, float)) or not 0.01 <= float(threshold) <= 100.0:
            raise ValueError("threshold_pct_out_of_bounds")
    else:
        lower = forecast.get("range_lower_pct")
        upper = forecast.get("range_upper_pct")
        if not isinstance(lower, (int, float)) or not isinstance(upper, (int, float)) or not -100.0 <= float(lower) < float(upper) <= 100.0:
            raise ValueError("explicit_range_pct_bounds_required")
    if not isinstance(forecast.get("start_value"), (int, float)):
        raise ValueError("start_value_required")
    if not forecast.get("metric_path"):
        raise ValueError("metric_path_required")


def classify(forecast: dict[str, Any], start: float, end: float) -> str:
    move = (end / start - 1.0) * 100 if start else 0.0
    direction = forecast["direction"]
    if direction == "UP":
        hit = move >= float(forecast["threshold_pct"])
    elif direction == "DOWN":
        hit = move <= -float(forecast["threshold_pct"])
    else:
        hit = float(forecast["range_lower_pct"]) <= move <= float(forecast["range_upper_pct"])
    return "HIT" if hit else "MISS"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--forecast-root", type=Path, required=True)
    ap.add_argument("--evidence-root", type=Path, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    ap.add_argument("--now-utc")
    ap.add_argument("--max-evidence-lag-hours", type=float, default=24.0)
    args = ap.parse_args()
    now = parse_dt(args.now_utc) if args.now_utc else datetime.now(timezone.utc)

    evidence: list[tuple[datetime, Path, dict[str, Any]]] = []
    for path in args.evidence_root.rglob("*.json") if args.evidence_root.exists() else []:
        try:
            value = read(path)
            timestamp = value.get("captured_at_utc") or value.get("freeze_utc") or value.get("created_at_utc") or value.get("snapshot_utc")
            if timestamp:
                evidence.append((parse_dt(timestamp), path, value))
        except Exception:
            continue
    evidence.sort(key=lambda row: row[0])

    matured = pending = censored = 0
    errors: list[dict[str, str]] = []
    for path in args.forecast_root.rglob("*.json") if args.forecast_root.exists() else []:
        try:
            forecast = read(path)
            if forecast.get("contract") not in {"FROZEN_FORECAST_v1", "FROZEN_FORECAST_v2"}:
                continue
            validate_forecast(forecast)
            forecast_id = forecast["forecast_id"]
            due = parse_dt(forecast["outcome_due_utc"])
            if now < due:
                pending += 1
                continue
            destination = args.output_root / f"{forecast_id}.json"
            if destination.exists():
                continue
            max_ts = due + timedelta(hours=args.max_evidence_lag_hours)
            candidates = [row for row in evidence if due <= row[0] <= max_ts]
            if not candidates:
                outcome = {"contract": "MATURED_OUTCOME_v2", "forecast_id": forecast_id, "status": "CENSORED", "reason": "NO_EVIDENCE_WITHIN_MAX_LAG", "forecast_sha256": sha(forecast), "created_at_utc": now.isoformat().replace("+00:00", "Z")}
                destination.parent.mkdir(parents=True, exist_ok=True); destination.write_bytes(canon(outcome)); censored += 1; continue
            _, evidence_path, evidence_value = candidates[0]
            metric_path = forecast["metric_path"]
            end_value = at_path(evidence_value, metric_path)
            start_value = float(forecast["start_value"])
            baseline_path = forecast.get("baseline_evidence_path")
            baseline_hash = forecast.get("baseline_evidence_sha256")
            if baseline_path and baseline_hash:
                baseline_file = Path(baseline_path)
                if not baseline_file.exists(): raise ValueError("baseline_evidence_missing")
                baseline_value = read(baseline_file)
                if sha(baseline_value) != baseline_hash: raise ValueError("baseline_evidence_hash_mismatch")
                baseline_metric = at_path(baseline_value, metric_path)
                if not isinstance(baseline_metric, (int, float)) or abs(float(baseline_metric) - start_value) > max(1e-9, abs(start_value) * 1e-8): raise ValueError("start_value_baseline_mismatch")
            if not isinstance(end_value, (int, float)):
                outcome = {"contract": "MATURED_OUTCOME_v2", "forecast_id": forecast_id, "status": "CENSORED", "reason": "METRIC_UNAVAILABLE", "forecast_sha256": sha(forecast), "evidence_path": str(evidence_path), "evidence_sha256": sha(evidence_value), "created_at_utc": now.isoformat().replace("+00:00", "Z")}; censored += 1
            else:
                outcome = {"contract": "MATURED_OUTCOME_v2", "forecast_id": forecast_id, "status": "MATURED", "result": classify(forecast, start_value, float(end_value)), "start_value": start_value, "end_value": end_value, "return_pct": round((float(end_value) / start_value - 1) * 100, 8) if start_value else None, "forecast_sha256": sha(forecast), "evidence_path": str(evidence_path), "evidence_sha256": sha(evidence_value), "evidence_lag_hours": round((candidates[0][0] - due).total_seconds() / 3600, 6), "created_at_utc": now.isoformat().replace("+00:00", "Z"), "authority": {"model_weight_change": False, "portfolio_action": False}}; matured += 1
            destination.parent.mkdir(parents=True, exist_ok=True); destination.write_bytes(canon(outcome))
        except Exception as exc:
            errors.append({"path": str(path), "error": str(exc)})
    print(json.dumps({"matured": matured, "censored": censored, "pending": pending, "errors": errors}, sort_keys=True))
    if errors: raise SystemExit(2)


if __name__ == "__main__":
    main()
