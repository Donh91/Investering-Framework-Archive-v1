"""Observation-only persistence from the existing owner's verified hourly window.

No new trading rule, candidate permission, confirmation threshold or independent
first-known assertion. Historical rows and frozen C01-C07 remain unchanged.
"""
from datetime import datetime, timedelta, timezone
from math import isfinite

HOUR = timedelta(hours=1)
N = 168
LEVEL = 0.03
METHOD = "DIRECT_ETHBTC_HOURLY_CLOSES_NO_RATIO_SYNTHESIS"


def _utc(value):
    if not isinstance(value, datetime) or value.utcoffset() != timedelta(0):
        raise ValueError("ETHBTC_CLOCK_INVALID")
    return value


def _iso(value):
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _side(value):
    if type(value) not in (float, int) or not isfinite(value) or value <= 0:
        raise ValueError("ETHBTC_CLOSE_INVALID")
    return "ABOVE" if value > LEVEL else "BELOW" if value < LEVEL else "AT"


def replay(window, cutoff):
    cutoff = _utc(cutoff)
    if len(window) != N:
        raise ValueError("ETHBTC_WINDOW_SIZE_INVALID")
    clocks, available, sides = [], [], []
    for row in window:
        t, a = _utc(row["ts"]), _utc(row["available"])
        if t.minute or t.second or t.microsecond or a < t + HOUR or a > cutoff:
            raise ValueError("ETHBTC_BAR_CLOCK_INVALID")
        if clocks and t - clocks[-1] != HOUR:
            raise ValueError("ETHBTC_WINDOW_CONTINUITY_INVALID")
        clocks.append(t)
        available.append(a)
        sides.append(_side(row["ethbtc"]))
    side = sides[-1]
    n = 1
    while n < N and sides[-n-1] == side:
        n += 1
    i = N-n
    censored = i == 0
    return {
        "contract": "ETHBTC_PERSISTENCE_REPLAY_v1",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "side": side,
        "consecutive_same_side": n,
        "left_censored": censored,
        "window_start_utc": _iso(clocks[0]),
        "window_end_utc": _iso(clocks[-1]),
        "observed_run_start_bar_utc": _iso(clocks[i]),
        "run_start_bar_utc": None if censored else _iso(clocks[i]),
        "prior_bar_utc": None if censored else _iso(clocks[i-1]),
        "first_above_bar_utc": _iso(clocks[i]) if side == "ABOVE" and not censored else None,
        "first_above_source_window_end_utc": _iso(available[i]) if side == "ABOVE" and not censored else None,
        "run_source_declared_end_max_utc": _iso(max(available[max(0,i-1):])),
        "independent_first_known_utc": None,
        "stable_confirmation_utc": None,
        "stable_confirmation_status": "NO_FROZEN_DURATION_RULE",
        "forecast_authority": False,
        "scientific_pit_eligible": False,
    }


def verify_window_inputs(window, cutoff, inputs):
    result = replay(window, cutoff)
    expected = {
        "lookback_rows": N, "sample_count": N, "continuous_hours": N,
        "window_start_utc": result["window_start_utc"],
        "window_end_utc": result["window_end_utc"],
        "consecutive_same_side": result["consecutive_same_side"],
        "method": METHOD,
    }
    for key, value in expected.items():
        supplied = inputs.get(key)
        if type(supplied) is not type(value) or supplied != value:
            raise ValueError(f"ETHBTC_PERSISTENCE_FIELD_MISMATCH:{key}")
    return result
