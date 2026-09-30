#!/usr/bin/env python3
"""Mature immutable Shadow Compass v2 forecasts using Official Compass outcome semantics."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

# Support direct workflow execution via `python scripts/learning/shadow_compass_v2_outcomes.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.learning.compass_outcomes import (
    HORIZONS,
    SIDEWAYS_TOLERANCE_PCT,
    canon,
    closest_target,
    direction_score,
    excursion,
    load_hourly,
    parse_utc,
    reference_close_time,
    row_close_time,
    TARGET_TOLERANCE,
    pct_change,
    read_json,
)

FORECAST_ROOT = Path("04_MARKET_LEARNING/handlekompas/shadow_v2/forecasts")
OUTPUT_ROOT = Path("04_MARKET_LEARNING/handlekompas/shadow_v2/outcomes")
CONTRACT = "SHADOW_COMPASS_V2_OUTCOME_v1"
SCORING_CONTRACT = "SHADOW_COMPASS_V2_SCORING_v2"


def _source_auto_state(repo: Path, forecast: Mapping[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    binding = ((forecast.get("source_bindings") or {}).get("auto_market_state") or {})
    path_raw = binding.get("packet_path")
    expected_sha = binding.get("packet_sha256")
    if not isinstance(path_raw, str) or not path_raw:
        return None, {"status": "UNAVAILABLE", "reason": "AUTO_STATE_PATH_MISSING"}
    path = repo / path_raw
    if not path.exists():
        return None, {"status": "UNAVAILABLE", "reason": "AUTO_STATE_FILE_MISSING", "path": path_raw}
    try:
        value = read_json(path)
    except Exception:
        return None, {"status": "UNAVAILABLE", "reason": "AUTO_STATE_UNREADABLE", "path": path_raw}
    actual_sha = value.get("packet_sha256")
    if expected_sha and actual_sha != expected_sha:
        return None, {
            "status": "FAIL",
            "reason": "AUTO_STATE_PACKET_SHA_MISMATCH",
            "path": path_raw,
            "expected_packet_sha256": expected_sha,
            "actual_packet_sha256": actual_sha,
        }
    return value, {
        "status": "PASS",
        "path": path_raw,
        "packet_sha256": actual_sha,
        "content_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _start_reference(auto_state: Mapping[str, Any] | None) -> dict[str, float | None]:
    live = ((auto_state or {}).get("normalized_state") or {}).get("live_market") or {}
    def f(key: str) -> float | None:
        v = live.get(key)
        return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None
    return {"btc": f("btc_usdt"), "eth": f("eth_usdt"), "ethbtc": f("ethbtc")}


def _persistence(auto_state: Mapping[str, Any] | None, realized_pct: float | None) -> dict[str, Any]:
    prior = (((auto_state or {}).get("deltas_since_prior_auto_packet") or {}).get("btc_usdt") or {}).get("pct")
    if not isinstance(prior, (int, float)) or isinstance(prior, bool) or prior == 0 or realized_pct is None:
        return {"status": "UNAVAILABLE", "reason": "NO_NONZERO_BOUND_PRE_FORECAST_BTC_DELTA"}
    prediction = "UP" if float(prior) > 0 else "DOWN"
    correct = realized_pct > 0 if prediction == "UP" else realized_pct < 0
    return {
        "status": "SCORED",
        "prediction": prediction,
        "correct": correct,
        "pre_forecast_btc_delta_pct": float(prior),
        "realized_pct": realized_pct,
    }


def mature_one(repo: Path, forecast_path: Path, horizon: str, now: datetime) -> dict[str, Any] | None:
    forecast = read_json(forecast_path)
    if forecast.get("contract") != "SHADOW_COMPASS_V2_FORECAST_v1":
        return None
    issued = parse_utc(forecast.get("issued_at_utc"))
    if issued is None:
        return None

    auto_state, auto_binding = _source_auto_state(repo, forecast)
    if auto_state is None:
        return {
            "status": "SOURCE_INTEGRITY_FAIL" if auto_binding.get("status") == "FAIL" else "PENDING_SOURCE_EVIDENCE",
            "forecast_id": forecast.get("forecast_id"),
            "horizon": horizon,
            "reason": auto_binding.get("reason"),
        }
    live_reference = ((auto_state.get("normalized_state") or {}).get("live_market") or {})
    start_reference = reference_close_time(live_reference)
    if start_reference is None:
        return {
            "status": "PENDING_REFERENCE_TIME",
            "forecast_id": forecast.get("forecast_id"),
            "horizon": horizon,
            "reason": "BOUND_AUTO_STATE_OBSERVATION_TIME_MISSING",
        }

    target = start_reference + timedelta(hours=HORIZONS[horizon])
    if now < target:
        return None

    rel = OUTPUT_ROOT / issued.strftime("%Y/%m/%d") / f"{forecast.get('forecast_id')}_{horizon}.json"
    out = repo / rel
    if out.exists():
        return {"status": "ALREADY_MATURED", "path": rel.as_posix()}

    auto_state, auto_binding = _source_auto_state(repo, forecast)
    if auto_state is None:
        return {
            "status": "PENDING_SOURCE_EVIDENCE" if auto_binding.get("status") == "UNAVAILABLE" else "SOURCE_INTEGRITY_FAIL",
            "forecast_id": forecast.get("forecast_id"),
            "horizon": horizon,
            "source_binding": auto_binding,
        }

    rows = load_hourly(repo, start_reference, target + TARGET_TOLERANCE)
    endpoint = closest_target(rows, target)
    if endpoint is None:
        return {
            "status": "PENDING_TARGET_EVIDENCE",
            "forecast_id": forecast.get("forecast_id"),
            "horizon": horizon,
            "target_at_utc": target.isoformat().replace("+00:00", "Z"),
        }

    start = _start_reference(auto_state)
    btc_return = pct_change(start["btc"], endpoint.get("btc"))
    eth_return = pct_change(start["eth"], endpoint.get("eth"))
    ratio_return = pct_change(start["ethbtc"], endpoint.get("ethbtc"))
    interval = [r for r in rows if (row_close_time(r) is not None and start_reference <= row_close_time(r) <= target)]
    btc_exc = excursion(start["btc"], [r["btc"] for r in interval if isinstance(r.get("btc"), (int, float))])
    eth_exc = excursion(start["eth"], [r["eth"] for r in interval if isinstance(r.get("eth"), (int, float))])

    endpoint_close = row_close_time(endpoint)
    effective_window_hours = ((endpoint_close - start_reference).total_seconds() / 3600.0) if endpoint_close else None
    window_deviation_hours = abs(effective_window_hours - HORIZONS[horizon]) if effective_window_hours is not None else None
    if window_deviation_hours is None or window_deviation_hours > 1.0:
        return {
            "status": "PENDING_TARGET_EVIDENCE",
            "forecast_id": forecast.get("forecast_id"),
            "horizon": horizon,
            "target_at_utc": target.isoformat().replace("+00:00", "Z"),
            "reason": "WINDOW_OUT_OF_TOLERANCE",
            "effective_window_hours": effective_window_hours,
        }

    row = (((forecast.get("model_output") or {}).get("horizons") or {}).get(horizon) or {})
    predicted = row.get("direction")
    value = {
        "contract": CONTRACT,
        "scoring_contract": SCORING_CONTRACT,
        "forecast_id": forecast.get("forecast_id"),
        "forecast_path": forecast_path.relative_to(repo).as_posix(),
        "forecast_sha256": forecast.get("forecast_sha256"),
        "model_id": forecast.get("model_id"),
        "reasoner_version": forecast.get("reasoner_version"),
        "horizon": horizon,
        "issued_at_utc": issued.isoformat().replace("+00:00", "Z"),
        "target_at_utc": target.isoformat().replace("+00:00", "Z"),
        "target_observation_at_utc": endpoint_close.isoformat().replace("+00:00", "Z") if endpoint_close else None,
        "target_observation_open_at_utc": endpoint["timestamp_utc"].isoformat().replace("+00:00", "Z"),
        "time_basis": {
            "status": "PASS",
            "nominal_horizon_hours": HORIZONS[horizon],
            "start_reference_at_utc": start_reference.isoformat().replace("+00:00", "Z"),
            "start_reference_age_hours": round((issued - start_reference).total_seconds() / 3600.0, 6),
            "effective_window_hours": round(effective_window_hours, 6),
            "window_deviation_hours": round(window_deviation_hours, 6),
            "endpoint_semantics": "HOURLY_CLOSE_TIME_NEAREST_TO_REFERENCE_PLUS_HORIZON",
        },
        "frozen_forecast": {
            "direction": predicted,
            "confidence": row.get("confidence"),
            "pullback_risk": row.get("pullback_risk"),
            "transmission_state": row.get("transmission_state"),
            "expected_path": row.get("expected_path"),
            "supporting_evidence": row.get("supporting_evidence"),
            "contradicting_evidence": row.get("contradicting_evidence"),
            "missing_evidence": row.get("missing_evidence"),
            "falsification_conditions": row.get("falsification_conditions"),
        },
        "realized": {
            "btc_return_pct": btc_return,
            "eth_return_pct": eth_return,
            "ethbtc_return_pct": ratio_return,
            "btc_mfe_pct": btc_exc.get("mfe_pct"),
            "btc_mae_pct": btc_exc.get("mae_pct"),
            "eth_mfe_pct": eth_exc.get("mfe_pct"),
            "eth_mae_pct": eth_exc.get("mae_pct"),
        },
        "direction_accuracy": {
            "btc": direction_score(predicted, btc_return, horizon),
            "eth": direction_score(predicted, eth_return, horizon),
        },
        "baselines": {
            "always_hold_btc_return_pct": btc_return,
            "persistence": _persistence(auto_state, btc_return),
            "no_edge_return_pct": 0.0,
        },
        "source_binding": auto_binding,
        "comparison_metadata": {
            "official_comparison_eligible": True,
            "matching_rule": "PAIR_ONLY_WITH_NEAREST_COMPARABLE_OFFICIAL_SLOT;DISCLOSE_TIME_AND_SOURCE_DIFFERENCES",
            "sideways_tolerance_pct": SIDEWAYS_TOLERANCE_PCT[horizon],
            "overlap_is_not_independence": True,
        },
        "unscored_reasoning_dimensions": {
            "expected_path": "RETAINED_NOT_SCORED_V1",
            "pullback_risk": "RETAINED_NOT_SCORED_V1",
            "transmission_state": "RETAINED_NOT_SCORED_V1",
            "falsification_conditions": "RETAINED_NOT_SCORED_V1",
        },
        "authority": {
            "portfolio_execution": False,
            "official_compass_override": False,
            "automatic_promotion": False,
            "purpose": "POST_MATURITY_SHADOW_ACCOUNTABILITY_ONLY",
        },
    }
    value["outcome_sha256"] = hashlib.sha256(canon(value)).hexdigest()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(canon(value))
    return {
        "status": "MATURED",
        "path": rel.as_posix(),
        "forecast_id": forecast.get("forecast_id"),
        "horizon": horizon,
        "outcome_sha256": value["outcome_sha256"],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--now-utc")
    args = ap.parse_args()
    repo = args.repo_root.resolve()
    now = parse_utc(args.now_utc) if args.now_utc else datetime.now(timezone.utc).replace(microsecond=0)
    if now is None:
        raise SystemExit("invalid_now")
    results: list[dict[str, Any]] = []
    root = repo / FORECAST_ROOT
    if root.exists():
        for forecast in sorted(root.rglob("SCV2-*.json")):
            for horizon in HORIZONS:
                result = mature_one(repo, forecast, horizon, now)
                if result is not None:
                    results.append(result)
    print(json.dumps({
        "contract": "SHADOW_COMPASS_V2_MATURITY_RUN_v1",
        "generated_at_utc": now.isoformat().replace("+00:00", "Z"),
        "results": results,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
