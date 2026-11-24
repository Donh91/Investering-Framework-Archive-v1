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


def sequence_census(observations, *, history_truncated=False):
    """Descriptive observation-order proxy for frozen sequence 1, never a signal.

    Inputs must come from full original-owner replay. A repeated snapshot is not
    a new transition. No confirmation duration, precise event order, causal
    effect, delay benefit, or independent first-known claim is inferred.
    """
    result = {
        "contract": "CORE_OBSERVED_SEQUENCE_CENSUS_v1",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "scientific_pit_eligible": False, "forecast_authority": False,
        "original_sequence_equivalence": False, "event_time_certified": False,
        "history_truncated": history_truncated,
        "status": "NO_OBSERVED_ABOVE_EPISODE", "observation_n": len(observations),
        "above_observation_n": 0, "unidentified_censored_above_n": 0,
        "observed_episode_n": 0, "ordered_proxy_episode_n": 0, "episodes": [],
        "stable_confirmation_status": "NO_FROZEN_DURATION_RULE",
        "step_value_status": "UNTESTED_MATCHED_OUTCOMES_AND_DELAY_COST_REQUIRED",
        "sequence_2": {"status": "BLOCKED_MISSING_SOURCE", "missing": ["BTC_ETF_ABSORPTION"]},
        "sequence_3": {"status": "BLOCKED_MISSING_SOURCE",
                       "missing": ["PRICE_STRESS", "LIQUIDATION_CLEARANCE", "OI_FUNDING_RESET", "RECLAIM"]},
    }
    episodes = {}
    previous = None
    active = None
    closed = set()
    seen_btcd, seen_breadth = {}, {}
    for row in sorted(observations, key=lambda item: item["observation_utc"]):
        at = row["observation_utc"]
        if previous and at <= previous["observation_utc"]:
            raise ValueError("SEQUENCE_DUPLICATE_OBSERVATION_CLOCK")
        p = row["persistence"]
        # Same settled BTC.D prints or same breadth run cannot mint another
        # independent observation. Inconsistent revisions block this diagnostic.
        for seen, key, state in ((seen_btcd, tuple(row["btcd_settled_dates"]), row["btcd_state"]),
                                  (seen_breadth, row["breadth_run_id"], row["breadth_state"])):
            if not key or (key in seen and seen[key] != state):
                raise ValueError("SEQUENCE_SOURCE_IDENTITY_CONFLICT")
            seen[key] = state
        key = p["first_above_bar_utc"] if p["side"] == "ABOVE" else None
        if p["side"] == "ABOVE":
            result["above_observation_n"] += 1
            if key is None:
                result["unidentified_censored_above_n"] += 1
        if active != key:
            if active is not None:
                closed.add(active)
            if key is not None and key in closed:
                raise ValueError("SEQUENCE_EPISODE_REAPPEARED_AFTER_BREAK")
            active = key
        if key is not None:
            ep = episodes.setdefault(key, {
                "observed_crossing_bar_utc": key,
                "first_observation_utc": at, "last_observation_utc": at,
                "observation_n": 0, "max_observed_consecutive_hours": 0,
                "btcd_falling_path_interval": None, "breadth_majority_interval": None,
                "stable_confirmation_utc": None, "status": "CROSSING_OBSERVED_ONLY",
            })
            ep["observation_n"] += 1
            ep["last_observation_utc"] = at
            ep["max_observed_consecutive_hours"] = max(
                ep["max_observed_consecutive_hours"], p["consecutive_same_side"])
            if previous and previous["persistence"]["first_above_bar_utc"] == key:
                # Reset downstream confirmation when the observed path is lost.
                if row["btcd_state"] != "FALLING_PATH":
                    ep["btcd_falling_path_interval"] = None
                    ep["breadth_majority_interval"] = None
                if row["breadth_state"] != "BROAD_MAJORITY":
                    ep["breadth_majority_interval"] = None
                if (previous["btcd_state"] != "FALLING_PATH" and
                        row["btcd_state"] == "FALLING_PATH" and
                        row["btcd_settled_dates"][-1] > previous["btcd_settled_dates"][-1]):
                    ep["btcd_falling_path_interval"] = [previous["observation_utc"], at]
                interval = ep["btcd_falling_path_interval"]
                if (interval and interval[1] <= previous["observation_utc"] and
                        previous["breadth_state"] == "NON_BROAD_MAJORITY" and
                        row["breadth_state"] == "BROAD_MAJORITY" and
                        row["breadth_run_id"] != previous["breadth_run_id"] and
                        row["breadth_capture_utc"] > previous["breadth_capture_utc"]):
                    ep["breadth_majority_interval"] = [previous["observation_utc"], at]
            ep["status"] = ("ORDERED_OBSERVATION_PROXY" if ep["breadth_majority_interval"]
                            else "BTCD_PATH_OBSERVED_AFTER_CROSSING" if ep["btcd_falling_path_interval"]
                            else "CROSSING_OBSERVED_ONLY")
        previous = row
    result["episodes"] = list(episodes.values())
    result["observed_episode_n"] = len(episodes)
    result["ordered_proxy_episode_n"] = sum(e["status"] == "ORDERED_OBSERVATION_PROXY"
                                            for e in episodes.values())
    if episodes:
        result["status"] = ("ORDERED_OBSERVATION_PROXY_PRESENT" if result["ordered_proxy_episode_n"]
                            else "NO_ORDERED_OBSERVATION_PROXY")
    elif result["unidentified_censored_above_n"]:
        result["status"] = "ABOVE_EPISODE_START_UNAVAILABLE"
    return result
