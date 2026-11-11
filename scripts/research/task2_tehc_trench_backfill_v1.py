#!/usr/bin/env python3
"""Task2/S7 Tehc-style daily heat retrospective. Public-data, offline, no authority.

Inputs are explicit local snapshots of public API JSON. This module performs NO
HTTP requests, does not activate a scheduler, and is never a Compass forecast.
Historic API rows are vendor backfills, NOT original point-in-time issued data.
"""
from __future__ import annotations

import argparse
import json
import hashlib
import math
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

CONTRACT = "TASK2_TEHC_TRENCH_METHOD_RETROSPECTIVE_v1"
WEIGHTS = {
    "pad_volume": 0.35,
    "tokens_launched": 0.20,
    "bot_volume": 0.25,
    "bot_fees": 0.20,
}
WINDOWS = (90, 365)
COOLDOWN = 0.65
MIN_HISTORY_DAYS = 365
QUOTE = "USD"  # Kraken independent spot benchmark. Never reinterpret as USDT.
BANDS = ("COLD", "MID", "HOT")


def valid_date(value: Any) -> date:
    if not isinstance(value, str) or len(value) != 10:
        raise ValueError("DATE_ISO_REQUIRED")
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError("DATE_ISO_REQUIRED")
    return parsed


def value(v: Any) -> float:
    if v is None or isinstance(v, bool) or isinstance(v, str):
        raise ValueError("SOURCE_VALUE_NOT_NUMERIC")
    n = float(v)
    if not math.isfinite(n) or n < 0:
        raise ValueError("SOURCE_VALUE_INVALID")
    return n


def sequence(days: Any) -> list[str]:
    if not isinstance(days, list) or not days:
        raise ValueError("SOURCE_DAYS_REQUIRED")
    parsed = [valid_date(x) for x in days]
    if any(y - x != timedelta(days=1) for x, y in zip(parsed, parsed[1:])):
        raise ValueError("SOURCE_DATES_NOT_CONTIGUOUS")
    return days


def source_daily(snapshot: dict[str, Any], kind: str) -> dict[str, dict[str, float]]:
    if not isinstance(snapshot, dict):
        raise ValueError("SOURCE_SNAPSHOT_REQUIRED")
    days = sequence(snapshot.get("days"))
    series = snapshot.get("series")
    if not isinstance(series, list) or not series:
        raise ValueError("SOURCE_SERIES_REQUIRED")
    ret = {d: {k: 0.0 for k in WEIGHTS} for d in days}
    observed: set[str] = set()
    for row in series:
        if not isinstance(row, dict):
            raise ValueError("SOURCE_SERIES_ROW_REQUIRED")
        identity = ((row.get("chain"), row.get("pad")) if kind == "pads"
                    else (row.get("name"),))
        if not all(isinstance(x, str) and x for x in identity):
            raise ValueError("SOURCE_IDENTITY_REQUIRED")
        key = "/".join(identity)
        if key in observed:
            raise ValueError("SOURCE_DUPLICATE_SERIES_ID")
        observed.add(key)
        fields = (("pad_volume", "volume_usd"), ("tokens_launched", "tokens_launched")) if kind == "pads" else (
            ("bot_volume", "volume_usd"), ("bot_fees", "fees_usd"))
        for output_key, source_key in fields:
            vals = row.get(source_key)
            if not isinstance(vals, list) or len(vals) != len(days):
                raise ValueError("SOURCE_SERIES_LENGTH_MISMATCH")
            for day, raw in zip(days, vals):
                ret[day][output_key] += value(raw)
    if snapshot.get("through") != days[-1]:
        raise ValueError("SOURCE_THROUGH_DAY_MISMATCH")
    return ret


def percentile(current: float, history: list[float], *, ties: str) -> float:
    if not history:
        raise ValueError("PERCENTILE_EMPTY_HISTORY")
    if ties not in ("inclusive", "midrank"):
        raise ValueError("PERCENTILE_TIE_POLICY_INVALID")
    below = sum(x < current for x in history)
    equal = sum(x == current for x in history)
    return 100 * (below + (equal if ties == "inclusive" else 0.5 * equal)) / len(history)


