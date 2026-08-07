from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from itertools import combinations
from pathlib import Path
from statistics import mean
from typing import Any

FIELDS = ["score","volatility","volume","impulse","technical","social","dominance","trends","whales","orders"]
Q_LEVELS = (0.10, 0.20, 0.30)
EPOCH = "UPGRADED_POST_20260708"


def canon(v: Any) -> bytes:
    return (json.dumps(v, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(v: Any) -> str:
    return hashlib.sha256(canon(v)).hexdigest()


def read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def quantile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("empty_quantile")
    xs = sorted(values)
    pos = (len(xs) - 1) * q
    lo, hi = int(pos), min(int(pos) + 1, len(xs) - 1)
    frac = pos - lo
    return xs[lo] * (1 - frac) + xs[hi] * frac


def row_values(row: dict[str, Any]) -> dict[str, float] | None:
    nested = row.get("components") if isinstance(row.get("components"), dict) else {}
    out: dict[str, float] = {}
    for field in FIELDS:
        value = row.get(field) if field == "score" else nested.get(field, row.get(field))
        if not isinstance(value, (int, float)):
            return None
        out[field] = float(value)
    return out


def cfgi_rows(block: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for row in block.get("rows", []):
        if not isinstance(row, dict) or row.get("pdlt_engine_epoch") != EPOCH:
            continue
        if str(row.get("symbol")) != "MARKET":
            continue
        values = row_values(row)
        if values is None or not row.get("timestamp"):
            continue
        out.append({"timestamp": row["timestamp"], "dt": ts(row["timestamp"]), "values": values})
    out.sort(key=lambda r: r["dt"])
    return out


def btc_candles(owner: dict[str, Any]) -> list[dict[str, Any]]:
    rows = owner.get("candles", {}).get("BTCUSDT", [])
    out = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        out.append({**row, "dt": ts(row["open_time"])})
    out.sort(key=lambda r: r["dt"])
    return out


def locate(candles: list[dict[str, Any]], when: datetime) -> int | None:
    idx = None
    for i, row in enumerate(candles):
        if row["dt"] <= when:
            idx = i
        else:
            break
    return idx


def forward_stats(candles: list[dict[str, Any]], idx: int, hours: int) -> dict[str, float] | None:
    start = float(candles[idx]["close"])
    end_time = candles[idx]["dt"] + timedelta(hours=hours)
    future = [r for r in candles[idx + 1:] if r["dt"] <= end_time]
    expected = int(hours / 4)
    if len(future) < max(1, expected - 1):
        return None
    low = min(float(r["low"]) for r in future)
    high = max(float(r["high"]) for r in future)
    end_close = float(future[-1]["close"])
    adverse = max(0.0, (1.0 - low / start) * 100.0)
    favorable = max(0.0, (high / start - 1.0) * 100.0)
    return {"adverse_pct": adverse, "favorable_pct": favorable, "end_close": end_close, "start": start}


def build_dataset(block: dict[str, Any], price_owner: dict[str, Any]) -> list[dict[str, Any]]:
    rows = cfgi_rows(block)
    candles = btc_candles(price_owner)
    out = []
    previous: dict[str, float] | None = None
    for row in rows:
        current = row["values"]
        if previous is None:
            previous = current
            continue
        idx = locate(candles, row["dt"])
        if idx is None:
            previous = current
            continue
        stats72 = forward_stats(candles, idx, 72)
        stats7d = forward_stats(candles, idx, 168)
        stats14d = forward_stats(candles, idx, 336)
        if stats72 is None:
            previous = current
            continue
        out.append({
            "timestamp": row["timestamp"],
            "dt": row["dt"],
            "deltas": {field: current[field] - previous[field] for field in FIELDS},
            "72h": stats72,
            "7d": stats7d,
            "14d": stats14d,
        })
        previous = current
    return out


def brier(rows: list[dict[str, Any]], key: str, p: float) -> float:
    if not rows:
        return 1.0
    return mean((p - float(r[key])) ** 2 for r in rows)


def matches(row: dict[str, Any], conditions: list[dict[str, Any]]) -> bool:
    for c in conditions:
        value = row["deltas"].get(c["field"])
        if value is None or float(value) > float(c["threshold"]):
            return False
    return True


def add_labels(rows: list[dict[str, Any]], thresholds: dict[str, float]) -> None:
    for row in rows:
        row["event72"] = int(row["72h"]["adverse_pct"] >= thresholds["pullback_72h_pct"])
        row["event7d"] = int(row["7d"] is not None and row["7d"]["adverse_pct"] >= thresholds["heavy_pullback_7d_pct"])
        row["event14d"] = int(row["14d"] is not None and row["14d"]["adverse_pct"] >= thresholds["distribution_14d_pct"] and row["14d"]["end_close"] < row["14d"]["start"])


def candidate_metrics(rows: list[dict[str, Any]], conditions: list[dict[str, Any]], baseline: dict[str, float]) -> dict[str, Any]:
    fired = [r for r in rows if matches(r, conditions)]
    probs = {
        "p_pullback_72h": mean(r["event72"] for r in fired) if fired else baseline["p_pullback_72h"],
        "p_heavy_pullback_7d": mean(r["event7d"] for r in fired) if fired else baseline["p_heavy_pullback_7d"],
        "p_persistent_distribution_14d": mean(r["event14d"] for r in fired) if fired else baseline["p_persistent_distribution_14d"],
    }
    b_base = brier(rows, "event72", baseline["p_pullback_72h"])
    b_rule = mean(((probs["p_pullback_72h"] if matches(r, conditions) else baseline["p_pullback_72h"]) - r["event72"]) ** 2 for r in rows) if rows else 1.0
    return {"fires": len(fired), "probabilities": probs, "brier72": b_rule, "baseline_brier72": b_base, "brier_improvement72": b_base - b_rule, "fired_event_rate72": mean(r["event72"] for r in fired) if fired else None}


def discover(block: dict[str, Any], price_owner: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    rows = build_dataset(block, price_owner)
    if len(rows) < 60:
        raise ValueError(f"insufficient_post_epoch_rows:{len(rows)}")
    split = max(30, int(len(rows) * 0.60))
    purge = 18
    train = rows[:split]
    holdout = rows[min(len(rows), split + purge):]
    if len(holdout) < 12:
        raise ValueError(f"insufficient_holdout_rows:{len(holdout)}")

    thresholds = {
        "pullback_72h_pct": quantile([r["72h"]["adverse_pct"] for r in train], 0.75),
        "heavy_pullback_7d_pct": quantile([r["7d"]["adverse_pct"] for r in train if r["7d"] is not None], 0.85),
        "distribution_14d_pct": quantile([r["14d"]["adverse_pct"] for r in train if r["14d"] is not None], 0.80),
    }
    add_labels(train, thresholds)
    add_labels(holdout, thresholds)
    baseline = {
        "p_pullback_72h": mean(r["event72"] for r in train),
        "p_heavy_pullback_7d": mean(r["event7d"] for r in train),
        "p_persistent_distribution_14d": mean(r["event14d"] for r in train),
    }
    field_thresholds = {field: {str(q): quantile([r["deltas"][field] for r in train], q) for q in Q_LEVELS} for field in FIELDS}
    raw_candidates = []
    for field in FIELDS:
        for q in Q_LEVELS:
            conditions = [{"symbol":"MARKET","field":field,"operator":"<=","threshold":field_thresholds[field][str(q)],"quantile":q}]
            m = candidate_metrics(train, conditions, baseline)
            if m["fires"] >= 8:
                raw_candidates.append((conditions, m))
    for a, b in combinations(FIELDS, 2):
        for q in (0.20, 0.30):
            conditions = [
                {"symbol":"MARKET","field":a,"operator":"<=","threshold":field_thresholds[a][str(q)],"quantile":q},
                {"symbol":"MARKET","field":b,"operator":"<=","threshold":field_thresholds[b][str(q)],"quantile":q},
            ]
            m = candidate_metrics(train, conditions, baseline)
            if m["fires"] >= 8:
                raw_candidates.append((conditions, m))
    raw_candidates.sort(key=lambda item: (item[1]["brier_improvement72"], item[1]["fires"]), reverse=True)
    selected = []
    used_signatures = set()
    for conditions, train_metrics in raw_candidates:
        signature = tuple(sorted(c["field"] for c in conditions))
        if signature in used_signatures:
            continue
        hold = candidate_metrics(holdout, conditions, baseline)
        hold_baseline_rate = mean(r["event72"] for r in holdout)
        eligible = hold["fires"] >= 3 and hold["brier72"] <= hold["baseline_brier72"] + 0.02 and (hold["fired_event_rate72"] or 0.0) >= hold_baseline_rate
        cid = "PDLT-CAND-" + hashlib.sha256(canon(conditions)).hexdigest()[:12]
        selected.append({
            "candidate_id": cid,
            "conditions": conditions,
            "probabilities": train_metrics["probabilities"],
            "train_metrics": train_metrics,
            "holdout_metrics": hold,
            "holdout_baseline_event_rate72": hold_baseline_rate,
            "forward_eligible": bool(eligible),
        })
        used_signatures.add(signature)
        if len(selected) == 3:
            break
    model = {
        "contract": "PDLT_FROZEN_MODEL_v1",
        "experiment_id": "PDLT-v1.1-RUN",
        "engine_epoch": EPOCH,
        "selection_target": "PULLBACK_72H",
        "selection_rule": "top discovery Brier improvement; blind holdout only gates forward eligibility and never changes thresholds",
        "split": {"post_epoch_rows": len(rows), "train_rows": len(train), "purge_rows": min(purge, max(0, len(rows)-split)), "holdout_rows": len(holdout)},
        "outcome_thresholds": thresholds,
        "baseline_probabilities": baseline,
        "candidates": selected,
        "authority": {"canonical_promotion":False,"framework_state_change":False,"model_weight_change":False,"portfolio_action":False},
    }
    report = {
        "contract": "PDLT_DISCOVERY_REPORT_v1",
        "model_sha256": sha(model),
        "post_epoch_rows": len(rows),
        "eligible_candidate_count": sum(c["forward_eligible"] for c in selected),
        "selected_candidates": selected,
        "thresholds": thresholds,
        "baseline_probabilities": baseline,
        "warning": "Historical holdout is validation evidence only. Prospective rows remain required for any framework use.",
    }
    return model, report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--validated-market-4h", type=Path, required=True)
    ap.add_argument("--binance-owner", type=Path, required=True)
    ap.add_argument("--model-output", type=Path, required=True)
    ap.add_argument("--report-output", type=Path, required=True)
    args = ap.parse_args()
    model, report = discover(read(args.validated_market_4h), read(args.binance_owner))
    args.model_output.parent.mkdir(parents=True, exist_ok=True)
    args.model_output.write_bytes(canon(model))
    args.report_output.write_bytes(canon(report))
    print(json.dumps({"status":"PASS","model_sha256":report["model_sha256"],"post_epoch_rows":report["post_epoch_rows"],"eligible_candidates":report["eligible_candidate_count"]}, sort_keys=True))


if __name__ == "__main__":
    main()
