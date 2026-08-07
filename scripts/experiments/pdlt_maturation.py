from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HORIZONS = {
    "PULLBACK_72H": (72, "p_pullback_72h", "pullback_72h_pct"),
    "HEAVY_PULLBACK_7D": (168, "p_heavy_pullback_7d", "heavy_pullback_7d_pct"),
    "PERSISTENT_DISTRIBUTION_14D": (336, "p_persistent_distribution_14d", "distribution_14d_pct"),
}


def canon(v: Any) -> bytes:
    return (json.dumps(v, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(v: Any) -> str:
    return hashlib.sha256(canon(v)).hexdigest()


def read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def candles(owner: dict[str, Any]) -> list[dict[str, Any]]:
    rows = owner.get("candles", {}).get("BTCUSDT", [])
    out = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        out.append({**row, "dt": ts(row["open_time"])})
    out.sort(key=lambda r: r["dt"])
    return out


def stats(rows: list[dict[str, Any]], start_time: datetime, hours: int, start: float, threshold_pct: float, persistent: bool) -> dict[str, Any] | None:
    end_time = start_time + __import__("datetime").timedelta(hours=hours)
    future = [r for r in rows if start_time < r["dt"] <= end_time]
    expected = hours
    if len(future) < max(1, int(hours * 0.90)):
        return None
    low_row = min(future, key=lambda r: float(r["low"]))
    high_row = max(future, key=lambda r: float(r["high"]))
    low = float(low_row["low"])
    high = float(high_row["high"])
    end_close = float(future[-1]["close"])
    adverse = max(0.0, (1.0 - low / start) * 100.0)
    favorable = max(0.0, (high / start - 1.0) * 100.0)
    event = adverse >= threshold_pct and (end_close < start if persistent else True)
    breach = None
    for row in future:
        if max(0.0, (1.0 - float(row["low"]) / start) * 100.0) >= threshold_pct:
            breach = round((row["dt"] - start_time).total_seconds() / 3600, 4)
            break
    return {
        "event": bool(event),
        "mae_pct": round(adverse, 8),
        "mfe_pct": round(favorable, 8),
        "end_close": end_close,
        "return_pct": round((end_close / start - 1.0) * 100.0, 8),
        "threshold_pct": round(threshold_pct, 8),
        "lead_time_hours": breach,
        "low_time_utc": low_row["open_time"],
        "high_time_utc": high_row["open_time"],
        "sample_rows": len(future),
    }


def mature(forecast: dict[str, Any], price_owner: dict[str, Any], now: datetime) -> list[dict[str, Any]]:
    rows = candles(price_owner)
    start_time = ts(forecast["frozen_at_utc"])
    start = float(forecast["start_btc"])
    thresholds = forecast["outcome_thresholds"]
    outcomes = []
    for horizon, (hours, prob_key, threshold_key) in HORIZONS.items():
        due = ts(forecast["outcome_due_utc"][horizon])
        if now < due:
            continue
        observed = stats(rows, start_time, hours, start, float(thresholds[threshold_key]), horizon == "PERSISTENT_DISTRIBUTION_14D")
        if observed is None:
            continue
        for arm, payload in forecast.get("arms", {}).items():
            pred = payload.get("prediction", {})
            if pred.get("prediction_valid") is not True:
                continue
            probability = pred.get(prob_key)
            if not isinstance(probability, (int, float)):
                continue
            outcome_id = f"{forecast['forecast_id']}-{arm}-{horizon}"
            event_numeric = 1.0 if observed["event"] else 0.0
            outcomes.append({
                "contract": "MATURED_OUTCOME_v2",
                "forecast_id": outcome_id,
                "parent_forecast_id": forecast["forecast_id"],
                "experiment_id": "PDLT-v1.1-RUN",
                "arm": arm,
                "horizon": horizon,
                "status": "MATURED",
                "result": "EVENT" if observed["event"] else "NO_EVENT",
                "probability": round(float(probability), 8),
                "brier": round((float(probability) - event_numeric) ** 2, 10),
                "start_value": start,
                "end_value": observed["end_close"],
                "return_pct": observed["return_pct"],
                "mae_pct": observed["mae_pct"],
                "mfe_pct": observed["mfe_pct"],
                "lead_time_hours": observed["lead_time_hours"],
                "threshold_pct": observed["threshold_pct"],
                "forecast_sha256": sha(forecast),
                "created_at_utc": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                "authority": {"model_weight_change":False,"portfolio_action":False,"canonical_promotion":False},
            })
    return outcomes


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--forecast-root", type=Path, required=True)
    ap.add_argument("--binance-owner", type=Path, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    ap.add_argument("--now-utc")
    args = ap.parse_args()
    now = ts(args.now_utc) if args.now_utc else datetime.now(timezone.utc)
    owner = read(args.binance_owner)
    created = 0
    for path in args.forecast_root.rglob("*.json") if args.forecast_root.exists() else []:
        try:
            forecast = read(path)
        except Exception:
            continue
        if forecast.get("contract") != "PDLT_FROZEN_CENSUS_v1":
            continue
        for outcome in mature(forecast, owner, now):
            dest = args.output_root / f"{outcome['forecast_id']}.json"
            if dest.exists():
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(canon(outcome))
            created += 1
    print(json.dumps({"status":"PASS","new_matured_outcomes":created}, sort_keys=True))


if __name__ == "__main__":
    main()
