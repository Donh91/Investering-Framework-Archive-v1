from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

HORIZONS_HOURS = (1, 4, 12, 24, 72)
NUMERIC_FIELDS = (
    "btc_close", "eth_close", "ethbtc_close",
    "btc_open_interest", "eth_open_interest",
    "btc_long_short_ratio", "eth_long_short_ratio",
)


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def parse_ts(raw: Any) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def to_float(raw: Any) -> float | None:
    try:
        if raw in (None, ""):
            return None
        return float(raw)
    except Exception:
        return None


def load_hourly_rows(root: Path, cutoff: datetime) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not root.exists():
        return rows
    for path in sorted(root.rglob("*.csv")):
        try:
            with path.open(newline="", encoding="utf-8") as handle:
                for raw in csv.DictReader(handle):
                    ts = parse_ts(raw.get("timestamp_utc"))
                    if ts is None or ts > cutoff:
                        continue
                    row: dict[str, Any] = {"timestamp": ts, "source_path": str(path)}
                    for field in NUMERIC_FIELDS:
                        row[field] = to_float(raw.get(field))
                    row["btc_taker_buy_quote_share"] = to_float(raw.get("btc_taker_buy_quote_share"))
                    row["eth_taker_buy_quote_share"] = to_float(raw.get("eth_taker_buy_quote_share"))
                    row["btc_high"] = to_float(raw.get("btc_high"))
                    row["btc_low"] = to_float(raw.get("btc_low"))
                    row["eth_high"] = to_float(raw.get("eth_high"))
                    row["eth_low"] = to_float(raw.get("eth_low"))
                    rows.append(row)
        except Exception:
            continue
    rows.sort(key=lambda item: item["timestamp"])
    return rows


def pct_change(latest: float | None, anchor: float | None) -> float | None:
    if latest is None or anchor in (None, 0):
        return None
    return round((latest / anchor - 1.0) * 100.0, 6)


def mean(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 6) if values else None


def select_anchor(rows: list[dict[str, Any]], target: datetime, max_lag_hours: float) -> dict[str, Any] | None:
    candidates = [row for row in rows if row["timestamp"] <= target]
    if not candidates:
        return None
    anchor = candidates[-1]
    lag = (target - anchor["timestamp"]).total_seconds() / 3600.0
    return anchor if lag <= max_lag_hours else None


def build_horizon(rows: list[dict[str, Any]], cutoff: datetime, hours: int) -> dict[str, Any]:
    if not rows:
        return {"status": "UNAVAILABLE", "target_hours": hours}
    latest = rows[-1]
    target = cutoff - timedelta(hours=hours)
    tolerance = 1.25 if hours == 1 else min(6.0, max(2.0, hours * 0.25))
    anchor = select_anchor(rows, target, tolerance)
    if anchor is None:
        return {"status": "UNAVAILABLE", "target_hours": hours, "reason": "NO_ANCHOR_WITHIN_TOLERANCE"}
    window = [row for row in rows if anchor["timestamp"] <= row["timestamp"] <= latest["timestamp"]]
    btc_highs = [v for v in (row.get("btc_high") for row in window) if isinstance(v, float)]
    btc_lows = [v for v in (row.get("btc_low") for row in window) if isinstance(v, float)]
    eth_highs = [v for v in (row.get("eth_high") for row in window) if isinstance(v, float)]
    eth_lows = [v for v in (row.get("eth_low") for row in window) if isinstance(v, float)]
    btc_taker = [v for v in (row.get("btc_taker_buy_quote_share") for row in window) if isinstance(v, float)]
    eth_taker = [v for v in (row.get("eth_taker_buy_quote_share") for row in window) if isinstance(v, float)]
    return {
        "status": "READY",
        "target_hours": hours,
        "anchor_timestamp_utc": anchor["timestamp"].isoformat().replace("+00:00", "Z"),
        "latest_timestamp_utc": latest["timestamp"].isoformat().replace("+00:00", "Z"),
        "actual_span_hours": round((latest["timestamp"] - anchor["timestamp"]).total_seconds() / 3600.0, 3),
        "sample_count": len(window),
        "btc_return_pct": pct_change(latest.get("btc_close"), anchor.get("btc_close")),
        "eth_return_pct": pct_change(latest.get("eth_close"), anchor.get("eth_close")),
        "ethbtc_return_pct": pct_change(latest.get("ethbtc_close"), anchor.get("ethbtc_close")),
        "btc_oi_change_pct": pct_change(latest.get("btc_open_interest"), anchor.get("btc_open_interest")),
        "eth_oi_change_pct": pct_change(latest.get("eth_open_interest"), anchor.get("eth_open_interest")),
        "btc_long_short_change_pct": pct_change(latest.get("btc_long_short_ratio"), anchor.get("btc_long_short_ratio")),
        "eth_long_short_change_pct": pct_change(latest.get("eth_long_short_ratio"), anchor.get("eth_long_short_ratio")),
        "btc_taker_buy_quote_share_mean": mean(btc_taker),
        "eth_taker_buy_quote_share_mean": mean(eth_taker),
        "btc_window_high": max(btc_highs) if btc_highs else None,
        "btc_window_low": min(btc_lows) if btc_lows else None,
        "eth_window_high": max(eth_highs) if eth_highs else None,
        "eth_window_low": min(eth_lows) if eth_lows else None,
    }


