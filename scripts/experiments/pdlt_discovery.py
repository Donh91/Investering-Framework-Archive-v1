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

# Phase II / Claude P2 pre-execution methods hardening.
# Fixed calendar boundaries replace the data-dependent 60/40 row split.
TRAIN_END_UTC = "2026-07-22T00:00:00Z"
HOLDOUT_START_UTC = "2026-08-05T00:00:00Z"
PURGE_HOURS = 14 * 24
MIN_TRAIN_ROWS = 60
MIN_HOLDOUT_ROWS = 12
MIN_TRAIN_FIRES = 8
MIN_HOLDOUT_FIRES = 8
MAX_FORWARD_CANDIDATES = 3
DISCOVERY_FAMILY_SIZE = len(FIELDS) * len(Q_LEVELS) + (len(FIELDS) * (len(FIELDS) - 1) // 2) * 2


def canon(v: Any) -> bytes:
    return (json.dumps(v, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(v: Any) -> str:
    return hashlib.sha256(canon(v)).hexdigest()


def read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def iso(dt: datetime | None) -> str | None:
    return None if dt is None else dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


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
        # Preserved legacy surrogate for archival comparability only. It is
        # explicitly blocked from inferential use because it does not implement
        # the full contracted 14d distribution definition in the runbook.
        row["event14d"] = int(
            row["14d"] is not None
            and row["14d"]["adverse_pct"] >= thresholds["distribution_14d_pct"]
            and row["14d"]["end_close"] < row["14d"]["start"]
        )


def empirical_probabilities(fired: list[dict[str, Any]], baseline: dict[str, float]) -> dict[str, float]:
    return {
        "p_pullback_72h": mean(r["event72"] for r in fired) if fired else baseline["p_pullback_72h"],
        "p_heavy_pullback_7d": mean(r["event7d"] for r in fired) if fired else baseline["p_heavy_pullback_7d"],
        "p_persistent_distribution_14d": mean(r["event14d"] for r in fired) if fired else baseline["p_persistent_distribution_14d"],
    }


def candidate_metrics(
    rows: list[dict[str, Any]],
    conditions: list[dict[str, Any]],
    baseline: dict[str, float],
    *,
    fixed_probabilities: dict[str, float] | None = None,
) -> dict[str, Any]:
    fired = [r for r in rows if matches(r, conditions)]
    probs = dict(fixed_probabilities) if fixed_probabilities is not None else empirical_probabilities(fired, baseline)
    b_base = brier(rows, "event72", baseline["p_pullback_72h"])
    b_rule = mean(
        (
            (probs["p_pullback_72h"] if matches(r, conditions) else baseline["p_pullback_72h"])
            - r["event72"]
        ) ** 2
        for r in rows
    ) if rows else 1.0

    fired_losses = []
    for row in fired:
        y = float(row["event72"])
        base_loss = (baseline["p_pullback_72h"] - y) ** 2
        rule_loss = (probs["p_pullback_72h"] - y) ** 2
        fired_losses.append({
            "improved": rule_loss < base_loss,
            "worsened": rule_loss > base_loss,
        })
    improved = sum(x["improved"] for x in fired_losses)
    worsened = sum(x["worsened"] for x in fired_losses)
    ties = len(fired_losses) - improved - worsened
    return {
        "fires": len(fired),
        "probabilities": probs,
        "probability_source": "FIXED_TRAIN_DERIVED" if fixed_probabilities is not None else "EMPIRICAL_SAME_SAMPLE_DISCOVERY_ONLY",
        "brier72": b_rule,
        "baseline_brier72": b_base,
        "brier_improvement72": b_base - b_rule,
        "fired_event_rate72": mean(r["event72"] for r in fired) if fired else None,
        "paired_fired_loss_counts": {"improved": improved, "worsened": worsened, "ties": ties},
    }


def fixed_split(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    train_end = ts(TRAIN_END_UTC)
    holdout_start = ts(HOLDOUT_START_UTC)
    if (holdout_start - train_end).total_seconds() < PURGE_HOURS * 3600:
        raise ValueError("purge_shorter_than_frozen_14d_horizon")
    train = [r for r in rows if r["dt"] < train_end]
    purged = [r for r in rows if train_end <= r["dt"] < holdout_start]
    holdout = [r for r in rows if r["dt"] >= holdout_start]
    if len(train) < MIN_TRAIN_ROWS:
        raise ValueError(f"insufficient_fixed_train_rows:{len(train)}")
    if len(holdout) < MIN_HOLDOUT_ROWS:
        raise ValueError(f"insufficient_fixed_holdout_rows:{len(holdout)}")
    return train, purged, holdout


def range_meta(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "row_count": len(rows),
        "min_timestamp_utc": iso(rows[0]["dt"]) if rows else None,
        "max_timestamp_utc": iso(rows[-1]["dt"]) if rows else None,
    }


def discover(block: dict[str, Any], price_owner: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    rows = build_dataset(block, price_owner)
    train, purged, holdout = fixed_split(rows)

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
    field_thresholds = {
        field: {str(q): quantile([r["deltas"][field] for r in train], q) for q in Q_LEVELS}
        for field in FIELDS
    }

    raw_candidates = []
    for field in FIELDS:
        for q in Q_LEVELS:
            conditions = [{
                "symbol": "MARKET",
                "field": field,
                "operator": "<=",
                "threshold": field_thresholds[field][str(q)],
                "quantile": q,
            }]
            metrics = candidate_metrics(train, conditions, baseline)
            if metrics["fires"] >= MIN_TRAIN_FIRES:
                raw_candidates.append((conditions, metrics))
    for a, b in combinations(FIELDS, 2):
        for q in (0.20, 0.30):
            conditions = [
                {"symbol": "MARKET", "field": a, "operator": "<=", "threshold": field_thresholds[a][str(q)], "quantile": q},
                {"symbol": "MARKET", "field": b, "operator": "<=", "threshold": field_thresholds[b][str(q)], "quantile": q},
            ]
            metrics = candidate_metrics(train, conditions, baseline)
            if metrics["fires"] >= MIN_TRAIN_FIRES:
                raw_candidates.append((conditions, metrics))

    raw_candidates.sort(key=lambda item: (item[1]["brier_improvement72"], item[1]["fires"]), reverse=True)
    selected = []
    used_signatures = set()
    for conditions, train_metrics in raw_candidates:
        signature = tuple(sorted(c["field"] for c in conditions))
        if signature in used_signatures:
            continue
        hold = candidate_metrics(
            holdout,
            conditions,
            baseline,
            fixed_probabilities=train_metrics["probabilities"],
        )
        hold_baseline_rate = mean(r["event72"] for r in holdout)
        eligible = hold["fires"] >= MIN_HOLDOUT_FIRES and hold["brier_improvement72"] > 0.0
        cid = "PDLT-CAND-" + hashlib.sha256(canon(conditions)).hexdigest()[:12]
        selected.append({
            "candidate_id": cid,
            "conditions": conditions,
            "probabilities": train_metrics["probabilities"],
            "train_metrics": train_metrics,
            "holdout_metrics": hold,
            "holdout_baseline_event_rate72": hold_baseline_rate,
            "forward_eligible": bool(eligible),
            "eligibility_contract": {
                "historical_holdout_is_validation_evidence": False,
                "role": "PRE_PROSPECTIVE_SCREEN_ONLY",
                "minimum_holdout_fires": MIN_HOLDOUT_FIRES,
                "requires_strict_positive_brier_improvement72": True,
                "holdout_probability_source": "TRAIN_DERIVED_ONLY",
            },
        })
        used_signatures.add(signature)
        if len(selected) == MAX_FORWARD_CANDIDATES:
            break

    source_meta = {
        "validated_market_4h_canonical_sha256": sha(block),
        "binance_owner_canonical_sha256": sha(price_owner),
        "validated_market_source_sha256": block.get("source_sha256"),
        "cfgi_market_post_epoch_rows": len(cfgi_rows(block)),
        "btc_candle_rows": len(btc_candles(price_owner)),
        "dataset": range_meta(rows),
    }
    split_meta = {
        "policy": "FIXED_CALENDAR_BOUNDARIES_NOT_ROW_FRACTION",
        "train_end_utc_exclusive": TRAIN_END_UTC,
        "holdout_start_utc_inclusive": HOLDOUT_START_UTC,
        "purge_hours": PURGE_HOURS,
        "train": range_meta(train),
        "purged": range_meta(purged),
        "holdout": range_meta(holdout),
    }
    family_meta = {
        "enumerated_rule_count": DISCOVERY_FAMILY_SIZE,
        "single_rules": len(FIELDS) * len(Q_LEVELS),
        "pair_rules": (len(FIELDS) * (len(FIELDS) - 1) // 2) * 2,
        "fields": FIELDS,
        "single_quantiles": list(Q_LEVELS),
        "pair_quantiles": [0.20, 0.30],
        "maximum_frozen_candidates": MAX_FORWARD_CANDIDATES,
        "historical_discovery_is_inferential_evidence": False,
    }

    model = {
        "contract": "PDLT_FROZEN_MODEL_v1",
        "experiment_id": "PDLT-v1.1-RUN",
        "engine_epoch": EPOCH,
        "methods_amendment": "PDLT_METHODS_HARDENING_P2_2026-08-10",
        "selection_target": "PULLBACK_72H",
        "selection_rule": (
            "rank 120-rule discovery family on training Brier improvement; apply frozen training probabilities unchanged to fixed-calendar holdout; "
            "forward eligibility requires >=8 holdout fires and strictly positive holdout Brier improvement; historical holdout is screening only"
        ),
        "split": split_meta,
        "source_provenance": source_meta,
        "discovery_family": family_meta,
        "outcome_thresholds": thresholds,
        "outcome_semantics": {
            "PULLBACK_72H": "PRIMARY_DISCOVERY_TARGET",
            "HEAVY_PULLBACK_7D": "SECONDARY_DESCRIPTIVE_ONLY",
            "PRICE_DISTRIBUTION_14D": "BLOCKED_CONTRACT_CODE_MISMATCH_NOT_INFERENTIAL",
            "ECOSYSTEM_DISTRIBUTION_14D": "NOT_MODELED_BY_DISCOVERY",
        },
        "baseline_probabilities": baseline,
        "candidates": selected,
        "authority": {"canonical_promotion":False,"framework_state_change":False,"model_weight_change":False,"portfolio_action":False},
    }
    report = {
        "contract": "PDLT_DISCOVERY_REPORT_v1",
        "model_sha256": sha(model),
        "post_epoch_rows": len(rows),
        "split": split_meta,
        "source_provenance": source_meta,
        "discovery_family": family_meta,
        "eligible_candidate_count": sum(c["forward_eligible"] for c in selected),
        "selected_candidates": selected,
        "thresholds": thresholds,
        "baseline_probabilities": baseline,
        "scientific_status": "HISTORICAL_SCREEN_ONLY_NOT_EVIDENCE",
        "warning": "Historical discovery/holdout is candidate screening only. Prospective independent episodes remain required for any scientific or framework claim.",
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
    print(json.dumps({"status":"PASS","scientific_status":report["scientific_status"],"model_sha256":report["model_sha256"],"post_epoch_rows":report["post_epoch_rows"],"eligible_candidates":report["eligible_candidate_count"]}, sort_keys=True))


if __name__ == "__main__":
    main()