def own_history(pads: dict[str, Any], bots: dict[str, Any], *, ties: str = "inclusive") -> list[dict[str, Any]]:
    p = source_daily(pads, "pads")
    b = source_daily(bots, "bots")
    combined = []
    # Any gap in either source becomes an unavailable day; never treat missing as zero.
    for d in sorted(set(p) & set(b)):
        if valid_date(d) >= valid_date(pads["days"][0]):
            combined.append({"day": d, **{f: p[d][f] + b[d][f] for f in WEIGHTS}})
    if not combined:
        raise ValueError("NO_DAILY_SOURCE_OVERLAP")
    sequence([x["day"] for x in combined])
    results: list[dict[str, Any]] = []
    previous: float | None = None
    for i in range(MIN_HISTORY_DAYS, len(combined)):
        current = combined[i]
        hist90 = combined[i - 90:i]
        hist365 = combined[i - 365:i]
        ranks = {
            k: (0.6 * percentile(current[k], [x[k] for x in hist90], ties=ties)
                + 0.4 * percentile(current[k], [x[k] for x in hist365], ties=ties))
            for k in WEIGHTS
        }
        raw = sum(ranks[k] * WEIGHTS[k] for k in WEIGHTS)
        equal = sum(ranks.values()) / len(WEIGHTS)
        smoothed = (raw if previous is None or raw >= previous
                    else COOLDOWN * previous + (1 - COOLDOWN) * raw)
        previous = smoothed
        results.append({"day": current["day"], "own_raw": raw, "own_cool": smoothed,
                        "own_equal": equal, "factor_percentiles": ranks,
                        "asof_provider_first_known": "UNVERIFIED_HISTORIC_BACKFILL"})
    return results


def vendor_history(obj: dict[str, Any]) -> dict[str, int]:
    if not isinstance(obj, dict) or not isinstance(obj.get("history"), list):
        raise ValueError("VENDOR_HISTORY_REQUIRED")
    h: dict[str, int] = {}
    for row in obj["history"]:
        d = row.get("day")
        valid_date(d)
        n = row.get("score")
        if type(n) is not int or not (0 <= n <= 100) or d in h:
            raise ValueError("VENDOR_HISTORY_INVALID")
        h[d] = n
    if not h:
        raise ValueError("VENDOR_HISTORY_EMPTY")
    sequence(sorted(h))
    if obj.get("today", {}).get("day") != sorted(h)[-1]:
        raise ValueError("VENDOR_LATEST_DAY_MISMATCH")
    return h


def kraken_daily(data: dict[str, Any], as_of: datetime) -> dict[str, float]:
    if not isinstance(data, dict) or data.get("error") != []:
        raise ValueError("KRAKEN_ERROR_OR_MISSING")
    found = [v for k, v in data.get("result", {}).items() if isinstance(v, list)]
    if len(found) != 1:
        raise ValueError("KRAKEN_SINGLE_PAIR_REQUIRED")
    ret = {}
    # Kraken's LAST row is always an uncommitted interval at snapshot capture,
    # even when this archival JSON is replayed days/months later.
    candles = found[0]
    if not candles:
        raise ValueError("KRAKEN_CANDLES_REQUIRED")
    for row in candles[:-1]:
        if not isinstance(row, list) or len(row) < 5:
            raise ValueError("KRAKEN_CANDLE_MALFORMED")
        t = datetime.fromtimestamp(int(row[0]), tz=timezone.utc)
        if t.hour or t.minute or t.second:
            raise ValueError("KRAKEN_NOT_UTC_DAILY")
        d = t.date().isoformat()
        if d in ret:
            raise ValueError("KRAKEN_DUPLICATE_DAY")
        # Kraken's public OHLC JSON encodes its close field as a decimal
        # string. Tehc's own numeric series intentionally stay stricter.
        raw_close = row[4]
        if isinstance(raw_close, str):
            if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?", raw_close):
                raise ValueError("KRAKEN_CLOSE_STRING_INVALID")
            raw_close = float(raw_close)
        price = value(raw_close)
        if price <= 0:
            raise ValueError("KRAKEN_NONPOSITIVE_CLOSE")
        if t + timedelta(days=1) <= as_of:
            ret[d] = price
    return ret