def breadth_ratio(metrics: dict[str, Any]) -> float | None:
    breadth = metrics.get("breadth") if isinstance(metrics.get("breadth"), dict) else {}
    values = [breadth.get("advancers"), breadth.get("decliners"), breadth.get("flat")]
    if not all(isinstance(value, (int, float)) for value in values):
        return None
    total = float(sum(values))
    return round(float(breadth["advancers"]) / total, 6) if total else None


def breadth_context(base: dict[str, Any]) -> dict[str, Any]:
    latest = base.get("latest_capture") if isinstance(base.get("latest_capture"), dict) else {}
    previous = base.get("previous_capture") if isinstance(base.get("previous_capture"), dict) else {}
    latest_ratio = breadth_ratio(latest.get("market_metrics", {}))
    previous_ratio = breadth_ratio(previous.get("market_metrics", {}))
    return {
        "latest_advance_ratio": latest_ratio,
        "previous_advance_ratio": previous_ratio,
        "advance_ratio_delta_pp": round((latest_ratio - previous_ratio) * 100.0, 4) if latest_ratio is not None and previous_ratio is not None else None,
        "source": "OWNER_CAPTURE_BREADTH_ONLY",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", type=Path, required=True)
    parser.add_argument("--hourly-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    context = json.loads(args.context.read_text())
    latest = context.get("latest_capture") if isinstance(context.get("latest_capture"), dict) else {}
    cutoff = parse_ts(latest.get("captured_at_utc"))
    if cutoff is None:
        raise SystemExit("latest_capture_timestamp_required")
    rows = load_hourly_rows(args.hourly_root, cutoff)
    context["api_intelligence_v2"] = {
        "contract": "API_INTELLIGENCE_SEQUENCE_CONTEXT_v2",
        "authority": "SHADOW_CONTEXT_ONLY",
        "canonical_state": False,
        "cutoff_utc": cutoff.isoformat().replace("+00:00", "Z"),
        "hourly_rows_available": len(rows),
        "horizons": {str(hours): build_horizon(rows, cutoff, hours) for hours in HORIZONS_HOURS},
        "breadth_delta": breadth_context(context),
        "rules": [
            "All deltas are deterministic observations from retained owner/hourly data.",
            "Unavailable horizons remain unknown and are not imputed.",
            "This layer routes analytical attention only and cannot create market state or portfolio action."
        ],
    }
    context["context_hash"] = hashlib.sha256(canonical_bytes({k: v for k, v in context.items() if k != "context_hash"})).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_bytes(context))
    print(json.dumps({"status": "PASS", "hourly_rows": len(rows), "context_hash": context["context_hash"]}, sort_keys=True))


if __name__ == "__main__":
    main()
