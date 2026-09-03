from __future__ import annotations

import math
from datetime import datetime
from typing import Any

from forecast_study_common_v1_3_2 import digest, iso, parse_dt

def b1_climatology(
    bars: list[dict[str, Any]],
    freeze_utc: str,
    horizon_days: int,
    direction: str,
    threshold_pct: float,
    trailing_origins: int = 180,
    min_events: int = 20,
) -> dict[str, Any]:
    if direction not in {"UP", "DOWN"}:
        raise ValueError("F1_DIRECTIONAL_ONLY")
    if horizon_days not in {1, 2, 3, 5, 7}:
        raise ValueError("UNSUPPORTED_HORIZON")
    if not isinstance(threshold_pct, (int, float)) or float(threshold_pct) <= 0:
        raise ValueError("THRESHOLD_POSITIVE_REQUIRED")
    freeze = parse_dt(freeze_utc)
    xs: list[tuple[datetime, float]] = []
    for row in bars:
        t = parse_dt(str(row["close_utc"]))
        v = float(row["close"])
        if not math.isfinite(v) or v <= 0:
            raise ValueError("INVALID_DAILY_CLOSE")
        if t >= freeze:
            raise ValueError("B1_INPUT_CONTAINS_POST_FREEZE_OBSERVATION")
        xs.append((t, v))
    xs.sort(key=lambda item: item[0])
    if len(xs) < min_events + horizon_days:
        raise ValueError("B1_MIN_EVENTS_NOT_MET")
    if any(xs[i][0] >= xs[i + 1][0] for i in range(len(xs) - 1)):
        raise ValueError("NON_UNIQUE_DAILY_CLOSE_TIME")
    for i in range(len(xs) - 1):
        delta = xs[i + 1][0] - xs[i][0]
        if abs(delta.total_seconds() - 86400.0) > 0.01:
            raise ValueError("B1_DAILY_HISTORY_GAP_OR_DUPLICATE")

    events: list[tuple[int, datetime, datetime, bool, float]] = []
    for i in range(0, len(xs) - horizon_days):
        t0, v0 = xs[i]
        t1, v1 = xs[i + horizon_days]
        if t1 >= freeze:
            continue
        move = (v1 / v0 - 1.0) * 100.0
        hit = move >= float(threshold_pct) if direction == "UP" else move <= -float(threshold_pct)
        events.append((i, t0, t1, hit, move))
    if len(events) < min_events:
        raise ValueError("B1_MIN_EVENTS_NOT_MET")
    selected = events[-trailing_origins:]
    if len(selected) < min_events:
        raise ValueError("B1_MIN_EVENTS_NOT_MET")
    p_clim = sum(1 for *_, hit, _move in selected if hit) / len(selected)
    first_origin_idx = selected[0][0]
    last_end_idx = selected[-1][0] + horizon_days
    selected_bars = [
        {"close_utc": iso(t), "close": v}
        for t, v in xs[first_origin_idx : last_end_idx + 1]
    ]
    return {
        "contract": "B1_CLIMATOLOGY_FREEZE_v1",
        "freeze_utc": iso(freeze),
        "horizon_days": horizon_days,
        "direction": direction,
        "threshold_pct": float(threshold_pct),
        "trailing_origin_window": trailing_origins,
        "minimum_events": min_events,
        "admissible_event_count": len(selected),
        "p_clim": p_clim,
        "first_origin_close_utc": iso(selected[0][1]),
        "last_origin_close_utc": iso(selected[-1][1]),
        "last_event_end_close_utc": iso(selected[-1][2]),
        "selected_input_bar_count": len(selected_bars),
        "selected_input_bars_sha256": digest(selected_bars),
        "selected_input_bars": selected_bars,
        "no_lookahead": selected[-1][2] < freeze,
        "daily_origin_continuity_verified": True,
    }