def corr(x: list[float], y: list[float]) -> float | None:
    if len(x) != len(y) or len(x) < 3:
        return None
    ma, mb = sum(x) / len(x), sum(y) / len(y)
    a = sum((v - ma) ** 2 for v in x)
    b = sum((v - mb) ** 2 for v in y)
    if a == 0 or b == 0:
        return None
    return sum((v - ma) * (w - mb) for v, w in zip(x, y)) / (a * b) ** 0.5


def avg(rows: list[dict[str, Any]], field: str) -> float | None:
    return sum(x[field] for x in rows) / len(rows) if rows else None


def metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "n": len(rows),
        "sol_3d_mean_pct": avg(rows, "sol3"),
        "sol_7d_mean_pct": avg(rows, "sol7"),
        "sol_btc_3d_relative_mean_pct": avg(rows, "sol_btc3"),
        "sol_3d_drop_gt5_pct": 100 * avg(rows, "severe_down") if rows else None,
    }


def evaluate(pads: dict, bots: dict, trench: dict, price: dict[str, dict], *,
             as_of: datetime, ties: str = "inclusive") -> dict[str, Any]:
    if as_of.tzinfo is None or as_of.utcoffset() != timedelta(0):
        raise ValueError("AS_OF_UTC_REQUIRED")
    own = own_history(pads, bots, ties=ties)
    vendor = vendor_history(trench)
    aligned = [dict(x, vendor=vendor[x["day"]]) for x in own if x["day"] in vendor]
    if not aligned:
        raise ValueError("NO_VENDOR_RECONSTRUCTION_OVERLAP")
    kraken = {sym: kraken_daily(price[sym], as_of) for sym in ("btc", "eth", "sol")}
    targets: list[dict] = []
    def plus(d: str, offset: int) -> str:
        return (valid_date(d) + timedelta(days=offset)).isoformat()
    for idx, row in enumerate(aligned):
        d0, d3, d7 = plus(row["day"], 1), plus(row["day"], 4), plus(row["day"], 8)
        required = [kraken[sym].get(d) for sym in kraken for d in (d0, d3, d7)]
        if any(x is None for x in required):
            continue
        sol0, sol3, sol7 = (kraken["sol"][d] for d in (d0, d3, d7))
        btc0, btc3 = (kraken["btc"][d] for d in (d0, d3))
        r3 = 100 * (sol3 / sol0 - 1)
        targets.append({
            "day": row["day"], "vendor": row["vendor"],
            "own_raw": row["own_raw"], "own_cool": row["own_cool"],
            "delta": row["vendor"] - vendor.get(plus(row["day"], -1), row["vendor"]),
            "sol3": r3, "sol7": 100 * (sol7 / sol0 - 1),
            "sol_btc3": 100 * ((sol3 / sol0) / (btc3 / btc0) - 1),
            "severe_down": int(r3 <= -5),
        })
    recon = {
        "n": len(aligned),
        "mae_raw": avg([{"d": abs(r["own_raw"] - r["vendor"])} for r in aligned], "d"),
        "mae_cool": avg([{"d": abs(r["own_cool"] - r["vendor"])} for r in aligned], "d"),
        "mae_equal": avg([{"d": abs(r["own_equal"] - r["vendor"])} for r in aligned], "d"),
        "corr_raw": corr([r["own_raw"] for r in aligned], [r["vendor"] for r in aligned]),
        "corr_cool": corr([r["own_cool"] for r in aligned], [r["vendor"] for r in aligned]),
        "last_day": aligned[-1]["day"],
        "last_vendor": aligned[-1]["vendor"],
        "last_own_raw": aligned[-1]["own_raw"],
        "last_own_cool": aligned[-1]["own_cool"],
    }
    cold = [x for x in targets if x["vendor"] < 40]
    mid = [x for x in targets if 40 <= x["vendor"] < 60]
    hot = [x for x in targets if x["vendor"] >= 60]
    nonoverlap = [x for i, x in enumerate(targets) if i % 7 == 0]
    groups = {
        "all": metrics(targets), "cold_lt40": metrics(cold),
        "mid_40_59": metrics(mid), "hot_gte60": metrics(hot),
        "cold_warming_delta_gte5": metrics([x for x in targets if x["vendor"] < 40 and x["delta"] >= 5]),
        "cold_cooling_delta_lte_minus5": metrics([x for x in targets if x["vendor"] < 40 and x["delta"] <= -5]),
        "cold_to_active_crossing40": metrics([
            x for x in targets if x["vendor"] >= 40 and
            (vendor.get(plus(x["day"], -1), 101) < 40)
        ]),
        "sampled_every_seventh_day": metrics(nonoverlap),
        "sampled_every_seventh_cold": metrics([x for x in nonoverlap if x["vendor"] < 40]),
        "sampled_every_seventh_hot": metrics([x for x in nonoverlap if x["vendor"] >= 60]),
    }
    return {
        "contract": CONTRACT, "classification": "RETROSPECTIVE_VENDOR_BACKFILL_ONLY",
        "original_point_in_time_source_attested": False,
        "original_forecast_issued_or_delivered": False,
        "predictive_edge_admitted": False,
        "action_or_production_authority": False, "new_scheduled_poll": False,
        "as_of_utc": as_of.isoformat().replace("+00:00", "Z"),
        "vendor_calendar_day_is_not_first_available_at": True,
        "price_entry_assumption": "NEXT_UTC_DAY_CLOSE_AFTER_SOURCE_DAY; NO_TRADING_FEES_OR_FILL_PROOF",
        "vendor_provenance": {"url": "https://tehcscreener.com/api", "latest_day": trench["today"]["day"],
                               "pit_status": "HISTORIC_BACKFILL_FIRST_KNOWN_UNVERIFIED"},
        "benchmark_provenance": {"url": "https://api.kraken.com/0/public/OHLC",
                                  "quote": QUOTE, "latest_incomplete_day": "EXCLUDED"},
        "calculation": {"percentile_ties": ties, "lookback_days": [90, 365],
                        "blend": [0.6, 0.4], "weights": WEIGHTS, "cooldown": COOLDOWN,
                        "first_365_source_days_scored": False},
        "reconstruction": recon,
        "outcomes": {"n": len(targets), "first_day": targets[0]["day"] if targets else None,
                     "last_day": targets[-1]["day"] if targets else None, "groups": groups,
                     "vendor_heat_vs_sol_btc_3d_corr": corr([x["vendor"] for x in targets],
                                                             [x["sol_btc3"] for x in targets]),
                     "vendor_heat_vs_abs_sol_3d_corr": corr([x["vendor"] for x in targets],
                                                             [abs(x["sol3"]) for x in targets]),
                     "overlapping_targets_are_not_independent": True,
                     "thresholds_explored_after_outcomes_no_confirmatory_claim": True},
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    for flag in ("pads", "bots", "trench", "btc", "eth", "sol"):
        p.add_argument("--" + flag, type=Path, required=True)
    p.add_argument("--as-of-utc", required=True)
    p.add_argument("--ties", choices=("inclusive", "midrank"), default="inclusive")
    a = p.parse_args()
    t = datetime.fromisoformat(a.as_of_utc.replace("Z", "+00:00"))
    snapshot_bytes = {k: getattr(a, k).read_bytes()
                      for k in ("pads", "bots", "trench", "btc", "eth", "sol")}
    source = {k: json.loads(data) for k, data in snapshot_bytes.items()}
    result = evaluate(source["pads"], source["bots"], source["trench"],
                      {k: source[k] for k in ("btc", "eth", "sol")}, as_of=t, ties=a.ties)
    # Exact replay-byte hashes make new results inspectable; they DO NOT
    # retroactively attest provider availability, provenance or Nov10 inputs.
    result["snapshot_input_sha256"] = {
        k: hashlib.sha256(data).hexdigest() for k, data in snapshot_bytes.items()
    }
    result["snapshot_hash_scope"] = "CURRENT_REPLAY_BYTES_ONLY_NOT_HISTORICAL_FIRST_KNOWN"
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
