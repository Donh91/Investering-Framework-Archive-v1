#!/usr/bin/env python3
"""Mature immutable Strategic Compass checkpoints from governed hourly BTC/ETH evidence."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path("04_MARKET_LEARNING/handlekompas/strategic")
HOURLY = Path("03_DAILY_CAPTURE_LOGS/hourly")
CHECKPOINTS = {
    "21_30d": {"7d": 7, "14d": 14, "21d": 21, "30d": 30},
    "4_8w": {"14d": 14, "28d": 28, "42d": 42, "56d": 56},
}


def canon(v: Any) -> bytes:
    return (json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()


def parse_time(v: Any) -> datetime | None:
    if not isinstance(v, str):
        return None
    try:
        d = datetime.fromisoformat(v.replace("Z", "+00:00"))
        return d.astimezone(timezone.utc) if d.utcoffset() is not None else None
    except ValueError:
        return None


def pct(a: Any, b: Any) -> float | None:
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)) or isinstance(a, bool) or isinstance(b, bool) or float(a) == 0:
        return None
    return (float(b) / float(a) - 1.0) * 100.0


def load_hourly(repo: Path, start: datetime, end: datetime) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    day = start.date()
    while day <= end.date():
        path = repo / HOURLY / f"{day:%Y/%m}/{day:%Y-%m-%d}.csv"
        if path.exists():
            try:
                for row in csv.DictReader(io.StringIO(path.read_text(encoding="utf-8-sig"))):
                    t = parse_time(row.get("timestamp_utc"))
                    if t is None or t < start - timedelta(hours=2) or t > end + timedelta(hours=2):
                        continue
                    def num(key: str) -> float | None:
                        try:
                            return float(row[key]) if row.get(key) not in (None, "") else None
                        except (TypeError, ValueError):
                            return None
                    rows.append({"t": t, "btc": num("btc_close"), "eth": num("eth_close"), "ethbtc": num("ethbtc_close")})
            except Exception:
                pass
        day += timedelta(days=1)
    return sorted(rows, key=lambda x: x["t"])


def closest(rows: list[dict[str, Any]], target: datetime) -> dict[str, Any] | None:
    eligible = [r for r in rows if abs((r["t"] - target).total_seconds()) <= 7200]
    return min(eligible, key=lambda r: abs((r["t"] - target).total_seconds())) if eligible else None


def excursion(start: float | None, values: list[float]) -> tuple[float | None, float | None]:
    changes = [pct(start, v) for v in values] if start is not None else []
    finite = [v for v in changes if v is not None]
    return (max(finite), min(finite)) if finite else (None, None)


def direction_score(predicted: str, realized: float | None) -> dict[str, Any]:
    if predicted in {"UNAVAILABLE", "NO_EDGE", "MIXED"}:
        return {"result": "ABSTAINED", "correct": None, "predicted": predicted, "realized_pct": realized}
    if realized is None:
        return {"result": "UNAVAILABLE", "correct": None, "predicted": predicted, "realized_pct": None}
    if predicted == "SIDEWAYS":
        return {"result": "UNAVAILABLE_NO_REGISTERED_SIDEWAYS_TOLERANCE", "correct": None, "predicted": predicted, "realized_pct": realized}
    correct = realized > 0 if predicted == "UP" else realized < 0 if predicted == "DOWN" else None
    if correct is None:
        return {"result": "UNSUPPORTED", "correct": None, "predicted": predicted, "realized_pct": realized}
    return {"result": "CORRECT" if correct else "INCORRECT", "correct": correct, "predicted": predicted, "realized_pct": realized}



def checkpoint_role(lane: str, label: str) -> str:
    if (lane, label) in {("21_30d", "30d"), ("4_8w", "56d")}:
        return "FINAL_MATURITY"
    if (lane, label) in {("21_30d", "21d"), ("4_8w", "42d")}:
        return "STRATEGIC_CHECKPOINT"
    return "MONITOR_ONLY"


def mature(repo: Path, anchor_path: Path, lane: str, label: str, days: int, now: datetime) -> dict[str, Any] | None:
    anchor = json.loads(anchor_path.read_text())
    issued = parse_time(anchor.get("issued_at_utc"))
    if issued is None:
        return None
    target = issued + timedelta(days=days)
    if now < target:
        return None
    out = repo / ROOT / "outcomes" / issued.strftime("%Y/%m/%d") / f"{anchor['anchor_id']}_{label}.json"
    if out.exists():
        return {"status": "ALREADY_MATURED", "path": str(out.relative_to(repo))}

    rows = load_hourly(repo, issued, target)
    endpoint = closest(rows, target)
    if endpoint is None:
        return {"status": "PENDING_TARGET_EVIDENCE", "anchor_id": anchor.get("anchor_id"), "checkpoint": label}

    ref = anchor.get("market_reference") or {}
    btc0, eth0, ratio0 = ref.get("btc_usdt"), ref.get("eth_usdt"), ref.get("ethbtc")
    btc_r, eth_r, ratio_r = pct(btc0, endpoint.get("btc")), pct(eth0, endpoint.get("eth")), pct(ratio0, endpoint.get("ethbtc"))
    interval = [r for r in rows if issued <= r["t"] <= target]
    btc_mfe, btc_mae = excursion(btc0, [r["btc"] for r in interval if isinstance(r.get("btc"), (int, float))])
    eth_mfe, eth_mae = excursion(eth0, [r["eth"] for r in interval if isinstance(r.get("eth"), (int, float))])
    forecast = anchor["strategic_21_30d"] if lane == "21_30d" else anchor["cycle_4_8w"]
    structural_direction = str(forecast.get("direction") or "UNAVAILABLE")
    if lane == "21_30d":
        btc_predicted = str(forecast.get("btc_direction") or "UNAVAILABLE")
        eth_predicted = str(forecast.get("eth_direction") or "UNAVAILABLE")
        ethbtc_predicted = str(forecast.get("ethbtc_direction") or "UNAVAILABLE")
        direction_accuracy = {
            "btc": direction_score(btc_predicted, btc_r),
            "eth": direction_score(eth_predicted, eth_r),
            "ethbtc": direction_score(ethbtc_predicted, ratio_r),
        }
    else:
        direction_accuracy = {
            "btc": {"result": "UNAVAILABLE_NO_ASSET_SPECIFIC_FORECAST", "correct": None, "predicted": None, "realized_pct": btc_r},
            "eth": {"result": "UNAVAILABLE_NO_ASSET_SPECIFIC_FORECAST", "correct": None, "predicted": None, "realized_pct": eth_r},
            "ethbtc": {"result": "UNAVAILABLE_NO_ASSET_SPECIFIC_FORECAST", "correct": None, "predicted": None, "realized_pct": ratio_r},
        }

    value = {
        "contract": "STRATEGIC_COMPASS_OUTCOME_v1",
        "scoring_contract": anchor.get("scoring_contract"),
        "anchor_id": anchor.get("anchor_id"),
        "forecast_path": str(anchor_path.relative_to(repo)),
        "lane": lane,
        "checkpoint": label,
        "checkpoint_role": checkpoint_role(lane, label),
        "target_at_utc": target.isoformat().replace("+00:00", "Z"),
        "target_observation_at_utc": endpoint["t"].isoformat().replace("+00:00", "Z"),
        "realized": {
            "btc_return_pct": btc_r, "eth_return_pct": eth_r, "ethbtc_return_pct": ratio_r,
            "btc_mfe_pct": btc_mfe, "btc_mae_pct": btc_mae,
            "eth_mfe_pct": eth_mfe, "eth_mae_pct": eth_mae,
        },
        "frozen_direction_fields": {
            "structural_direction": structural_direction,
            "btc_direction": forecast.get("btc_direction") if lane == "21_30d" else None,
            "eth_direction": forecast.get("eth_direction") if lane == "21_30d" else None,
            "ethbtc_direction": forecast.get("ethbtc_direction") if lane == "21_30d" else None,
        },
        "direction_accuracy": direction_accuracy,
        "unscored_dimensions": {
            "path_sequence": "PENDING_GOVERNED_PATH_SCORER",
            "regime_destination": "PENDING_GOVERNED_REGIME_OUTCOME_SERIES",
            "rotation_ladder": "PENDING_GOVERNED_CAP_BUCKET_OUTCOME_SERIES",
            "breadth_transmission": "PENDING_GOVERNED_BREADTH_OUTCOME_SERIES",
            "distribution_warning": "PENDING_GOVERNED_EVENT_SCORER",
        },
        "authority": {"portfolio_execution": False, "forecast_rewrite": False, "purpose": "POST_MATURITY_ACCOUNTABILITY_ONLY"},
    }
    value["outcome_sha256"] = hashlib.sha256(canon(value)).hexdigest()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(canon(value))
    return {"status": "MATURED", "path": str(out.relative_to(repo)), "anchor_id": anchor.get("anchor_id"), "checkpoint": label, "outcome_sha256": value["outcome_sha256"]}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--now-utc")
    args = ap.parse_args()
    repo = args.repo_root.resolve()
    now = parse_time(args.now_utc) if args.now_utc else datetime.now(timezone.utc).replace(microsecond=0)
    if now is None:
        raise SystemExit("invalid_now")
    anchors = repo / ROOT / "anchors"
    results: list[dict[str, Any]] = []
    if anchors.exists():
        for anchor in sorted(anchors.rglob("SC-*.json")):
            for lane, checkpoints in CHECKPOINTS.items():
                for label, days in checkpoints.items():
                    result = mature(repo, anchor, lane, label, days, now)
                    if result:
                        results.append(result)
    print(json.dumps({"contract": "STRATEGIC_COMPASS_MATURITY_RUN_v1", "generated_at_utc": now.isoformat().replace("+00:00", "Z"), "results": results}, sort_keys=True))


if __name__ == "__main__":
    main()
